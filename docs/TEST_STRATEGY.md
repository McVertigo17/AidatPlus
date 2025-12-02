# Test Stratejisi ve Rehberi

**Yazılım**: Aidat Plus  
**Tarih**: 2 Aralık 2025  
**Versiyon**: v1.4 (Test Framework)

---

## 📋 İçindekiler

1. [Test Türleri](#test-türleri)
2. [Test Strukturu](#test-strukturu)
3. [Yazı Kılavuzları](#yazı-kılavuzları)
4. [Test Çalıştırma](#test-çalıştırma)
5. [Coverage Hedefleri](#coverage-hedefleri)
6. [Örnek Testler](#örnek-testler)
7. [Sorun Giderme](#sorun-giderme)

---

## Test Türleri

### 1. **Unit Tests** (Birim Testleri)

Tek bir fonksiyon veya metodu test et.

```python
# test_sakin_controller.py
def test_create_sakin_success():
    """Should create sakin with valid data"""
    controller = SakinController()
    sakin = controller.create("Ali Yıldız", "12345678901")
    assert sakin.ad_soyad == "Ali Yıldız"
```

**Kapsamı**: Controllers, Models, Validators

### 2. **Integration Tests** (Entegrasyon Testleri)

Birden fazla bileşenin birlikte çalışmasını test et.

```python
# test_aidat_workflow.py
def test_create_aidat_and_record_payment():
    """Should create aidat and record payment"""
    aidat_controller = AidatController()
    sakin_controller = SakinController()
    
    # 1. Create sakin
    sakin = sakin_controller.create(...)
    
    # 2. Create aidat
    aidat = aidat_controller.create(sakin.id, ...)
    
    # 3. Record payment
    payment = aidat_controller.record_payment(aidat.id, ...)
    
    assert payment.miktar > 0
```

**Kapsamı**: Multi-component workflows

### 3. **Negative Tests** (Negatif Testler)

Hata senaryolarını test et.

```python
def test_create_sakin_invalid_tc():
    """Should raise ValidationError for invalid TC"""
    controller = SakinController()
    
    with pytest.raises(ValidationError):
        controller.create("Ali Yıldız", "invalid_tc")
```

**Kapsamı**: Error handling, validation

### 4. **Edge Cases** (Sınır Durumları)

Ekstrem durumları test et.

```python
def test_transfer_with_zero_balance():
    """Should handle transfer with zero balance"""
    hesap_controller = HesapController()
    
    # Create hesap with zero balance
    hesap = hesap_controller.create("Boş Hesap", "Aktif", 0)
    
    # Try transfer
    with pytest.raises(ValidationError):
        finans_controller.create(
            tur="Transfer",
            hesap_id=hesap.id,
            tutar=100
        )
```

**Kapsamı**: Boundary conditions

### 5. **Regression Tests** (Regresyon Testleri)

Eski bugs'ların tekrar oluşmaması kontrolü.

```python
def test_sakin_archive_preservation():
    """Should preserve sakin archive (Regression: v1.2 fix)"""
    # Test that when reactivating a sakin, old archive is preserved
    pass
```

**Kapsamı**: Known issues

### 6. **UI Tests** (Kullanıcı Arayüzü Testleri)

Grafiksel arayüz bileşenlerini test et.

```python
# test_lojman_panel.py
def test_lojman_creation_ui():
    """Should create lojman through UI"""
    # Mock UI components
    # Simulate user input
    # Verify UI response
    pass
```

**Kapsamı**: Panel interactions, user workflows

### 7. **End-to-End Tests** (Uçtan Uca Testler)

Tüm sistemin tamamını test et.

```python
# test_end_to_end_flow.py
def test_complete_lojman_sakin_finans_flow():
    """Should complete full workflow from lojman to finans"""
    # 1. Create lojman → blok → daire
    # 2. Add sakin to daire
    # 3. Create aidat for sakin
    # 4. Record payment
    # 5. Verify finans records
    pass
```

**Kapsamı**: Full business workflows

---

## Test Strukturu

### Dosya Organizasyonu

```
tests/
├── __init__.py
├── conftest.py                      # Fixtures ve setup
├── test_sakin_controller.py        # Sakin tests
├── test_aidat_controller.py        # Aidat tests
├── test_finans_islem_controller.py # Finans tests
├── test_hesap_controller.py        # Hesap tests
├── test_base_controller.py         # Base controller tests
├── test_backup_controller.py       # Backup tests
├── test_belge_controller.py        # Belge tests
├── test_end_to_end_flow.py         # E2E tests
├── test_models/
│   ├── test_validation.py          # Validator tests
│   └── test_config_manager.py      # Config tests
└── ui/
    ├── test_lojman_panel.py        # Lojman UI tests
    ├── test_sakin_panel.py         # Sakin UI tests
    └── test_lojman_sakin_integration.py # Integration tests
```

### Fixture'lar (conftest.py)

```python
# tests/conftest.py
import pytest
from database.config import SessionLocal, Base, engine
from models.base import Lojman, Sakin, Daire

@pytest.fixture
def test_db():
    """Create test database (in-memory SQLite)"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session(test_db):
    """Provide database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_lojman(session):
    """Create sample lojman"""
    lojman = Lojman(ad="Test Lojmanı", lokasyon="Ankara")
    session.add(lojman)
    session.commit()
    return lojman
```

---

## Yazı Kılavuzları

### Test Adlandırması

```python
# ✅ İyi
def test_create_sakin_with_valid_data():
    """Should create sakin"""
    pass

# ❌ Kötü
def test_1():
    pass

def test_create():
    pass
```

### Test Yapısı (AAA Pattern)

```python
def test_transfer_between_accounts():
    """Test transfer logic"""
    
    # Arrange: Veri hazırla
    source_account = hesap_controller.create("Kaynak", "Aktif", 1000)
    dest_account = hesap_controller.create("Hedef", "Aktif", 0)
    
    # Act: İşlemi yap
    transfer = finans_controller.create(
        tur="Transfer",
        hesap_id=source_account.id,
        tutar=500
    )
    
    # Assert: Sonucu kontrol et
    assert source_account.bakiye == 500
    assert dest_account.bakiye == 500
```

### Docstring Formatı

```python
def test_create_sakin_success():
    """Should create sakin with valid data
    
    Scenario: Create sakin with all required fields
    - Create sakin with name and TC ID
    - Verify sakin record created
    - Check return value is Sakin instance
    """
    pass
```

### Exception Testing

```python
# ✅ İyi
def test_invalid_tc_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        controller.create("Ali", "invalid")
    
    assert "TC" in str(exc_info.value)

# ❌ Kötü
def test_invalid_tc():
    try:
        controller.create("Ali", "invalid")
        assert False, "Should raise error"
    except:
        pass
```

---

## Test Çalıştırma

### Temel Komutlar

```bash
# Tüm testler
pytest tests/ -v

# Spesifik dosya
pytest tests/test_sakin_controller.py -v

# Spesifik test
pytest tests/test_sakin_controller.py::test_create_sakin_success -v

# Coverage raporu
pytest tests/ --cov=. --cov-report=html

# Hızlı (durup devam etmese print output)
pytest tests/ -x  # Stop on first failure
pytest tests/ -q  # Quiet mode

# Paralel (hızlı)
pytest tests/ -n auto
```

### Coverage Raporu Açma

```bash
# HTML rapor oluştur
pytest tests/ --cov=. --cov-report=html

# Tarayıcıda açı
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

### Continuous Testing (Watch Mode)

```bash
# Dosya değişince otomatik test çalıştır
pytest-watch tests/ -- -v
```

---

## Coverage Hedefleri

### Hedefler (v1.4)

| Modül | Hedef | Durum |
|-------|-------|-------|
| **Controllers** | %70+ | ✅ Tamamlandı (%93) |
| **Models** | %80+ | ✅ Tamamlandı (%94) |
| **Validators** | %85+ | ✅ Tamamlandı (%94) |
| **Utils** | %80+ | ✅ Tamamlandı (%99) |
| **UI** | %30+ | ✅ Tamamlandı (%70+) |

### Coverage Anlama

```
Line Coverage:    % = (executed lines) / (total lines)
Branch Coverage:  % = (executed branches) / (total branches)

Örnek:
def create_sakin(name):
    if name:        # Branch 1
        return True # Line 1
    return False    # Line 2

100% Line Coverage: Tüm satırlar çalıştırılmış
100% Branch Coverage: Both if/else çalıştırılmış
```

---

## Örnek Testler

### Controller Test Örneği

```python
# tests/test_sakin_controller.py
import pytest
from controllers.sakin_controller import SakinController
from models.exceptions import ValidationError, NotFoundError

class TestSakinController:
    
    @pytest.fixture
    def controller(self, session):
        return SakinController(session)
    
    def test_create_sakin_success(self, controller):
        """Test sakin creation with valid data"""
        sakin = controller.create(
            ad_soyad="Ali Yıldız",
            tc_id="12345678901",
            telefon="+90 555 123 4567"
        )
        
        assert sakin.ad_soyad == "Ali Yıldız"
        assert sakin.tc_id == "12345678901"
    
    def test_create_sakin_invalid_tc(self, controller):
        """Test sakin creation with invalid TC"""
        with pytest.raises(ValidationError):
            controller.create(
                ad_soyad="Ali Yıldız",
                tc_id="invalid"
            )
    
    def test_update_sakin_success(self, controller):
        """Test sakin update"""
        sakin = controller.create("Ali Yıldız", "12345678901")
        
        updated = controller.update(sakin.id, ad_soyad="Veli Yıldız")
        
        assert updated.ad_soyad == "Veli Yıldız"
    
    def test_delete_sakin_success(self, controller):
        """Test sakin deletion"""
        sakin = controller.create("Ali Yıldız", "12345678901")
        
        controller.delete(sakin.id)
        
        with pytest.raises(NotFoundError):
            controller.read(sakin.id)
```

### Validation Test Örneği

```python
# tests/test_models/test_validation.py
import pytest
from models.validation import Validator

class TestValidator:
    
    def test_valid_tc_id(self):
        """Test valid TC ID validation"""
        assert Validator.validate_tc_id("12345678901") is True
    
    def test_invalid_tc_id(self):
        """Test invalid TC ID validation"""
        with pytest.raises(ValidationError):
            Validator.validate_tc_id("invalid")
    
    def test_positive_number(self):
        """Test positive number validation"""
        assert Validator.validate_positive_number(100) is True
    
    def test_negative_number_fails(self):
        """Test negative number validation fails"""
        with pytest.raises(ValidationError):
            Validator.validate_positive_number(-100)
```

### UI Test Örneği

```python
# tests/ui/test_lojman_panel.py
import pytest
from unittest.mock import MagicMock, patch
from ui.lojman_panel import LojmanPanel

class TestLojmanPanel:
    
    @pytest.fixture
    def mock_app(self):
        return MagicMock()
    
    @pytest.fixture
    def panel(self, mock_app):
        with patch('ui.lojman_panel.LojmanController') as mock_controller:
            panel = LojmanPanel(mock_app)
            panel.lojman_controller = mock_controller
            return panel
    
    def test_create_lojman_success(self, panel):
        """Test successful lojman creation through UI"""
        # Mock UI inputs
        panel.entry_lojman_ad.get.return_value = "Test Lojman"
        panel.entry_lojman_adres.get.return_value = "Test Adres"
        
        # Call method
        panel.create_lojman()
        
        # Verify controller was called
        panel.lojman_controller.create.assert_called_once_with(
            ad="Test Lojman",
            adres="Test Adres"
        )
```

---

## Sorun Giderme

### Problem: "ModuleNotFoundError"

```bash
# Çözüm: Proje path'ini ekle
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Problem: "Database is locked"

```bash
# Çözüm: Fixture'da transaction isolation
@pytest.fixture
def session(test_db):
    session = SessionLocal()
    session.begin_nested()  # Savepoint
    yield session
    session.rollback()
```

### Problem: "Timeout during test"

```bash
# Çözüm: Pytest timeout ekle
pytest tests/ --timeout=30
```

### Problem: "Test passes locally but fails on CI"

```bash
# Çözüm: Platform-agnostic path'ler kullan
from pathlib import Path
test_file = Path(__file__).parent / "fixtures" / "test.xlsx"
```

---

## 📊 Test Metrikleri

### Mevcut Test Coverage (v1.4)

```
controllers/
  ├── test_sakin_controller.py         : 22 tests, 95% coverage
  ├── test_aidat_controller.py         : 15 tests, 88% coverage
  ├── test_finans_islem_controller.py : 28 tests, 92% coverage
  ├── test_hesap_controller.py         : 18 tests, 90% coverage
  ├── test_base_controller.py          : 22 tests, 96% coverage
  ├── test_backup_controller.py        : 30 tests, 99% coverage
  ├── test_belge_controller.py         : 28 tests, 99% coverage
  ├── test_daire_controller.py         : 12 tests, 92% coverage
  ├── test_blok_controller.py          : 10 tests, 90% coverage
  └── test_lojman_controller.py        : 10 tests, 91% coverage

models/
  └── test_validation.py               : 16 tests, 94% coverage

ui/
  ├── test_lojman_panel.py             : 15 tests, 100% coverage
  └── test_lojman_sakin_integration.py : 3 tests, 100% coverage

integration/
  └── test_end_to_end_flow.py          : 2 tests, 100% coverage

Total: ~200 tests, average 94% coverage
```

---

## 🔗 İlişkili Dokümantasyon

- [CI_PIPELINE.md](CI_PIPELINE.md) - CI/CD yapılandırması
- [TODO.md](../TODO.md) - Test hedefleri
- [pytest.ini](../pytest.ini) - Pytest konfigürasyonu

---

**Son Güncelleme**: 2 Aralık 2025  
**Versiyon**: 1.1 (Test Strategy - v1.4 Updates)  
**Yapımcı**: Aidat Plus Ekibi