"""
Boş konut listesi hesaplama controller
JS dosyasındaki hesaplama mantığının Python uyarlaması
"""

from datetime import datetime, timedelta
from calendar import monthrange
from typing import List, Dict, Tuple
from controllers.base_controller import BaseController

# Logger import
from utils.logger import get_logger


class BosKonutController(BaseController):
    """Boş konut listesi hesaplamaları"""
    
    def __init__(self) -> None:
        super().__init__(None)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """Ay içindeki gün sayısını döndür"""
        return monthrange(year, month)[1]
    
    @staticmethod
    def get_month_start_end(year: int, month: int) -> Tuple[datetime, datetime]:
        """Ayın başlangıç ve bitiş tarihlerini döndür"""
        start = datetime(year, month, 1)
        days = BosKonutController.get_days_in_month(year, month)
        end = datetime(year, month, days)
        return start, end
    
    @staticmethod
    def calculate_empty_housing_costs(
        year: int,
        month: int,
        daire_listesi: List[Dict],
        blok_listesi: List[Dict],
        lojman_listesi: List[Dict],
        gider_kayitlari: List[Dict],
        sakin_listesi: List[Dict],
    ) -> Tuple[List[Dict], float]:
        """
        Boş konut maliyetlerini hesapla
        
        Args:
            year: Seçilen yıl
            month: Seçilen ay (1-12)
            daire_listesi: Daireler
            blok_listesi: Bloklar
            lojman_listesi: Lojmanlar
            gider_kayitlari: Giderler
            sakin_listesi: Sakinler
            
        Returns:
            (rapor kayıtları listesi, toplam maliyet)
        """
        logger = get_logger("BosKonutController.calculate_empty_housing_costs")
        
        days_in_month = BosKonutController.get_days_in_month(year, month)
        month_start, month_end = BosKonutController.get_month_start_end(year, month)
        
        logger.debug(f"Ay: {year}-{month}, Gün Sayısı: {days_in_month}")
        
        # Seçilen ay için giderleri filtrele
        month_giderler = []
        for gider in gider_kayitlari:
            if not gider.get('islem_tarihi'):
                continue
            try:
                gider_date = datetime.fromisoformat(str(gider['islem_tarihi']).split(' ')[0])
                if gider_date.year == year and gider_date.month == month:
                    month_giderler.append(gider)
            except (ValueError, AttributeError, IndexError):
                continue
        
        # Toplam aylık giderleri hesapla
        total_monthly_expenses = sum(g.get('tutar', 0) for g in month_giderler)
        total_housing_count = len(daire_listesi)
        
        # Konut başına günlük maliyet
        daily_cost_per_housing = (
            total_monthly_expenses / total_housing_count / days_in_month
            if total_housing_count > 0
            else 0
        )
        
        # Her daire için işle
        records = []
        record_index = 1
        
        # Debug: İlk daire için sakin bilgilerini log et
        if daire_listesi:
            first_daire = daire_listesi[0]
            first_daire_sakinleri = [
                s for s in sakin_listesi
                if s.get('daire_id') == first_daire.get('id') or s.get('bagliDaireId') == first_daire.get('id')
            ]
            if first_daire_sakinleri:
                logger.debug(f"İlk dairenin sakinleri:")
                for s in first_daire_sakinleri[:3]:
                    logger.debug(f"  - Giriş: {s.get('giris_tarihi')} (type: {type(s.get('giris_tarihi')).__name__}), Çıkış: {s.get('cikis_tarihi')} (type: {type(s.get('cikis_tarihi')).__name__})")
        
        for daire in daire_listesi:
            daire_id = daire.get('id')
            
            # Bu dairenin sakinlerini bul (daire_id)
            # raporlar_panel.py'de sakin_listesi'ndeki daire_id, eski_daire_id fallback'i içeriyor
            daire_sakinleri = [
                s for s in sakin_listesi
                if s.get('daire_id') == daire_id
            ]
            
            # Ayda her gün için işgal durumunu kontrol et
            occupied_days = [False] * days_in_month
            
            for sakin in daire_sakinleri:
                # Giriş tarihi: giris_tarihi (konut kullanan başlangıç tarihi)
                # NOT: tahsis_tarihi ≠ giris_tarihi (tahsis = tahsis, giriş = gerçek yerleşim)
                entry_date = None
                date_str = sakin.get('giris_tarihi')  # Sadece giris_tarihi kullan!
                if date_str:
                    try:
                        # datetime nesnesi olup olmadığını kontrol et
                        if isinstance(date_str, datetime):
                            entry_date = datetime(date_str.year, date_str.month, date_str.day)
                        else:
                            parsed = datetime.fromisoformat(str(date_str).split(' ')[0])
                            entry_date = datetime(parsed.year, parsed.month, parsed.day)
                    except (ValueError, AttributeError, IndexError) as e:
                        logger.debug(f"Giriş tarihi parse hatası: {e}, date_str: {date_str}")
                
                # Çıkış tarihi (sadece cikis_tarihi kontrol et)
                exit_date = None
                exit_date_str = sakin.get('cikis_tarihi')
                if exit_date_str:
                    try:
                        # datetime nesnesi olup olmadığını kontrol et
                        if isinstance(exit_date_str, datetime):
                            exit_date = datetime(exit_date_str.year, exit_date_str.month, exit_date_str.day)
                        else:
                            parsed = datetime.fromisoformat(str(exit_date_str).split(' ')[0])
                            exit_date = datetime(parsed.year, parsed.month, parsed.day)
                    except (ValueError, AttributeError, IndexError) as e:
                        logger.debug(f"Çıkış tarihi parse hatası: {e}, exit_date_str: {exit_date_str}")
                
                # Dönem sınırlarını belirle
                # Eğer giriş tarihi yoksa, bu sakin bu ayda hiç olmamış demektir
                if entry_date is None:
                    continue
                
                # Giriş tarihi seçili aydan sonraki ayda ise, bu ay için skip
                if entry_date.year > year or (entry_date.year == year and entry_date.month > month):
                    continue
                
                period_start = entry_date
                # Çıkış tarihi dahil olmalı (çıkış günü dahil işgal sayılır), o yüzden sonraki günü limit yap
                if exit_date:
                    # Çıkış gününün sonraki günü limit olsun (günü dahil et)
                    period_end = exit_date + timedelta(days=1)
                else:
                    period_end = datetime(2100, 12, 31)
                
                # İşgal günlerini işaretle (ay içinde)
                for day in range(1, days_in_month + 1):
                    current_date = datetime(year, month, day)
                    # Sakin bu gün dairede mi?
                    if period_start <= current_date < period_end:
                        occupied_days[day - 1] = True
            
            # Boş gün sayısını hesapla
            empty_days = sum(1 for day in occupied_days if not day)
            
            # Sakin yoksa tüm ay boş
            final_empty_days = days_in_month if len(daire_sakinleri) == 0 else empty_days
            
            # Debug
            occupied_list = [d+1 for d in range(days_in_month) if occupied_days[d]]
            empty_list = [d+1 for d in range(days_in_month) if not occupied_days[d]]
            logger.debug(f"Daire {daire.get('daire_no')}: Sakin={len(daire_sakinleri)}, İşgal={len(occupied_list)}, Boş={final_empty_days}")
            if len(daire_sakinleri) > 0:
                logger.debug(f"  İşgal günleri: {occupied_list}")
                logger.debug(f"  Boş günleri: {empty_list}")
            
            if final_empty_days > 0:
                # Daire, blok, lojman bilgisini bul
                blok = next(
                    (b for b in blok_listesi if b.get('id') == daire.get('bagliBlokId')),
                    None
                )
                lojman = (
                    next(
                        (l for l in lojman_listesi if l.get('id') == blok.get('bagliLojmanId')),
                        None
                    )
                    if blok
                    else None
                )
                
                lojman_adi = lojman.get('lojman_adi', 'Bilinmeyen Lojman') if lojman else 'Bilinmeyen Lojman'
                blok_adi = blok.get('blok_adi', 'Bilinmeyen Blok') if blok else 'Bilinmeyen Blok'
                daire_adi = f"{lojman_adi} - {blok_adi}"
                
                konut_aidat_bedeli = daily_cost_per_housing * final_empty_days
                
                # Boş dönemin başlangıç ve bitiş tarihlerini hesapla
                if len(daire_sakinleri) == 0:
                    # Dairede hiç sakin yok → Tüm ay boş
                    empty_period_start = month_start
                    # Ayın son günü
                    empty_period_end = datetime(year, month, days_in_month)
                else:
                    # Dairede sakin(ler) var → Boş günleri bul
                    first_empty_index = None
                    last_empty_index = None
                    consecutive_empty_start = None
                    consecutive_empty_end = None
                    
                    for day in range(days_in_month):
                        if not occupied_days[day]:
                            if first_empty_index is None:
                                first_empty_index = day  # İlk boş gün indeksi
                                consecutive_empty_start = day
                            consecutive_empty_end = day
                            last_empty_index = day
                        else:
                            # İşgal gün bulundu, ardışık boş dönem sonlanıyor
                            consecutive_empty_start = None
                            consecutive_empty_end = None
                    
                    # Hiç boş gün yoksa bu dairenin boş konut raporu yok
                    if first_empty_index is None:
                        continue
                    
                    # Boş dönem türü belirle
                    # Eğer boş günler ay başından başlamışsa: ay başlangıcını kullan
                    # Eğer boş günler ay sonunda bitmişse: ay sonunu kullan
                    # Aksi halde: boş günlerin gerçek başlangıcını ve bitişini kullan
                    
                    if first_empty_index == 0:
                        # Ay başından boş
                        empty_period_start = month_start
                    else:
                        # Orta bölgede başlayan boş gün
                        empty_period_start = datetime(year, month, first_empty_index + 1)
                    
                    if last_empty_index == days_in_month - 1:
                        # Ay sonuna kadar boş
                        empty_period_end = datetime(year, month, days_in_month)
                    else:
                        # Orta bölgede biten boş gün
                        empty_period_end = datetime(year, month, last_empty_index + 1)
                
                records.append({
                    'sira_no': record_index,
                    'daire_adi': daire_adi,
                    'daire_no': daire.get('daire_no'),
                    'alan': daire.get('kiraya_esasi_alan', 0),
                    'ilk_tarih': empty_period_start,
                    'son_tarih': empty_period_end,
                    'sorumlu_gun_sayisi': final_empty_days,
                    'konut_aidat_bedeli': konut_aidat_bedeli,
                })
                record_index += 1
        
        total_cost = sum(r.get('konut_aidat_bedeli', 0) for r in records)
        
        return records, total_cost
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Tutarı TL formatında döndür"""
        return f"₺{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def format_date(date_obj: datetime) -> str:
        """Tarihi dd.MM.yyyy formatında döndür"""
        return date_obj.strftime("%d.%m.%Y")
