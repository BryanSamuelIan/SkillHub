# ==================== ENROLLMENT MODEL ====================
from .baseModel import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

class Enrollment(BaseModel):
    """
    Model untuk mengelola pendaftaran peserta ke kelas.
    Mengimplementasikan relasi many-to-many antara peserta dan kelas.
    """
    
    def create(self, participant_id: int, course_id: int) -> bool:
        """
        Mendaftarkan peserta ke kelas.
        
        Args:
            participant_id: ID peserta
            course_id: ID kelas
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        # Cek apakah sudah terdaftar
        check_query = """
        SELECT * FROM enrollments 
        WHERE participant_id = %s AND course_id = %s
        """
        existing = self.db.fetch_one(check_query, (participant_id, course_id))
        
        if existing:
            st.warning("Peserta sudah terdaftar di kelas ini!")
            return False
        
        query = """
        INSERT INTO enrollments (participant_id, course_id, tanggal_daftar)
        VALUES (%s, %s, %s)
        """
        params = (participant_id, course_id, datetime.now())
        return self.db.execute_query(query, params)
    
    def get_courses_by_participant(self, participant_id: int) -> List[Dict]:
        """
        Mengambil daftar kelas yang diikuti peserta.
        
        Args:
            participant_id: ID peserta
            
        Returns:
            List[Dict]: List kelas yang diikuti
        """
        query = """
        SELECT c.*, e.tanggal_daftar
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.participant_id = %s
        ORDER BY e.tanggal_daftar DESC
        """
        return self.db.fetch_all(query, (participant_id,))
    
    def get_participants_by_course(self, course_id: int) -> List[Dict]:
        """
        Mengambil daftar peserta yang terdaftar di kelas.
        
        Args:
            course_id: ID kelas
            
        Returns:
            List[Dict]: List peserta yang terdaftar
        """
        query = """
        SELECT p.*, e.tanggal_daftar
        FROM participants p
        JOIN enrollments e ON p.id = e.participant_id
        WHERE e.course_id = %s
        ORDER BY e.tanggal_daftar DESC
        """
        return self.db.fetch_all(query, (course_id,))
    
    def delete(self, participant_id: int, course_id: int) -> bool:
        """
        Menghapus pendaftaran peserta dari kelas.
        
        Args:
            participant_id: ID peserta
            course_id: ID kelas
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        query = """
        DELETE FROM enrollments 
        WHERE participant_id = %s AND course_id = %s
        """
        return self.db.execute_query(query, (participant_id, course_id))
    
    def get_all_enrollments(self) -> List[Dict]:
        """
        Mengambil semua data pendaftaran dengan detail peserta dan kelas.
        
        Returns:
            List[Dict]: List semua pendaftaran
        """
        query = """
        SELECT 
            e.id,
            e.participant_id,
            p.nama as nama_peserta,
            e.course_id,
            c.nama_kelas,
            e.tanggal_daftar
        FROM enrollments e
        JOIN participants p ON e.participant_id = p.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.tanggal_daftar DESC
        """
        return self.db.fetch_all(query)