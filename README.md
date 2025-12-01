# Aidat Plus - Lojman Yönetim Sistemi

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![CI](https://github.com/McVertigo17/AidatPlus/workflows/CI%20Pipeline/badge.svg)
![Tests](https://img.shields.io/badge/Tests-pytest-blue)

Modern, offline çalışan lojman kompleksi aidat ve finansal yönetim uygulaması.

---

## 🎯 Amaç

**Aidat Plus**, Türkiye'deki devlet lojman komplekslerinin:
- 🏢 Binayı, bloğu, daireyi yönet
- 👥 Sakinleri ve kiracıları takip et
- 💳 Aylık aidatları hesapla ve ödemeleri kaydet
- 💰 Finansal işlemleri (gelir, gider, transfer) yönet
- 📊 Detaylı raporlar ve analizler oluştur
- 💾 Veriyi Excel/XML formatında yedekle

Bu özellikleri sağlayan, tamamen **çevrimdışı** çalışan bir çözümdür.

---

## ✨ Özellikler

### Lojman Yönetimi
- ✅ Lojman kompleksi oluştur ve yönet
- ✅ Blok/bina hiyerarşisi
- ✅ Daire CRUD işlemleri
- ✅ Boş/Dolu durumu takibi

### Sakin Yönetimi
- ✅ Sakin bilgileri kaydı
- ✅ TC Kimlik doğrulama
- ✅ İletişim bilgileri (telefon, email)
- ✅ Sakin profili

### Aidat Sistemi
- ✅ Aylık aidat oluşturma
- ✅ Çoklu aidat türü desteği
- ✅ Kısmi ödeme kaydı
- ✅ Ödeme geçmişi izleme

### Finansal Yönetim
- ✅ Gelir kaydı (Yeşil 🟢)
- ✅ Gider kaydı (Kırmızı 🔴)
- ✅ Transfer işlemleri (Mavi 🔵)
- ✅ Çoklu hesap yönetimi
- ✅ Kategorize işlemler

### Raporlar ve Analizler
1. 📋 Tüm İşlem Detayları
2. 💹 Bilanço (Finansal özet)
3. 📊 İcmal (Kategori özeti)
4. 🏠 Konut Mali Durumları
5. 🏚️ Boş Konut Listesi
6. 📈 Kategori Dağılımı (Grafik)
7. 📅 Aylık Özet
8. 📉 Trend Analizi

### Yedekleme
- ✅ Excel (.xlsx) yedekleme
- ✅ XML yedekleme
- ✅ Otomatik yedekleme
- ✅ Geri yükleme

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- **Python**: 3.7 veya üstü
- **Windows/macOS/Linux**: Herhangi bir işletim sistemi

### Kurulum

```bash
# 1. Proje dosyalarını indir
git clone https://github.com/McVertigo17/AidatPlus.git
cd AidatPlus

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Uygulamayı çalıştır
python main.py
```

**Not**: Veritabanı (`aidat_plus.db`) ilk çalıştırmada otomatik oluşturulur.

---

## 📦 Kurulum Adımı Adım

### Windows'ta

**Command Prompt:**
```batch
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

**PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

> **Not**: PowerShell'de execution policy hatası alırsanız, yönetici olarak açıp şu komutu çalıştırın:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### macOS/Linux'ta

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## 📚 Dokümantasyon

Tüm dokümantasyon `docs/` klasöründe:

| Dosya | Konu |
|------|------|
| **PROJE_YAPISI.md** | Mimari, dosya yapısı, bileşenler |
| **TODO.md** | Geliştirme planı, iyileştirmeler |
| **KILAVUZLAR.md** | Özellik kılavuzları, adım adım |
| **SORULAR_CEVAPLAR.md** | FAQ, sorun giderme, ipuçları |
| **ERROR_HANDLING_GUIDE.md** | Error handling & validation rehberi |
| **IMPLEMENTATION_SUMMARY.md** | v1.1 implementasyon özeti |
| **IMPLEMENTATION_CHECKLIST.md** | Tamamlanan görevlerin listesi |
| **TYPE_HINTS_STANDARDIZATION.md** | Type hints standardizasyon rehberi |

**Not**: AGENTS.md stil rehberi kök klasördedir (tüm geliştiriciler için erişim).

### Hızlı Linkler

- 🏢 [Lojman Yönetimi Kılavuzu](docs/KILAVUZLAR.md#lojman-yönetimi)
- 👥 [Sakin Yönetimi Kılavuzu](docs/KILAVUZLAR.md#sakin-yönetimi)
- 💳 [Aidat İşlemleri Kılavuzu](docs/KILAVUZLAR.md#aidat-işlemleri)
- 💰 [Finansal İşlemler Kılavuzu](docs/KILAVUZLAR.md#finansal-işlemler)
- 📊 [Raporlar Kılavuzu](docs/KILAVUZLAR.md#raporlar)
- ⚙️ [Ayarlar Kılavuzu](docs/KILAVUZLAR.md#ayarlar)

---

## 💻 Teknoloji Stack

```
Python 3.7+
├── CustomTkinter (Modern GUI)
├── SQLAlchemy (ORM)
├── SQLite (Veritabanı)
├── Pandas (Veri işleme)
├── Matplotlib (Grafikler)
└── openpyxl (Excel export)
```

---

## 📊 Proje Yapısı

```
AidatPlus/
├── main.py                    # Giriş noktası
├── requirements.txt           # Bağımlılıklar
├── aidat_plus.db              # Veritabanı
│
├── database/                  # DB Konfigürasyonu
│   └── config.py              # SQLAlchemy ayarları
│
├── models/                    # ORM Modelleri
│   └── base.py                # Tüm modeller
│
├── controllers/               # İş Mantığı (15 dosya)
│   ├── base_controller.py
│   ├── lojman_controller.py
│   ├── aidat_controller.py
│   ├── finans_islem_controller.py
│   └── ... (daha fazla)
│
├── ui/                        # Arayüz (9 dosya)
│   ├── base_panel.py
│   ├── dashboard_panel.py
│   ├── aidat_panel.py
│   ├── finans_panel.py
│   ├── raporlar_panel.py
│   └── ... (daha fazla)
│
├── docs/                      # Dokümantasyon
│   ├── PROJE_YAPISI.md
│   ├── TODO.md
│   ├── KILAVUZLAR.md
│   └── SORULAR_CEVAPLAR.md
│
└── belgeler/                  # Ek dökümanlar
```

---

## 🎨 Özellikleri Kullan

### Dashboard
Ana sayfa: Özet istatistikler, grafikleri, temel bilgileri

### Modüller
1. **💰 Finans**: Gelir/Gider/Transfer yönetimi
2. **💳 Aidat**: Aylık aidat ve ödeme takibi
3. **👥 Sakin**: Kiracı yönetimi
4. **🏠 Lojman**: Kompleks yapısı yönetimi
5. **📊 Raporlar**: 8 tür farklı rapor
6. **⚙️ Ayarlar**: Kategoriler ve sistem ayarları

### İşlem Türleri

**Gelir (🟢 Yeşil)**:
- Aidat ödemeleri
- Bağış ve ek gelirler
- Hizmet gelirleri

**Gider (🔴 Kırmızı)**:
- Elektrik, su, doğal gaz
- Personel ödeneği
- Bakım ve onarım
- Yönetim giderleri

**Transfer (🔵 Mavi)**:
- Hesaplar arası transfer
- Banka yatırımları

---

## 📈 Raporlar

### 8 Farklı Rapor Türü

1. **Tüm İşlem Detayları**: Tüm işlemlerin listesi + Excel export
2. **Bilanço**: Toplam gelir, gider, net sonuç
3. **İcmal**: Kategori bazında özet
4. **Konut Mali Durumları**: Daire başına aidat ve ödemeler
5. **Boş Konut Listesi**: Boş daireler ve maliyet analizi
6. **Kategori Dağılımı**: Pasta ve bar grafikler
7. **Aylık Özet**: Aylar arası karşılaştırma
8. **Trend Analizi**: Zaman serisi grafiği

### Filtreler
- 📅 Tarih aralığı
- 📂 Kategori seçimi
- 🏦 Hesap seçimi
- 💳 Aidat durumu (Ödenmiş/Ödenmemiş)

---

## 💾 Yedekleme ve Geri Yükleme

### Excel Yedeklemesi
```
⚙️ Ayarlar → "Yedekleme" → "Excel Yedekle"
Dosya: aidat_plus_YYYY-MM-DD.xlsx
```

### XML Yedeklemesi
```
⚙️ Ayarlar → "Yedekleme" → "XML Yedekle"
Dosya: aidat_plus_YYYY-MM-DD.xml
```

### Geri Yükleme
```
⚙️ Ayarlar → "Yedekleme" → "İçe Aktar"
Eski yedek dosyasını seç
```

---

## 🆘 Sorun Giderme

### Sık Karşılaşılan Sorunlar

**Problem**: "ModuleNotFoundError: No module named 'customtkinter'"
```bash
pip install -r requirements.txt --upgrade
```

**Problem**: Veritabanı kilitli
```
Uygulamayı kapat (Alt+F4) ve yeniden aç
```

**Problem**: Veri kaydedilmiyor
- Tüm zorunlu alanları doldur
- Tarih formatı (DD.MM.YYYY) kontrol et
- Veritabanı dosyasının yazılabilir olup olmadığını kontrol et

Daha fazla sorun giderme: [SORULAR_CEVAPLAR.md](docs/SORULAR_CEVAPLAR.md#-sorun-giderme)

---

## 🤝 Katkıda Bulunma

Katkı sağlamak isterseniz:

1. Fork proje
2. Feature branch oluştur (`git checkout -b feature/YeniÖzellik`)
3. Değişiklikleri commit et (`git commit -m "Yeni özellik ekle"`)
4. Branch'e push et (`git push origin feature/YeniÖzellik`)
5. Pull Request oluştur

---

## 📋 Roadmap

### v1.0 (Mevcut - Stable)
- ✅ Temel CRUD operasyonları
- ✅ Finansal işlemler
- ✅ Raporlar (8 tür)
- ✅ Backup/Restore

### v1.1 (Tamamlandı)
- ✅ Gelişmiş error handling
- ✅ Input validasyon (Tüm controller'lar)
- ✅ Logging sistemi
- ✅ Type hints standardizasyonu (Tamamlandı - 0 hata)
- ✅ Docstring standardizasyonu

### v1.2 (Planlı)
- 🔜 Configuration management
- 🔜 Bütçe planlama
- 🔜 Tekrarlı işlemler
- 🔜 PDF export

### v1.3+ (Gelecek)
- 🔜 Cloud backup
- 🔜 Multi-user support
- 🔜 Mobile app
- 🔜 API desteği

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasını görün.

---

## 📞 İletişim ve Destek

**Hata Raporları**: [GitHub Issues](https://github.com/McVertigo17/AidatPlus/issues)  
**Öneriler**: [Discussions](https://github.com/McVertigo17/AidatPlus/discussions)  
**Dokümantasyon**: [Wiki](https://github.com/McVertigo17/AidatPlus/wiki)

---

## 👨‍💼 Proje Ekibi

- **Proje Yöneticisi**: [Name]
- **Teknik Lider**: [Name]
- **Katkı Sağlayanlar**: [List]

---

## 🙏 Teşekkürler

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Pandas](https://pandas.pydata.org/) - Veri işleme
- [Matplotlib](https://matplotlib.org/) - Grafikler

---

## 📖 Ek Kaynaklar

- 🏢 [Lojman Yönetimi Kılavuzu](docs/KILAVUZLAR.md#lojman-yönetimi)
- 💰 [Finansal İşlemler Kılavuzu](docs/KILAVUZLAR.md#finansal-işlemler)
- 📊 [Raporlar Kılavuzu](docs/KILAVUZLAR.md#raporlar)
- ❓ [Sıkça Sorulan Sorular](docs/SORULAR_CEVAPLAR.md)
- 🛠️ [Geliştirici Kılavuzu](docs/PROJE_YAPISI.md)

---

**Son Güncelleme**: 28 Kasım 2025  
**Versiyon**: 1.0  
**Durum**: ✅ Aktif Geliştirme

Yapımcı: Aidat Plus Ekibi  
© 2025 - Tüm Hakları Saklıdır
