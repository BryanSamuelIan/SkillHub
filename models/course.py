# ==================== Course MODEL ====================

from datetime import datetime
from .baseModel import BaseModel
from typing import List, Dict, Optional

class Course(BaseModel):
    """
    Model untuk mengelola data kelas.
    Mengimplementasikan operasi CRUD untuk tabel courses.
    """
    
    def create(self, nama_kelas: str, deskripsi: str, instruktur: str) -> bool:
        """
        Menambah kelas baru.
        
        Args:
            nama_kelas: Nama kelas
            deskripsi: Deskripsi kelas
            instruktur: Nama instruktur
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        query = """
        INSERT INTO courses (nama_kelas, deskripsi, instruktur, tanggal_dibuat)
        VALUES (%s, %s, %s, %s)
        """
        params = (nama_kelas, deskripsi, instruktur, datetime.now())
        return self.db.execute_query(query, params)
    
    def get_all(self) -> List[Dict]:
        """
        Mengambil semua data kelas.
        
        Returns:
            List[Dict]: List kelas
        """
        query = "SELECT * FROM courses ORDER BY id DESC"
        return self.db.fetch_all(query)
    
    def get_by_id(self, course_id: int) -> Optional[Dict]:
        """
        Mengambil data kelas berdasarkan ID.
        
        Args:
            course_id: ID kelas
            
        Returns:
            Optional[Dict]: Data kelas atau None
        """
        query = "SELECT * FROM courses WHERE id = %s"
        return self.db.fetch_one(query, (course_id,))
    
    def update(self, course_id: int, nama_kelas: str, 
               deskripsi: str, instruktur: str) -> bool:
        """
        Mengubah data kelas.
        
        Args:
            course_id: ID kelas
            nama_kelas: Nama kelas
            deskripsi: Deskripsi kelas
            instruktur: Nama instruktur
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        query = """
        UPDATE courses 
        SET nama_kelas = %s, deskripsi = %s, instruktur = %s
        WHERE id = %s
        """
        params = (nama_kelas, deskripsi, instruktur, course_id)
        return self.db.execute_query(query, params)
    
    def delete(self, course_id: int) -> bool:
        """
        Menghapus kelas dan relasinya dengan peserta.
        
        Args:
            course_id: ID kelas
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        # Hapus relasi di tabel enrollments terlebih dahulu
        delete_enrollments = "DELETE FROM enrollments WHERE course_id = %s"
        self.db.execute_query(delete_enrollments, (course_id,))
        
        # Hapus kelas
        query = "DELETE FROM courses WHERE id = %s"
        return self.db.execute_query(query, (course_id,))