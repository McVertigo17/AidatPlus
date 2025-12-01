import os
from controllers.belge_controller import BelgeController
from datetime import datetime
import tempfile


def test_dosya_ekle_sil_var_mi(db_session):
    bc = BelgeController()
    # Create temporary file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(b'Test PDF content')
    tmp.close()

    try:
        ok, msg, path = bc.dosya_ekle(tmp.name, 1234, 'Gelir')
        assert ok
        assert path is not None
        assert bc.dosya_var_mi(path)

        # test dosya_adi_al
        assert bc.dosya_adi_al(path) != ""

        # test dosya_sil
        ok2, msg2 = bc.dosya_sil(path)
        assert ok2
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
