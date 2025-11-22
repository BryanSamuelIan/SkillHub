# ==================== BASE MODEL CLASS ====================
from databaseConnection import DatabaseConnection

class BaseModel:
    """
    Base class untuk semua model.
    Menyediakan fungsi umum untuk akses database.
    """
    
    def __init__(self, db: DatabaseConnection):
        """
        Inisialisasi model dengan koneksi database.
        
        Args:
            db: Instance DatabaseConnection
        """
        self.db = db