"""
Unit tests for Enrollment model.
"""

import pytest
from unittest.mock import MagicMock, patch
from models.enrollment import Enrollment


class TestEnrollmentCreate:
    #Test Enrollment create method
    
    @pytest.fixture
    def enrollment(self):
        #Fixture for Enrollment instance
        mock_db = MagicMock()
        return Enrollment(mock_db)
    
    def test_create_success(self, enrollment):
        #Test successful enrollment creation
        # Mock: enrollment doesn't exist yet
        enrollment.db.fetch_one.return_value = None
        enrollment.db.execute_query.return_value = True
        
        result = enrollment.create(participant_id=1, course_id=1)
        
        assert result is True
        enrollment.db.execute_query.assert_called_once()
    
    def test_create_duplicate(self, enrollment):
        #Test creating duplicate enrollment
        # Mock: enrollment already exists
        enrollment.db.fetch_one.return_value = {'id': 1}
        
        with patch('streamlit.warning'):
            result = enrollment.create(participant_id=1, course_id=1)
            
            assert result is False


class TestEnrollmentRelations:
    #Test Enrollment relation methods
    
    @pytest.fixture
    def enrollment(self):
        #Fixture for Enrollment instance
        mock_db = MagicMock()
        return Enrollment(mock_db)
    
    def test_get_courses_by_participant(self, enrollment):
        #Test get courses by participant
        expected_courses = [
            {'id': 1, 'nama_kelas': 'Python', 'instruktur': 'Prof. A'},
            {'id': 2, 'nama_kelas': 'Java', 'instruktur': 'Prof. B'}
        ]
        enrollment.db.fetch_all.return_value = expected_courses
        
        result = enrollment.get_courses_by_participant(1)
        
        assert result == expected_courses
        assert len(result) == 2
    
    def test_get_participants_by_course(self, enrollment):
        #Test get participants by course
        expected_participants = [
            {'id': 1, 'nama': 'John', 'email': 'john@test.com'},
            {'id': 2, 'nama': 'Jane', 'email': 'jane@test.com'}
        ]
        enrollment.db.fetch_all.return_value = expected_participants
        
        result = enrollment.get_participants_by_course(1)
        
        assert result == expected_participants
        assert len(result) == 2
    
    def test_get_all_enrollments(self, enrollment):
        #Test get all enrollments
        expected_enrollments = [
            {
                'id': 1,
                'participant_id': 1,
                'nama_peserta': 'John',
                'course_id': 1,
                'nama_kelas': 'Python'
            }
        ]
        enrollment.db.fetch_all.return_value = expected_enrollments
        
        result = enrollment.get_all_enrollments()
        
        assert result == expected_enrollments