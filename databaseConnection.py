# ==================== DATABASE CONNECTION CLASS ====================

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
import streamlit as st
from datetime import datetime


class DatabaseConnection:
    """
    Kelas untuk mengelola koneksi database MySQL.
    Mengimplementasikan context manager untuk koneksi yang aman.
    """
    
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Inisialisasi parameter koneksi database.
        
        Args:
            host: Host database MySQL
            user: Username database
            password: Password database
            database: Nama database
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Membuat koneksi ke database MySQL.
        
        Returns:
            bool: True jika koneksi berhasil, False jika gagal
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return True
        except Error as e:
            st.error(f"Error koneksi database: {e}")
            return False
    
    def disconnect(self):
        """Menutup koneksi database."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Menjalankan query INSERT, UPDATE, DELETE.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (optional)
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Error as e:
            st.error(f"Error menjalankan query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Mengambil semua hasil query SELECT.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (optional)
            
        Returns:
            List[Dict]: List of dictionary hasil query
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            st.error(f"Error fetch data: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Mengambil satu hasil query SELECT.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (optional)
            
        Returns:
            Optional[Dict]: Dictionary hasil query atau None
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Error as e:
            st.error(f"Error fetch data: {e}")
            return None