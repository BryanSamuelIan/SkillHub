"""
Unit tests for Participant model.
"""

import pytest
from unittest.mock import MagicMock
from models.participant import Participant
from datetime import datetime


class TestParticipantCreate:
    #Test Participant create method
    
    @pytest.fixture
    def participant(self):
        #Fixture for Participant instance
        mock_db = MagicMock()
        return Participant(mock_db)
    
    def test_create_success(self, participant):
        #Test successful participant creation
        participant.db.execute_query.return_value = True
        
        result = participant.create(
            nama="John Doe",
            email="john@example.com",
            no_telp="081234567890",
            alamat="Test Address"
        )
        
        assert result is True
        participant.db.execute_query.assert_called_once()
        
        # Verify query structure
        call_args = participant.db.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "INSERT INTO participants" in query
        assert params[0] == "John Doe"
        assert params[1] == "john@example.com"
    
    def test_create_failure(self, participant):
        #Test failed participant creation
        participant.db.execute_query.return_value = False
        
        result = participant.create("John", "john@test.com", "", "")
        
        assert result is False
    
    def test_create_with_all_fields(self, participant):
        #Test creation with all fields filled
        participant.db.execute_query.return_value = True
        
        result = participant.create(
            nama="Complete Name",
            email="complete@example.com",
            no_telp="081234567890",
            alamat="Complete Address, Street 123"
        )
        
        assert result is True


class TestParticipantRead:
    #Test Participant read methods
    
    @pytest.fixture
    def participant(self):
        #Fixture for Participant instance
        mock_db = MagicMock()
        return Participant(mock_db)
    
    def test_get_all_success(self, participant):
        #Test get all participants
        expected_data = [
            {'id': 1, 'nama': 'John', 'email': 'john@test.com'},
            {'id': 2, 'nama': 'Jane', 'email': 'jane@test.com'}
        ]
        participant.db.fetch_all.return_value = expected_data
        
        result = participant.get_all()
        
        assert result == expected_data
        assert len(result) == 2
    
    def test_get_all_empty(self, participant):
        #Test get all when no participants exist
        participant.db.fetch_all.return_value = []
        
        result = participant.get_all()
        
        assert result == []
        assert len(result) == 0
    
    def test_get_by_id_found(self, participant):
        #Test get participant by ID when found
        expected_data = {'id': 1, 'nama': 'John', 'email': 'john@test.com'}
        participant.db.fetch_one.return_value = expected_data
        
        result = participant.get_by_id(1)
        
        assert result == expected_data
        assert result['id'] == 1
    
    def test_get_by_id_not_found(self, participant):
        #Test get participant by ID when not found
        participant.db.fetch_one.return_value = None
        
        result = participant.get_by_id(999)
        
        assert result is None


class TestParticipantUpdate:
    #Test Participant update method
    
    @pytest.fixture
    def participant(self):
        #Fixture for Participant instance
        mock_db = MagicMock()
        return Participant(mock_db)
    
    def test_update_success(self, participant):
        #Test successful participant update
        participant.db.execute_query.return_value = True
        
        result = participant.update(
            participant_id=1,
            nama="Updated Name",
            email="updated@example.com",
            no_telp="081234567891",
            alamat="Updated Address"
        )
        
        assert result is True
        
        # Verify query
        call_args = participant.db.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "UPDATE participants" in query
        assert params[0] == "Updated Name"
        assert params[4] == 1  # participant_id


class TestParticipantDelete:
    #Test Participant delete method
    
    @pytest.fixture
    def participant(self):
        #Fixture for Participant instance
        mock_db = MagicMock()
        return Participant(mock_db)
    
    def test_delete_success(self, participant):
        #Test successful participant deletion
        participant.db.execute_query.return_value = True
        
        result = participant.delete(1)
        
        assert result is True
        # Should call execute_query twice (enrollments + participant)
        assert participant.db.execute_query.call_count == 2