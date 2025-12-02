"""
Veritabanı query optimizasyonu utilities
"""

from typing import List, Optional, Type, TypeVar, Any, Dict, Tuple
from sqlalchemy.orm import Query, Session, joinedload, selectinload
from sqlalchemy import inspect, func
from datetime import datetime

T = TypeVar('T')  # Generic type variable


class QueryOptimizer:
    """Query performans optimizasyonu helper'ları"""
    
    @staticmethod
    def eager_load_relationships(
        query: Any,  # Query[T]
        relationships: List[str]
    ) -> Any:  # Query[T]
        """
        N+1 problem'ini çözmek için eager loading uygula
        
        Args:
            query: SQLAlchemy Query nesnesi
            relationships: Yüklenecek relationship adları
        
        Returns:
            Optimize edilmiş query
        
        Example:
            >>> query = session.query(Sakin)
            >>> optimized = QueryOptimizer.eager_load_relationships(
            ...     query, ['daire', 'aidatlar']
            ... )
        """
        for rel in relationships:
            query = query.options(selectinload(getattr(query.column_descriptions[0]['entity'], rel)))
        
        return query
    
    @staticmethod
    def select_specific_columns(
        query: Any,  # Query[T]
        model: Type,  # Type[T]
        columns: List[str]
    ) -> Any:  # Query
        """
        Sadece gerekli sütunları seç (veri transferi azalt)
        
        Args:
            query: SQLAlchemy Query nesnesi
            model: Model sınıfı
            columns: Seçilecek sütun adları
        
        Returns:
            Optimize edilmiş query
        
        Example:
            >>> query = session.query(Sakin)
            >>> optimized = QueryOptimizer.select_specific_columns(
            ...     query, Sakin, ['id', 'ad_soyad', 'telefon']
            ... )
        """
        column_objs = [getattr(model, col) for col in columns if hasattr(model, col)]
        
        if column_objs:
            return query.with_entities(*column_objs)
        
        return query
    
    @staticmethod
    def apply_indexes_hint(
        query: Any,  # Query[T]
        index_name: str
    ) -> Any:  # Query[T]
        """
        Query'ye index kullanma hint'i ekle (database tarafından uygulanması önerilir)
        
        Args:
            query: SQLAlchemy Query nesnesi
            index_name: Index adı
        
        Returns:
            Hint'li query (Bazı database'ler desteklemez)
        """
        # Not: SQLite bu hint'i desteklemez, ama dokümantasyon için bırakıyoruz
        # Diğer database'ler (PostgreSQL, MySQL) için kullanılabilir
        return query
    
    @staticmethod
    def count_optimized(query: Any) -> int:  # Query[T]
        """
        Optimized count query (SELECT COUNT(*))
        
        Args:
            query: SQLAlchemy Query nesnesi
        
        Returns:
            Toplam kayıt sayısı
        """
        # N+1 problem'i olmadan count et
        return query.with_entities(func.count()).scalar()
    
    @staticmethod
    def exists_optimized(query: Any) -> bool:  # Query[T]
        """
        Optimized existence check (LIMIT 1)
        
        Args:
            query: SQLAlchemy Query nesnesi
        
        Returns:
            Kayıt var mı
        """
        # Tek satır kontrolü yap
        return query.limit(1).first() is not None


class QueryAnalyzer:
    """Query performans analiz araçları"""
    
    @staticmethod
    def get_query_stats(
        query: Any,  # Query[T]
        label: str = "Query"
    ) -> Dict[str, Any]:
        """
        Query istatistiklerini al
        
        Args:
            query: SQLAlchemy Query nesnesi
            label: Query etiketi
        
        Returns:
            İstatistik dictionary'si
        """
        import time
        
        start = time.time()
        count = query.count()
        duration = time.time() - start
        
        return {
            "label": label,
            "count": count,
            "duration_ms": duration * 1000,
            "statement": str(query),
        }
    
    @staticmethod
    def print_query(query: Any) -> str:  # Query[T]
        """
        Generate edilen SQL sorgusunu yazdır (debugging için)
        
        Args:
            query: SQLAlchemy Query nesnesi
        
        Returns:
            SQL sorgusunun string'i
        """
        return str(query)


class PerformanceHelper:
    """Performans iyileştirme helper'ları"""
    
    @staticmethod
    def bulk_insert(
        session: Session,
        model: Type,  # Type[T]
        data_list: List[Dict]
    ) -> int:
        """
        Toplu insert işlemi (daha hızlı)
        
        Args:
            session: Database session
            model: Model sınıfı
            data_list: Veri listesi
        
        Returns:
            Eklenen kayıt sayısı
        
        Example:
            >>> data = [
            ...     {"ad_soyad": "Ali", "telefon": "123456"},
            ...     {"ad_soyad": "Veli", "telefon": "654321"},
            ... ]
            >>> count = PerformanceHelper.bulk_insert(session, Sakin, data)
        """
        try:
            objects = [model(**item) for item in data_list]
            session.add_all(objects)
            session.commit()
            return len(objects)
        except Exception as e:
            session.rollback()
            raise Exception(f"Toplu insert başarısız: {str(e)}")
    
    @staticmethod
    def bulk_update(
        session: Session,
        model: Type,  # Type[T]
        updates: List[Tuple[int, Dict]]
    ) -> int:
        """
        Toplu update işlemi
        
        Args:
            session: Database session
            model: Model sınıfı
            updates: [(id, update_dict), ...] listesi
        
        Returns:
            Güncellenen kayıt sayısı
        
        Example:
            >>> updates = [
            ...     (1, {"ad_soyad": "Ali Yıldız"}),
            ...     (2, {"ad_soyad": "Veli Kaya"}),
            ... ]
            >>> count = PerformanceHelper.bulk_update(session, Sakin, updates)
        """
        try:
            updated = 0
            for obj_id, data in updates:
                session.query(model).filter(model.id == obj_id).update(data)
                updated += 1
            
            session.commit()
            return updated
        except Exception as e:
            session.rollback()
            raise Exception(f"Toplu update başarısız: {str(e)}")
    
    @staticmethod
    def batch_delete(
        session: Session,
        query: Any,  # Query[T]
        batch_size: int = 1000
    ) -> int:
        """
        Toplu delete işlemi (memory-efficient)
        
        Args:
            session: Database session
            query: Silinecek query
            batch_size: Batch boyutu
        
        Returns:
            Silinen kayıt sayısı
        """
        try:
            total_deleted = 0
            
            while True:
                # Batch olarak sil
                batch = query.limit(batch_size).all()
                if not batch:
                    break
                
                for item in batch:
                    session.delete(item)
                
                session.commit()
                total_deleted += len(batch)
            
            return total_deleted
        except Exception as e:
            session.rollback()
            raise Exception(f"Toplu delete başarısız: {str(e)}")


class CacheHelper:
    """Basit query result caching"""
    
    _cache: Dict[str, Any] = {}
    _cache_expiry: Dict[str, datetime] = {}
    
    @staticmethod
    def get_cached(
        key: str,
        query_fn,
        ttl_seconds: int = 300
    ) -> Any:
        """
        Cache'ten veri al veya query çalıştır
        
        Args:
            key: Cache anahtarı
            query_fn: Query fonksiyonu
            ttl_seconds: Cache validity süresi
        
        Returns:
            Cached veya yeni query sonucu
        """
        now = datetime.now()
        
        # Cache'te varsa ve hala geçerliyse döndür
        if key in CacheHelper._cache:
            expiry = CacheHelper._cache_expiry.get(key)
            if expiry and now < expiry:
                return CacheHelper._cache[key]
        
        # Yeni query çalıştır
        result = query_fn()
        
        # Cache'e kaydet
        CacheHelper._cache[key] = result
        CacheHelper._cache_expiry[key] = now + \
            type('obj', (object,), {'__lt__': lambda self, other: False,
                                     '__gt__': lambda self, other: True})()
        
        return result
    
    @staticmethod
    def clear_cache(key: Optional[str] = None) -> None:
        """
        Cache'i temizle
        
        Args:
            key: Temizlenecek cache anahtarı (None = tümü)
        """
        if key:
            CacheHelper._cache.pop(key, None)
            CacheHelper._cache_expiry.pop(key, None)
        else:
            CacheHelper._cache.clear()
            CacheHelper._cache_expiry.clear()
