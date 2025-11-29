# Sakin Tarih Validasyon Sistemi

## Genel Bakış

Bu dokümantasyon, sakin yönetiminde tarih çakışmalarını önlemek için uygulanan validasyon kurallarını açıklamaktadır.

**Problem**: Aynı daireye yeni sakin eklenirken, giriş/çıkış tarihleri çakışabiliyor.
- Örnek: Ali (01.01-31.12.2024) + Veli (15.12-20.12.2024) = Aynı anda 2 sakin!

**Çözüm**: Üç seviye tarih validasyon kuralı uygulanıyor.

---

## Önemli Notlar ve Root Causes

⚠️ **Tarih Çakışması Kontrol Kuralları**:
1. Create() ve Update() metodlarında **HER ZAMAN** yapılmalı (aktif/pasif fark etmez)
2. daire_id ve giris_tarihi zorunlu olduğunda tetiklenir
3. Pasif sakinde daire_id=None ise eski_daire_id kontrol edilir
4. _parse_date() check sırası: datetime ÖNCE, sonra date (datetime subclass)

### Root Causes (Hata Analizleri)

**Problem 1: Create metodunda kontrol atlanması**
```
Eski Kod (HATALI):
self._validate_daire_tarih_cakmasi(...)  # Hep çağrılıyor

Yeni Kod (DOĞRU):
if daire_id and giris_tarihi:  # Kontrol etilmesi gereken koşullar
    self._validate_daire_tarih_cakmasi(...)
```
**Neden**: Normal aktif sakin eklenirken (cikis_tarihi yok) kontrol atlanabilirdi.

**Problem 2: _parse_date check sırası**
```
Eski Kod (HATALI):
if isinstance(date_value, date):  # ← date check önce
    return datetime.combine(...)
if isinstance(date_value, datetime):  # ← datetime check sonra
    return date_value

Yeni Kod (DOĞRU):
if isinstance(date_value, datetime):  # ← datetime check ÖNCE
    return date_value
if isinstance(date_value, date):  # ← date check sonra
    return datetime.combine(...)
```
**Neden**: Python'da `datetime` da `date`'in subclass'ıdır. date check önce yapılırsa datetime objeler yanlış parsing edilir.

**Problem 3: Pasif sakin düzenlemede daire bulunamması**
```
Eski Kod (HATALI):
daire_id = data.get("daire_id", existing.daire_id)
# Pasif sakinde daire_id=None olduğu için kontrol atlanıyor

Yeni Kod (DOĞRU):
daire_id = data.get("daire_id", existing.daire_id)
if daire_id is None and existing.eski_daire_id is not None:
    daire_id = existing.eski_daire_id  # ← Geçmiş daire kullan
```
**Neden**: Pasif sakin `pasif_yap()` çağrıldığında `daire_id=None`, `eski_daire_id=[eski_daire]` olur. Validasyon sırasında eski daireyi kontrol etmeli.

---

## Validasyon Kuralları

### 1. Kural: Çıkış > Giriş (VAL_SAKN_001)

**Açıklama**: Sakin ayrılış tarihi her zaman giriş tarihinden sonra olmalıdır.

**Formula**: `cikis_tarihi > giris_tarihi`

**Hata Kodu**: `VAL_SAKN_001`

**Örnek**:
- ✅ Geçerli: Giriş 01.01.2024, Çıkış 31.12.2024
- ❌ Geçersiz: Giriş 01.06.2024, Çıkış 31.05.2024 (tarihler ters)
- ❌ Geçersiz: Giriş 01.01.2024, Çıkış 01.01.2024 (aynı tarih)

**Hata Mesajı**: "Çıkış tarihi giriş tarihinden sonra olmalıdır."

---

### 2. Kural: Dairede Aktif Sakin Yok (VAL_SAKN_002)

**Açıklama**: Aynı anda dairede sadece bir aktif sakin bulunabilir (cikis_tarihi=None).

**Kural Detayı**:
- Yeni sakin ekleniyorsa (cikis_tarihi=None) ve dairede zaten aktif sakin varsa **HATA**
- Pasif sakin (cikis_tarihi!=None) varsa sorun yok

**Hata Kodu**: `VAL_SAKN_002`

**Örnek Senaryo 1** (Hata):
```
Daire 101:
├── Ali (Aktif - cikis_tarihi=NULL) ✅ Var
└── Yeni Sakin (Aktif - cikis_tarihi=NULL) ❌ Eklenemez!
```

**Örnek Senaryo 2** (Başarılı):
```
Daire 101:
├── Ali (Pasif - cikis_tarihi=31.12.2023) ✅ Var
└── Veli (Aktif - cikis_tarihi=NULL) ✅ Eklenebilir
```

**Hata Mesajı**: "Bu dairede zaten aktif sakin bulunmaktadır: [Ad-Soyad]"

---

### 3. Kural: Giriş > Eski Sakin Ayrılış (VAL_SAKN_003)

**Açıklama**: Yeni sakin giriş tarihi, dairede olan eski sakinlerin ayrılış tarihinden sonra olmalıdır.

**Formula**: `yeni_sakin.giris_tarihi > eski_sakin.cikis_tarihi`

**Hata Kodu**: `VAL_SAKN_003`

**Örnek Senaryo 1** (Başarılı):
```
Daire 101:
├── Ali (01.01.2024 - 31.12.2024) ✅ Çıkış
└── Veli (Giriş 01.01.2025 >) ✅ Eklenebilir (sonrasında giris)
```

**Örnek Senaryo 2** (HATA):
```
Daire 101:
├── Ali (01.01.2024 - 31.12.2024) ✅ Çıkış
└── Veli (Giriş 25.12.2024 <) ❌ Hata! (Ali ile çakışıyor)
```

**Hata Mesajı**: "Yeni sakin giriş tarihi [Ad-Soyad]'ın ayrılış tarihinden sonra olmalıdır (31.12.2024)."

---

### 4. Kural: Tarih Format Validasyonu (VAL_SAKN_004)

**Açıklama**: Tarih değerleri DD.MM.YYYY formatında olmalıdır.

**Kabul Edilen Formatlar**:
- String: "01.01.2024"
- Python datetime: datetime(2024, 1, 1)
- Python date: date(2024, 1, 1)

**Hata Kodu**: `VAL_SAKN_004`

**Hata Mesajı**: "Geçersiz tarih formatı. DD.MM.YYYY kullanınız."

---

## Metodlar

### `_parse_date(date_value)`

String/datetime/date değerini `datetime` objesine çevirir.

```python
def _parse_date(self, date_value: Union[str, datetime, date, None]) -> Optional[datetime]:
```

**Parametreler**:
- `date_value`: Tarih (str "DD.MM.YYYY" | datetime | date | None)

**Dönüş**: `datetime` object veya None

**Raises**: `ValidationError` (VAL_SAKN_004) - Geçersiz format

**Örnekler**:
```python
# String parsing
parsed = controller._parse_date("01.01.2024")  # datetime(2024, 1, 1)

# datetime object - aynı döner
parsed = controller._parse_date(datetime.now())  # datetime.now()

# date object - datetime'a çevirir
parsed = controller._parse_date(date(2024, 1, 1))  # datetime(2024, 1, 1)

# None - None döner
parsed = controller._parse_date(None)  # None
```

---

### `_validate_daire_tarih_cakmasi()`

Aynı dairede tarih çakışmasını kontrol eder (3 kuralı uygular).

```python
def _validate_daire_tarih_cakmasi(
    self, 
    daire_id: int, 
    giris_tarihi: Optional[datetime],
    cikis_tarihi: Optional[datetime],
    exclude_sakin_id: Optional[int] = None,
    db: Optional[Session] = None
) -> None:
```

**Parametreler**:
- `daire_id`: Daire ID'si
- `giris_tarihi`: Giriş tarihi (datetime)
- `cikis_tarihi`: Çıkış tarihi (datetime)
- `exclude_sakin_id`: Güncellemede hariç tutulacak sakin ID (opsiyonel)
- `db`: Veritabanı session (opsiyonel)

**Raises**:
- `ValidationError` (VAL_SAKN_001) - Çıkış > Giriş değil
- `ValidationError` (VAL_SAKN_002) - Dairede zaten aktif sakin var
- `ValidationError` (VAL_SAKN_003) - Giriş > Eski sakin ayrılış değil

**Örnek Kullanım**:
```python
# Yeni sakin oluşturma sırasında
self._validate_daire_tarih_cakmasi(
    daire_id=5,
    giris_tarihi=datetime(2024, 1, 1),
    cikis_tarihi=datetime(2024, 12, 31),
    db=session
)

# Sakin güncelleme sırasında (kendi kaydını hariç tut)
self._validate_daire_tarih_cakmasi(
    daire_id=5,
    giris_tarihi=datetime(2024, 1, 1),
    cikis_tarihi=None,
    exclude_sakin_id=existing_sakin_id,
    db=session
)
```

---

## Entegrasyon

### `create()` Metodunda

```python
def create(self, data: dict, db: Session = None) -> Sakin:
    # ... diğer validasyonlar ...
    
    # Tarih parsing (String → datetime)
    tahsis_tarihi = self._parse_date(data.get("tahsis_tarihi"))      # VAL_SAKN_004
    giris_tarihi = self._parse_date(data.get("giris_tarihi"))        # VAL_SAKN_004
    cikis_tarihi = self._parse_date(data.get("cikis_tarihi"))        # VAL_SAKN_004
    
    # Tarih çakışması validasyonu (HER ZAMAN yapılmalı)
    daire_id = data.get("daire_id")
    if daire_id and giris_tarihi:  # daire_id ve giris_tarihi zorunlu
        self._validate_daire_tarih_cakmasi(
            daire_id=daire_id,
            giris_tarihi=giris_tarihi,
            cikis_tarihi=cikis_tarihi,
            db=session
        )  # VAL_SAKN_001, VAL_SAKN_002, VAL_SAKN_003
    
    # Parsed tarihler veri sözlüğüne koyun
    if tahsis_tarihi is not None:
        data["tahsis_tarihi"] = tahsis_tarihi
    if giris_tarihi is not None:
        data["giris_tarihi"] = giris_tarihi
    if cikis_tarihi is not None:
        data["cikis_tarihi"] = cikis_tarihi
    
    return super().create(data, session)
```

### `update()` Metodunda

```python
def update(self, id: int, data: dict, db: Session = None) -> Optional[Sakin]:
    # ... diğer validasyonlar ...
    
    # Tarih parsing (String → datetime)
    if "tahsis_tarihi" in data:
        data["tahsis_tarihi"] = self._parse_date(data.get("tahsis_tarihi"))
    if "giris_tarihi" in data:
        data["giris_tarihi"] = self._parse_date(data.get("giris_tarihi"))
    if "cikis_tarihi" in data:
        data["cikis_tarihi"] = self._parse_date(data.get("cikis_tarihi"))
    
    # Güncel sakin bilgisini al
    existing = session.query(Sakin).filter(Sakin.id == id).first()
    if existing:
        # Tarih çakışması validasyonu (HER ZAMAN yapılmalı, kendi kaydı hariç)
        giris_tarihi = data.get("giris_tarihi", existing.giris_tarihi)
        cikis_tarihi = data.get("cikis_tarihi", existing.cikis_tarihi)
        # Pasif sakinde daire_id=None ise eski_daire_id kullan
        daire_id = data.get("daire_id", existing.daire_id)
        if daire_id is None and existing.eski_daire_id is not None:
            daire_id = existing.eski_daire_id
        
        if daire_id and giris_tarihi:  # daire_id ve giris_tarihi zorunlu
            self._validate_daire_tarih_cakmasi(
                daire_id=daire_id,
                giris_tarihi=giris_tarihi,
                cikis_tarihi=cikis_tarihi,
                exclude_sakin_id=id,  # Kendini hariç tut
                db=session
            )
    
    return super().update(id, data, session)
```

---

## Test Senaryoları

### Senaryo 1: Basit Sakin Oluşturma

```python
controller = SakinController()

# ✅ Başarılı
data = {
    "ad_soyad": "Ali Yıldız",
    "daire_id": 5,
    "giris_tarihi": "01.01.2024",
    "cikis_tarihi": "31.12.2024"
}
sakin = controller.create(data)  # Başarılı
```

### Senaryo 2: Çakışan Tarihler (VAL_SAKN_001)

```python
# ❌ Hata: Çıkış < Giriş
data = {
    "ad_soyad": "Veli Kaya",
    "daire_id": 5,
    "giris_tarihi": "31.12.2024",
    "cikis_tarihi": "01.01.2024"
}
try:
    sakin = controller.create(data)
except ValidationError as e:
    print(e.message)  # "Çıkış tarihi giriş tarihinden sonra olmalıdır."
    print(e.code)     # "VAL_SAKN_001"
```

### Senaryo 3: Dairede Aktif Sakin Var (VAL_SAKN_002)

```python
# Dairede 5'te Ali zaten aktif
# ❌ Hata: Dairede zaten aktif sakin var
data = {
    "ad_soyad": "Veli Kaya",
    "daire_id": 5,  # Ali'nin dairesi
    "giris_tarihi": "01.07.2024"  # cikis_tarihi=None (aktif)
}
try:
    sakin = controller.create(data)
except ValidationError as e:
    print(e.message)  # "Bu dairede zaten aktif sakin bulunmaktadır: Ali Yıldız"
    print(e.code)     # "VAL_SAKN_002"
```

### Senaryo 4: Tarih Çakışması (VAL_SAKN_003)

```python
# Dairede 5'te:
# - Ali: 01.01.2024 - 31.12.2024
# - Veli ekleniyorsa: 25.12.2024 başlangıç (Ali ile çakışıyor!)

# ❌ Hata: Tarih çakışması
data = {
    "ad_soyad": "Veli Kaya",
    "daire_id": 5,
    "giris_tarihi": "25.12.2024",  # Ali'nin çıkışından önce
    "cikis_tarihi": "31.12.2024"
}
try:
    sakin = controller.create(data)
except ValidationError as e:
    print(e.message)  # "Yeni sakin giriş tarihi Ali Yıldız'ın ayrılış tarihinden sonra olmalıdır (31.12.2024)."
    print(e.code)     # "VAL_SAKN_003"

# ✅ Başarılı: Tarihler çakışmıyor
data["giris_tarihi"] = "01.01.2025"  # Ali'nin çıkışından sonra
sakin = controller.create(data)  # Başarılı
```

### Senaryo 5: Pasif Sakin Yönetimi

```python
# Dairede 5'te:
# - Ali: 01.01.2024 - 31.12.2024 (pasif, çıkış tarihi var)
# - Yeni sakin ekleniyorsa

# ✅ Başarılı: Pasif sakinin dışında yeni sakin eklenebilir
data = {
    "ad_soyad": "Veli Kaya",
    "daire_id": 5,
    "giris_tarihi": "01.01.2025",  # Başlangıç tarihi = Ali'nin çıkış+1 gün
    "cikis_tarihi": None  # Aktif
}
sakin = controller.create(data)  # Başarılı
```

### Senaryo 6: String & DateTime Parsing

```python
from datetime import datetime, date

# ✅ String parsing
data = {"giris_tarihi": "01.01.2024"}  # String
sakin = controller.create(data)  # Başarılı - parsed

# ✅ datetime parsing
data = {"giris_tarihi": datetime(2024, 1, 1)}  # datetime
sakin = controller.create(data)  # Başarılı - aynı kalır

# ✅ date parsing
data = {"giris_tarihi": date(2024, 1, 1)}  # date
sakin = controller.create(data)  # Başarılı - datetime'a çevirilir

# ❌ Hata: Geçersiz format
data = {"giris_tarihi": "01/01/2024"}  # Yanlış format
try:
    sakin = controller.create(data)
except ValidationError as e:
    print(e.code)  # "VAL_SAKN_004"
```

---

## Hata Kodları Özeti

| Kod | Açıklama | Tetikleyici |
|-----|----------|-------------|
| **VAL_SAKN_001** | Çıkış > Giriş değil | cikis_tarihi ≤ giris_tarihi |
| **VAL_SAKN_002** | Dairede aktif sakin var | Yeni aktif sakin + mevcut aktif sakin |
| **VAL_SAKN_003** | Tarih çakışması | Yeni giriş ≤ Eski çıkış |
| **VAL_SAKN_004** | Geçersiz tarih formatı | String formatı ≠ DD.MM.YYYY |

---

## Best Practices

### 1. UI'dan Sakin Ekleme

```python
# ui/sakin_panel.py
try:
    data = {
        "ad_soyad": entry_ad.get(),
        "daire_id": selected_daire_id,
        "giris_tarihi": entry_giris.get(),  # "01.01.2024"
        "cikis_tarihi": entry_cikis.get()   # "31.12.2024"
    }
    sakin = self.controller.create(data)
    messagebox.showinfo("Başarı", "Sakin eklendi")
except ValidationError as e:
    if e.code == "VAL_SAKN_001":
        messagebox.showerror("Hata", "Çıkış tarihi giriş tarihinden sonra olmalıdır")
    elif e.code == "VAL_SAKN_002":
        messagebox.showerror("Hata", f"Bu dairede zaten aktif sakin var: {e.message}")
    elif e.code == "VAL_SAKN_003":
        messagebox.showerror("Hata", e.message)
    elif e.code == "VAL_SAKN_004":
        messagebox.showerror("Hata", "Tarih formatı DD.MM.YYYY olmalıdır")
```

### 2. Sakin Güncelleme

```python
# Tarih güncellemesi sırasında
try:
    data = {
        "cikis_tarihi": "15.06.2024"  # Çıkış tarihi ekle
    }
    sakin = self.controller.update(sakin_id, data)
    messagebox.showinfo("Başarı", "Sakin güncelendi")
except ValidationError as e:
    messagebox.showerror("Hata", str(e.message))
```

### 3. Daire Taşıma (daire_id değişimi)

```python
# Sakin başka daireye taşıyorken
try:
    # Çıkış tarihi ile pasif yap
    controller.pasif_yap(sakin_id, cikis_tarihi=datetime.now())
    
    # Yeni daire + giriş tarihi ile yeni sakin oluştur
    new_data = {
        "ad_soyad": sakin.ad_soyad,
        "daire_id": new_daire_id,
        "giris_tarihi": datetime.now()
    }
    new_sakin = controller.create(new_data)
except ValidationError as e:
    messagebox.showerror("Hata", str(e.message))
```

---

## Dokümantasyon Tarihi

- **Oluşturulma**: 29 Kasım 2025
- **Versiyon**: v1.0
- **Durum**: ✅ Aktif

---

## İlgili Dosyalar

- `controllers/sakin_controller.py` - Validasyon metodları
- `models/base.py` - Sakin modeli
- `models/exceptions.py` - ValidationError sınıfı
- `ui/sakin_panel.py` - UI entegrasyonu
