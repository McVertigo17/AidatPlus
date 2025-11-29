# Sakin Silme vs Pasif Yapma - Teknik Açıklama

**Tarih**: 29 Kasım 2025  
**Konu**: Sakinleri silme işleminde neler olduğu, raporlamada neden görüneceği

---

## 🤔 Soru
"Sakinleri sildim, ama raporlamada giriş/çıkış tarihleri görünüyor. Sorun mu?"

---

## ✅ Cevap: SORUN DEĞİL, TASARLANMIŞ ŞEKILDE ÇALIŞIYOR

Lojman yönetiminde **sakinleri "silme"** ve **"pasif yapma"** arasında büyük fark var:

---

## 📊 Sakin'in Veritabanı Kaydı

Her sakininin veritabanında **benzersiz bir ID'si** vardır:

```sql
Sakinler Tablosu:
┌────┬─────────────┬──────────────┬────────────────┬──────────────┐
│ ID │ ad_soyad    │ giris_tarihi │ cikis_tarihi   │ aktif        │
├────┼─────────────┼──────────────┼────────────────┼──────────────┤
│ 1  │ Ali Yıldız  │ 01.01.2020   │ NULL           │ TRUE (Aktif) │
│ 2  │ Ayşe Kara   │ 15.03.2021   │ NULL           │ TRUE (Aktif) │
│ 3  │ Mehmet Demir│ 20.06.2019   │ 31.12.2023     │ FALSE(Pasif) │
└────┴─────────────┴──────────────┴────────────────┴──────────────┘
```

---

## 🔄 "Silme" İşlemi Nedir?

Kullanıcı arabiriminde "Sil" butonuna tıklandığında, aslında **VERITABANINDA SİLİNMİYOR**:

### Gerçek İşlem:
```python
# controllers/sakin_controller.py - delete() metodu

def delete(self, id: int, db: Session = None) -> bool:
    """Sakini sil (pasife çek)"""
    # Sakin'i bulup güncelle
    sakin = self.get_by_id(id, session)
    sakin.aktif = False                    # ← Pasif yap
    sakin.cikis_tarihi = datetime.now()    # ← Çıkış tarihi ekle
    session.commit()
    return True
```

### Sonuç:
```
ESKI:
│ 1  │ Ali Yıldız  │ 01.01.2020   │ NULL           │ TRUE  │

SİLME SONRASI:
│ 1  │ Ali Yıldız  │ 01.01.2020   │ 31.12.2025     │ FALSE │
                              ↑                    ↑
                        Korunur!              Pasif işareti
```

---

## 💾 Veritabanında Neler Değişiyor?

| Alan | Silmeden Önce | Silmeden Sonra |
|------|---------------|----------------|
| **ID** | 1 | **1 (aynı)** ✅ |
| **ad_soyad** | "Ali Yıldız" | **"Ali Yıldız" (aynı)** ✅ |
| **giris_tarihi** | 01.01.2020 | **01.01.2020 (aynı)** ✅ |
| **cikis_tarihi** | NULL | **31.12.2025 (eklendi)** |
| **aktif** | TRUE | **FALSE (pasif)** |

**Sonuç**: Sakin kaydı **tamamen silinmiyor**, **pasif işaretlenmiyor**

---

## 📈 Raporlamada Neler Görünüyor?

### 1. **Aktif Sakinler Sekmesi** (Yaşayan sakinler)
```
Sakinler (Aktif)
├─ Ali Yıldız
├─ Ayşe Kara
└─ ... (sadece aktif=TRUE olan)
```

### 2. **Arşiv/Pasif Sekmesi** (Ayrılan sakinler)
```
Arşiv (Pasif)
└─ Mehmet Demir (giriş: 20.06.2019, çıkış: 31.12.2023)
```

### 3. **Raporlarda**
```
Tüm Sakinlerin Giriş/Çıkış Tarihleri:

Mehmet Demir:
  • Giriş Tarihi: 20.06.2019
  • Çıkış Tarihi: 31.12.2023  ← GÖSTERILIR (Arşivde olduğu için)
  • Kalış Süresi: ~4.5 yıl

Ali Yıldız:
  • Giriş Tarihi: 01.01.2020
  • Çıkış Tarihi: (boş - hala aktif)
  • Kalış Süresi: 5+ yıl (devam ediyor)
```

---

## ❓ Neden Silmiyorum da Pasif Yapıyorum?

### Senaryo:
```
Mehmet Demir 4.5 yıl ikamet etti.
Arılış tarihi: 31.12.2023
Aidat borcu: 50,000 TL (hesaplanacak)

Sorualar:
1. Kaç ay oturdu? → giris_tarihi ve cikis_tarihi'ndan hesapla
2. Aylık aidat ne kadar? → Kalış döneminden kesiş
3. Denetim raporu? → Historik veri gerekli
```

**Eğer sakin tamamen silinirse**:
- ❌ Aidat borcu hesaplanamaz
- ❌ Kalış süresi bilinmez
- ❌ Denetim izi kaybolur
- ❌ Vergi/mali raporlamada sorun

**Pasif yapılırsa**:
- ✅ Tüm historik bilgi korunur
- ✅ Aidat hesapları doğru olur
- ✅ Denetim izi tam
- ✅ Mali raporlar tutarlı

---

## 🔑 Teknik Detaylar

### Sakin Modeli (`models/base.py`)
```python
class Sakin(Base):
    id = Column(Integer, primary_key=True)  # ← Her sakininin benzersiz ID'si
    ad_soyad = Column(String(100))
    giris_tarihi = Column(DateTime)         # ← Yerleşim tarihi
    cikis_tarihi = Column(DateTime)         # ← Ayrılış tarihi (NULL = hala aktif)
    aktif = Column(Boolean, default=True)   # ← Aktif/Pasif işareti
```

### Durum Belirleme
```python
@property
def durum(self) -> str:
    if self.cikis_tarihi:  # ← Çıkış tarihi varsa
        return "Pasif"     # Pasif sakin
    return "Aktif"         # Aktif sakin
```

---

## 📋 Kullanıcı Arayüzündeki Görünüş

### Silme Öncesi:
```
Sakinler (Aktif) Sekmesi:
├─ Mehmet Demir
├─ Ali Yıldız
└─ Ayşe Kara

Arşiv (Pasif) Sekmesi:
   (boş)
```

### Silme Sonrası:
```
Sakinler (Aktif) Sekmesi:
├─ Ali Yıldız
└─ Ayşe Kara

Arşiv (Pasif) Sekmesi:
└─ Mehmet Demir (giriş: 20.06.2019, çıkış: 31.12.2025)
```

---

## 🎯 Sonuç

| Soru | Cevap |
|------|-------|
| **Sakinler siliniyor mu?** | Hayır, pasif işaretleniyor |
| **Veritabanında kalıyor mu?** | Evet, aktif=FALSE olarak |
| **Giriş/Çıkış tarihleri korunuyor mu?** | Evet, hiç kaybolmaz |
| **Raporlamada görünüyor mu?** | Evet, arşiv sakinleri olarak |
| **Bu normal mi?** | Evet, tasarlanmış şekilde ✅ |
| **Sorun var mı?** | Hayır, her şey yolunda |

---

## 📊 Mali İşlemler Örneği

```
Mehmet Demir'in Dönemi: 20.06.2019 - 31.12.2023 (4.5 yıl)

Aylık Aidat:
├─ 2019 Haziran-Aralık: 8 ay × 1,000 TL = 8,000 TL
├─ 2020-2022: 36 ay × 1,000 TL = 36,000 TL
├─ 2023 Ocak-Aralık: 12 ay × 1,000 TL = 12,000 TL
└─ TOPLAM: 56,000 TL

Bu hesaplama için:
✅ giris_tarihi (20.06.2019) gerekli
✅ cikis_tarihi (31.12.2023) gerekli
✅ Sakin kaydı (ID: 3) gerekli
```

---

## 🚀 Önemli Noktalar

1. **Benzersiz ID**: Her sakininin kendi ID'si vardır. Yeni sakin = yeni ID
2. **Historik Veri**: Geçmiş sakinler asla silinmez, sadece pasif yapılır
3. **Veri Bütünlüğü**: Tüm mali işlemler, aidatlar, taşınmışlıklar korunur
4. **Raporlama**: Pasif sakinler arşiv sekmesinde görünür
5. **Mali Kontrol**: Denetim izi tam ve doğru olur

---

**Sonuç**: Sakinleri "sildikten" sonra raporlamada giriş/çıkış tarihleri görmek **tamamen normal ve doğru**'dur. ✅
