# Sakin Arşiv Yönetimi - Bug Fix (v1.2)

**Tarih**: 29 Kasım 2025  
**Statü**: ✅ Çözüldü  
**Etkilen Alan**: Sakin yönetimi - Arşiv/Pasif sekmesi

---

## 🐛 Sorun Tanımı

Arşiv (Pasif) sekmesindeki bir sakini tekrar aktif ettiğinde:
- ❌ Arşivdeki sakin kaydı siliniyordu
- ❌ Arşiv sekemesi boş kalıyordu
- ❌ Raporlamada giriş/çıkış tarihlerine göre hesaplama yapıldığında tutarsızlık oluşuyordu

**Neden Sorun?**
- Giriş/çıkış tarihleri raporlamalarda kritik
- Arşiv kaydı silinince historik veri kaybı
- İki kez gelen sakinin ilk gelmişinde etkinliği kontrol edilemiyor

---

## ✅ Çözüm

### Değiştirilmiş Davranış

Arşiv sekmesindeki sakini aktif ederken:
- ✅ Arşivdeki sakin kaydı **korunur** (sıfır değişiklik)
- ✅ Sakin'in tüm bilgileri (ad, daire, giriş tarihi vb.) **yeniden girilir**
- ✅ **Yeni aktif sakin kaydı oluşturulur** (cikis_tarihi = None)
- ✅ Raporlamada iki ayrı kayıt: arşiv + aktif

### Örnek Senaryo

```
Senaryo: Ali Yıldız isminde sakin var

Başlangıç:
├─ Sakinler (Aktif) sekmesi
│  └─ Ali Yıldız (ID: 1, giriş: 01.01.2020, çıkış: null)
│
└─ Arşiv (Pasif) sekmesi
   (boş)

İşlem: Ali Yıldız'ın istifa ettiğini kabul et
└─ Ali Yıldız (ID: 1) → çıkış_tarihi = 31.12.2023

Sonrası:
├─ Sakinler (Aktif) sekmesi
│  (boş)
│
└─ Arşiv (Pasif) sekmesi
   └─ Ali Yıldız (ID: 1, giriş: 01.01.2020, çıkış: 31.12.2023)

---

İşlem: Ali Yıldız yeniden istihdam edildi!
└─ Yeni aktif sakin oluştur (ad, daire, giriş tarihi vb. yeniden gir)

Sonrası (FIX SONRASI):
├─ Sakinler (Aktif) sekmesi
│  └─ Ali Yıldız (ID: 2, giriş: 01.01.2024, çıkış: null) ← YENİ KAYIT
│
└─ Arşiv (Pasif) sekmesi
   └─ Ali Yıldız (ID: 1, giriş: 01.01.2020, çıkış: 31.12.2023) ← KORUNMUŞ
```

### İmplikasyonları

**Raporlama Açısından**:
- 📊 Ali Yıldız'ın ilk dönemi: 01.01.2020 - 31.12.2023 (3 yıl)
- 📊 Ali Yıldız'ın ikinci dönemi: 01.01.2024 - Devam ediyor
- 📊 Dönemler ayrı ayrı analiz edilebilir

**Finansal Hesaplamalar**:
- ✅ Aidat: Her döneme göre hesaplanabilir
- ✅ Dönem sonu raporu: Arşivdeki kayıt kullanılır
- ✅ Hiçbir veri kaybı: Tüm historik bilgi korunur

---

## 📝 Teknik Detaylar

### Dosya: `ui/sakin_panel.py`

**Metod**: `confirm_aktif_yap()`

**Eski Davranış**:
```python
# ESKI - SAKİN KAYDINI GÜNCELLE (SİL VE YENİLE)
if self.sakin_controller.aktif_yap(pasif_sakin_id):
    # Mevcut sakin'i güncelle
    update_data = {...}
    self.sakin_controller.update(pasif_sakin_id, update_data)  # ❌ Eski kaydı siliyor!
```

**Yeni Davranış**:
```python
# YENİ - YENİ SAKİN KAYDI OLUŞTUR (ESKİ KORUNUR)
new_sakin_data = {
    "ad_soyad": ad_soyad,
    "daire_id": daire_id,
    "giris_tarihi": giris_tarihi,
    "cikis_tarihi": None,  # ← Aktif sakin
    ...
}
# Yeni sakin oluştur (arşivdeki sakin dokunulmaz)
new_sakin = self.sakin_controller.create(**new_sakin_data)  # ✅ Yeni kayıt
```

### Değişen Kod

| Satır | Eski | Yeni |
|-------|------|------|
| 809 | `aktif_yap()` + `update()` | `create()` |
| Sonuç | Mevcut sakin güncellenmiş | Yeni sakin oluşturulmuş |
| Arşiv | Silinmiş | Korunmuş |

### Kullanıcı Mesajı

**Eski**:
```
Sakin #1 başarıyla aktif yapıldı!
```

**Yeni**:
```
Sakin 'Ali Yıldız' yeni aktif sakin olarak eklendi!
Eski arşiv kaydı korunmuştur (ID: #1)
```

---

## ✨ Yararları

1. **Veri Bütünlüğü**: Historik bilgi hiç kaybolmaz
2. **Raporlama Doğruluğu**: Giriş/çıkış tarihleri her zaman doğru
3. **Finansal Hassasiyet**: Aidat hesaplamaları yanılmaz
4. **Denetim İzi**: Her dönemi ayrı takip edilebilir
5. **İş Kuralı Uyumluluğu**: Lojman yönetiminin gerçek iş akışını yansıtıyor

---

## 🔧 İlgili Kodlar

- `ui/sakin_panel.py` - `confirm_aktif_yap()` metodu (satır 804-860)
- `controllers/sakin_controller.py` - `create()` metodu
- `models/base.py` - `Sakin` modeli

---

## 📋 Test Edilenler

- [x] Arşiv sekmesinden sakin seçme
- [x] Modal açma ve form doldurma
- [x] Yeni daire seçme
- [x] Giriş tarihi değiştirme
- [x] Yeni sakin oluşturma
- [x] Arşivdeki sakin kaydının korunması
- [x] Listeyi yenileme ve görünüm kontrolü

---

## 🚀 Deployment

Bu fix v1.2'ye dahildir ve otomatik olarak uygulanır.  
Veritabanı migration gerekmez (şema değişikliği yok).

---

**Sonuç**: Arşiv yönetimi düzeltildi. Raporlama artık tamamen tutarlı. ✅
