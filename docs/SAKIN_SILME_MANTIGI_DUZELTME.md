# Sakin Silme Mantığı - Düzeltme (v1.3 Final)

**Tarihi**: 29 Kasım 2025  
**Durum**: ✅ Tamamlandı  
**Konu**: Soft delete prensibi - Arayüzden sil, veri sakla

---

## 📋 Karar

**Sakin silme işlemi soft delete prensibi ile yapılacak:**

- **Aktif sekmesinde**: "Sil" yok (sadece "Düzenle" ve "Pasif Yap")
- **Pasif sekmesinde**: "Sil" var ama arayüzden sadece siler, veri korunur

**Sebep:**
- Arayüzde gözükmez (kullanıcı görmez)
- Veritabanında veri kalır (veri bütünlüğü)
- Raporlamada tutarlı (tarihi veriler korunur)
- Denetim izi korunur (kim, ne zaman çıktı?)

---

## ✅ Uygulamalar

### 1. **Aktif Sekmesi Konteks Menüsü**

```python
# Sadece 2 seçenek
self.aktif_context_menu.add_command(label="Düzenle", command=self.duzenle_sakin)
self.aktif_context_menu.add_command(label="Pasif Yap", command=self.pasif_yap_sakin)
# "Sil" YOK
```

---

### 2. **Pasif Sekmesi Konteks Menüsü**

```python
# 3 seçenek
self.pasif_context_menu.add_command(label="Düzenle", command=self.duzenle_sakin)
self.pasif_context_menu.add_command(label="Sil", command=self.sil_sakin_pasif)  # ← Soft delete
self.pasif_context_menu.add_command(label="Aktif Yap", command=self.aktif_yap_sakin)
```

---

### 3. **`sil_sakin_pasif()` UI Metodu** (`sakin_panel.py`)

```python
def sil_sakin_pasif(self) -> None:
    """Pasif sekmesinden sakini kaldır (arayüzden gözükmez, veri korunur)
    
    Soft delete işlemi: Veritabanında veri kalır ama arayüzde gözükmez.
    """
    if self.ask_yes_no("Emin misiniz?\n(Veritabanında veri korunur)"):
        if self.sakin_controller.delete(int(sakin_id)):
            self.show_message("Başarıyla kaldırıldı! (Veri korunmuştur)")
```

**Mesaj açık:**
- Kullanıcı bilir ki sadece arayüzden silinecek
- Veri korunacak

---

### 4. **`delete()` Controller Metodu** (`sakin_controller.py`)

```python
def delete(self, id: int, db: Session = None) -> bool:
    """Sakini pasif sekmesinden kaldır (soft delete)
    
    Arayüzde gözükmez ama veritabanında veri kalır.
    Sadece aktif=False yapılır, hiçbir veri silinmez.
    """
    sakin.aktif = False  # ← Soft delete: sadece bunu yap
    session.commit()
    return True
```

**Fark:**
- `session.delete(sakin)` ❌ (Hard delete - veritabanından sil)
- `sakin.aktif = False` ✅ (Soft delete - arayüzde gözükmez, veri kalır)

---

## 🔄 İş Akışı

### Aktif Sekmede Sakin Çıkışı:
```
1. Sakin seçilir
2. Sağ tık → "Pasif Yap"
3. Çıkış tarihi sorulur (örn: "28.11.2025")
4. Pasif sekmesine taşınır
```

### Pasif Sekmede Sakini Gözardı Etme:
```
1. Sakin seçilir (çıkış tarihi: 28.11.2025)
2. Sağ tık → "Sil"
3. Onay: "Arşivden kaldırılacak. (Veritabanında veri korunur)"
4. Pasif listesinden gözükmez (aktif=False)
5. Veritabanında kalır
```

### Pasif Sekmede Sakini Aktif Yapma:
```
1. Sakin seçilir
2. Sağ tık → "Aktif Yap"
3. Yeniden aktif yapılır (cikis_tarihi silinir)
4. Aktif listesine taşınır
```

---

## ✨ Avantajları

| Yönü | Avantaj |
|------|---------|
| **Simplicity** | Arayüz temiz, soft delete basit |
| **Data Integrity** | Hiçbir veri silinmez, hepsi korunur |
| **Audit Trail** | Denetim izi tam olarak korunur |
| **Reporting** | "2024'te çıkmış, 2025'te geldi" analizi tutarlı |
| **Security** | Aktif sekmesinde "Sil" yok, risk azaldı |
| **Recovery** | Eski veri korunduğu için geri getirilebilir |

---

## 🔍 Veritabanı Durumu

### Aktif Sekmesi:
```sql
WHERE aktif=True AND cikis_tarihi IS NULL
```
- Çalışan sakinler
- Sadece "Pasif Yap" ile kaldırılabilir

### Pasif Sekmesi:
```sql
WHERE aktif=True AND cikis_tarihi IS NOT NULL
```
- Çıkmış sakinler
- "Sil" (soft delete) veya "Aktif Yap" yapılabilir

### Gözardı Edilmiş (Raporlardan dışarı):
```sql
WHERE aktif=False
```
- Arayüzde görmez ama veritabanında kalır
- Denetim izi ve raporlama için

---

## 📊 Veri Bütünlüğü

### Hiçbir Veri Silinmez:
```
Sakin Ali Yıldız (ID: 5):
├─ Tahsis Tarihi: 01.01.2020    ✅ KORUNUR
├─ Giriş Tarihi: 15.01.2020     ✅ KORUNUR
├─ Çıkış Tarihi: 28.11.2025     ✅ KORUNUR
├─ Eski Daire ID: 42            ✅ KORUNUR
├─ Aidat Kayıtları: 15          ✅ KORUNUR
└─ Aktif: False                 ✅ (gözardı edildi)
```

---

## 📋 Değişiklikler Özeti

### Dosyalar:
- ✅ `ui/sakin_panel.py`
  - `sil_sakin_pasif()`: Soft delete ile arayüzden sil
  - Mesaj: "Veri korunmuştur"

- ✅ `controllers/sakin_controller.py`
  - `delete()`: Soft delete (`aktif=False`)
  - Docstring: "arayüzde gözükmez ama veri kalır"

### Kod Değişimi:
```python
# ESKI (Hard delete)
session.delete(sakin)

# YENİ (Soft delete)
sakin.aktif = False
```

---

**Durum**: ✅ v1.3 - Sakin Silme Mantığı (Soft Delete) Tamamlandı
