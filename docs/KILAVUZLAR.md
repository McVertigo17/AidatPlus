# Aidat Plus - Özellik Kılavuzları

**Son Güncelleme**: 28 Kasım 2025

---

## 📚 İçindekiler

1. [Lojman Yönetimi](#lojman-yönetimi)
2. [Sakin Yönetimi](#sakin-yönetimi)
3. [Aidat İşlemleri](#aidat-işlemleri)
4. [Finansal İşlemler](#finansal-işlemler)
5. [Raporlar](#raporlar)
6. [Ayarlar](#ayarlar)
7. [Yedekleme](#yedekleme)

---

## 🏢 Lojman Yönetimi

### Lojman Oluşturma

**Adım 1**: Ana menüden "🏠 Lojman" butonuna tıkla

**Adım 2**: "Yeni Lojman Ekle" butonuna tıkla

**Adım 3**: Form doldur:
- **Lojman Adı** *(Zorunlu)*: Örn. "Merkez Lojmanı", "Kışlak Lojmanı"
- **Lokasyon** *(Zorunlu)*: Şehir/İlçe
- **Kuruluş Tarihi**: Lojmanın açıldığı tarih
- **Açıklama** *(Opsiyonel)*: Ekstra bilgiler

**Adım 4**: "Kaydet" butonuna tıkla

### Blok Yönetimi

Bir lojman oluşturduktan sonra bloklar ekleyebilirsin:

**Blok Ekleme**:
1. Lojmana sağ tıkla
2. "Blok Ekle" seç
3. Blok numarası (A, B, C, vb.) gir
4. Kat sayısı belirt
5. "Kaydet" tıkla

**Blok Silme**:
1. Bloka sağ tıkla
2. "Sil" seç
3. Onay ver

### Daire Yönetimi

Her blok içinde daireleri yönet:

**Daire Ekleme**:
1. Bloka sağ tıkla
2. "Daire Ekle" seç
3. Form doldur:
   - **Daire Numarası**: 101, 102, vb.
   - **Kat**: Hangi katta olduğu
   - **Metrekare**: m²
   - **Daire Tipi**: 1+1, 2+1, vb.
   - **Durum**: Boş/Dolu
4. "Kaydet" tıkla

**Daire Durumu Değiştirme**:
1. Daireye sağ tıkla
2. "Durum Değiştir" seç
3. Yeni durumu seç (Boş/Dolu)

---

## 👥 Sakin Yönetimi

### Sakin Ekleme

**Yol**: 👥 Sakin → "Yeni Sakin Ekle"

**Form Alanları**:
- **Ad Soyad** *(Zorunlu)*: Tam ad
- **TC Kimlik** *(Zorunlu)*: 11 haneli TC numarası
- **Telefon**: Cep telefonu
- **Email**: E-posta adresi
- **İşyeri**: Çalıştığı yer
- **Meslek**: Mesleği

**Adımlar**:
1. Formu tamamen doldur
2. Daire seç (Lojman → Blok → Daire)
3. "Kaydet" tıkla

### Sakin Güncelleme

1. Sakin tablosunda sakinle sağ tıkla
2. "Düzenle" seç
3. Bilgileri güncelle
4. "Kaydet" tıkla

### Sakin Silme

1. Sakin tablosunda sakinle sağ tıkla
2. "Sil" seç
3. Onay ver

**⚠️ Dikkat**: Sakin silinirse, onun aidatları da silinir!

---

## 💳 Aidat İşlemleri

### Aidat Türü Tanımlama

**Yol**: 💳 Aidat → "Aidat Türü Oluştur"

**Form**:
- **Aidat Adı**: Örn. "Elektrik", "Su", "Ortak İçişleri"
- **Aylık Tutar**: Aylık bedel (TL)
- **Açıklama**: İsteğe bağlı

### Aylık Aidat Oluşturma

1. Lojman seç
2. Ayı ve yılı seç (Aralık 2025)
3. "Aidat Oluştur" butonuna tıkla
4. Sistem otomatik olarak tüm sakınlar için aidat kaydı oluşturur

**Not**: Aynı ay için iki kez aidat oluşturamazsın!

### Aidat Ödemesi Kaydetme

**Yol**: 💳 Aidat → "Ödeme Kaydet"

**Adımlar**:
1. Lojman, Blok, Daire seç
2. Sakin seç
3. Hangi aidatların ödendiğini işaretle
4. Ödeme tarihi ve tutarını gir
5. Ödeme yapılan hesabı seç (Nakit, Banka, vb.)
6. Açıklama ekle (opsiyonel)
7. "Kaydet" tıkla

### Aidat Durumu İnceleme

**Rapor**: 📊 Raporlar → "Ödeme Durumu"

- Hangi sakinler ödeme yapmış
- Hangi sakinler ödeme yapmamış
- Toplam ödenmiş/ödenmemiş tutarlar
- Ödeme geçmişi

---

## 💰 Finansal İşlemler

### Hesap Yönetimi

**Yol**: 💰 Finans → "Hesap Yönetimi"

#### Hesap Ekleme

1. "Yeni Hesap Ekle" tıkla
2. Form doldur:
   - **Hesap Adı**: "Merkez Nalan Hesabı", "İş Bankası"
   - **Hesap Tipi**: Nakit, Banka, Yatırım, vb.
   - **Başlangıç Bakiyesi**: Açılış tutarı
   - **Açıklama**: Opsiyonel
3. "Kaydet" tıkla

#### Hesap Durumu Değiştirme

1. Hesap tablosunda sağ tıkla
2. Aktif/Pasif durumunu seç
3. **Pasif hesaplar** griye döner ve finansal işlemlerde görünmez

### Gelir Kaydı

**Yol**: 💰 Finans → "Gelir" sekmesi

**Form Alanları**:
- **Tarih**: İşlem tarihi
- **Kategori**: Kategori seç (Ana kategori → Alt kategori)
- **Tuttar**: Gelir miktarı
- **Hesap**: Gelir alındığı hesap
- **Kod No**: Opsiyonel işlem kodu
- **Açıklama**: Detaylı açıklama

**Örnek**:
- Kategori: Eğitim → Kurs Geliri
- Tutar: 5.000 TL
- Hesap: Merkez Nakit Hesabı
- Açıklama: "Kışlak eğitim programı"

### Gider Kaydı

**Yol**: 💰 Finans → "Gider" sekmesi

**Form Alanları**:
- **Tarih**: İşlem tarihi
- **Kategori**: Kategori seç
- **Tuttar**: Gider miktarı
- **Hesap**: Giderden çıkarılacak hesap
- **Kod No**: Opsiyonel
- **Açıklama**: Detaylı açıklama

**Örnek**:
- Kategori: Çalışan Giderleri → Ödeneği
- Tutar: 2.000 TL
- Hesap: Merkez Nakit Hesabı
- Açıklama: "Aralık aylık ödeneği"

### Transfer İşlemi

**Yol**: 💰 Finans → "Transfer" sekmesi

Bir hesaptan diğer hesaba para transfer:

**Form Alanları**:
- **Tarih**: Transfer tarihi
- **Kaynak Hesap**: Paralı çıkan hesap
- **Hedef Hesap**: Paralı gelen hesap
- **Tuttar**: Transfer miktarı
- **Açıklama**: Transfer nedeni

**Örnek**:
- Kaynak: Nakit Kasası
- Hedef: Merkez Banka Hesabı
- Tutar: 10.000 TL
- Açıklama: "Günlük kapatma transferi"

### İşlem Silme

1. İşlem tablosunda sağ tıkla
2. "Sil" seç
3. Onay ver

**Not**: Silinen işlemler geri yüklenemez!

---

## 📊 Raporlar

### Raporlar Modülü

**Yol**: 📊 Raporlar

8 sekme içerir:

#### 1. Tüm İşlem Detayları
Tüm finansal işlemlerin listesi:
- Gelir, Gider, Transfer
- Tarihe göre sıralı
- Hesap bilgileri
- Açıklama
- Excel export

#### 2. Bilanço
Finansal durum özeti:
- Toplam Gelirler
- Toplam Giderler
- Net Sonuç
- Hesap Bazında Bakiyeler

#### 3. İcmal
Özet görünüm:
- Dönem seç (Ay/Yıl)
- Kategori bazında özet
- Grafik gösterimi
- PDF export

#### 4. Konut Mali Durumları
Daire bazında ayrıntılı bilgi:
- Daire numarası
- Sakin adı
- Toplam aidat
- Ödenen miktar
- Kalan borç

#### 5. Boş Konut Listesi
Boş daireler ve maliyet analizi:
- Boş daire sayısı
- Toplam m²
- Aylık gider etkisi
- Gelir kaybı analizi

#### 6. Kategori Dağılımı
Grafik ve tablo:
- Kategorilere göre harcama dağılımı
- Pasta ve bar grafikler
- Yüzdelik oranlar

#### 7. Aylık Özet
Aydan aya karşılaştırma:
- Önceki aylar
- Mevcut ay
- Trend analizi

#### 8. Trend Analizi
Zaman serisi grafikleri:
- Gelir trendi
- Gider trendi
- Bakiye trendi

### Filtreler

Çoğu raporda filtreleme var:
- **Tarih Aralığı**: Başlangıç - Bitiş tarihi
- **Kategori**: Belirli kategorileri seç
- **Hesap**: Belirli hesapları seç
- **Durum**: Ödenmiş/Ödenmemiş (aidat raporu)

### Export Seçenekleri

**Desteklenen Formatlar**:
- 📊 **Excel (.xlsx)**: Detaylı veriler
- 📄 **PDF** (Planlı): Profesyonel raporlar

---

## ⚙️ Ayarlar

### Kategori Yönetimi

**Yol**: ⚙️ Ayarlar → "Kategoriler"

#### Kategori Hiyerarşisi

```
Ana Kategori
├── Alt Kategori 1
├── Alt Kategori 2
└── Alt Kategori 3
```

#### Ana Kategori Ekleme

1. Sol tarafta "Ana Kategori Ekle" tıkla
2. Kategori adı gir
3. Kategori tipi seç: Gelir / Gider
4. "Kaydet" tıkla

#### Alt Kategori Ekleme

1. Sol tarafta ana kategori seç
2. Sağ tarafta "Alt Kategori Ekle" tıkla
3. Alt kategori adı gir
4. "Kaydet" tıkla

#### Kategori Silme

1. Kategoriyi seç
2. "Sil" butonuna tıkla
3. Onay ver

### Uygulama Ayarları

**Yol**: ⚙️ Ayarlar → "Genel"

**Ayarlar**:
- Lojman seçimi (varsayılan lojman)
- Raporlar klasörü
- Yedekleme klasörü
- Dil seçimi (Planlı)
- Tema seçimi (Planlı)

### Veri Yönetimi

#### Tüm Veriyi Dışa Aktarma

1. "Yedekleme" sekmesi
2. "Excel Yedekle" tıkla
3. Klasör seç
4. Dosya otomatik kaydedilir

#### Tüm Veriyi İçe Aktar

1. "Yedekleme" sekmesi
2. "Excel'den İçe Aktar" tıkla
3. Daha önceden alınan yedek dosyasını seç
4. Onay ver

**⚠️ Dikkat**: İçe aktarma mevcut verileri değiştirir!

---

## 💾 Yedekleme

### Otomatik Yedekleme

Uygulama başında otomatik yedekleme yapılır:
- Dosya: `aidat_plus_backup_YYYY-MM-DD_HH-MM-SS.db`
- Klasör: `backups/` (proje dizini altında)

### Manuel Yedekleme

#### Excel Yedeklemesi

1. ⚙️ Ayarlar → "Yedekleme"
2. "Excel Yedekle" tıkla
3. Klasör seç
4. Dosya kaydedilir: `aidat_plus_YYYY-MM-DD.xlsx`

**İçerikler**:
- Lojman, Blok, Daire
- Sakin
- Aidat
- Finansal işlemler
- Hesaplar

#### XML Yedeklemesi

1. ⚙️ Ayarlar → "Yedekleme"
2. "XML Yedekle" tıkla
3. Klasör seç
4. Dosya kaydedilir: `aidat_plus_YYYY-MM-DD.xml`

### Geri Yükleme

#### Excel'den Geri Yükleme

1. ⚙️ Ayarlar → "Yedekleme"
2. "Excel'den İçe Aktar" tıkla
3. Eski yedek Excel dosyasını seç
4. Onay ver

#### XML'den Geri Yükleme

1. ⚙️ Ayarlar → "Yedekleme"
2. "XML'den İçe Aktar" tıkla
3. Eski yedek XML dosyasını seç
4. Onay ver

---

## 🎨 UI İpuçları ve Klavye Kısayolları

### Sık Kullanılan İşlemler

| İşlem | Kısayol |
|-------|---------|
| Tabloyu Yenile | F5 |
| Ara | Ctrl+F |
| Yeni Kayıt | Ctrl+N |
| Sil | Delete veya Sağ Tıkla |
| Tüm Veriyi Seç | Ctrl+A |

### Tablo İşlemleri

- **Sağ tık**: Bağlam menüsü (Ekle, Düzenle, Sil)
- **Çift tık**: Kaydı düzenle
- **Sütun başlığı tıkla**: Sıralama
- **Ara kutusu**: Tabloda arama

### Renk Kodlaması

**Finansal İşlemler**:
- 🟢 **Yeşil**: Gelirler
- 🔴 **Kırmızı**: Giderler
- 🔵 **Mavi**: Transferler

**Durum İşaretleri**:
- ✅ **Aktif hesap**: Normal
- ⚫ **Pasif hesap**: Gri renk
- ❌ **Ödenmemiş aidat**: Kırmızı arka plan

---

## 🆘 Yaygın Sorunlar

### Problem 1: "Kategori bulunamadı" hatası
**Çözüm**: 
1. ⚙️ Ayarlar → "Kategoriler"
2. Gerekli kategorileri ekle
3. Uygulamayı yeniden başlat

### Problem 2: Veri kaydedilmiyor
**Çözüm**:
1. Tüm zorunlu alanları doldur
2. Veri formatı kontrol et (tarih, tutar vb.)
3. Veritabanı dosyasının yazılabilir olduğunu kontrol et

### Problem 3: Excel yedeklemesi açılmıyor
**Çözüm**:
1. Excel 2010+ sürümünü kullan
2. Dosya konumuna git: `backups/` klasörü
3. Dosyayı manuel olarak Excel'le aç

---

**Not**: Bu kılavuz düzenli olarak güncellenecektir. Sorularınız için `SORULAR_CEVAPLAR.md` dosyasını kontrol edin.
