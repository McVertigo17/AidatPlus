# Aidat Plus - Sıkça Sorulan Sorular (FAQ) ve Sorun Giderme

**Son Güncelleme**: 28 Kasım 2025

---

## 📚 İçindekiler

1. [Genel Sorular](#genel-sorular)
2. [Kurulum ve Başlangıç](#kurulum-ve-başlangıç)
3. [Veri Yönetimi](#veri-yönetimi)
4. [Finansal İşlemler](#finansal-işlemler)
5. [Raporlar](#raporlar)
6. [Sorun Giderme](#sorun-giderme)
7. [İpuçları ve Best Practices](#ipuçları-ve-best-practices)

---

## ❓ Genel Sorular

### S: Aidat Plus nedir?
**C**: Aidat Plus, Türkiye'deki lojman komplekslerinin aidat ve finansmanını yönetmek için tasarlanmış modern bir yazılımdır. Gelir-gider takibi, aidat ödemeleri, raporlar ve analitik özellikleri içerir.

### S: Hangi işletim sistemlerinde çalışır?
**C**: Windows 10/11, macOS ve Linux'ta çalışır. Python 3.7+ gereklidir.

### S: Veri buluta yedeklenir mi?
**C**: Hayır, Aidat Plus tamamen çevrimdışı (offline) çalışır. Verileriniz yerel bir SQLite veritabanında saklanır. Bulut yedeklemesi planlanan bir özelliktir (v1.3+).

### S: Kaç kullanıcı eşzamanlı kullanabilir?
**C**: Mevcut sürümde sadece bir kullanıcı. Multi-user desteği v1.3+ planlanmaktadır.

### S: Teknisk destek nasıl alırım?
**C**: Bkz. "Sorun Giderme" bölümü. Sorununuzu bulamadıysanız, proje yöneticisine başvur.

---

## 🚀 Kurulum ve Başlangıç

### S: Nasıl yüklerim?
**C**: 
```bash
# 1. Python 3.7+ yükle
# 2. Proje dosyasını indir
cd AidatPlus

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Uygulamayı çalıştır
python main.py
```

### S: "Python bulunamadı" hatası alıyorum
**C**: 
1. Python'u https://www.python.org adresinden indir
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretle
3. Bilgisayarı yeniden başlat
4. Komut isteminde `python --version` yazıp sürümü kontrol et

### S: Bağımlılık kurulumu başarısız
**C**:
```bash
# Pip'i güncelle
python -m pip install --upgrade pip

# Bağımlılıkları yeniden yükle
pip install -r requirements.txt --upgrade
```

### S: Veritabanı otomatik oluşturulmuyor
**C**: 
1. `aidat_plus.db` dosyasının bulunup bulunmadığını kontrol et
2. Dosya yoksa, uygulamayı bir kez başlat - otomatik oluşturulacak
3. Hala oluşturulmazsa, dosya izinlerini kontrol et

### S: İlk çalıştırmada aşağıdakilerden birini yap:
- **Seçenek 1**: Demo veriyle başla (⚙️ Ayarlar → "Demo Veri Oluştur")
- **Seçenek 2**: Boş başla ve verini gir
- **Seçenek 3**: Eski yedekten geri yükle (⚙️ Ayarlar → "Yedekleme")

---

## 📊 Veri Yönetimi

### S: Kaç tane lojman yönetebilirim?
**C**: Sınırsız. Her lojman için blok ve daireler ekleyebilirsin.

### S: Daire silinirse ne olur?
**C**: 
- Dairenin tüm verileri silinir (sakin, aidat, vb.)
- Finansal işlemler şartsız kalır (silinmez)
- **Çözüm**: Daireyi "Boş" durumuna getir ve silme

### S: Sakin değiştirmek istiyorum
**C**: 
1. Yeni sakin ekle (👥 Sakin → "Yeni Sakin Ekle")
2. Aynı daireye ata
3. Eski sakin verilerini tutarsan, "Sakin Güncelle" yap
4. Eski sakin silinecek

### S: Verileri başka formata aktarabilirim?
**C**: Evet:
- **Excel**: ⚙️ Ayarlar → "Yedekleme" → "Excel Yedekle"
- **XML**: ⚙️ Ayarlar → "Yedekleme" → "XML Yedekle"

### S: Eski yedekten veri geri yükleyelim mi?
**C**: 
1. ⚙️ Ayarlar → "Yedekleme"
2. "Excel'den İçe Aktar" veya "XML'den İçe Aktar" seç
3. Eski dosyayı seç
4. **UYARI**: Mevcut veriler değişir!

---

## 💰 Finansal İşlemler

### S: Gelir ve Gider arasındaki fark nedir?
**C**: 
- **Gelir (🟢 Yeşil)**: Para giriş (aidat ödemesi, bağış, vb.)
- **Gider (🔴 Kırmızı)**: Para çıkış (elektrik, su, personel, vb.)

### S: Transfer nedir?
**C**: 
**Transfer (🔵 Mavi)**: Bir hesaptan diğerine para aktarma. Net gelir/gider değil.

**Örnek**:
- Nakit Hesabından Banka Hesabına 5.000 TL transfer
- Bakiye: Nakit -5.000, Banka +5.000
- Toplam: Değişmez

### S: Hesap bakiyesi yanlış gözüküyor
**C**:
1. **Başlangıç bakiyesi**: Hesap oluştururken girilen tutar
2. **Sonraki işlemler**: Gelir (+), Gider (-), Transfer (±)
3. **Bakiye = Başlangıç + Gelir - Gider + Transfer In - Transfer Out**

**Kontrol**:
- 💰 Finans → "İşlemler" tablosunda tüm işlemleri kontrol et
- 📊 Raporlar → "Bilanço"da bakiyeyi doğrula

### S: Yanlış işlem kaydettim, silebilir miyim?
**C**: Evet:
1. İşlem tablosunda işleme sağ tıkla
2. "Sil" seç
3. Onay ver
4. İşlem silinir ve bakiye otomatik güncellenir

### S: Tekrarlı giderler otomatikleşir mi?
**C**: Hayır (şu an). Plan v1.2'de otomatik tekrarlı işlemler var.

**Geçici Çözüm**:
- Her ay aynı gideri manuel ekle, tarih değiştir

### S: Kategori olmadan işlem kaydedemiyorum
**C**: 
1. Kategoriyi oluştur: ⚙️ Ayarlar → "Kategoriler"
2. Ana kategori ve alt kategori ekle
3. Yeni işlem kaydederken seç

---

## 💳 Aidat İşlemleri

### S: Aidat nedir?
**C**: Aidat, sakinlerin her ay ödediği ortak gider payıdır. Elektrik, su, temizlik, yönetim giderleri vb.

### S: Aidat türü nedir?
**C**: Kategorilerin dışında, lojman tarafından tanımlanan yapılar:
- Elektrik
- Su
- Doğal Gaz
- Ortak İçişleri
- Yönetim Gideri

**Oluşturma**: 💳 Aidat → "Aidat Türü Oluştur"

### S: Aylık aidat nasıl oluşturulur?
**C**:
1. 💳 Aidat paneline git
2. Lojman seç
3. Ay ve yılı seç
4. "Aidat Oluştur" tıkla
5. Sistem her sakin için kaydı oluşturur

### S: Aynı ay iki kez aidat oluşturduk
**C**:
- Hata: "Bu ay için aidat zaten oluşturulmuş"
- **Çözüm**: Eski aydatı sil, sonra yeniden oluştur
- Veya, aidat tutarını düzenle: Aidat Türü → Tutarı değiştir

### S: Kısmi ödeme kaydedebilir miyim?
**C**: Evet:
1. Sakin A'nın 3 aidat türü var (toplam 1.500 TL)
2. Sadece 2 tanesini öde (1.000 TL)
3. Ödeme Kaydet: 1.000 TL gir
4. Kalan 500 TL borç kalır

### S: Ödeme geçmişini görebilir miyim?
**C**: Evet:
1. 📊 Raporlar → "Ödeme Durumu"
2. Sakin seç
3. Ödeme geçmiş gösterilir

---

## 📊 Raporlar

### S: Raporlar nedir?
**C**: Uygulamanın veri analitik modülü. 8 farklı rapor türü:
1. Tüm İşlem Detayları
2. Bilanço
3. İcmal
4. Konut Mali Durumları
5. Boş Konut Listesi
6. Kategori Dağılımı
7. Aylık Özet
8. Trend Analizi

### S: Excel'e rapor aktarabilirim?
**C**: Evet, çoğu raporda Excel export vardır:
1. Rapor tablosunda "Excel Aktarma" butonuna tıkla
2. Klasör seç
3. Dosya otomatik kaydedilir

### S: Tarih aralığı filtresi nasıl çalışır?
**C**:
1. Rapor açılırken, tarih aralığı gir
2. "Başlangıç Tarihi": Hangi tarihten başlasın
3. "Bitiş Tarihi": Hangi tarihte bitsyn
4. Örn: 01.01.2025 - 31.12.2025 = Bütün yıl

### S: Grafikleri Excel'e aktarabilirim?
**C**: Şu an grafikleri doğrudan export edemezsin, ama:
- Veriler Excel'e aktarılır
- Excel'de grafik oluşturabilirsin
- v1.2'de PDF export planlanıyor

---

## 🆘 Sorun Giderme

### Hata 1: "Veritabanı kilitli" hatası
**Semptom**: Uygulamayı kapatamıyorum, "Veritabanı kilitli" mesajı

**Çözüm**:
1. Uygulamayı kapatmaya zorla (Alt+F4)
2. Başka bir program veritabanını açmadığını kontrol et
3. Uygulamayı yeniden başlat

### Hata 2: "Modül bulunamadı" hatası
**Semptom**: `ModuleNotFoundError: No module named 'customtkinter'`

**Çözüm**:
```bash
pip install -r requirements.txt --upgrade
```

### Hata 3: Uygulama açılmıyor
**Semptom**: Python script hata verileri olmadan açılmıyor

**Çözüm**:
```bash
# Komut satırından çalıştır (hata görüntüle)
python main.py

# Veya Python'un debug modunda çalıştır
python -u main.py
```

### Hata 4: Dosya izin hatası
**Semptom**: "Permission denied" - dosyaya yazılamıyor

**Çözüm (Windows)**:
1. Proje klasörüne sağ tıkla
2. "Özellikler" → "Güvenlik"
3. Kullanıcıyı seç
4. "Yazma" izni ver

### Hata 5: Veri kaydedilmiyor
**Semptom**: Kaydet butonuna tıklasam da veri eklenmedi

**Çözüm**:
1. Tüm zorunlu alanları doldur
2. Veri türünü kontrol et:
   - **Tarih**: DD.MM.YYYY formatında
   - **Tutar**: Sayı (nokta veya virgül)
   - **TC Kimlik**: 11 haneli sayı
3. Veritabanını "Yedekleme" ile kontrol et
4. Error mesajı yoksa, "Tablo Yenile" butonuna tıkla

### Hata 6: Pencereleri sürükleyemiyorum
**Semptom**: Açılan panelleri hareket ettiremiyorum

**Çözüm**:
- CustomTkinter sınırlaması, pencerenin başlığından sürükle
- Pencerenin başlığı (title bar) olmadıysa, Windows başlık çubuğunu kullan

### Hata 7: Metin adi görünüyor veya bozuk
**Semptom**: Türkçe karakterler (ç, ğ, ş, ü, ö) yanlış görünüyor

**Çözüm**:
1. Dosya kodlaması UTF-8 olduğunu kontrol et
2. Uygulamayı yeniden başlat
3. İşletim sistemi dilini Türkçe'ye değiştir

---

## 💡 İpuçları ve Best Practices

### İpucu 1: Düzenli Yedekleme
**Öneri**: Haftada en az bir kez yedek al:
```
⚙️ Ayarlar → "Yedekleme" → "Excel Yedekle"
```
- Dosya: `aidat_plus_YYYY-MM-DD.xlsx`
- Klasör: `backups/` (opsiyonel özel klasör)

### İpucu 2: Dönem Başında Kategori Oluştur
**Öneri**: Yılın başında tüm kategorileri oluştur:
- Ana kategoriler: Gelir, Gider
- Alt kategoriler: Elektrik, Su, vb.

### İpucu 3: Aylık Kontrol Listesi
Her ayın sonunda:
1. Tüm aidatlar kaydedildi mi? (💳 Aidat)
2. Tüm ödemeler kaydedildi mi? (💰 Finans)
3. Bakiye denetimleri uyuyor mu? (📊 Raporlar → Bilanço)
4. Rapor dışa aktarıldı mı? (Arşiv için)

### İpucu 4: Sakin Kullanmayı
Sakin ekleme kuralları:
- **Ad Soyad**: Tam isim (örn: "Ali AYDIN")
- **TC Kimlik**: 11 haneli (örn: "12345678901")
- **Telefon**: Ülke koduyla başlangıç (örn: "+90 555 123 4567")
- **Email**: Geçerli email formatı

### İpucu 5: İşlem Kodu Kullanma
İşlem kodları, büyük organizasyonlarda takip kolaylaştırır:
- **Gelir**: "GEL-001", "GEL-002"
- **Gider**: "GID-001", "GID-002"
- **Transfer**: "TRN-001", "TRN-002"

### İpucu 6: Açıklama Alanını Kullanma
Her işlemde açıklama ekleme alışkanlığı:
- **Gelir**: "Aralık aidatı: Elektrik + Su"
- **Gider**: "Personel aylık ödeneği - Fatıma"
- **Transfer**: "Günlük muhasebe kapatma"

### İpucu 7: Raporları Arşivle
Dönem raporlarını düzenli kaydet:
- **Aylık**: 📊 Raporlar → Tüm İşlemler → Excel
- **Yıllık**: 💾 Yedekleme → Excel Yedekle
- **Klasör**: `Arşiv/2025/` vb.

### İpucu 8: Hesap Durumunu Yönet
Kullanılmayan hesapları pasif yapma:
- 💰 Finans → Hesap Tablosu → Sağ tıkla → "Pasif"
- Pasif hesaplar gri gösterilir
- Yeni işlemler için görünmez

### İpucu 9: Kategori Hiyerarşisi
Ana kategoriler organize:
- **Gelirler**: Aidat, Ek Gelir, Bağış
- **Giderler**: Personel, Kamu, Bakım, Temel İşletim
- **Transferler**: Banka, Muhasebe, Yatırım

### İpucu 10: Veri Temizliği
Aylık temizlik:
- Boş daireyi "Boş" duruma getir (silme)
- Pasif sakları sakla (silme)
- Eski işlemler yerine rapor al
- Kategori düzenlemesi yap

---

## 📞 Daha Fazla Yardım

**Yardım Kaynakları**:
- 📖 **KILAVUZLAR.md**: Ayrıntılı özellik kılavuzları
- 📋 **PROJE_YAPISI.md**: Teknik mimari bilgi
- 🔍 **Arama**: Uygulama menüsünde Ctrl+F ile arama yap

**Geri Bildirim**:
- Hata rapor etmek için: [GitHub Issues]
- Önerileri paylaşmak için: [Discussions]
- Katkıda bulunmak için: [Pull Requests]

---

**Son Güncelleme**: 28 Kasım 2025  
**Versiyon**: 1.0  
**Durum**: ✅ Cevaplandırılmış Sorular (Aktif Güncellenecek)
