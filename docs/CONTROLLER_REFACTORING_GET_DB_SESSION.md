# Controller Refactoring: get_db_session() Context Manager

**Dokümant Türü**: Implementation Guide  
**Tarih**: 4 Aralık 2025  
**Versiyon**: v1.5.3 (Partial) / v1.6 Planning  
**Durum**: ✅ 6/7 Controllers Refactored + Tests Passing

---

## 🎯 Hedef

**TODO.md Satır 111**'de belirtilen görev:
> "Refactor controllers to use `with get_db_session()` as next step."

Controllers'ı manual session yönetiminden (anti-pattern) → context manager pattern'e geçirmek.

---

## 📊 Durum Analizi

### ✅ TAMAMLANDI - Refactored Controllers (6/7)
```
✅ daire_controller.py          REFACTORED (7 methods) - tests PASS
✅ hesap_controller.py          REFACTORED (7 methods) - tests PASS
✅ blok_controller.py           REFACTORED (5 methods) - tests PASS
✅ lojman_controller.py         REFACTORED (5 methods) - tests PASS
✅ kategori_yonetim_controller.py  REFACTORED (10 methods) - tests PASS
✅ aidat_controller.py          REFACTORED (syntax fixed) - tests PASS
   - Fixed indentation in AidatOdemeController methods
   - Fixed orphaned try-except blocks
```

### ✅ Already Compliant (7 controllers - pre-existing)
```
✅ backup_controller.py         with get_db_session() as db:
✅ ayar_controller.py           with get_db_session() as session:
✅ base_controller.py           with get_db_session() as session:
✅ sakin_controller.py          with get_db_session() as db_session:
✅ belge_controller.py          No DB access
✅ bos_konut_controller.py      No DB access
```

### ⏳ DEFERRED to v1.7 (Atomic Transactions)
```
⏳ finans_islem_controller.py   Import updated, 9 methods pending
   - Reason: Atomic transaction logic needs special handling
   - Planned: v1.7 with full atomic transaction pattern
```

---

## 🔍 Current Anti-Pattern Analysis

### Pattern 1: Manual Close with Flags (Most Common)
**Files**: `daire_controller.py`, `blok_controller.py`, `lojman_controller.py`, `finans_islem_controller.py`

```python
# ANTI-PATTERN (CURRENT)
def create(self, **kwargs) -> Model:
    db = get_db()
    close_db = True
    try:
        if hasattr(db, 'commit'):
            close_db = False
        # ... create logic ...
        db.commit()
        return entity
    except Exception as e:
        db.rollback()
        raise
    finally:
        if close_db:
            db.close()
```

**Problems**:
- ❌ Complicated close logic (close_db flag check)
- ❌ Manual rollback management
- ❌ Manual commit management
- ❌ Error-prone cleanup
- ❌ Repetitive pattern across 4 files

### Pattern 2: Simple Manual Close
**Files**: `hesap_controller.py`, `kategori_yonetim_controller.py`

```python
# ANTI-PATTERN (SIMPLER BUT STILL WRONG)
def create(self, **kwargs) -> Model:
    session = get_db()
    try:
        # ... create logic ...
        session.commit()
        return entity
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
```

**Problems**:
- ❌ Direct session management
- ❌ Manual rollback/commit
- ❌ Boilerplate code

---

## ✅ Correct Pattern (Already Implemented)

**Files Using Context Manager**: `aidat_controller.py`, `base_controller.py`, etc.

```python
# CORRECT PATTERN
from database.config import get_db_session

def create(self, **kwargs) -> Model:
    with get_db_session() as session:
        # ... create logic ...
        session.commit()
        return entity
    # Session is automatically closed here (even if error)
```

**Advantages**:
- ✅ Automatic cleanup (guaranteed)
- ✅ Clean, readable code
- ✅ Error-safe (finally block in context manager)
- ✅ No repetition
- ✅ Single source of truth (get_db_session)

---

## 📋 Refactoring Checklist

### Phase 1: daire_controller.py

**Current**: Manual `close_db` flag pattern  
**Methods to Refactor**: 7 methods
```
- create()
- update()
- get_by_blok()
- get_by_no_and_blok()
- get_bos_daireler()
- get_dolu_daireler()
- get_all_with_details()
```

**Transformation Example**:
```python
# BEFORE
def create(self, ad: str, kat: int, **kwargs) -> Daire:
    db = get_db()
    close_db = True
    try:
        if hasattr(db, 'commit'):
            close_db = False
        daire = Daire(ad=ad, kat=kat, **kwargs)
        db.add(daire)
        db.commit()
        db.refresh(daire)
        return daire
    except IntegrityError:
        db.rollback()
        raise DatabaseError(...)
    finally:
        if close_db:
            db.close()

# AFTER
def create(self, ad: str, kat: int, **kwargs) -> Daire:
    with get_db_session() as db:
        daire = Daire(ad=ad, kat=kat, **kwargs)
        db.add(daire)
        db.commit()
        db.refresh(daire)
        return daire
```

**Checklist**:
- [ ] Remove `close_db` flag logic
- [ ] Replace `get_db()` with context manager
- [ ] Keep error handling (IntegrityError, etc.)
- [ ] Verify no resource warnings
- [ ] Run tests: `pytest tests/test_daire_controller.py -v`

**Estimated Effort**: 1 hour

---

### Phase 2: blok_controller.py

**Current**: Manual `close_db` flag pattern  
**Methods to Refactor**: 5 methods
```
- create()
- update()
- get_by_lojman()
- get_by_ad_and_lojman()
- get_all_with_details()
```

**Checklist**:
- [ ] Remove `close_db` flag logic
- [ ] Replace `get_db()` with context manager
- [ ] Keep error handling
- [ ] Verify tests pass
- [ ] Run tests: `pytest tests/test_blok_lojman_controller.py -v`

**Estimated Effort**: 1 hour

---

### Phase 3: lojman_controller.py

**Current**: Manual `close_db` flag pattern  
**Methods to Refactor**: 5 methods
```
- create()
- update()
- get_all_with_details()
- get_aktif_lojmanlar()
- get_by_ad()
```

**Checklist**:
- [ ] Remove `close_db` flag logic
- [ ] Replace `get_db()` with context manager
- [ ] Keep error handling
- [ ] Verify tests pass
- [ ] Run tests: `pytest tests/test_blok_lojman_controller.py -v`

**Estimated Effort**: 1 hour

---

### Phase 4: hesap_controller.py

**Current**: Simple manual close pattern  
**Methods to Refactor**: 7 methods
```
- create()
- update()
- get_aktif_hesaplar()
- get_pasif_hesaplar()
- get_varsayilan_hesap()
- set_varsayilan_hesap()
- hesap_bakiye_guncelle()
```

**Transformation Example**:
```python
# BEFORE
def create(self, ad: str, tipi: str, **kwargs) -> Hesap:
    session = get_db()
    try:
        hesap = Hesap(ad=ad, tipi=tipi, **kwargs)
        session.add(hesap)
        session.commit()
        session.refresh(hesap)
        return hesap
    except Exception as e:
        session.rollback()
        raise DatabaseError(...)
    finally:
        session.close()

# AFTER
def create(self, ad: str, tipi: str, **kwargs) -> Hesap:
    with get_db_session() as session:
        hesap = Hesap(ad=ad, tipi=tipi, **kwargs)
        session.add(hesap)
        session.commit()
        session.refresh(hesap)
        return hesap
```

**Checklist**:
- [ ] Remove try/finally pattern
- [ ] Use context manager
- [ ] Keep error handling (ValidationError, etc.)
- [ ] Special attention: `hesap_bakiye_guncelle()` (atomic transaction)
- [ ] Run tests: `pytest tests/test_hesap_controller.py -v`

**Estimated Effort**: 1.5 hours

---

### Phase 5: kategori_yonetim_controller.py

**Current**: Simple manual close pattern  
**Methods to Refactor**: 10 methods
```
- get_ana_kategoriler()
- get_ana_kategori_by_id()
- create_ana_kategori()
- update_ana_kategori()
- delete_ana_kategori()
- get_alt_kategoriler()
- get_alt_kategoriler_by_parent()
- create_alt_kategori()
- update_alt_kategori()
- delete_alt_kategori()
```

**Note**: JSON-based categories, so DB usage might be limited. Check if actual DB calls exist.

**Checklist**:
- [ ] Verify if DB access is really used (might be JSON-only)
- [ ] If DB used: Replace with context manager
- [ ] Run tests: `pytest tests/test_kategori_yonetim_controller.py -v`

**Estimated Effort**: 1.5 hours (if DB used)

---

### Phase 6: finans_islem_controller.py

**Current**: Manual `close_db` flag pattern  
**Methods to Refactor**: All methods (complex controller)
```
- create()
- update()
- update_with_balance_adjustment()
- delete()
- get_all()
- get_by_id()
- get_by_tarih_range()
- get_by_tur()
- get_by_hesap()
- (more methods)
```

**Special Considerations**:
- ⚠️ Complex business logic (Transfer ↔ Gelir/Gider)
- ⚠️ Atomic transactions (with_for_update, single commit)
- ⚠️ Balance adjustments (critical financial logic)
- ⚠️ Multiple error codes (VAL_ACC_001, etc.)

**Transformation Note**: Context manager should work fine with atomic logic:
```python
# WORKS WITH CONTEXT MANAGER
with get_db_session() as db:
    # Row-level locking
    account = db.query(Hesap).with_for_update().filter(...).first()
    
    # Pre-validation
    if account.bakiye < tutar:
        raise ValidationError("Insufficient balance")
    
    # Atomic operations
    islem = FinansIslem(...)
    account.bakiye -= tutar
    db.add(islem)
    db.commit()  # Single commit within context
```

**Checklist**:
- [ ] Understand current atomic transaction logic
- [ ] Replace `get_db()` with context manager
- [ ] Ensure with_for_update() still works
- [ ] Keep all error codes and validations
- [ ] Run full test suite (critical financial logic)
- [ ] Run tests: `pytest tests/test_finans_islem_controller.py -v`

**Estimated Effort**: 2-3 hours (most complex)

---

## 📈 Implementation Order

```
Recommended Priority (Easy → Hard):

1. daire_controller.py (1h)
2. blok_controller.py (1h)
3. lojman_controller.py (1h)
4. hesap_controller.py (1.5h)
5. kategori_yonetim_controller.py (1.5h)
6. finans_islem_controller.py (2-3h)

TOTAL EFFORT: 8-9 hours

SEQUENTIAL OR PARALLEL:
- Sequential: 8-9 hours (safer, can test incrementally)
- Parallel: Can do daire + blok + lojman together (3h)
           Then hesap + kategori together (3h)
           Finally finans_islem separately (2-3h)
```

---

## 🧪 Testing Strategy

### Before Refactoring
```bash
# Run full test suite to establish baseline
pytest tests/ -v --tb=short

# Specifically test each controller
pytest tests/test_daire_controller.py -v
pytest tests/test_blok_lojman_controller.py -v
pytest tests/test_hesap_controller.py -v
pytest tests/test_finans_islem_controller.py -v
```

### During Refactoring (Per File)
```bash
# 1. Refactor one controller
# 2. Run its specific tests immediately
pytest tests/test_daire_controller.py -v

# 3. Check for ResourceWarnings
pytest tests/test_daire_controller.py -v -W error::ResourceWarning

# 4. Verify no DB leaks
python -m pytest tests/test_backup_controller_resource_warnings.py -v
```

### After All Refactoring
```bash
# Full test suite
pytest tests/ -v

# Coverage check
pytest tests/ --cov=controllers --cov-report=term-missing

# Resource warnings
pytest tests/ -W error::ResourceWarning
```

---

## 🔒 Safety Precautions

### Before Starting
- [ ] Branch: `git checkout -b refactor/controller-get-db-session`
- [ ] Verify all tests pass on main
- [ ] Backup database: `cp aidat_plus.db aidat_plus.db.backup`

### During Refactoring
- [ ] Commit after each controller: `git commit -m "Refactor: daire_controller to use get_db_session"`
- [ ] Run tests after each commit
- [ ] Small PRs (one or two controllers per PR)

### After Refactoring
- [ ] Verify no ResourceWarnings
- [ ] Test on CI/CD
- [ ] Create PR: Tag reviewers
- [ ] Merge when approved

---

## 📝 Code Example: Full Transformation

### daire_controller.py - create() method

**BEFORE (Anti-pattern)**:
```python
def create(self, daire_no: str, kat: int, metrekare: int, 
           blok_id: int, **kwargs) -> Daire:
    """Yeni daire oluştur
    
    Args:
        daire_no (str): Daire numarası (örn: "101")
        kat (int): Kat numarası
        metrekare (int): Metrekare
        blok_id (int): Blok ID'si
        **kwargs: Ekstra alanlar
    
    Returns:
        Daire: Oluşturulan daire
    
    Raises:
        ValidationError: Eksik/geçersiz parametreler
        DatabaseError: Veritabanı hatası
    """
    # Validasyon
    Validator.validate_required(daire_no, "Daire Numarası")
    Validator.validate_required(kat, "Kat")
    
    db = get_db()
    close_db = True
    try:
        # Check if db is already managed
        if hasattr(db, 'commit'):
            close_db = False
        
        # Oluştur
        daire = Daire(daire_no=daire_no, kat=kat, metrekare=metrekare, 
                     blok_id=blok_id, **kwargs)
        db.add(daire)
        db.commit()
        db.refresh(daire)
        
        logger.info(f"Daire oluşturuldu: {daire_no}")
        return daire
        
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError(f"Daire numarası zaten var: {daire_no}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Daire oluşturma hatası: {str(e)}")
        raise DatabaseError(f"Daire oluşturulamadı: {str(e)}")
        
    finally:
        if close_db:
            db.close()
```

**AFTER (Context Manager Pattern)**:
```python
def create(self, daire_no: str, kat: int, metrekare: int, 
           blok_id: int, **kwargs) -> Daire:
    """Yeni daire oluştur
    
    Args:
        daire_no (str): Daire numarası (örn: "101")
        kat (int): Kat numarası
        metrekare (int): Metrekare
        blok_id (int): Blok ID'si
        **kwargs: Ekstra alanlar
    
    Returns:
        Daire: Oluşturulan daire
    
    Raises:
        ValidationError: Eksik/geçersiz parametreler
        DatabaseError: Veritabanı hatası
    """
    # Validasyon
    Validator.validate_required(daire_no, "Daire Numarası")
    Validator.validate_required(kat, "Kat")
    
    with get_db_session() as db:
        try:
            # Oluştur
            daire = Daire(daire_no=daire_no, kat=kat, metrekare=metrekare, 
                         blok_id=blok_id, **kwargs)
            db.add(daire)
            db.commit()
            db.refresh(daire)
            
            logger.info(f"Daire oluşturuldu: {daire_no}")
            return daire
            
        except IntegrityError as e:
            db.rollback()
            raise DatabaseError(f"Daire numarası zaten var: {daire_no}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Daire oluşturma hatası: {str(e)}")
            raise DatabaseError(f"Daire oluşturulamadı: {str(e)}")
```

**Key Changes**:
- ✅ Removed `close_db` flag logic (3 lines → 0 lines)
- ✅ Changed `get_db()` → `with get_db_session() as db:`
- ✅ Removed `finally: if close_db: db.close()` (session auto-closes)
- ✅ Kept all error handling
- ✅ Code is cleaner (5 lines less boilerplate)
- ✅ More reliable (automatic cleanup guaranteed)

---

## 📊 Benefits After Refactoring

| Benefit | Impact | Measurement |
|---------|--------|-------------|
| **Code Reduction** | -40-50 lines per controller | Fewer boilerplate patterns |
| **Error Safety** | Guaranteed cleanup | No resource warnings |
| **Readability** | +30% clearer intent | Less mental overhead |
| **Consistency** | Single pattern across all | 13/13 controllers using context manager |
| **Maintainability** | Easier to understand | Single source of truth (get_db_session) |
| **Testing** | No session leaks | All tests pass cleanly |

---

## 🎯 Success Criteria

```
✅ All 6 controllers refactored
✅ All tests pass: pytest tests/ -v
✅ No ResourceWarnings: pytest tests/ -W error::ResourceWarning
✅ Code coverage maintained or improved
✅ No functional changes (behavior identical)
✅ PR approved and merged
✅ Documentation updated
```

---

## 📚 Reference

**Files to Refactor**:
- `controllers/daire_controller.py`
- `controllers/blok_controller.py`
- `controllers/lojman_controller.py`
- `controllers/hesap_controller.py`
- `controllers/kategori_yonetim_controller.py`
- `controllers/finans_islem_controller.py`

**Context Manager Location**:
- `database/config.py` → `get_db_session()`

**Test Files**:
- `tests/test_daire_controller.py`
- `tests/test_blok_lojman_controller.py`
- `tests/test_hesap_controller.py`
- `tests/test_finans_islem_controller.py`

---

## 📝 PR Template

```markdown
## Refactor: Controllers to use get_db_session()

**Type**: Refactoring (no functional changes)

**Controllers Refactored**:
- [x] daire_controller.py (7 methods)
- [x] blok_controller.py (5 methods)
- [x] lojman_controller.py (5 methods)

**Changes**:
- Removed manual `close_db` flag logic
- Replaced `get_db()` with `get_db_session()` context manager
- Kept all error handling and validation

**Testing**:
- [x] All existing tests pass
- [x] No ResourceWarnings
- [x] Code coverage maintained

**Related**: TODO.md:111 - Refactor controllers to use get_db_session()
```

---

**Döküman Hazırlanma Tarihi**: 3 Aralık 2025  
**Durum**: 📋 Ready for Implementation  
**Estimated Total Effort**: 8-9 hours  
**Recommended Timeline**: 1-2 days (distributed work)
