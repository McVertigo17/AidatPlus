# Aidat Plus - Proje Yapısı ve Dosya Organizasyonu

## 📁 Dizin Yapısı

```
AidatPlus/
├── main.py                          # Ana uygulama entry point
├── requirements.txt                 # Python bağımlılıkları
├── aidat_plus.db                    # SQLite veritabanı
│
├── database/                        # Veritabanı konfigürasyonu
│   ├── __init__.py
│   └── config.py                    # SQLAlchemy engine ve session
│
├── models/                          # SQLAlchemy ORM modelleri
│   ├── __init__.py
│   └── base.py                      # Tüm modeller (Lojman, Blok, Daire, vb.)
│
├── controllers/                     # İş mantığı katmanı (15 dosya)
│   ├── __init__.py
│   ├── base_controller.py           # Base sınıf
│   ├── lojman_controller.py         # Lojman yönetimi
│   ├── blok_controller.py           # Blok yönetimi
│   ├── daire_controller.py          # Daire yönetimi
│   ├── sakin_controller.py          # Sakin/kiracı yönetimi
│   ├── aidat_controller.py          # Aidat işlemleri
│   ├── finans_islem_controller.py   # Finansal işlemler (Gelir/Gider/Transfer)
│   ├── hesap_controller.py          # Banka hesapları
│   ├── kategori_yonetim_controller.py # Kategori yönetimi (JSON tabanlı)
│   ├── belge_controller.py          # Belge yönetimi
│   ├── backup_controller.py         # Excel/XML yedekleme
│   ├── ayar_controller.py           # Uygulama ayarları
│   └── bos_konut_controller.py      # Boş konut listesi hesaplamaları
│
├── ui/                              # Arayüz katmanı (CustomTkinter) - 9 dosya
│   ├── __init__.py
│   ├── base_panel.py                # Base panel sınıfı
│   ├── dashboard_panel.py           # Ana panel (özet istatistikler)
│   ├── lojman_panel.py              # Lojman yönetim paneli
│   ├── aidat_panel.py               # Aidat yönetim paneli
│   ├── sakin_panel.py               # Sakin yönetim paneli
│   ├── finans_panel.py              # Finans işlemleri paneli (Gelir/Gider/Transfer)
│   ├── raporlar_panel.py            # Raporlar paneli (8 sekme)
│   └── ayarlar_panel.py             # Ayarlar paneli
│
├── docs/                            # Dokümantasyon (Bu klasör)
│   ├── PROJE_YAPISI.md              # Proje mimarisi ve yapısı
│   ├── AGENTS.md                    # Agent komutları ve stil rehberi (kopyası)
│   ├── KILAVUZLAR.md                # Özellik kullanım kılavuzları
│   ├── SORULAR_CEVAPLAR.md          # FAQ ve sorun giderme
│   └── TODO.md                      # Geliştirme planı ve düzeltme listesi
│
├── belgeler/                        # Ek dokümantasyon dosyaları
├── AGENTS.md                        # Agent komutları, stil rehberi
└── PROJE_YAPISI.md                  # Kök seviye proje yapısı (eski)
```

---

## 🎯 Ana Bileşenler Detayı

### 1. **Database Layer** (`database/`)

#### config.py
- SQLAlchemy engine ve session yönetimi
- SQLite veritabanı bağlantı konfigürasyonu
- Base sınıf tanımı

**Önemli**: Tüm modeller `models/base.py`'de tanımlandığı için tablolar otomatik oluşturulur.

---

### 2. **Models Layer** (`models/base.py`)

Tüm SQLAlchemy ORM modelleri tek dosyada:

#### Temel Modeller
- **Lojman**: Lojman kompleksleri
- **Blok**: Blok/bina (Lojman'a bağlı)
- **Daire**: Konut/daire (Blok'a bağlı)
- **Sakin**: Kiracılar (Daire'ye bağlı, tek sakin)

#### Aidat Modelleri
- **Aidat**: Aylık aidat tanımlaması
- **AidatIslem**: Aidat işlem kayıtları
- **AidatOdeme**: Aidat ödeme kayıtları

#### Finans Modelleri
- **FinansIslem**: Finansal işlemler (Gelir, Gider, Transfer)
- **Hesap**: Banka hesapları (Nakit, Banka, vb.)
- **Kategori**: Gelir/Gider kategorileri

#### Diğer Modeller
- **Belge**: Belge yönetimi (fatura, sözleşme, vb.)

---

### 3. **Controllers Layer** (`controllers/`)

Business logic katmanı - modelleri manipüle eden fonksiyonlar.

#### Base Controller (`base_controller.py`)
Tüm controller'ların parent sınıfı:
- Veritabanı session yönetimi
- CRUD işlemlerinin temel metodları
- Error handling

#### Entity Controllers (CRUD İşlemleri)

| Controller | Sorumluluğu |
|-----------|-----------|
| `lojman_controller.py` | Lojman CRUD, validasyon |
| `blok_controller.py` | Blok CRUD, Lojman'a bağlama |
| `daire_controller.py` | Daire CRUD, Blok'a bağlama |
| `sakin_controller.py` | Sakin CRUD, güncel ad_soyad alanı |

#### Feature Controllers (Özel İşlemler)

| Controller | Sorumluluğu |
|-----------|-----------|
| `aidat_controller.py` | Aidat işlemleri, hesaplamalar |
| `finans_islem_controller.py` | Gelir/Gider/Transfer işlemleri, hesap yönetimi |
| `hesap_controller.py` | Banka hesapları (Aktif/Pasif yönetimi) |
| `kategori_yonetim_controller.py` | JSON tabanlı kategori yönetimi (kategoriler.json) |
| `belge_controller.py` | Belge yönetimi, dosya işlemleri |
| `backup_controller.py` | Excel ve XML formatında yedekleme/geri yükleme |
| `ayar_controller.py` | Uygulama genel ayarları |
| `bos_konut_controller.py` | Boş konut listesi hesaplamaları, maliyet analizi |

---

### 4. **UI Layer** (`ui/`)

CustomTkinter ile oluşturulan arayüz panelleri.

#### Base Panel (`base_panel.py`)
Tüm panellerin parent sınıfı:
- Ortak UI bileşenleri
- Event handling
- Veri yenileme

#### Ana Paneller

| Panel | Sorumluluğu |
|------|-----------|
| `dashboard_panel.py` | Ana sayfa, özet istatistikler, grafikleri |
| `lojman_panel.py` | Lojman CRUD, blok/daire yönetimi |
| `aidat_panel.py` | Aidat işlemleri, ödeme takibi |
| `sakin_panel.py` | Sakin yönetimi, kişi bilgileri |
| `finans_panel.py` | Finansal işlemler, 3 tabbed view (Gelir/Gider/Transfer) |

#### Özel Paneller

| Panel | Özellikler |
|------|-----------|
| `raporlar_panel.py` | 8 sekme: Tüm İşlemler, Bilanço, İcmal, Konut Mali Durumları, **Boş Konut Listesi**, Kategori Dağılımı, Aylık Özet, Trend Analizi |
| `ayarlar_panel.py` | Uygulama ayarları, kişiselleştirme, export/import |
| `finans_panel.py` | Finansal işlemler, 3 tabbed view (Gelir/Gider/Transfer), type-safe implementasyon |

---

## 📊 Veri Modeli ve İlişkileri

```
Lojman (1) ──────────────────→ (N) Blok
  │ (Lojman Kompleksi)         │
  │ (ad, yer, kurulus_tarihi) │
  │                            ├─→ (N) Daire
  │                            │     (no, kat, m2, durum)
  │                            │     └─→ (0-1) Sakin
  │                            │           (ad_soyad, telefon, email)
  │                            │           ├─→ (N) Aidat
  │                            │           │     (ay, yil, tutar)
  │                            │           └─→ (N) AidatOdeme
  │                            │                 └─→ FinansIslem (Gelir)
  │
  └─→ Aidat Operasyonları
        └─→ AidatIslem + AidatOdeme

Hesap (1) ────────────→ (N) FinansIslem
  │ (Banka Hesapları)         │ (Gelir/Gider/Transfer)
  │ (ad, saldo, tipi)         │ (tutar, tarih, kategori)
  │                           │ (aciklama, kod_no)
  └─→ Hesap Durumu (Aktif/Pasif)

Kategori (1) ──→ (N) FinansIslem
  │ (JSON: kategoriler.json)
  │ (ana_kategori, alt_kategori, tipi)
  │
  └─→ Hiyerarşik Yapı
        Ana Kategori
        └─→ Alt Kategoriler
```

---

## 🚀 Uygulama Akışı

```
1. Başlangıç
   └─→ main.py çalıştırılır
       └─→ database/config.py: Engine oluşturulur
           └─→ models/base.py: Tablolar otomatik oluşturulur

2. UI Oluşturma
   └─→ AidatPlusApp sınıfı: Ana pencere oluşturulur
       └─→ 6 navigasyon butonu: Finans, Aidat, Sakin, Lojman, Raporlar, Ayarlar
           └─→ DashboardPanel: İlk sayfada gösterilir

3. Panel Açılışı
   └─→ Kullanıcı buton tıklar
       └─→ Panel window oluşturulur
           └─→ İlgili Controller çağrılır
               └─→ Veriler DB'den çekilir
                   └─→ UI bileşenleri doldurulur (Treeview, Form, vb.)

4. Kullanıcı İşlemi
   └─→ Ekle/Güncelle/Sil butonları
       └─→ Form validation (UI tarafında)
           └─→ Controller metodu çağrılır
               └─→ Veritabanı işlemi (SQLAlchemy)
                   └─→ Veri yenileme (refresh_table())
```

---

## 📋 Dosya İstatistikleri

| Kategori | Dosya Sayısı | Açıklama |
|---------|------------|---------|
| **Controllers** | 15 | Entity + Feature controllers |
| **UI Panels** | 9 | Dashboard, yönetim ve raporlar panelleri |
| **Models** | 1 | Tüm modeller (base.py) |
| **Database** | 1 | config.py |
| **Docs** | 5 | Dokümantasyon dosyaları |
| **Toplam Aktif** | 31 | Python dosyası + dokümantasyon |

---

## 🔧 Kurulum ve Çalıştırma

### Gerekli Kütüphaneler

```
customtkinter>=5.2.0      # Modern GUI
sqlalchemy>=1.4.0         # ORM
pandas>=1.5.0             # Veri işleme
matplotlib>=3.6.0         # Grafikler
pillow>=9.0.0             # Resim işleme
openpyxl>=3.10.0          # Excel export
lxml>=4.9.0               # XML export
```

**Not**: `sqlite3` Python'a yerleşiktir, ayrıca kurmanız gerekmez.

### Kurulum Adımları

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Uygulamayı çalıştır
python main.py
```

**Not**: Veritabanı tabloları `main.py` başlatıldığında otomatik olarak oluşturulur.

---

## 🎨 Kod Stil Rehberi

### Adlandırma Kuralları

| Konu | Kural | Örnek |
|------|-------|-------|
| **Sınıflar** | PascalCase | `SakinController`, `FinansPanel` |
| **Metodlar** | snake_case | `get_aktif_sakinler()`, `setup_ui()` |
| **Değişkenler** | snake_case | `lojman_ad`, `daire_no`, `toplam_tutar` |
| **Sabitler** | UPPER_CASE | `COLORS`, `PAGE_SIZE`, `MAX_LENGTH` |
| **Dosyalar** | snake_case | `sakin_controller.py`, `finans_panel.py` |

### Diloloji Kuralları

| Konu | Kural | Örnek |
|------|-------|-------|
| **Veritabanı** | Türkçe tablo/sütun | `sakinler`, `daireler`, `ad_soyad` |
| **UI** | Türkçe etiketler | "Sakin Adı", "Daire Numarası" |
| **Yorum** | Türkçe açıklamalar | `# Sakin bilgilerini getir` |
| **Kodlar** | İngilizce | Fonksiyon adları, sınıf adları |

### İthalatlar

```python
# Standart kütüphane
import os
import sys
from typing import List, Optional, Dict, Type, TypeVar, Generic, Union, Callable

# Üçüncü taraf
import customtkinter as ctk
from sqlalchemy import Column, String
import pandas as pd

# Lokal modüller
from models.base import Sakin
from controllers.base_controller import BaseController
```

### Error Handling

```python
try:
    # İşlem
    sakinler = self.get_all_sakinler()
except Exception as e:
    # Hata mesajı
    messagebox.showerror("Hata", f"Sakinler yüklenirken hata oluştu: {str(e)}")
```

---

## 📚 Dokümantasyon Dosyaları

| Dosya | İçerik |
|------|--------|
| **PROJE_YAPISI.md** | Proje mimarisi, dosya yapısı, bileşenler |
| **AGENTS.md** | Agent komutları, stil rehberi (root + docs) |
| **KILAVUZLAR.md** | Özellik kullanım kılavuzları, örnekler |
| **SORULAR_CEVAPLAR.md** | FAQ, sorun giderme, best practices |
| **TODO.md** | Geliştirme planı, açık sorunlar, iyileştirmeler |
| **TYPE_HINTS_STANDARDIZATION.md** | Type hints standardizasyon rehberi (Devam ediyor - 277 MyPy hata) |

---

## ✅ Kalite Kontrol

### Mevcut Iyileştirmeler
- ✅ Temiz dizin yapısı
- ✅ MVC mimarisi
- ✅ JSON tabanlı kategori yönetimi
- ✅ Renkli finansal işlemler
- ✅ Excel/XML yedekleme
- ✅ Modern GUI (CustomTkinter)

### Planlanan Iyileştirmeler
Bkz. `TODO.md` detayları için.

### Uygulanan Iyileştirmeler
- ✅ Type Hints Standardizasyonu (Devam ediyor - 277 MyPy hata düzeltme bekleniyor)

---

**Son Güncelleme**: 28 Kasım 2025  
**Durum**: ✅ Güncellendi ve Düzenlenmiş (Type Hints ile)
