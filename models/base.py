"""
Temel modeller
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class Lojman(Base):
    """Lojman ana modeli"""
    __tablename__ = "lojmanlar"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), nullable=False, unique=True)
    adres = Column(Text, nullable=False)
    aktif = Column(Boolean, default=True)

    # İlişkiler
    bloklar = relationship("Blok", back_populates="lojman", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def blok_sayisi(self) -> int:
        """Toplam blok sayısı"""
        return len([b for b in self.bloklar if b.aktif])

    @property
    def toplam_daire_sayisi(self) -> int:
        """Toplam daire sayısı"""
        return sum(len([d for d in blok.daireler if d.aktif]) for blok in self.bloklar if blok.aktif)

    @property
    def toplam_kiraya_esas_alan(self) -> float:
        """Toplam kiraya esas alan"""
        return sum(sum(d.kiraya_esas_alan or 0 for d in blok.daireler if d.aktif) for blok in self.bloklar if blok.aktif)

    @property
    def toplam_isitilan_alan(self) -> float:
        """Toplam ısıtılan alan"""
        return sum(sum(d.isitilan_alan or 0 for d in blok.daireler if d.aktif) for blok in self.bloklar if blok.aktif)

    def __repr__(self) -> str:
        return f"<Lojman {self.ad}>"


class Blok(Base):
    """Blok modeli"""
    __tablename__ = "bloklar"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(10), nullable=False)  # A, B, C vb.
    kat_sayisi = Column(Integer, nullable=False)
    giris_kapi_no = Column(String(20))
    notlar = Column(Text)
    aktif = Column(Boolean, default=True)

    # İlişkiler
    lojman_id = Column(Integer, ForeignKey("lojmanlar.id"), nullable=False)
    lojman = relationship("Lojman", back_populates="bloklar")
    daireler = relationship("Daire", back_populates="blok", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def daire_sayisi(self) -> int:
        """Bloktaki toplam daire sayısı"""
        return len([d for d in self.daireler if d.aktif])

    @property
    def toplam_kiraya_esas_alan(self) -> float:
        """Bloktaki toplam kiraya esas alan"""
        return sum(d.kiraya_esas_alan or 0 for d in self.daireler if d.aktif)

    @property
    def toplam_isitilan_alan(self) -> float:
        """Bloktaki toplam ısıtılan alan"""
        return sum(d.isitilan_alan or 0 for d in self.daireler if d.aktif)

    def __repr__(self) -> str:
        return f"<Blok {self.ad} ({self.lojman.ad})>"


class Daire(Base):
    """Daire modeli"""
    __tablename__ = "daireler"

    id = Column(Integer, primary_key=True, index=True)
    daire_no = Column(String(10), nullable=False)  # 101, 102, vb.
    oda_sayisi = Column(Integer, default=3)
    kat = Column(Integer, nullable=False)
    kiraya_esas_alan = Column(Float)  # m²
    isitilan_alan = Column(Float)  # m²
    tahsis_durumu = Column(String(50))  # Kurumsal, Şahsi, vb.
    isinma_tipi = Column(String(50))  # Doğalgaz, Elektrik, vb.
    guncel_aidat = Column(Float, default=0)  # ₺
    katki_payi = Column(Float, default=0)  # ₺
    aciklama = Column(Text)
    aktif = Column(Boolean, default=True)

    # İlişkiler
    blok_id = Column(Integer, ForeignKey("bloklar.id"), nullable=False)
    blok = relationship("Blok", back_populates="daireler")
    sakini = relationship("Sakin", back_populates="daire", uselist=False, foreign_keys="[Sakin.daire_id]")
    aidatlar = relationship("Aidat", back_populates="daire")
    aidat_islemleri = relationship("AidatIslem", back_populates="daire")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def kullanim_durumu(self) -> str:
        """Kullanım durumu (otomatik hesaplanır)"""
        return "Dolu" if self.sakini and self.sakini.aktif else "Boş"

    @property
    def tam_adres(self) -> str:
        """Tam adres bilgisi"""
        return f"{self.blok.lojman.ad} - {self.blok.ad} Blok - Daire {self.daire_no}"

    def __repr__(self) -> str:
        return f"<Daire {self.blok.ad}-{self.daire_no}>"


class Sakin(Base):
    """Sakin/Kiracı modeli"""
    __tablename__ = "sakinler"

    id = Column(Integer, primary_key=True, index=True)
    ad_soyad = Column(String(100), nullable=False)
    rutbe_unvan = Column(String(100))  # Rütbesi/Ünvanı
    telefon = Column(String(20))
    email = Column(String(100))
    aile_birey_sayisi = Column(Integer, default=1)
    tahsis_tarihi = Column(DateTime)  # Tahsis tarihi
    giris_tarihi = Column(DateTime, default=func.now())  # Yerleşim tarihi
    cikis_tarihi = Column(DateTime, nullable=True)  # Ayrılış tarihi (opsiyonel)
    notlar = Column(Text)  # Notlar

    # İlişkiler
    daire_id = Column(Integer, ForeignKey("daireler.id"), nullable=True)
    daire = relationship("Daire", back_populates="sakini", foreign_keys="[Sakin.daire_id]")
    eski_daire_id = Column(Integer, ForeignKey("daireler.id"), nullable=True)  # Geçmiş daire
    eski_daire = relationship("Daire", foreign_keys="[Sakin.eski_daire_id]")  # Geçmiş daire ilişkisi
    aidatlar = relationship("Aidat", back_populates="sakin")

    aktif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def tam_ad(self) -> str:
        """Ad ve soyadı döndür"""
        return self.ad_soyad if self.ad_soyad else "İsimsiz"

    @property
    def durum(self) -> str:
        """Sakin durumunu döndür"""
        if self.cikis_tarihi:
            return "Pasif"
        return "Aktif"

    def __repr__(self) -> str:
        return f"<Sakin {self.tam_ad}>"


class AidatIslem(Base):
    """Aidat işlemleri modeli (daire aidat bilgileri)"""
    __tablename__ = "aidat_islemleri"

    id = Column(Integer, primary_key=True, index=True)
    yil = Column(Integer, nullable=False)
    ay = Column(Integer, nullable=False)  # 1-12

    # Aidat detayları
    aidat_tutari = Column(Float, default=0.0)
    katki_payi = Column(Float, default=0.0)
    elektrik = Column(Float, default=0.0)
    su = Column(Float, default=0.0)
    isinma = Column(Float, default=0.0)
    ek_giderler = Column(Float, default=0.0)

    toplam_tutar = Column(Float, nullable=False)
    son_odeme_tarihi = Column(DateTime, nullable=False)
    aciklama = Column(Text)
    aktif = Column(Boolean, default=True)

    # İlişkiler
    daire_id = Column(Integer, ForeignKey("daireler.id"), nullable=False)
    daire = relationship("Daire", back_populates="aidat_islemleri")
    odemeler = relationship("AidatOdeme", back_populates="aidat_islem", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def ay_adi(self) -> str:
        """Ay numarasını Türkçe ay adına çevir"""
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        return aylar[self.ay - 1] if 1 <= self.ay <= 12 else "Bilinmiyor"

    def __repr__(self) -> str:
        return f"<AidatIslem {self.yil}-{self.ay} {self.daire.tam_adres if self.daire else 'Bilinmiyor'}>"


class AidatOdeme(Base):
    """Aidat ödemesi modeli"""
    __tablename__ = "aidat_odemeleri"

    id = Column(Integer, primary_key=True, index=True)
    tutar = Column(Float, nullable=False)
    odeme_tarihi = Column(DateTime, nullable=True)
    son_odeme_tarihi = Column(DateTime, nullable=False)
    odendi = Column(Boolean, default=False)
    aciklama = Column(Text)
    finans_islem_id = Column(Integer, ForeignKey("finans_islemleri.id"), nullable=True)  # İlişkili finans kaydı

    # İlişkiler
    aidat_islem_id = Column(Integer, ForeignKey("aidat_islemleri.id"), nullable=False)
    aidat_islem = relationship("AidatIslem", back_populates="odemeler")
    finans_islem = relationship("FinansIslem", foreign_keys=[finans_islem_id])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def durum(self) -> str:
        """Ödeme durumunu string olarak döndür"""
        return "Ödendi" if self.odendi else "Ödenmedi"

    def __repr__(self) -> str:
        return f"<AidatOdeme {self.tutar} {self.durum}>"


class Aidat(Base):
    """Aidat ödemesi modeli"""
    __tablename__ = "aidatlar"

    id = Column(Integer, primary_key=True, index=True)
    yil = Column(Integer, nullable=False)
    ay = Column(Integer, nullable=False)  # 1-12
    tutar = Column(Float, nullable=False)
    odendi = Column(Boolean, default=False)
    odeme_tarihi = Column(DateTime, nullable=True)
    son_odeme_tarihi = Column(DateTime, nullable=False)
    aciklama = Column(Text)

    # İlişkiler
    daire_id = Column(Integer, ForeignKey("daireler.id"))
    daire = relationship("Daire", back_populates="aidatlar")

    sakin_id = Column(Integer, ForeignKey("sakinler.id"))
    sakin = relationship("Sakin", back_populates="aidatlar")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def ay_adi(self) -> str:
        """Ay numarasını Türkçe ay adına çevir"""
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        return aylar[self.ay - 1] if 1 <= self.ay <= 12 else "Bilinmiyor"

    @property
    def durum(self) -> str:
        """Ödeme durumunu string olarak döndür"""
        return "Ödendi" if self.odendi else "Ödenmedi"

    def __repr__(self) -> str:
        return f"<Aidat {self.yil}-{self.ay} {self.daire.tam_adres if self.daire else 'Bilinmiyor'}>"


class Hesap(Base):
    """Finansal hesap modeli"""
    __tablename__ = "hesaplar"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), nullable=False)
    tur = Column(String(50), nullable=False)  # Banka Hesabı, Nakit, Kredi Kartı, vb.
    bakiye_kurus = Column(Integer, default=0)  # kuruş cinsinden
    varsayilan = Column(Boolean, default=False)
    aktif = Column(Boolean, default=True)
    aciklama = Column(Text)
    # Para birimi alanı eklendi
    para_birimi = Column(String(10), default="₺", nullable=False)  # ₺, $, €

    # İlişkiler
    finans_islemleri = relationship("FinansIslem", back_populates="hesap", foreign_keys="[FinansIslem.hesap_id]")
    hedef_finans_islemleri = relationship("FinansIslem", back_populates="hedef_hesap", foreign_keys="[FinansIslem.hedef_hesap_id]")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def bakiye(self) -> float:
        """Bakiye (TL cinsinden) - backward compatibility"""
        return float(self.bakiye_kurus / 100.0)

    @bakiye.setter
    def bakiye(self, value: float) -> None:
        """Bakiye set (TL cinsinden) - backward compatibility"""
        self.bakiye_kurus = int(round(value * 100))

    @property
    def durum(self) -> str:
        """Hesap durumunu döndür"""
        return "Aktif" if self.aktif else "Pasif"

    def __repr__(self) -> str:
        return f"<Hesap {self.ad} ({self.tur})>"


class Kategori(Base):
    """Gelir/gider kategori modeli"""
    __tablename__ = "kategoriler"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), nullable=False)
    ana_kategori = Column(String(100), nullable=False)  # Gelir, Gider
    alt_kategori = Column(String(100))  # Alt kategoriler
    aktif = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Kategori {self.ana_kategori} - {self.ad}>"


class FinansIslem(Base):
    """Finans işlemleri modeli"""
    __tablename__ = "finans_islemleri"

    id = Column(Integer, primary_key=True, index=True)
    tarih = Column(DateTime, nullable=False, default=func.now())
    tur = Column(String(20), nullable=False)  # Gelir, Gider
    tutar_kurus = Column(Integer, nullable=False)  # kuruş cinsinden
    aciklama = Column(Text)
    aktif = Column(Boolean, default=True)

    # Belge alanları
    belge_yolu = Column(String(500), nullable=True)  # Belge dosya yolu
    belge_turu = Column(String(50), nullable=True)  # pdf, image, doc, vb.

    # İlişkiler
    hesap_id = Column(Integer, ForeignKey("hesaplar.id"))
    hesap = relationship("Hesap", back_populates="finans_islemleri", foreign_keys=[hesap_id])

    hedef_hesap_id = Column(Integer, ForeignKey("hesaplar.id"), nullable=True)  # Transfer için hedef hesap
    hedef_hesap = relationship("Hesap", back_populates="hedef_finans_islemleri", foreign_keys=[hedef_hesap_id])

    kategori_id = Column(Integer, ForeignKey("alt_kategoriler.id"), nullable=True)
    kategori = relationship("AltKategori", back_populates="finans_islemleri")
    ana_kategori_text = Column(String(100))  # Ana kategori adı (kategori seçilmediğinde)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def tutar(self) -> float:
        """Tutar (TL cinsinden) - backward compatibility"""
        return float(self.tutar_kurus / 100.0)

    @tutar.setter
    def tutar(self, value: float) -> None:
        """Tutar set (TL cinsinden) - backward compatibility"""
        self.tutar_kurus = int(round(value * 100))

    @property
    def islem_turu(self) -> str:
        """İşlem türünü döndür"""
        return "Gelir" if self.tur == "Gelir" else "Gider"

    def __repr__(self) -> str:
        return f"<FinansIslem {self.tur} {self.tutar}>"

# Eski Finans modelini kaldırıp yeni modele yönlendirelim
class Finans(Base):
    """Eski finans hareketleri modeli - geriye uyumluluk için"""
    __tablename__ = "finans"

    id = Column(Integer, primary_key=True, index=True)
    tarih = Column(DateTime, nullable=False, default=func.now())
    tur = Column(String(20), nullable=False)  # Gelir, Gider
    kategori = Column(String(50), nullable=False)  # Aidat Geliri, Bakım Onarım, vb.
    aciklama = Column(Text)
    tutar = Column(Float, nullable=False)
    odeme_yontemi = Column(String(30))  # Nakit, Havale, Kredi Kartı, vb.

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Finans {self.tur} {self.kategori} {self.tutar}>"


class Ayar(Base):
    """Uygulama ayarları modeli"""
    __tablename__ = "ayarlar"

    id = Column(Integer, primary_key=True, index=True)
    anahtar = Column(String(100), unique=True, nullable=False)
    deger = Column(Text)
    aciklama = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Ayar {self.anahtar}={self.deger}>"


class AnaKategori(Base):
    """Ana kategori modeli"""
    __tablename__ = "ana_kategoriler"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    aciklama = Column(Text)  # Optional description
    tip = Column(String(20), nullable=False, default="gelir")  # gelir veya gider

    # İlişkiler
    alt_kategoriler = relationship("AltKategori", back_populates="ana_kategori", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<AnaKategori {self.name} ({self.tip})>"


class AltKategori(Base):
    """Alt kategori modeli"""
    __tablename__ = "alt_kategoriler"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("ana_kategoriler.id"))
    name = Column(String(100), unique=True, nullable=False)
    aciklama = Column(Text)  # Optional description
    aktif = Column(Boolean, default=True)

    # İlişkiler
    ana_kategori = relationship("AnaKategori", back_populates="alt_kategoriler")
    finans_islemleri = relationship("FinansIslem", back_populates="kategori")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<AltKategori {self.name}>"

