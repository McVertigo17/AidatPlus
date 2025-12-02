"""
Pagination ve Lazy Loading utilities
"""

from typing import List, TypeVar, Generic, Optional, Tuple, Any
from sqlalchemy.orm import Query, Session
from dataclasses import dataclass

T = TypeVar('T')  # Generic type variable


@dataclass
class PaginationResult:
    """Pagination sonuç modeli"""
    items: List
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @property
    def offset(self) -> int:
        """Başlangıç indeksi"""
        return (self.page - 1) * self.page_size


class PaginationHelper(Generic[T]):
    """Generic pagination helper"""
    
    @staticmethod
    def paginate(
        query: Any,  # Query[T] - Python 3.8 compat
        page: int = 1,
        page_size: int = 50
    ) -> PaginationResult:
        """
        Query'yi paginate et
        
        Args:
            query: SQLAlchemy Query nesnesi
            page: Sayfa numarası (1-indexed)
            page_size: Sayfa başına kayıt sayısı (default: 50)
        
        Returns:
            PaginationResult: Sayfalanmış sonuç
        
        Raises:
            ValueError: Geçersiz sayfa veya sayfa_size değeri
        """
        if page < 1:
            raise ValueError("Sayfa numarası 1'den başlamalıdır")
        if page_size < 1:
            raise ValueError("Sayfa boyutu 1'den büyük olmalıdır")
        
        # Toplam kayıt sayısı
        total_count = query.count()
        
        # Toplam sayfa sayısı
        total_pages = (total_count + page_size - 1) // page_size
        
        # Offset ve limit ile veriler al
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        return PaginationResult(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    
    @staticmethod
    def paginate_with_search(
        query: Any,  # Query[T]
        page: int = 1,
        page_size: int = 50,
        search_text: Optional[str] = None,
        search_columns: Optional[List] = None
    ) -> PaginationResult:
        """
        Arama filtresi ile paginate et
        
        Args:
            query: SQLAlchemy Query nesnesi
            page: Sayfa numarası (1-indexed)
            page_size: Sayfa başına kayıt sayısı
            search_text: Arama metni
            search_columns: Aranacak sütunlar
        
        Returns:
            PaginationResult: Sayfalanmış sonuç
        """
        # Arama filtresi uygulanır
        if search_text and search_columns:
            from sqlalchemy import or_
            
            conditions = []
            for col in search_columns:
                conditions.append(col.ilike(f"%{search_text}%"))
            
            if conditions:
                query = query.filter(or_(*conditions))
        
        return PaginationHelper.paginate(query, page, page_size)


class LazyLoadHelper:
    """Lazy loading helper - büyük veri setleri için"""
    
    @staticmethod
    def load_in_batches(
        query: Any,  # Query[T]
        batch_size: int = 100
    ) -> List[List]:
        """
        Query sonuçlarını batch halinde yükle
        
        Args:
            query: SQLAlchemy Query nesnesi
            batch_size: Batch boyutu
        
        Returns:
            Batch listesi
        """
        total = query.count()
        batches = []
        
        for offset in range(0, total, batch_size):
            batch = query.offset(offset).limit(batch_size).all()
            batches.append(batch)
        
        return batches
    
    @staticmethod
    def load_in_chunks(
        query: Any,  # Query[T]
        chunk_size: int = 50
    ):
        """
        Query sonuçlarını chunk olarak yield et (memory-efficient)
        
        Args:
            query: SQLAlchemy Query nesnesi
            chunk_size: Chunk boyutu
        
        Yields:
            T: Sonuç nesneleri
        """
        offset = 0
        while True:
            chunk = query.offset(offset).limit(chunk_size).all()
            if not chunk:
                break
            
            for item in chunk:
                yield item
            
            offset += chunk_size


class OptimizedQueryHelper:
    """Optimize edilmiş query helper'ları"""
    
    @staticmethod
    def get_page_stats(
        query: Any,  # Query[T]
        page_size: int = 50
    ) -> Tuple[int, int]:
        """
        Sayfa istatistiklerini al (hızlı)
        
        Args:
            query: SQLAlchemy Query nesnesi
            page_size: Sayfa boyutu
        
        Returns:
            (total_count, total_pages)
        """
        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size
        return total_count, total_pages
    
    @staticmethod
    def exists(query: Any) -> bool:  # Query[T]
        """
        Query'nin sonuç döndürüp döndürmediğini kontrol et
        
        Args:
            query: SQLAlchemy Query nesnesi
        
        Returns:
            bool: Sonuç var mı
        """
        from sqlalchemy import exists as sql_exists
        return query.session.query(sql_exists(query)).scalar()
