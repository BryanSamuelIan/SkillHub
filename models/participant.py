# ==================== PARTICIPANT MODEL ====================
from .baseModel import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class Participant(BaseModel):
    """
    Model untuk mengelola data peserta.
    """
    
    def create(self, nama: str, email: str, no_telp: str, alamat: str) -> bool:
        """
        Menambah peserta baru.
        
        Args:
            nama: Nama peserta
            email: Email peserta
            no_telp: Nomor telepon
            alamat: Alamat peserta
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        query = """
        INSERT INTO participants (nama, email, no_telp, alamat, tanggal_daftar)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (nama, email, no_telp, alamat, datetime.now())
        return self.db.execute_query(query, params)
    
    def get_all(self) -> List[Dict]:
        """
        Mengambil semua data peserta.
        
        Returns:
            List[Dict]: List peserta
        """
        query = "SELECT * FROM participants ORDER BY id ASC"
        return self.db.fetch_all(query)
    
    def get_by_id(self, participant_id: int) -> Optional[Dict]:
        """
        Mengambil data peserta berdasarkan ID.
        
        Args:
            participant_id: ID peserta
            
        Returns:
            Optional[Dict]: Data peserta atau None
        """
        query = "SELECT * FROM participants WHERE id = %s"
        return self.db.fetch_one(query, (participant_id,))
    
    def update(self, participant_id: int, nama: str, email: str, 
               no_telp: str, alamat: str) -> bool:
        """
        Mengubah data peserta.
        
        Args:
            participant_id: ID peserta
            nama: Nama peserta
            email: Email peserta
            no_telp: Nomor telepon
            alamat: Alamat peserta
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        query = """
        UPDATE participants 
        SET nama = %s, email = %s, no_telp = %s, alamat = %s
        WHERE id = %s
        """
        params = (nama, email, no_telp, alamat, participant_id)
        return self.db.execute_query(query, params)
    
    def delete(self, participant_id: int) -> bool:
        """
        Menghapus peserta dan relasinya dengan kelas.
        
        Args:
            participant_id: ID peserta
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        # Hapus relasi di tabel enrollments terlebih dahulu
        delete_enrollments = "DELETE FROM enrollments WHERE participant_id = %s"
        self.db.execute_query(delete_enrollments, (participant_id,))
        
        # Hapus peserta
        query = "DELETE FROM participants WHERE id = %s"
        return self.db.execute_query(query, (participant_id,))