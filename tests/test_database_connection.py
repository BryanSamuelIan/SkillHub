"""
Unit tests for DatabaseConnection class.
"""

import pytest
from unittest.mock import patch, MagicMock
from mysql.connector import Error
from databaseConnection import DatabaseConnection


class TestDatabaseConnectionInit:
    #Test DatabaseConnection initialization
    
    def test_init_with_valid_parameters(self):
        #Test initialization with valid parameters
        db = DatabaseConnection('localhost', 'root', 'password', 'test_db')
        
        assert db.host == 'localhost'
        assert db.user == 'root'
        assert db.password == 'password'
        assert db.database == 'test_db'
        assert db.connection is None
        assert db.cursor is None


class TestDatabaseConnectionConnect:
    #Test DatabaseConnection connect method
    
    def test_connect_success(self):
        #Test successful connection
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        
        with patch('mysql.connector.connect', return_value=mock_conn), \
             patch('streamlit.error'):
            db = DatabaseConnection('localhost', 'root', '', 'test_db')
            result = db.connect()
            
            assert result is True
            assert db.connection is not None
    
    def test_connect_failure(self):
        #Test connection failure
        with patch('mysql.connector.connect', side_effect=Error("Connection failed")), \
             patch('streamlit.error') as mock_error:
            db = DatabaseConnection('localhost', 'root', 'wrong_pass', 'test_db')
            result = db.connect()
            
            assert result is False


class TestDatabaseConnectionQueries:
    #Test DatabaseConnection query methods
    
    @pytest.fixture
    def connected_db(self):
        #fixture For Connected Database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        
        with patch('mysql.connector.connect', return_value=mock_conn):
            db = DatabaseConnection('localhost', 'root', '', 'test_db')
            db.connect()
            return db
    
    def test_execute_query_success(self, connected_db):
        #Test successful query execution
        query = "INSERT INTO test (name) VALUES (%s)"
        params = ("Test",)
        
        result = connected_db.execute_query(query, params)
        
        assert result is True
        connected_db.cursor.execute.assert_called_once_with(query, params)
        connected_db.connection.commit.assert_called_once()
    
    def test_execute_query_failure(self, connected_db):
        #Test failed query execution
        connected_db.cursor.execute.side_effect = Error("SQL Error")
        
        with patch('streamlit.error'):
            result = connected_db.execute_query("INVALID SQL")
            
            assert result is False
            connected_db.connection.rollback.assert_called_once()
    
    def test_fetch_all_success(self, connected_db):
        #Test successful fetch_all
        expected_data = [{'id': 1, 'name': 'Test'}]
        connected_db.cursor.fetchall.return_value = expected_data
        
        result = connected_db.fetch_all("SELECT * FROM test")
        
        assert result == expected_data
    
    def test_fetch_one_success(self, connected_db):
        #Test successful fetch_one
        expected_data = {'id': 1, 'name': 'Test'}
        connected_db.cursor.fetchone.return_value = expected_data
        
        result = connected_db.fetch_one("SELECT * FROM test WHERE id = %s", (1,))
        
        assert result == expected_data