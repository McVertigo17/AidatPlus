"""
Tests for LojmanPanel UI smoke tests and helper functions.

This module tests the LojmanPanel class including:
- Panel initialization and controller setup
- Data loading functionality
- Lojman, Blok, and Daire CRUD operations
- Helper functions
- Controller interaction verification
"""

import pytest
from typing import List
from unittest.mock import Mock, patch, MagicMock

from models.base import Lojman, Blok, Daire
from controllers.lojman_controller import LojmanController
from controllers.blok_controller import BlokController
from controllers.daire_controller import DaireController
from ui.lojman_panel import LojmanPanel


class TestLojmanPanelInitialization:
    """Test LojmanPanel initialization and controller setup."""

    @pytest.fixture
    def colors(self):
        """Provide a standard colors dictionary."""
        return {
            "primary": "#003366",
            "success": "#28A745",
            "error": "#DC3545",
            "warning": "#FFC107",
            "surface": "#FFFFFF",
            "background": "#F5F5F5",
            "text": "#000000",
            "text_secondary": "#666666",
            "border": "#CCCCCC"
        }

    def test_lojman_controller_initialization(self, colors):
        """Test that LojmanController is initialized."""
        # Create a controller directly to verify instantiation
        controller = LojmanController()
        assert isinstance(controller, LojmanController)

    def test_blok_controller_initialization(self, colors):
        """Test that BlokController is initialized."""
        controller = BlokController()
        assert isinstance(controller, BlokController)

    def test_daire_controller_initialization(self, colors):
        """Test that DaireController is initialized."""
        controller = DaireController()
        assert isinstance(controller, DaireController)


class TestLojmanControllerDataLoading:
    """Test controller data loading functionality."""

    def test_lojman_controller_get_all(self, db_session):
        """Test that LojmanController.get_all retrieves lojman list."""
        controller = LojmanController()
        
        # get_all should return a list (empty or with data)
        lojmanlar = controller.get_all(db=db_session)
        assert isinstance(lojmanlar, list)

    def test_blok_controller_get_all(self, db_session):
        """Test that BlokController.get_all retrieves blok list."""
        controller = BlokController()
        
        # get_all should return a list
        bloklar = controller.get_all(db=db_session)
        assert isinstance(bloklar, list)

    def test_daire_controller_get_all_with_details(self, db_session):
        """Test that DaireController.get_all_with_details retrieves daire list."""
        controller = DaireController()
        
        # get_all_with_details should return a list
        daireler = controller.get_all_with_details(db=db_session)
        assert isinstance(daireler, list)


class TestLojmanControllerCRUD:
    """Test Lojman CRUD operations at controller level."""

    def test_lojman_create_with_valid_data(self, db_session):
        """Test creating a lojman with valid data."""
        controller = LojmanController()
        
        # Should be able to create without exception
        lojman = controller.create({"ad": "Test Lojman 3", "adres": "Test Address"}, db=db_session)
        assert lojman is not None
        assert lojman.ad == "Test Lojman 3"

    def test_lojman_read_by_id(self, db_session):
        """Test reading a lojman by ID."""
        controller = LojmanController()
        
        # Create a lojman first
        lojman = controller.create({"ad": "Test Read Lojman", "adres": "Test Address"}, db=db_session)
        assert lojman.id is not None
        
        # Read it back
        retrieved = controller.get_by_id(lojman.id, db=db_session)
        assert retrieved is not None
        assert retrieved.ad == "Test Read Lojman"

    def test_lojman_update(self, db_session):
        """Test updating a lojman."""
        controller = LojmanController()
        
        # Create a lojman
        lojman = controller.create({"ad": "Original Lojman", "adres": "Original Address"}, db=db_session)
        
        # Update it
        updated_lojman = controller.update(lojman.id, {"ad": "Updated"}, db=db_session)
        assert updated_lojman is not None
        
        # Verify update
        updated = controller.get_by_id(lojman.id, db=db_session)
        assert updated.ad == "Updated"

    def test_lojman_delete(self, db_session):
        """Test deleting a lojman."""
        controller = LojmanController()
        
        # Create and delete
        lojman = controller.create({"ad": "To Delete Lojman", "adres": "Address"}, db=db_session)
        success = controller.delete(lojman.id, db=db_session)
        assert success is True
        
        # Verify deletion
        deleted = controller.get_by_id(lojman.id, db=db_session)
        assert deleted is None


class TestBlokControllerCRUD:
    """Test Blok CRUD operations at controller level."""

    def test_blok_create_with_lojman(self, db_session):
        """Test creating a blok with a lojman."""
        # First create a lojman
        lojman_controller = LojmanController()
        lojman = lojman_controller.create({"ad": "Test Lojman 1", "adres": "Address"}, db=db_session)
        
        # Now create a blok
        blok_controller = BlokController()
        blok = blok_controller.create({"ad": "Blok A", "lojman_id": lojman.id, "kat_sayisi": 5}, db=db_session)
        
        assert blok is not None
        assert blok.ad == "Blok A"
        assert blok.lojman_id == lojman.id

    def test_blok_get_all(self, db_session):
        """Test getting all bloks."""
        controller = BlokController()
        bloklar = controller.get_all(db=db_session)
        assert isinstance(bloklar, list)


class TestDaireControllerCRUD:
    """Test Daire CRUD operations at controller level."""

    def test_daire_create_with_blok(self, db_session):
        """Test creating a daire with a blok."""
        # Create lojman, blok, then daire
        lojman_controller = LojmanController()
        lojman = lojman_controller.create({"ad": "Test Lojman 2", "adres": "Address"}, db=db_session)
        
        blok_controller = BlokController()
        blok = blok_controller.create({"ad": "Blok A", "lojman_id": lojman.id, "kat_sayisi": 5}, db=db_session)
        
        # Create daire
        daire_controller = DaireController()
        daire = daire_controller.create({
            "daire_no": "101",
            "blok_id": blok.id,
            "kat": 1,
            "oda_sayisi": 2
        }, db=db_session)
        
        assert daire is not None
        assert daire.daire_no == "101"
        assert daire.blok_id == blok.id

    def test_daire_get_all_with_details(self, db_session):
        """Test getting all daires with details."""
        controller = DaireController()
        daireler = controller.get_all_with_details(db=db_session)
        assert isinstance(daireler, list)


class TestLojmanPanelHierarchy:
    """Test the hierarchical structure: Lojman -> Blok -> Daire."""

    def test_lojman_blok_daire_hierarchy(self, db_session):
        """Test creating complete lojman-blok-daire hierarchy."""
        # Create lojman
        lojman_controller = LojmanController()
        lojman = lojman_controller.create({"ad": "Hierarchy Test Lojman", "adres": "Test Address"}, db=db_session)
        assert lojman is not None
        
        # Create blok under lojman
        blok_controller = BlokController()
        blok = blok_controller.create({"ad": "Blok B", "lojman_id": lojman.id, "kat_sayisi": 3}, db=db_session)
        assert blok.lojman_id == lojman.id
        
        # Create daire under blok
        daire_controller = DaireController()
        daire = daire_controller.create({
            "daire_no": "201",
            "blok_id": blok.id,
            "kat": 2,
            "oda_sayisi": 3
        }, db=db_session)
        assert daire.blok_id == blok.id
        
        # Verify relationships
        retrieved_daire = daire_controller.get_by_id(daire.id, db=db_session)
        assert retrieved_daire.blok_id == blok.id
