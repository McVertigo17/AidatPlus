# Docstring Rehberi - Aidat Plus

**Son Güncelleme**: 29 Kasım 2025  
**Versiyon**: 1.1

---

## 📚 Genel Kurallar

Aidat Plus projesinde **Google Style** docstring formatı kullanılmaktadır.

### Dosya Başında Docstring

Her Python dosyasının başında dosyanın amacını açıklayan bir docstring bulunmalıdır:

```python
"""
Sakin paneli - Sakin yönetim arayüzü
"""
```

---

## 🏗️ Sınıf Docstring'leri

### Format

```python
class SakinPanel(BasePanel):
    """Sakin yönetimi paneli
    
    Sakin (kiracı) kayıtlarının yönetimini sağlar.
    Aktif sakinler ve arşiv (geçmiş sakinler) olmak üzere iki sekmeye ayrılmıştır.
    
    Attributes:
        sakin_controller (SakinController): Sakin yönetim denetleyicisi
        daire_controller (DaireController): Daire yönetim denetleyicisi
        aktif_sakinler (List[Sakin]): Aktif sakinler listesi
        pasif_sakinler (List[Sakin]): Arşiv sakinleri listesi
        daireler (List[Daire]): Daire nesneleri listesi
    """
```

### Bileşenler

1. **İlk Satır**: Kısa açıklama (40 karakter altında)
2. **Boş Satır**
3. **Detaylı Açıklama**: Sınıfın amacı ve kullanım alanı
4. **Boş Satır**
5. **Attributes Bölümü**: Örnek göster
   - Atribut adı
   - Tür bilgisi (parantez içinde)
   - Açıklama

---

## 🔧 Method Docstring'leri

### Format - Basit Method

```python
def load_data(self) -> None:
    """Verileri yükle
    
    Başlangıç verilerini yüklemek için kullanılan metod.
    """
```

### Format - Parametreli Method

```python
def get_sakin_at_date(self, daire_id: int, yil: int, ay: int) -> Optional[str]:
    """Verilen tarihte dairede yaşayan sakinin adını getir
    
    Args:
        daire_id (int): Daire ID'si
        yil (int): Yıl
        ay (int): Ay (1-12)
    
    Returns:
        Optional[str]: Sakin adı ya da None
    """
```

### Format - Exception İçeren Method

```python
def create_sakin(self, ad_soyad: str, tc_id: str, **kwargs) -> Sakin:
    """Yeni sakin oluştur
    
    Args:
        ad_soyad (str): Sakin adı soyadı
        tc_id (str): TC Kimlik numarası (11 haneli)
        **kwargs: Ekstra alanlar (telefon, email, vb.)
    
    Returns:
        Sakin: Oluşturulan sakin nesnesi
    
    Raises:
        ValidationError: Eksik parametre veya geçersiz TC numarası
        DatabaseError: Veritabanı hatası
    
    Example:
        >>> controller = SakinController()
        >>> sakin = controller.create_sakin(
        ...     "Ali Yıldız", "12345678901",
        ...     telefon="+90 555 123 4567"
        ... )
    """
```

### Bölümler

| Bölüm | Amaç | Örnek |
|-------|------|-------|
| **Kısa Açıklama** | İlk satır - metodun amacı | "Yeni sakin oluştur" |
| **Detaylı Açıklama** | İsteğe bağlı - uzun açıklama | "Veritabanına yeni bir sakin kaydı ekler..." |
| **Args** | Parametreler ve tipleri | `daire_id (int): Daire ID'si` |
| **Returns** | Dönüş değeri ve tipi | `Optional[str]: Sakin adı ya da None` |
| **Raises** | Atılan exception'lar | `ValidationError: Doğrulama hatası` |
| **Example** | Kullanım örneği | `>>> sakin = controller.create(data)` |

---

## 📋 Properties İçin Docstring

```python
@property
def toplam_bakiye(self) -> float:
    """Tüm hesapların toplam bakiyesi
    
    Returns:
        float: Bakiye tutarı (₺)
    """
    return sum(h.bakiye for h in self.hesaplar)
```

---

## 🎯 UI Panel Docstring'leri

Tüm UI panelleri sınıfı docstring içermelidir:

```python
class DashboardPanel(BasePanel):
    """Dashboard/Ana sayfa paneli
    
    KPI kartları, finansal analizler ve grafiklerle ana özet görünümü sağlar.
    
    Attributes:
        hesap_controller (HesapController): Hesap yönetim denetleyicisi
        finans_controller (FinansIslemController): Finansal işlem denetleyicisi
        colors (dict): Renk şeması
        refresh_interval (int): Otomatik yenileme aralığı (milisaniye)
        scroll_frame (ctk.CTkScrollableFrame): Ana kaydırılabilir çerçeve
    """
```

---

## 💼 Controller Docstring'leri

```python
class SakinController(BaseController):
    """Sakin yönetimi için controller
    
    Sakin CRUD işlemleri ve validasyon işlevlerini sağlar.
    
    Attributes:
        session: Veritabanı session
    """
    
    def create(self, ad_soyad: str, tc_id: str, **kwargs) -> Sakin:
        """Yeni sakin oluştur
        
        Args:
            ad_soyad (str): Sakin adı soyadı (2-100 karakter)
            tc_id (str): TC Kimlik numarası (11 haneli, Luhn algoritması)
            **kwargs: Ekstra alanlar (telefon, email, daire_id, vb.)
        
        Returns:
            Sakin: Oluşturulan sakin nesnesi
        
        Raises:
            ValidationError: Doğrulama başarısız
            DatabaseError: Veritabanı hatası
            DuplicateError: TC ID zaten mevcut
        """
```

---

## ✅ Tür İpuçları (Type Hints)

Docstring'ler Type Hints ile birlikte kullanılmalı:

```python
def get_aktif_sakinler(self) -> List[Sakin]:
    """Aktif sakinleri getir
    
    Returns:
        List[Sakin]: Aktif sakinler listesi
    """

def find_by_id(self, sakin_id: int) -> Optional[Sakin]:
    """ID'ye göre sakin bul
    
    Args:
        sakin_id (int): Sakin ID'si
    
    Returns:
        Optional[Sakin]: Bulunan sakin ya da None
    """

def validate_and_create(self, data: Dict[str, Any]) -> Tuple[bool, str]:
    """Veri doğrula ve sakin oluştur
    
    Args:
        data (Dict[str, Any]): Sakin verileri
    
    Returns:
        Tuple[bool, str]: (başarı durumu, mesaj) tuple'ı
    """
```

---

## 🔄 Lambda ve İç Fonksiyonlar

Basit lambda fonksiyonları için:

```python
# Lambda'lara docstring gerekmez
filter_aktif = lambda s: s.aktif == True

# Ancak karmaşık inner fonksiyonlara eklenmeli
def process_data():
    """Ana veriye işleme fonksiyonu"""
    
    def normalize(value: str) -> str:
        """String'i normalize et"""
        return value.strip().lower()
    
    return normalize("  TEST  ")
```

---

## 📝 Türkçe Yazım Kuralları

### Terminoloji Standardı

| İngilizce | Türkçe |
|-----------|--------|
| Method/Function | Metod/Fonksiyon |
| Controller | Denetleyici |
| Panel/Widget | Panel/Widget (aynı) |
| Attribute | Atribut |
| Parameter | Parametre |
| Return | Dön/Döndür |
| Exception | İstisna/Hatası |
| Validation | Doğrulama |
| Database | Veritabanı |

### Örnek Türkçe Docstring

```python
def tahsilat_oranini_hesapla(self) -> float:
    """Toplam aidat tahsilat oranını hesapla
    
    Tüm aidatlar bazında ödenmemiş ve ödenen tutarları
    karşılaştırarak tahsilat yüzdesini hesaplar.
    
    Returns:
        float: Tahsilat yüzdesi (0-100 arası)
    """
```

---

## 🚀 İyi Pratikler

### ✅ Yapılması Gerekenler

1. **Her sınıf docstring içersin**
   ```python
   class SakinPanel(BasePanel):
       """Sakin yönetimi paneli"""
   ```

2. **Public metodlar docstring içersin**
   ```python
   def load_data(self):
       """Verileri yükle"""
   ```

3. **Karmaşık logic'e açıklama ekle**
   ```python
   def validate_tc_id(tc_id: str) -> bool:
       """TC kimlik numarasını Luhn algoritması ile doğrula"""
   ```

4. **Exception'lar belirtilsin**
   ```python
   Raises:
       ValidationError: TC numarası 11 haneli değilse
   ```

5. **Örnekler ekle (özellikle public API'ler)**
   ```python
   Example:
       >>> sakin = controller.create("Ali Yıldız", "12345678901")
   ```

### ❌ Yapılmaması Gerekenler

1. **Açık olmayan docstring'ler**
   ```python
   # ❌ Kötü
   def process():
       """Process something"""
   ```

2. **Eski docstring'ler (güncellenmemiş)**
   ```python
   # ❌ Kötü - Parametreler değişti
   def create(self, x, y):
       """Sakin oluştur
       
       Args:
           ad (str): Sakin adı
           soyad (str): Sakin soyadı
       """
   ```

3. **Türkçe ve İngilizce karışması**
   ```python
   # ❌ Kötü
   def load_data(self):
       """Verileri load et"""
   ```

---

## 📊 Docstring Coverage Hedefleri

| Kategori | Hedef | Mevcut |
|----------|-------|--------|
| **Controllers** | %100 | ✅ %100 |
| **Models** | %85+ | ✅ %90+ |
| **UI Panels** | %90+ | ✅ %95+ |
| **Utilities** | %80+ | 🟡 %70+ |
| **Tests** | %70+ | 🔴 0% |

---

## 🔍 Docstring Kontrolü

### Google Style Doğrulaması

```bash
# pydocstyle kullanarak docstring stilini kontrol et
pydocstyle ui/*.py controllers/*.py models/*.py
```

### Type Hints Kontrolü

```bash
# mypy kullanarak type checking
mypy --strict --config-file=mypy.ini .
```

---

## 📖 Kaynaklar

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Sphinx Documentation](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)

---

**Not**: Bu rehber proje geliştirilirken düzenli olarak güncellenecektir.
