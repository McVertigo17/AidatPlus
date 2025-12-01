import pytest
from models.validation import Validator, BatchValidator
from models.exceptions import ValidationError, DuplicateError


def test_validate_required_and_string_length():
    # Required
    with pytest.raises(ValidationError):
        Validator.validate_required(None, "Ad")
    with pytest.raises(ValidationError):
        Validator.validate_required("  ", "Ad")

    # String length
    with pytest.raises(ValidationError):
        Validator.validate_string_length("A", "Ad", 2, 3)
    with pytest.raises(ValidationError):
        Validator.validate_string_length("A"*10, "Ad", 1, 3)


def test_validate_phone_and_email():
    # Phone
    Validator.validate_phone("05331234567")
    Validator.validate_phone("+90 533 123 45 67")
    with pytest.raises(ValidationError):
        Validator.validate_phone("1234")

    # Email
    Validator.validate_email("ali@example.com")
    with pytest.raises(ValidationError):
        Validator.validate_email("invalid-email")


def test_validate_positive_integer_date_choice():
    Validator.validate_positive_number(10, "Tutar")
    with pytest.raises(ValidationError):
        Validator.validate_positive_number(-5, "Tutar")
    Validator.validate_positive_number(0, "Tutar", allow_zero=True)

    # Integer
    with pytest.raises(ValidationError):
        Validator.validate_integer(1.5, "Kat")

    # Date
    assert Validator.validate_date("25.12.2025")
    with pytest.raises(ValidationError):
        Validator.validate_date("25/12/2025")

    # choice
    Validator.validate_choice("a", "Opt", ["a", "b"])
    with pytest.raises(ValidationError):
        Validator.validate_choice("c", "Opt", ["a", "b"])


def test_unique_field_and_batchvalidator(db_session):
    from models.base import Lojman
    # create a lojman
    l = Lojman(ad="UniqueLojmanTest", adres="adr")
    db_session.add(l)
    db_session.commit()

    # Should raise DuplicateError
    with pytest.raises(DuplicateError):
        Validator.validate_unique_field(db_session, Lojman, "ad", "UniqueLojmanTest")

    # BatchValidator
    b = BatchValidator()
    b.add_error("ad", "Too short")
    assert b.has_errors()
    assert "ad" in b.get_errors()
    with pytest.raises(ValidationError):
        b.raise_if_errors()
