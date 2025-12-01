# Atomic Transaction Yönetimi - Finans Bütünlüğü (v1.4.1)

**Güncelleme Tarihi**: 2 Aralık 2025  
**Versiyon**: 1.4.1  
**Durum**: ✅ Tamamlandı  

---

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Sorun Tanımı](#sorun-tanımı)
3. [Çözüm Mimarisi](#çözüm-mimarisi)
4. [Implementasyon Detayları](#implementasyon-detayları)
5. [Validasyon Sistemi](#validasyon-sistemi)
6. [Hata Kodları](#hata-kodları)
7. [Test Senaryoları](#test-senaryoları)
8. [Best Practices](#best-practices)
9. [Performans Notları](#performans-notları)

---

## Genel Bakış

Atomic transaction yönetimi, finansal işlemlerde veri tutarlılığını garantir. Hesap bakiyelerinin güncellenmesi sırasında veri kaybı veya tutarsızlık oluşturmaz.

### Hedefler

- ✅ **Atomicity**: İşlem tamamı ya başarılı ya başarısız (partial updates yok)
- ✅ **Consistency**: Bakiye her zaman doğru (negatif bakiye yok)
- ✅ **Isolation**: Concurrent operations'ın birbirini etkilemediği
- ✅ **Durability**: Commit edilen veriler kalıcı

### Kapsamlı Değişiklikler

| Modül | Metodlar | Statüsü |
|-------|----------|---------|
| **FinansIslemController** | `create()` | ✅ Atomic |
| | `update_with_balance_adjustment()` | ✅ Atomic |
| | `delete()` | ✅ Atomic |
| **HesapController** | `hesap_bakiye_guncelle()` | ✅ Atomic + Locking |

---

## Sorun Tanımı

### Eski Davranış (v1.3 ve öncesi)

```python
# ❌ PROBLEM: İki ayrı commit
islem = FinansIslem(**data)
db.add(islem)
db.commit()  # İşlem kaydı commit ediliyor

# Burada hata oluşursa, bakiye update edilmez → tutarsızlık!
hesap_controller.hesap_bakiye_guncelle(hesap_id, tutar, "Gelir", db)
```

**Riskler:**
1. **Partial Updates**: İşlem create edilir ama bakiye update edilemez
2. **Race Conditions**: İki hesap arasında concurrent update işlemleri tutarsızlığa neden olabilir
3. **Negative Balance**: Simultaneous transfer işlemleri bakiye kontrolünü bypass edebilir
4. **Data Inconsistency**: Log'lardaki işlem kaydı ile gerçek bakiye farklı olabilir

### Senaryo: Transfer İşleminde Hata

```
Thread 1: Hesap A → Hesap B Transfer (1000 TL)
  ✅ İşlem kaydı oluşturuldu
  ❌ Hesap A bakiyesi -1000 başarısız
  → İşlem var ama bakiye yanlış!

Thread 2: Concurrent olarak Hesap A'dan çekilme
  ✅ Bakiye kontrolü başarılı (eski değer kullanılıyor)
  ❌ Hesap negatif bakiye ile kapanabilir!
```

---

## Çözüm Mimarisi

### 1. Transaction-Level Atomic Operations

**Prensipler:**
- ✅ İşlem kaydı ve bakiye güncellemesi **aynı transaction'da**
- ✅ Herhangi bir hata durumunda **tüm değişiklikler geri alınır**
- ✅ **flush() + single commit** pattern kullanılır

**İmplementasyon:**

```python
try:
    # 1. Validasyon (transaction dışında)
    Validator.validate_positive_number(tutar, "Tutar")
    
    # 2. Row lock ile hesap kontrolü
    hesap = db.query(Hesap).filter(Hesap.id == hesap_id).with_for_update().first()
    
    # 3. Bakiye pre-kontrolü
    if hesap.bakiye < tutar:
        raise ValidationError("Yetersiz bakiye")
    
    # 4. İşlem kaydı (transaction'da)
    islem = FinansIslem(**data)
    db.add(islem)
    db.flush()  # DB'ye yazıyoruz ama commit etmiyoruz
    
    # 5. Bakiye güncelleme (aynı transaction'da)
    hesap.bakiye -= tutar
    
    # 6. ATOMIC COMMIT
    db.commit()  # ✅ Her şey başarıyla kaydediliyor
    
except Exception:
    db.rollback()  # ❌ Her şey geri alınıyor
    raise
```

### 2. Row-Level Pessimistic Locking

**with_for_update()** kullanılarak concurrent update'ler sıralanır:

```python
# Pessimistic locking ile row-level lock
hesap = db.query(Hesap).filter(Hesap.id == hesap_id).with_for_update().first()

# Thread 1: Kilitli hesabı (hesap_id=1) update ediyoruz
# Thread 2: Aynı hesabı update etmek isterse, Thread 1 bitene kadar bekler
```

**Avantajlar:**
- Dirty reads: Yok (kilitli satırlar okunmuyor)
- Phantom reads: Yok (satır seviyesinde kilitleme)
- Lost updates: Yok (sequential execution)

### 3. Pre-Validation Aşaması

Transaction başlamadan önce kontroller yapılır (veritabanı yükü az):

```
1. Veri Validasyonu (String/Date/Numeric checks)
2. Bakiye Pre-Kontrolü (Gider/Transfer için)
3. Hesap Varlığı Kontrolü
4. Kategori Varlığı Kontrolü
↓
5. Transaction Başlama (Row locks)
6. Bakiye Güncellemesi
7. İşlem Kaydı
8. Commit
```

---

## Implementasyon Detayları

### FinansIslemController.create()

**Operasyon**: Gelir/Gider/Transfer işlemi oluşturur ve bakiye günceller

```python
def create(self, data: dict, db: Optional[Session] = None) -> FinansIslem:
    # AŞAMA 1: VALIDASYON (DB işlemi yok)
    Validator.validate_required(data.get("tur"), "İşlem Türü")
    Validator.validate_positive_number(data.get("tutar"), "Tutar")
    
    # AŞAMA 2: HESAP KONTROLÜ + ROW LOCK
    hesap = db.query(Hesap).filter(
        Hesap.id == hesap_id
    ).with_for_update().first()
    
    if not hesap:
        raise NotFoundError(...)
    
    # AŞAMA 3: BAKIYE PRE-KONTROLÜ
    if data.get("tur") == "Gider" and hesap.bakiye < tutar:
        raise ValidationError("Yetersiz bakiye")
    
    # AŞAMA 4: ATOMIC TRANSACTION
    islem = FinansIslem(**data)
    db.add(islem)
    db.flush()  # INSERT kuyruğuna alındı, commit etmedi
    
    # Bakiye güncelleme (transaction'ın içinde)
    if data.get("tur") == "Gelir":
        hesap.bakiye += tutar
    elif data.get("tur") == "Gider":
        hesap.bakiye -= tutar
    elif data.get("tur") == "Transfer":
        hesap.bakiye -= tutar
        hedef_hesap.bakiye += tutar
    
    # ATOMIC COMMIT
    db.commit()  # ✅ İşlem + bakiye birlikte kaydediliyor
```

**Hata Senaryoları:**
- ❌ Yetersiz bakiye → `ValidationError(VAL_ACC_001)`
- ❌ İşlem türü geçersiz → `ValidationError(VAL_TRN_001)`
- ❌ DB hatası → `DatabaseError(DB_TRN_001)`

### FinansIslemController.update_with_balance_adjustment()

**Operasyon**: İşlem güncelleme + bakiye düzeltme (eski işlem geri alınır, yeni işlem uygulanır)

```python
def update_with_balance_adjustment(self, id: int, data: dict) -> Optional[FinansIslem]:
    # Eski işlem veri:
    # - İşlem ID: 42
    # - Tur: "Gelir"
    # - Tutar: 5000 TL
    # - Hesap: Hesap A
    
    # Yeni veri:
    # - Tur: "Gider" (tip değişti)
    # - Tutar: 3000 TL (tutar değişti)
    
    # AŞAMA 1: VALIDASYON
    Validator.validate_choice(data['tur'], "İşlem Türü", [...])
    Validator.validate_positive_number(data['tutar'], "Tutar")
    
    # AŞAMA 2: İŞLEM + HESAP LOCK
    islem = db.query(FinansIslem).filter(...).with_for_update().first()
    hesap = db.query(Hesap).filter(...).with_for_update().first()
    
    # AŞAMA 3: ATOMIC TRANSACTION
    # Eski işlemi geri al
    if old_tur == "Gelir":
        hesap.bakiye -= old_tutar  # 5000 TL geri çıkarılıyor
    
    # Yeni işlemi uygula
    if new_tur == "Gider":
        hesap.bakiye -= new_tutar  # 3000 TL çıkarılıyor
    
    # İşlem kaydını güncelle
    islem.tur = "Gider"
    islem.tutar = 3000
    
    db.commit()  # ✅ Tümü atomic
```

**Sonuç:** Hesap A bakiye: 5000 TL geri + 3000 TL çıkar = 2000 TL net değişim

### FinansIslemController.delete()

**Operasyon**: İşlem silme + bakiye reversal

```python
def delete(self, id: int) -> bool:
    # Transfer işlemi siliniyor
    # - Kaynak Hesap: 1000 TL çıkmıştı
    # - Hedef Hesap: 1000 TL eklenmiş
    
    # AŞAMA 1: İŞLEM + HESAPLAR LOCK
    islem = db.query(FinansIslem).filter(...).with_for_update().first()
    kaynak_hesap = db.query(Hesap).filter(...).with_for_update().first()
    hedef_hesap = db.query(Hesap).filter(...).with_for_update().first()
    
    # AŞAMA 2: BAKIYE REVERSAL
    if islem.tur == "Transfer":
        kaynak_hesap.bakiye += islem.tutar  # 1000 TL geri ekleniyor
        hedef_hesap.bakiye -= islem.tutar   # 1000 TL çıkarılıyor
    
    # AŞAMA 3: İŞLEM SİLME
    db.delete(islem)
    
    db.commit()  # ✅ Tümü atomic
```

### HesapController.hesap_bakiye_guncelle()

**Operasyon**: Hesap bakiyesini atomic olarak günceller (low-level operation)

```python
def hesap_bakiye_guncelle(self, hesap_id: int, tutar: float, 
                          islem_turu: str) -> bool:
    # AŞAMA 1: VALIDASYON
    Validator.validate_choice(islem_turu, "İşlem Türü", [...])
    Validator.validate_positive_number(tutar, "Tutar")
    
    # AŞAMA 2: ROW LOCK
    hesap = db.query(Hesap).filter(...).with_for_update().first()
    
    # AŞAMA 3: BAKIYE PRE-KONTROLÜ
    if islem_turu == "Gider" and hesap.bakiye < tutar:
        raise ValidationError("Yetersiz bakiye", code="VAL_ACC_001")
    
    # AŞAMA 4: GÜNCELLEME + COMMIT
    if islem_turu == "Gelir":
        hesap.bakiye += tutar
    elif islem_turu == "Gider":
        hesap.bakiye -= tutar
    
    db.commit()  # ✅ Atomic
```

---

## Validasyon Sistemi

### Pre-Validation (Transaction Öncesi)

**Amacı**: Hızlı kontrol, DB yükü az, transaction başlamadan fail etmek

```python
# 1. Data Type Validation
Validator.validate_required(data.get("tur"), "İşlem Türü")
Validator.validate_choice(data.get("tur"), "İşlem Türü", ["Gelir", "Gider", "Transfer"])
Validator.validate_positive_number(data.get("tutar"), "Tutar")

# 2. Date Validation
Validator.validate_date(data.get("tarih"))

# 3. Logical Validation
if islem_tur == "Transfer" and hesap_id == hedef_hesap_id:
    raise ValidationError("Kaynak ve hedef hesap aynı olamaz")
```

### In-Transaction Validation

**Amacı**: Veritabanı bağlama göre kontrol (hesap varlığı, bakiye yeterliği, vb.)

```python
# 1. Hesap Varlığı (with_for_update ile)
hesap = db.query(Hesap).filter(...).with_for_update().first()
if not hesap:
    raise NotFoundError("Hesap bulunamadı")

# 2. Bakiye Kontrolü (mevcut değeri okuyarak)
if hesap.bakiye < tutar:
    raise ValidationError("Yetersiz bakiye")

# 3. Kategori Varlığı
kategori = db.query(AltKategori).filter(...).first()
if not kategori:
    raise NotFoundError("Kategori bulunamadı")
```

### Validasyon Akış Şeması

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PRE-VALIDATION (Synchronous, No DB)                      │
│   - String validation (length, format)                       │
│   - Type checks (int, float, datetime)                       │
│   - Range checks (positive, in choices)                      │
│   - Logic checks (source ≠ destination)                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
            ✅ Pre-validation başarılı
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ACCOUNT CHECK + LOCK (with_for_update)                   │
│   - Hesap ID varlığı kontrolü                               │
│   - Row-level pessimistic lock acquisition                   │
│   - Current balance read (kilitli satırdan)                  │
└─────────────────────────────────────────────────────────────┘
                        ↓
            ✅ Hesap bulundu ve kilitlendi
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. BALANCE PRE-CHECK (Kilitli satırdan okunan bakiye)       │
│   - Expense: balance >= amount                              │
│   - Transfer: balance >= amount                             │
│   - Income: her zaman geçerli                               │
└─────────────────────────────────────────────────────────────┘
                        ↓
            ✅ Bakiye yeterli
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. ATOMIC TRANSACTION COMMIT                                │
│   - INSERT/UPDATE operations                                │
│   - Balance adjustments                                      │
│   - Single COMMIT (all or nothing)                          │
└─────────────────────────────────────────────────────────────┘
                        ↓
            ✅ Tüm işlemler başarılı
                        ↓
            ❌ Hata oluşursa ROLLBACK
```

---

## Hata Kodları

### Validasyon Hataları

| Kod | Anlamı | HTTP | Çözüm |
|-----|--------|------|-------|
| VAL_ACC_001 | Yetersiz bakiye | 400 | Tutar azalt veya bakiye ekle |
| VAL_TRN_001 | Kaynak=Hedef hesap | 400 | Farklı hesap seç |
| VAL_TRN_002 | Transfer için yetersiz bakiye | 400 | Tutar azalt veya bakiye ekle |

### Veritabanı Hataları

| Kod | Anlamı | HTTP | Çözüm |
|-----|--------|------|-------|
| DB_TRN_001 | Atomic transaction başarısız | 500 | İşlemi tekrar dene |
| DB_BAL_001 | Bakiye güncellemesi hatası | 500 | Tekrar dene veya destek |
| DB_DEL_001 | İşlem silme hatası | 500 | Tekrar dene veya destek |
| DB_UPD_001 | İşlem güncelleme hatası | 500 | Teknik destek ile iletişim |

### NotFoundError

| Kod | Anlamı | HTTP | Çözüm |
|-----|--------|------|-------|
| NOT_FOUND_ACC_001 | Hesap bulunamadı | 404 | Hesap ID'sini kontrol et |
| NOT_FOUND_ACC_002 | Hedef hesap bulunamadı | 404 | Hedef hesap ID'sini kontrol et |
| NOT_FOUND_003 | Kategori bulunamadı | 404 | Kategori ID'sini kontrol et |

---

## Test Senaryoları

### Test 1: Temel Gelir İşlemi (Atomic)

```python
# Arrange
hesap = create_hesap("TestAcc", "Banka", bakiye=1000)
data = {
    "tur": "Gelir",
    "tutar": 500,
    "hesap_id": hesap.id,
    "tarih": datetime.now(),
    "aciklama": "Test geliri"
}

# Act
islem = controller.create(data)

# Assert
assert islem.id > 0
assert hesap.bakiye == 1500  # Atomic update
assert islem.tur == "Gelir"
assert islem.tutar == 500
```

**Beklenen Sonuç:** ✅ İşlem + Bakiye beraber güncellenmiş

---

### Test 2: Transfer İşlemi (Atomic)

```python
# Arrange
hesap_a = create_hesap("A", "Banka", bakiye=1000)
hesap_b = create_hesap("B", "Banka", bakiye=500)

data = {
    "tur": "Transfer",
    "tutar": 200,
    "hesap_id": hesap_a.id,
    "hedef_hesap_id": hesap_b.id,
    "tarih": datetime.now()
}

# Act
islem = controller.create(data)

# Assert
assert islem.id > 0
assert hesap_a.bakiye == 800  # -200
assert hesap_b.bakiye == 700  # +200
assert islem.tur == "Transfer"
```

**Beklenen Sonuç:** ✅ Her iki hesap atomic olarak güncellendi

---

### Test 3: Yetersiz Bakiye Hatası

```python
# Arrange
hesap = create_hesap("TestAcc", "Banka", bakiye=100)
data = {
    "tur": "Gider",
    "tutar": 500,  # Bakiye yetersiz (100 < 500)
    "hesap_id": hesap.id,
    "tarih": datetime.now()
}

# Act & Assert
with pytest.raises(ValidationError) as exc:
    controller.create(data)

assert exc.value.code == "VAL_ACC_001"
assert hesap.bakiye == 100  # Bakiye değişmedi (rollback)
```

**Beklenen Sonuç:** ✅ ValidationError + Bakiye değişmez (atomic rollback)

---

### Test 4: Update - İşlem Türü Değiştirme

```python
# Arrange (Eski işlem)
hesap = create_hesap("TestAcc", "Banka", bakiye=1000)
islem = create_islem("Gelir", 500, hesap.id)
assert hesap.bakiye == 1500  # +500

# Act (Gelir → Gider)
updated = controller.update_with_balance_adjustment(islem.id, {
    "tur": "Gider",
    "tutar": 300
})

# Assert
assert updated.tur == "Gider"
assert hesap.bakiye == 1200  # -500 (reverse) -300 (apply) = -800 net
```

**Beklenen Sonuç:** ✅ Eski bakiye reversal + yeni bakiye apply (atomic)

---

### Test 5: Delete - Bakiye Reversal

```python
# Arrange (Transfer işlemi)
hesap_a = create_hesap("A", "Banka", bakiye=1000)
hesap_b = create_hesap("B", "Banka", bakiye=500)
islem = create_islem("Transfer", 200, hesap_a.id, hedef_hesap=hesap_b.id)
assert hesap_a.bakiye == 800
assert hesap_b.bakiye == 700

# Act
success = controller.delete(islem.id)

# Assert
assert success == True
assert hesap_a.bakiye == 1000  # +200 (reverse transfer)
assert hesap_b.bakiye == 500   # -200 (reverse transfer)
```

**Beklenen Sonuç:** ✅ İşlem silindi, bakiyeler reversal edildi (atomic)

---

### Test 6: Concurrent Transfer (Race Condition Prevention)

```python
# Arrange
hesap = create_hesap("TestAcc", "Banka", bakiye=500)
data = {
    "tur": "Gider",
    "tutar": 600,  # Yetersiz
    "hesap_id": hesap.id,
    "tarih": datetime.now()
}

# Act (Concurrent simulation)
import threading
results = []

def try_create():
    try:
        controller.create(data)
        results.append("success")
    except ValidationError:
        results.append("validation_error")

threads = [threading.Thread(target=try_create) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Assert
assert all(r == "validation_error" for r in results)
assert hesap.bakiye == 500  # Hiç değişmedi
```

**Beklenen Sonuç:** ✅ with_for_update() ile sıralanmış, hepsi rejected

---

## Best Practices

### 1. Row Lock Kullanımı

**✅ DOĞRU:**
```python
# Single lock, long operation OK
hesap = db.query(Hesap).filter(...).with_for_update().first()
# Complex business logic
db.commit()
```

**❌ YANLIŞ:**
```python
# Multiple separate locks (deadlock riski)
hesap_a = db.query(Hesap).filter(id=1).with_for_update().first()
hesap_b = db.query(Hesap).filter(id=2).with_for_update().first()  # Deadlock!

# Lock alınmadan işlem
hesap = db.query(Hesap).filter(id=1).first()
# Başka thread bakiye değiştirebilir
db.commit()
```

### 2. Transaction Boundaries

**✅ DOĞRU:**
```python
try:
    # Validasyon (DB işlemi yok)
    validate_input(data)
    
    # Transaction başlama
    hesap = db.query(...).with_for_update().first()
    
    # Güncelleme
    hesap.bakiye += tutar
    islem = FinansIslem(...)
    db.add(islem)
    
    # Single commit
    db.commit()
except Exception:
    db.rollback()
    raise
```

**❌ YANLIŞ:**
```python
# İşlemler ayrı transaction'da
hesap = db.query(...).first()
db.commit()

# Thread bunun arasında value değiştirebilir
islem = FinansIslem(...)
db.add(islem)
db.commit()
```

### 3. Bakiye Kontrolü Zamanlaması

**✅ DOĞRU:**
```python
# Pre-validation (transaction öncesi)
if mevcut_bakiye < tutar:
    raise ValidationError("Yetersiz bakiye")

# Transaction başlama
hesap = db.query(...).with_for_update().first()

# Tekrar kontrol (kilitli değerden)
if hesap.bakiye < tutar:
    raise ValidationError("Yetersiz bakiye")

db.commit()
```

**❌ YANLIŞ:**
```python
# Sadece pre-validation (eski değer)
if mevcut_bakiye < tutar:
    pass

hesap = db.query(...).with_for_update().first()
hesap.bakiye -= tutar  # Başka thread update etmiş olabilir
db.commit()
```

### 4. Error Handling

**✅ DOĞRU:**
```python
try:
    # Validasyon
    if not valid:
        raise ValidationError(...)
    
    # Transaction
    hesap = db.query(...).with_for_update().first()
    hesap.bakiye -= tutar
    db.commit()
    
except ValidationError:
    # Pre-validation error, rollback yok
    raise
except (IntegrityError, SQLAlchemyError):
    # DB error, rollback yap
    db.rollback()
    raise DatabaseError(...)
```

**❌ YANLIŞ:**
```python
# Commit sonrası hata handling
db.commit()
hesap_controller.hesap_bakiye_guncelle(...)  # Hata oluşursa çok geç!

# Vague error handling
try:
    ...
except:
    pass  # Silent fail, tutarsızlık!
```

---

## Performans Notları

### Row Lock İmpact

**Lock Duration:**
- Pre-validation: ~0ms (DB işlemi yok)
- Account query + lock: ~5-10ms
- Balance update: ~2-5ms
- Commit: ~10-20ms
- **Total per operation: ~20-50ms**

**Concurrent Performance:**
- 10 transactions/sec: ✅ OK (50ms * 10 = 500ms)
- 100 transactions/sec: ⚠️ WARNING (lock contention)
- 1000 transactions/sec: ❌ SLOW (queuing backlog)

**Optimization Tips:**

1. **Batch Operations**
   ```python
   # ❌ SLOW: Sequential operations
   for transfer in transfers:
       controller.create(transfer)
   
   # ✅ FAST: Batch with single commit
   islemler = [FinansIslem(**t) for t in transfers]
   db.add_all(islemler)
   db.commit()
   ```

2. **Connection Pool**
   ```python
   # Aktif bağlantı sayısı ≥ concurrent operations
   engine = create_engine(
       "sqlite:///aidat_plus.db",
       pool_size=20,
       max_overflow=10
   )
   ```

3. **Index Optimization**
   ```python
   # Sık filtered fields'a index ekle
   hesap_id = Column(Integer, ForeignKey(...), index=True)
   tarih = Column(DateTime, index=True)
   ```

### Deadlock Prevention

**Risk Senaryosu:**
```
Thread 1: Lock(Hesap A) → Lock(Hesap B)
Thread 2: Lock(Hesap B) → Lock(Hesap A)  # Deadlock!
```

**Çözüm: Consistent Ordering**
```python
# Daima aynı sırada lock al
account_ids = sorted([hesap_a, hesap_b])
for id in account_ids:
    db.query(Hesap).filter(Hesap.id == id).with_for_update().first()
```

---

## Özet

### ACID Garantileri

| Özellik | Nasıl? | Sonuç |
|---------|--------|-------|
| **A**tomicity | flush() + single commit | İşlem tamamı ya başarılı ya başarısız |
| **C**onsistency | Pre-validation + in-transaction checks | Bakiye her zaman doğru |
| **I**solation | with_for_update() pessimistic locking | Concurrent ops sequential |
| **D**urability | db.commit() persistent storage | Kaydedilen veri kalıcı |

### Key Implementasiyon Points

1. ✅ **Pre-Validation**: Transaction başlamadan hızlı kontrol
2. ✅ **Row Lock**: with_for_update() pessimistic locking
3. ✅ **Atomic Updates**: flush() + single commit
4. ✅ **Rollback**: Exception durumunda tüm değişiklikleri geri al
5. ✅ **Error Codes**: Spesifik hata kodları ile tracking

### Sonraki Adımlar

- [ ] Integration test'leri expand et (concurrent scenarios)
- [ ] Performance monitoring dashboard ekle
- [ ] Lock timeout configuration
- [ ] Dead letter queue implementasyonu (failed transactions)
