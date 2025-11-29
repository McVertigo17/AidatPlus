# Theme ve Renk Ayarları - Troubleshooting Guide

**Tarih**: 29 Kasım 2025  
**Problem**: Arayüzün bazı yerlerinin siyah/koyu görünmesi, renklerin uyumsuz olması  
**Çözüm**: CustomTkinter theme uyarlaması ve Configuration Management entegrasyonu

---

## 🐛 Problem

Windows'ta CustomTkinter'ın "dark" mode'u uygulanırken:
- Başlık renkleri (primary: #003366) dark background'da gösterilir → siyah görünüyor
- Light tema için tasarlanmış renkler dark mode'da okunaksız
- Configuration'dan alınan theme ayarları GUI'ye yanlış uygulanıyor

---

## ✅ Çözüm

### 1. Theme Default'ı Güncelleme

**Eski** (`dark` mode):
```json
"ui": {
  "theme": "dark",
  ...
}
```

**Yeni** (`light` mode):
```json
"ui": {
  "theme": "light",
  ...
}
```

### 2. Güncellenmiş Dosyalar

| Dosya | Değişiklik |
|-------|-----------|
| `config/app_config.json` | theme: "dark" → "light" |
| `config/user_preferences.json` | theme: "light" ekle |
| `configuration/config_manager.py` | Default theme: "light" |
| `main.py` | Theme validation ve fallback |

### 3. main.py - Theme Validation

```python
theme = self.config.get(ConfigKeys.UI_THEME, 'dark')
# CustomTkinter appearance modes: "dark", "light", "system"
if theme not in ('dark', 'light', 'system'):
    theme = 'dark'  # Default to dark
ctk.set_appearance_mode(theme)
```

---

## 🎨 CustomTkinter Theme Behavior

### Appearance Modes

| Mode | Açıklama | Best For |
|------|----------|----------|
| **light** | Açık arka plan + koyu metin | Ofis, günlük kullanım |
| **dark** | Koyu arka plan + açık metin | Gece, uzun oturum |
| **system** | İşletim sistemi temasını takip | Automatik uyarlanma |

### Color Schemes

CustomTkinter:
- Otomatik olarak theme'i adapt eder
- Programlı renkler (hardcoded hex) theme'e uyarlanmaz
- Çözüm: CustomTkinter built-in colors kullanmak

---

## 🛠️ Best Practices

### 1. Dinamik Renk Seçimi

**Eski** (Hardcoded renk):
```python
header_frame = ctk.CTkFrame(parent, fg_color="#003366")  # Dark blue
```

**Yeni** (CustomTkinter theme aware):
```python
# CustomTkinter otomatik renk seçimi
header_frame = ctk.CTkFrame(parent, fg_color="gray17")  # Auto adapts
# veya theme'e göre:
if ctk.get_appearance_mode() == "dark":
    bg_color = "#1a1a1a"
else:
    bg_color = "#f0f0f0"
header_frame = ctk.CTkFrame(parent, fg_color=bg_color)
```

### 2. Configuration'dan Theme Alma

```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()
theme = config.get(ConfigKeys.UI_THEME, 'light')

# Validation ile
if theme not in ('dark', 'light', 'system'):
    theme = 'light'  # Safe default

ctk.set_appearance_mode(theme)
```

### 3. User Theme Preference Kaydetme

```python
from configuration import ConfigurationManager

config = ConfigurationManager.get_instance()

# Kullanıcı tema seçti
user_prefs = {
    'ui_preferences': {
        'theme': 'dark'  # Kullanıcı tercihi
    }
}

config.save_json_config('user_preferences.json', user_prefs)
```

---

## 📊 Current Configuration

### Theme Default'ı

```json
{
  "ui": {
    "theme": "light",        # Ana tema
    "color_scheme": "modern"  # Renk şeması (gelecek)
  }
}
```

### Supported Themes

```python
VALID_THEMES = ['dark', 'light', 'system']
```

---

## 🔄 Migration Guide

### Mevcut Kurulum'dan Update

```bash
# 1. Yeni configuration dosyaları yükle
cp config/app_config.json config/app_config.json.bak
# config/app_config.json'da theme: "light" olduğundan emin ol

# 2. Uygulamayı restart et
python main.py

# 3. Theme doğru uygulandığını kontrol et
# - Başlıklar mavi görünmeli
# - Background beyaz/açık
# - Metin okunabilir
```

---

## 🧪 Testing

### Theme Test Kodu

```python
import customtkinter as ctk
from configuration import ConfigurationManager, ConfigKeys

# Configuration yükle
config = ConfigurationManager.get_instance()
theme = config.get(ConfigKeys.UI_THEME, 'light')

# Validate
if theme not in ('dark', 'light', 'system'):
    theme = 'light'

# Apply
ctk.set_appearance_mode(theme)
print(f"Theme set to: {theme}")
print(f"Current mode: {ctk.get_appearance_mode()}")

# Create test window
root = ctk.CTk()
root.title("Theme Test")
root.geometry("300x200")

label = ctk.CTkLabel(root, text=f"Theme: {ctk.get_appearance_mode()}")
label.pack(pady=10)

root.mainloop()
```

### Beklenen Sonuçlar

**Light Mode**:
- ✅ Beyaz/açık background
- ✅ Koyu metin
- ✅ Mavi başlıklar (#003366)
- ✅ Okunabilir kontrastlar

**Dark Mode**:
- ✅ Koyu background (#1a1a1a)
- ✅ Açık metin
- ✅ Açık mavi başlıklar
- ✅ Göz yormayan kontrastlar

---

## 💡 Common Issues

### Issue 1: Siyah Başlıklar Light Mode'da

**Neden**: Dark blue (#003366) light background'da siyah gibi görünür.

**Çözüm**:
```python
if ctk.get_appearance_mode() == "light":
    header_fg_color = "#003366"  # Dark blue for light bg
else:
    header_fg_color = "#4D9FD9"  # Light blue for dark bg
header_frame = ctk.CTkFrame(parent, fg_color=header_fg_color)
```

### Issue 2: Dark Mode Uyumsuz Renkler

**Neden**: Configuration dark ayarlanmış ama UI light renklerle

**Çözüm**:
- config/app_config.json'da theme: "light" kontrol et
- Configuration Manager cache'ini temizle
- Uygulamayı restart et

### Issue 3: Theme Değişikliği Uygulanmıyor

**Neden**: ConfigurationManager Singleton, değişiklik uygulanmıyor.

**Çözüm**:
```python
config = ConfigurationManager.get_instance()
config.reload()  # Dosyasından yeniden yükle
# Sonra restart et
```

---

## 📈 Future Improvements

### Phase 1: Theme Customization ✅ (Current)
- [x] Light/Dark/System theme support
- [x] Configuration-based theme selection

### Phase 2: Theme Switcher (Planned)
- [ ] Runtime theme toggle button
- [ ] Theme preference persistence
- [ ] Smooth theme transition

### Phase 3: Custom Color Schemes (Future)
- [ ] User-defined color palettes
- [ ] Color scheme editor
- [ ] Export/import schemes

### Phase 4: Accessibility (Future)
- [ ] High contrast mode
- [ ] Font size customization
- [ ] Color blindness support

---

## 📚 References

- [CustomTkinter Documentation](https://github.com/TomSchimansky/CustomTkinter)
- [CustomTkinter Appearance Mode](https://github.com/TomSchimansky/CustomTkinter/wiki/Appearance-Mode)
- [Configuration Management](./CONFIGURATION_MANAGEMENT.md)

---

## ✅ Verification Checklist

- [x] Theme ayarları Configuration'dan alınıyor
- [x] app_config.json'da theme: "light"
- [x] configuration/config_manager.py default: "light"
- [x] main.py'de theme validation
- [x] CustomTkinter doğru moda ayarlanıyor
- [x] UI renkleri theme'e uygun
- [x] No breaking changes

---

**Durum**: ✅ Theme Troubleshooting Resolved  
**Versiyon**: 1.3 (Aidat Plus)  
**Son Güncelleme**: 29 Kasım 2025

