# Hata Yönetimi & Doğrulama Rehberi (v1.1)

**Sürüm**: 1.1  
**Tarih**: 28 Kasım 2025  
**Durum**: ✅ Tamamlandı

Bu rehber, Aidat Plus'ta yeni Hata Yönetimi ve Doğrulama sisteminin nasıl kullanılacağını açıklar.

---

## 📚 İçindekiler

1. [Exception Sistemi](#exception-sistemi)
2. [Validation Framework](#validation-framework)
3. [UI Error Handling](#ui-error-handling)
4. [Best Practices](#best-practices)
5. [Örnekler](#örnekler)

---

## Exception Sistemi

### Nedir?

Exception sistemi, uygulamada oluşan hataları kontrollü bir şekilde işlemek için kullanılır.

### Exception Hiyerarşisi

```
Exception
└── AidatPlusException (Temel)
    ├── ValidationError
    │   └── DuplicateError
    ├── DatabaseError
    ├── FileError
    ├── ConfigError
    └── BusinessLogicError
        ├── NotFoundError
        └── InsufficientDataError
```

### İmport Etme

```python
from models.exceptions import (
    ValidationError,
    DatabaseError,
    NotFoundError,
    DuplicateError
)
```

### Exception Fırlatma

```python
# Simple
raise ValidationError("Ad boş bırakılamaz")

# Hata koduyla
raise ValidationError("Ad boş bırakılamaz", code="VAL_001")

# Detaylı
raise DuplicateError(
    "Bu TC kimliği zaten kayıtlı",
    code="DUP_001",
    details={"tc_id": "12345678901"}
)
```

---

## Validation Framework

### Validator Sınıfı

```python
from models.validation import Validator

# 1. Boş alan kontrolü
Validator.validate_required("Ali", "Ad Soyad")

# 2. Metin uzunluğu
Validator.validate_string_length("Ali", "Ad", min_length=2, max_length=50)

# 3. TC Kimlik
Validator.validate_tc_id("12345678901")

# 4. Email
Validator.validate_email("ali@example.com")

# 5. Telefon
Validator.validate_phone("05331234567")

# 6. Pozitif sayı
Validator.validate_positive_number(100, "Tutar")

# 7. Tamsayı
Validator.validate_integer(5, "Kat")

# 8. Tarih
date = Validator.validate_date("25.12.2024", "%d.%m.%Y")

# 9. Seçenek
Validator.validate_choice("aktif", "Durum", ["aktif", "pasif"])
```

### UIValidator Sınıfı

```python
from models.validation import UIValidator

# Text Entry
ad = UIValidator.validate_text_entry(
    entry_ad, "Ad Soyad", min_length=2, max_length=50, parent=self
)
if ad is None:
    return

# Number Entry
tutar = UIValidator.validate_number_entry(
    entry_tutar, "Tutar", allow_negative=False, parent=self
)

# Combobox
durum = UIValidator.validate_combobox(combo_durum, "Durum", parent=self)
```

---

## UI Error Handling

### Dialog Fonksiyonları

```python
from ui.error_handler import (
    show_error,
    show_warning,
    show_success,
    handle_exception
)

# Hata dialog
show_error("Başlık", "Hata mesajı", parent=self)

# Uyarı dialog
show_warning("Uyarı", "Uyarı mesajı", parent=self)

# Başarı mesajı
show_success("Başarılı", "İşlem tamamlandı", parent=self)
```

### Context Manager

```python
from ui.error_handler import ErrorHandler

# Success message otomatik
with ErrorHandler(parent=self, show_success_msg=True):
    sakin = self.controller.create(data)

# Özel mesaj
with ErrorHandler(
    parent=self,
    show_success_msg=True,
    success_message="Sakin kaydedildi"
):
    sakin = self.controller.create(data)
```

### Manuel Exception Handling

```python
from ui.error_handler import handle_exception

try:
    sakin = self.controller.create(data)
except Exception as e:
    handle_exception(e, parent=self)
```

---

## Best Practices

### 1. Spesifik Exception Kullan

```python
# ✅ Doğru
from models.exceptions import ValidationError
raise ValidationError("Ad boş bırakılamaz")

# ❌ Yanlış
raise Exception("Hata")
```

### 2. Türkçe Mesajlar

```python
# ✅ Doğru
raise ValidationError("Ad soyad en az 2 karakter olmalıdır")

# ❌ Yanlış
raise ValidationError("Invalid input")
```

### 3. Defense in Depth

```python
# ✅ Doğru - Multiple validation layers
ad = UIValidator.validate_text_entry(entry_ad, "Ad", 2, 50)
if ad is None:
    return

try:
    Validator.validate_string_length(ad, "Ad", 2, 50)
    sakin = controller.create({"ad_soyad": ad})
except ValidationError as e:
    show_error("Hata", e.message)
```

---

## Örnekler

### Sakin Oluşturma

```python
from models.validation import Validator, UIValidator
from ui.error_handler import ErrorHandler, show_error

def create_sakin(self):
    # UI Validation
    ad = UIValidator.validate_text_entry(
        self.entry_ad, "Ad Soyad", 2, 50, self
    )
    if ad is None:
        return
    
    # Database operation
    try:
        with ErrorHandler(parent=self, show_success_msg=True):
            sakin = self.controller.create({
                "ad_soyad": ad,
                "telefon": UIValidator.validate_text_entry(
                    self.entry_telefon, "Telefon", parent=self
                )
            })
    except Exception as e:
        from ui.error_handler import handle_exception
        handle_exception(e, parent=self)
```

---

**Son Güncelleme**: 28 Kasım 2025  
**Versiyon**: v1.1  
**Status**: ✅ Tamamlandı
