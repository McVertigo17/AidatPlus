"""
BelgeController unit tests — Happy path + comprehensive negative/edge case tests.

Tests cover:
    1. Happy path: File add, delete, check, open, get name
    2. Negative tests: Invalid paths, disk errors, permission issues
    3. Edge cases: Empty paths, path traversal, non-existent files
    4. Size and type validation: Max size, unsupported file types
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import shutil
from datetime import datetime

from controllers.belge_controller import BelgeController


# ============================================================================
# Test Group 1: HAPPY PATH TESTS (Baseline)
# ============================================================================

class TestBelgeControllerHappyPath:
    """Test basic functionality with valid inputs."""

    def test_dosya_ekle_sil_var_mi(self):
        """
        Scenario: Add PDF file, verify existence, delete.
        Expected: All operations succeed.
        """
        bc = BelgeController()
        # Create temporary file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test PDF content')
        tmp.close()

        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, 1234, 'Gelir')
            assert ok is True
            assert path is not None
            assert bc.dosya_var_mi(path) is True

            # test dosya_adi_al
            adi = bc.dosya_adi_al(path)
            assert adi != ""
            assert "1234" in adi

            # test dosya_sil
            ok2, msg2 = bc.dosya_sil(path)
            assert ok2 is True
            assert bc.dosya_var_mi(path) is False
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

    def test_dosya_ekle_multiple_file_types(self):
        """
        Scenario: Add files of different allowed types (pdf, jpg, xlsx, txt, zip).
        Expected: All succeed with proper extension handling.
        """
        bc = BelgeController()
        file_types = ['.pdf', '.jpg', '.xlsx', '.txt', '.zip']
        added_files = []

        try:
            for ext in file_types:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                tmp.write(b'Test content')
                tmp.close()

                ok, msg, path = bc.dosya_ekle(tmp.name, 1001 + file_types.index(ext), 'Gider')
                assert ok is True, f"Failed to add {ext} file"
                assert path is not None
                assert ext in path
                added_files.append((path, tmp.name))
        finally:
            for path, tmp_name in added_files:
                if path and bc.dosya_var_mi(path):
                    bc.dosya_sil(path)
                if os.path.exists(tmp_name):
                    os.remove(tmp_name)

    def test_dosya_ekle_creates_type_directory(self):
        """
        Scenario: Add file with transaction type 'Transfer' (non-existent type directory).
        Expected: Directory created, file stored successfully.
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test PDF')
        tmp.close()

        try:
            # Use a fresh type directory
            unique_type = f"Transfer_{datetime.now().timestamp()}"
            ok, msg, path = bc.dosya_ekle(tmp.name, 9999, unique_type)
            assert ok is True
            
            # Verify directory was created
            type_dir = os.path.join(bc.BELGELER_KLASORU, unique_type)
            assert os.path.exists(type_dir)
            assert bc.dosya_var_mi(path) is True
            
            # Cleanup
            bc.dosya_sil(path)
            shutil.rmtree(type_dir, ignore_errors=True)
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 2: NEGATIVE TESTS — FILE NOT FOUND / INVALID PATHS
# ============================================================================

class TestDosyaEkleFileNotFound:
    """Test dosya_ekle() with non-existent source files."""

    def test_dosya_ekle_nonexistent_source_file_fails(self):
        """
        Scenario: Add file from path that doesn't exist.
        Expected: Returns (False, error_msg, None).
        """
        bc = BelgeController()
        nonexistent_path = "/nonexistent/path/to/file.pdf"
        
        ok, msg, path = bc.dosya_ekle(nonexistent_path, 1, 'Gelir')
        
        assert ok is False
        assert path is None
        assert "bulunamadı" in msg.lower() or "not found" in msg.lower()

    def test_dosya_ekle_empty_source_path_fails(self):
        """
        Scenario: Add file with empty source path.
        Expected: Fails gracefully.
        """
        bc = BelgeController()
        
        ok, msg, path = bc.dosya_ekle("", 1, 'Gelir')
        
        assert ok is False
        assert path is None


class TestDosyaSilNonexistent:
    """Test dosya_sil() with non-existent files."""

    def test_dosya_sil_nonexistent_file_returns_false(self):
        """
        Scenario: Delete file that doesn't exist.
        Expected: Returns (False, error_msg).
        """
        bc = BelgeController()
        nonexistent_path = "/nonexistent/file.pdf"
        
        ok, msg = bc.dosya_sil(nonexistent_path)
        
        assert ok is False
        assert "bulunamadı" in msg.lower() or "not found" in msg.lower()

    def test_dosya_sil_empty_path_fails(self):
        """
        Scenario: Delete with empty path.
        Expected: Returns (False, error_msg).
        """
        bc = BelgeController()
        
        ok, msg = bc.dosya_sil("")
        
        assert ok is False
        assert "belirtilmedi" in msg.lower() or "not specified" in msg.lower()

    def test_dosya_sil_none_path_fails(self):
        """
        Scenario: Delete with None path.
        Expected: Returns (False, error_msg).
        """
        bc = BelgeController()
        
        ok, msg = bc.dosya_sil(None)
        
        assert ok is False


# ============================================================================
# Test Group 3: FILE SIZE VALIDATION
# ============================================================================

class TestFileSizeValidation:
    """Test file size limits."""

    def test_dosya_ekle_file_too_large_fails(self):
        """
        Scenario: Add file larger than MAX_DOSYA_BOYUTU (50 MB).
        Expected: Fails with size error message.
        """
        bc = BelgeController()
        
        # Create a mock file that reports as too large
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'x')  # Small actual file
        tmp.close()

        try:
            # Mock os.path.getsize to return oversized value
            with patch('os.path.getsize', return_value=bc.MAX_DOSYA_BOYUTU + 1):
                ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            
            assert ok is False
            assert path is None
            assert "çok büyük" in msg.lower() or "too large" in msg.lower()
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

    def test_dosya_ekle_file_at_max_size_succeeds(self):
        """
        Scenario: Add file exactly at MAX_DOSYA_BOYUTU.
        Expected: Succeeds (at limit is allowed).
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'x')  # Small actual
        tmp.close()

        try:
            # Mock getsize to return exactly MAX_DOSYA_BOYUTU
            with patch('os.path.getsize', return_value=bc.MAX_DOSYA_BOYUTU):
                ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            
            assert ok is True
            assert path is not None
            
            # Cleanup
            if path and bc.dosya_var_mi(path):
                bc.dosya_sil(path)
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 4: FILE TYPE VALIDATION
# ============================================================================

class TestFileTypeValidation:
    """Test file type restrictions."""

    def test_dosya_ekle_unsupported_extension_fails(self):
        """
        Scenario: Add file with unsupported extension (.exe, .sh, .bat).
        Expected: Fails with type error message.
        """
        bc = BelgeController()
        invalid_types = ['.exe', '.sh', '.bat', '.com', '.ps1']

        for ext in invalid_types:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            tmp.write(b'content')
            tmp.close()

            try:
                ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
                
                assert ok is False, f"Should reject {ext} files"
                assert path is None
                assert "izin yok" in msg.lower() or "not allowed" in msg.lower()
            finally:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)

    def test_dosya_ekle_no_extension_fails(self):
        """
        Scenario: Add file without extension.
        Expected: Fails.
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='')
        tmp.write(b'content')
        tmp.close()

        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            
            assert ok is False
            assert path is None
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

    def test_dosya_ekle_case_insensitive_extension(self):
        """
        Scenario: Add file with uppercase extension (.PDF, .JPG).
        Expected: Succeeds (case-insensitive check).
        """
        bc = BelgeController()
        
        # Create file with uppercase extension
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.PDF')
        tmp.write(b'PDF content')
        tmp.close()

        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            
            assert ok is True, "Should accept uppercase extensions"
            assert path is not None
            
            # Cleanup
            if path and bc.dosya_var_mi(path):
                bc.dosya_sil(path)
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 5: DISK AND PERMISSION ERRORS
# ============================================================================

class TestDiskAndPermissionErrors:
    """Test error handling for disk I/O and permission issues."""

    def test_dosya_ekle_shutil_copy2_fails(self):
        """
        Scenario: shutil.copy2() raises exception (e.g., permission denied).
        Expected: Catches exception, returns (False, error_msg, None).
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        try:
            # Mock shutil.copy2 to raise PermissionError
            with patch('shutil.copy2', side_effect=PermissionError("Permission denied")):
                ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            
            assert ok is False
            assert path is None
            assert "hatası" in msg.lower() or "error" in msg.lower()
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

    def test_dosya_sil_permission_denied(self):
        """
        Scenario: os.remove() raises PermissionError (file is locked).
        Expected: Catches exception, returns (False, error_msg).
        """
        bc = BelgeController()
        
        # Create temporary file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            assert ok is True
            
            # Mock os.remove to raise PermissionError
            with patch('os.remove', side_effect=PermissionError("File is locked")):
                ok_del, msg_del = bc.dosya_sil(path)
            
            assert ok_del is False
            assert "hatası" in msg_del.lower() or "error" in msg_del.lower()
        finally:
            # Try to cleanup
            if os.path.exists(tmp.name):
                os.remove(tmp.name)
            if path and bc.dosya_var_mi(path):
                try:
                    bc.dosya_sil(path)
                except:
                    pass

    def test_dosya_ekle_handles_generic_exception(self):
        """
        Scenario: Any exception during dosya_ekle (not just PermissionError).
        Expected: Catches exception, returns (False, error_msg, None).
        Note: Testing exception handling wrapper (try-except in dosya_ekle).
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        try:
            # Mock shutil.copy2 to raise an unexpected error (e.g., FileSystemError)
            with patch('shutil.copy2', side_effect=OSError("Unexpected filesystem error")):
                ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            
            # Should catch the exception and return False
            assert ok is False
            assert path is None
            assert "hatası" in msg.lower() or "error" in msg.lower()
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 6: PATH TRAVERSAL AND SECURITY
# ============================================================================

class TestPathTraversalAndSecurity:
    """Test path traversal attempts and security edge cases."""

    def test_dosya_sil_with_path_traversal_attempt(self):
        """
        Scenario: Attempt to delete with path traversal (../../../etc/passwd).
        Expected: Fails or safely handled (no root file deletion).
        Note: On Windows/modern systems, abspath() should handle this safely.
        """
        bc = BelgeController()
        
        # Try path traversal
        traversal_path = "../../../../etc/passwd"
        ok, msg = bc.dosya_sil(traversal_path)
        
        # Should fail because file doesn't exist
        assert ok is False

    def test_dosya_ekle_destination_with_special_chars(self):
        """
        Scenario: Transaction type contains special characters (../../, ../foo).
        Expected: Path is stored, but note BelgeController doesn't actively sanitize type names.
        Note: This documents current behavior — path traversal in type can create dirs outside belgeler/.
               Security improvement: sanitize type parameter before path construction.
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        try:
            # Use special chars in type - will create unsafe path (documenting current behavior)
            special_type = "Gel../../../ir"
            ok, msg, path = bc.dosya_ekle(tmp.name, 1, special_type)
            
            # Current behavior: does NOT actively block this (path traversal possible)
            # TODO: Sanitize type parameter in BelgeController.dosya_ekle()
            if ok:
                # Path was created (possibly outside belgeler/)
                # Clean up if it exists
                if path and bc.dosya_var_mi(path):
                    bc.dosya_sil(path)
                # Also try to clean up the traversed directory
                try:
                    traversed = os.path.join(bc.BELGELER_KLASORU, special_type)
                    if os.path.exists(traversed) and os.path.isdir(traversed):
                        shutil.rmtree(traversed, ignore_errors=True)
                except:
                    pass
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 7: EMPTY AND NULL INPUTS
# ============================================================================

class TestEmptyAndNullInputs:
    """Test handling of empty and null inputs."""

    def test_dosya_var_mi_empty_path(self):
        """
        Scenario: Check if empty path exists.
        Expected: Returns False.
        """
        bc = BelgeController()
        
        result = bc.dosya_var_mi("")
        
        assert result is False

    def test_dosya_var_mi_none_path(self):
        """
        Scenario: Check if None path exists.
        Expected: Returns False.
        """
        bc = BelgeController()
        
        result = bc.dosya_var_mi(None)
        
        assert result is False

    def test_dosya_adi_al_empty_path(self):
        """
        Scenario: Get filename from empty path.
        Expected: Returns empty string.
        """
        bc = BelgeController()
        
        result = bc.dosya_adi_al("")
        
        assert result == ""

    def test_dosya_adi_al_none_path(self):
        """
        Scenario: Get filename from None path.
        Expected: Returns empty string.
        """
        bc = BelgeController()
        
        result = bc.dosya_adi_al(None)
        
        assert result == ""

    def test_dosya_ac_empty_path(self):
        """
        Scenario: Open file with empty path.
        Expected: Returns (False, error_msg).
        """
        bc = BelgeController()
        
        ok, msg = bc.dosya_ac("")
        
        assert ok is False
        assert "belirtilmedi" in msg.lower() or "not specified" in msg.lower()

    def test_dosya_ac_nonexistent_file(self):
        """
        Scenario: Open file that doesn't exist.
        Expected: Returns (False, error_msg).
        """
        bc = BelgeController()
        
        ok, msg = bc.dosya_ac("/nonexistent/file.pdf")
        
        assert ok is False
        assert "bulunamadı" in msg.lower() or "not found" in msg.lower()


# ============================================================================
# Test Group 8: FILENAME GENERATION AND STORAGE
# ============================================================================

class TestFilenameGenerationAndStorage:
    """Test proper filename generation and path storage."""

    def test_dosya_ekle_filename_includes_islem_id_and_timestamp(self):
        """
        Scenario: Add file and verify generated filename format.
        Expected: Filename contains islem_id and timestamp.
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        islem_id = 12345
        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, islem_id, 'Gelir')
            assert ok is True
            
            # Extract filename from path
            filename = os.path.basename(path)
            
            # Should start with islem_id
            assert filename.startswith(str(islem_id))
            
            # Should have timestamp pattern (YYYYMMDD_HHMMSS)
            # Example: 12345_20250101_120000.pdf
            parts = filename.split('_')
            assert len(parts) >= 3  # islem_id, date, time+ext
            
            # Cleanup
            if bc.dosya_var_mi(path):
                bc.dosya_sil(path)
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

    def test_dosya_ekle_returns_normalized_path(self):
        """
        Scenario: Verify returned path is normalized (forward slashes on all platforms).
        Expected: Path uses forward slashes, not backslashes.
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            assert ok is True
            
            # Path should not contain Windows-style backslashes
            assert '\\' not in path, f"Path should use forward slashes: {path}"
            
            # Cleanup
            if bc.dosya_var_mi(path):
                bc.dosya_sil(path)
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 9: FILE OPENING ACROSS PLATFORMS
# ============================================================================

class TestFileOpeningPlatforms:
    """Test file opening behavior on different platforms."""

    def test_dosya_ac_windows_uses_startfile(self):
        """
        Scenario: Open file on Windows.
        Expected: Uses os.startfile() (mocked).
        """
        bc = BelgeController()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.write(b'Test')
        tmp.close()

        try:
            ok, msg, path = bc.dosya_ekle(tmp.name, 1, 'Gelir')
            assert ok is True
            
            # Mock os.name for Windows
            with patch('os.name', 'nt'), \
                 patch('os.startfile') as mock_startfile:
                ok_ac, msg_ac = bc.dosya_ac(path)
            
            assert ok_ac is True
            # os.startfile should be called on Windows
            if sys.platform == 'win32':
                assert mock_startfile.called
            
            # Cleanup
            if bc.dosya_var_mi(path):
                bc.dosya_sil(path)
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)


# ============================================================================
# Test Group 10: CONCURRENT AND SEQUENTIAL OPERATIONS
# ============================================================================

class TestSequentialOperations:
    """Test multiple operations in sequence."""

    def test_add_delete_add_same_islem_id(self):
        """
        Scenario:
            1. Add file with islem_id=100
            2. Delete the file
            3. Add another file with same islem_id=100
        Expected: Both files created and deleted successfully (different timestamps).
        """
        bc = BelgeController()
        islem_id = 100
        paths = []

        try:
            # Add first file
            tmp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            tmp1.write(b'File 1')
            tmp1.close()
            
            ok1, msg1, path1 = bc.dosya_ekle(tmp1.name, islem_id, 'Gelir')
            assert ok1 is True
            paths.append((path1, tmp1.name))
            
            # Delete first file
            ok_del, msg_del = bc.dosya_sil(path1)
            assert ok_del is True
            
            # Add second file with same ID (but different timestamp)
            import time
            time.sleep(1.1)  # Ensure different timestamp
            
            tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            tmp2.write(b'File 2')
            tmp2.close()
            
            ok2, msg2, path2 = bc.dosya_ekle(tmp2.name, islem_id, 'Gelir')
            assert ok2 is True
            assert path2 != path1  # Different filenames due to timestamp
            paths.append((path2, tmp2.name))
        finally:
            for path, tmp_name in paths:
                if path and bc.dosya_var_mi(path):
                    bc.dosya_sil(path)
                if tmp_name and os.path.exists(tmp_name):
                    os.remove(tmp_name)
