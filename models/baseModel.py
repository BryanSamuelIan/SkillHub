# ==================== BASE MODEL CLASS ====================
from databaseConnection import DatabaseConnection

class BaseModel:
    """
    Parent class untuk semua model.
    """
    
    def __init__(self, db: DatabaseConnection):
        """
        Inisialisasi model dengan koneksi database.
        
        Args:
            db: Instance DatabaseConnection
        """
        self.db = db 