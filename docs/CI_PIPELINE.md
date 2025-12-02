# CI Pipeline Rehberi

**Yazılım**: Aidat Plus  
**Tarih**: 2 Aralık 2025  
**Versiyon**: v1.4 (CI Integration)

---

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Workflow Konfigürasyonu](#workflow-konfigürasyonu)
3. [Yapılandırma Dosyaları](#yapılandırma-dosyaları)
4. [Yerel Çalıştırma](#yerel-çalıştırma)
5. [GitHub Actions Entegrasyonu](#github-actions-entegrasyonu)
6. [Sorun Giderme](#sorun-giderme)
7. [Best Practices](#best-practices)

---

## Genel Bakış

### CI Pipeline Hedefleri

Aidat Plus CI Pipeline, kod kalitesini ve stabilitesini sağlamak için aşağıdaki kontrolleri gerçekleştirir:

| Aşama | Araç | Görev | Durum |
|-------|------|-------|-------|
| **Lint** | flake8 | Python syntax ve stil | ✅ |
| **Type Check** | mypy | Static type checking | ✅ |
| **Unit Tests** | pytest | Birim testleri çalıştır | ✅ |
| **Coverage** | coverage | Test kapsama raporı | ✅ |
| **Build Check** | py_compile | Import ve build doğrulama | ✅ |

### İş Akışı (Workflow)

```
Push/PR → Lint → Type Check → Tests → Coverage → Build → Summary
         (P)      (P)         (P)       (P)       (P)      (P)
```

**P** = Parallel (Aynı anda çalışan görevler)

---

## Workflow Konfigürasyonu

### CI Workflow (Ubuntu/Linux - `.github/workflows/ci.yml`)

**Tetikleyiciler**:
- Push: `main`, `develop` branch'lerine
- Pull Request: `main`, `develop` branch'lerine

**Görevler (Jobs)**:

#### 1. **Lint Job**
```yaml
- Name: Lint & Code Quality
- Runner: ubuntu-latest
- Python: 3.11
- Araçlar: flake8, pylint
- Konfigürasyon: .flake8 (opsiyonel)
```

**Flake8 Kuralları**:
- E9, F63, F7, F82: Syntax hatalarını durdur (fail)
- Diğer hatalar: Uyarı olarak göster (continue-on-error: true)

#### 2. **MyPy Job**
```yaml
- Name: Type Check (MyPy)
- Runner: ubuntu-latest
- Python: 3.11
- Araçlar: mypy, types-setuptools, types-requests
- Konfigürasyon: mypy.ini (strict mode)
```

**MyPy Ayarları** (`mypy.ini`):
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

#### 3. **Tests Job**
```yaml
- Name: Unit Tests & Coverage
- Runner: ubuntu-latest
- Python: 3.11
- Araçlar: pytest, pytest-cov, coverage
- Konfigürasyon: pytest.ini, .coveragerc
```

**Pytest Ayarları** (`pytest.ini`):
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov-fail-under=70
```

**Coverage Raporlaması**:
- XML format: `coverage.xml` (Codecov için)
- HTML format: `htmlcov/` (yerel inceleme)
- Terminal: stdout'a yazdırır
- Minimum coverage: 70% (fail_under)

#### 4. **Build Job**
```yaml
- Name: Build Check
- Runner: ubuntu-latest
- Python: 3.11
- Görev: Import ve syntax kontrol
```

**Kontroller**:
- `main.py` syntax doğrulaması
- `AidatPlusApp` sınıfı import kontrolü
- Success mesajı: "✓ Main module loads successfully"

#### 5. **Summary Job**
```yaml
- Name: CI Summary
- Runner: ubuntu-latest
- Dependency: Diğer tüm görevler
```

**Çıktı**: Tüm görevlerin sonuçları
```
✅ CI Pipeline completed!
- Lint: <result>
- Type Check: <result>
- Tests: <result>
- Build: <result>
```

### Windows CI Workflow (`.github/workflows/ci-windows.yml`)

**Amaç**: Windows üzerinde test uyumluluğu

```yaml
- Name: Tests on Windows
- Runner: windows-latest
- Python: 3.11
- Araçlar: pytest
```

---

## Yapılandırma Dosyaları

### `.coveragerc` - Coverage Ayarları

```ini
[run]
source = .
omit = */tests/*, */__pycache__/*, ...

[report]
exclude_lines = pragma: no cover, ...
precision = 2

[html]
directory = htmlcov
```

**Anlamı**:
- `source = .`: Tüm proje dosyalarını ölç
- `omit`: Belirtilen dosyaları hariç tut
- `exclude_lines`: Type hints, abstract methods, vb. hariç tut
- HTML raporu: `htmlcov/index.html`'de

### `.github/workflows/ci.yml` - Ana Workflow

**Temel Yapı**:
```yaml
name: CI Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
jobs:
  lint: { ... }
  mypy: { ... }
  tests: { ... }
  build: { ... }
  summary: { ... }
```

---

## Yerel Çalıştırma

### Lint Kontrol

```bash
# Sadece syntax hataları
flake8 . --select=E9,F63,F7,F82

# Tüm uyarılar
flake8 . --max-line-length=127 --max-complexity=10
```

### Type Check

```bash
mypy . --config-file=mypy.ini
```

### Test Çalıştırma

```bash
# Tüm testler
pytest tests/ -v

# Spesifik test dosyası
pytest tests/test_sakin_controller.py -v

# Coverage raporu ile
pytest tests/ --cov=. --cov-report=html

# Minimum coverage ile test
pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=70
```

### Coverage Raporu

```bash
# HTML rapor oluştur
coverage run -m pytest tests/
coverage html

# Sonra açı: htmlcov/index.html
```

### Build Kontrol

```bash
python -m py_compile main.py
python -c "import main; print('✓ Success')"
```

---

## GitHub Actions Entegrasyonu

### Workflow Durum

1. **Repo'ya Git Push**
   ```bash
   git add .github/workflows/
   git add .coveragerc
   git commit -m "Add CI Pipeline"
   git push origin main
   ```

2. **GitHub'da Kontrol**
   - Repo'ya git: https://github.com/McVertigo17/AidatPlus
   - "Actions" sekmesi
   - "CI Pipeline" workflow'u göreceksin

3. **Workflow Sonuçları**
   - ✅ Başarılı: Tüm görevler geçti
   - ❌ Başarısız: Bir veya daha fazla görev başarısız

### Badges (README)

```markdown
![CI](https://github.com/McVertigo17/AidatPlus/workflows/CI%20Pipeline/badge.svg)
![Tests](https://img.shields.io/badge/Tests-pytest-blue)
```

---

## Sorun Giderme

### Problem: "No module named 'customtkinter'"

**Çözüm**: requirements.txt'i güncelle
```bash
pip install -r requirements.txt --upgrade
```

### Problem: "MyPy errors on CI"

**Çözüm**: Yerel MyPy kontrolü
```bash
mypy . --config-file=mypy.ini
```

Hataları düzelt, sonra push et.

### Problem: "Test failures on CI"

**Çözüm**: Yerel pytest çalıştır
```bash
pytest tests/ -v --tb=short
```

Hataları düzelt, sonra push et.

### Problem: Coverage Codecov'a Upload Başarısız

**Not**: Codecov gerekli değil, opsiyonel. `fail_ci_if_error: false` olduğu için CI başarısız olmaz.

---

## Best Practices

### 1. Commit Öncesi Yerel Test

```bash
# Lint
flake8 . --select=E9,F63,F7,F82

# Type check
mypy . --config-file=mypy.ini

# Tests
pytest tests/ -v

# Sonra commit et
git add .
git commit -m "Feature: ..."
git push
```

### 2. Type Hints Ekle

Her yeni fonksiyona:
```python
def create_sakin(self, ad_soyad: str, tc_id: str) -> Sakin:
    """Docstring with types"""
    pass
```

### 3. Test Yazma

Her yeni controller fonksiyonu için:
```python
def test_create_sakin():
    controller = SakinController()
    sakin = controller.create("Ali Yıldız", "12345678901")
    assert sakin.ad_soyad == "Ali Yıldız"
```

### 4. Coverage Hedefi

- **Kritik modüller** (controllers): %70+
- **Utilities**: %80+
- **Models**: %80+

### 5. UI Testleri

UI testleri için mock kullan:
```python
# tests/ui/test_lojman_panel.py
def test_create_lojman_ui():
    with patch('ui.lojman_panel.LojmanController') as mock_controller:
        # Test UI interactions
        pass
```

---

## 🔗 İlişkili Dokümantasyon

- [TODO.md](../TODO.md) - Geliştirme planı
- [AGENTS.md](../AGENTS.md) - Kod stili rehberi
- [pytest.ini](../pytest.ini) - Test konfigürasyonu
- [TEST_STRATEGY.md](TEST_STRATEGY.md) - Test stratejisi

---

## 📊 Workflow Durumu

```
Aşama              | Araç        | Durum
------------------|-------------|-------
Lint              | flake8      | ✅ Kurulu
Type Check        | mypy        | ✅ Kurulu
Tests             | pytest      | ✅ Kurulu
Coverage          | coverage    | ✅ Kurulu
Build             | py_compile  | ✅ Kurulu
Windows Tests     | pytest      | ✅ Kurulu
CI Badges         | shields.io  | ✅ Kurulu
Test Coverage     | pytest-cov  | ✅ 70%+ Hedef
```

---

**Son Güncelleme**: 2 Aralık 2025  
**Versiyon**: 1.1 (CI Pipeline v1.4 Updates)  
**Yapımcı**: Aidat Plus Ekibi