from controllers.ayar_controller import AyarController


def test_ayar_controller_create_and_get(db_session):
    """Test creating and getting an ayar"""
    session = db_session
    controller = AyarController()
    
    # Create a new ayar
    result = controller.set_ayar("test_key", "test_value", "Test ayarı", db=session)
    assert result is True
    
    # Get the ayar
    ayar = controller.get_ayar("test_key", db=session)
    assert ayar is not None
    assert ayar.anahtar == "test_key"
    assert ayar.deger == "test_value"
    assert ayar.aciklama == "Test ayarı"


def test_ayar_controller_update_existing(db_session):
    """Test updating an existing ayar"""
    session = db_session
    controller = AyarController()
    
    # Create initial ayar
    controller.set_ayar("update_key", "initial_value", "Initial", db=session)
    
    # Update the ayar
    result = controller.set_ayar("update_key", "updated_value", "Updated", db=session)
    assert result is True
    
    # Get updated ayar
    ayar = controller.get_ayar("update_key", db=session)
    assert ayar is not None
    assert ayar.deger == "updated_value"
    assert ayar.aciklama == "Updated"


def test_ayar_controller_get_all(db_session):
    """Test getting all ayarlar"""
    session = db_session
    controller = AyarController()
    
    # Create multiple ayarlar
    controller.set_ayar("key1", "value1", "First", db=session)
    controller.set_ayar("key2", "value2", "Second", db=session)
    controller.set_ayar("key3", "value3", "Third", db=session)
    
    # Get all ayarlar
    ayarlar = controller.get_all_ayarlar(db=session)
    assert len(ayarlar) >= 3
    assert ayarlar["key1"] == "value1"
    assert ayarlar["key2"] == "value2"
    assert ayarlar["key3"] == "value3"


def test_ayar_controller_get_with_default(db_session):
    """Test getting ayar with default value"""
    session = db_session
    controller = AyarController()
    
    # Test non-existent ayar with default
    result = controller.get_ayar_with_default("non_existent", "default_value", db=session)
    assert result == "default_value"
    
    # Test existing ayar
    controller.set_ayar("existent_key", "actual_value", db=session)
    result = controller.get_ayar_with_default("existent_key", "default_value", db=session)
    assert result == "actual_value"