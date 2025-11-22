"""
Unit tests for Course model.
"""

import pytest
from unittest.mock import MagicMock
from models.course import Course
from datetime import datetime

class TestCourseCreate:
    #Test Course create method
    
    @pytest.fixture
    def course(self):
        #fixture For Connected Database
        mock_db = MagicMock()
        return Course(mock_db)

    def test_create_success(self, course):
        #Test successful course creation
        course.db.execute_query.return_value = True

        result = course.create(
            nama_kelas="Python Dasar",
            deskripsi="Belajar Python dari nol",
            instruktur="Budi"
        )

        assert result is True
        course.db.execute_query.assert_called_once()

        # Verify query and params
        query, params = course.db.execute_query.call_args[0]
        assert "INSERT INTO courses" in query
        assert params[0] == "Python Dasar"
        assert params[1] == "Belajar Python dari nol"
        assert params[2] == "Budi"
        assert isinstance(params[3], datetime)

    def test_create_failure(self, course):
        #Test failed course creation
        course.db.execute_query.return_value = False

        result = course.create("Kelas", "Desc", "Instruktur")
        
        assert result is False



class TestCourseRead:
    #Test Course read methods
    
    @pytest.fixture
    def course(self):
        #fixture For Connected Database
        mock_db = MagicMock()
        return Course(mock_db)

    def test_get_all_success(self, course):
        #Test successful get all courses
        expected = [
            {"id": 1, "nama_kelas": "Python", "instruktur": "Budi"},
            {"id": 2, "nama_kelas": "Java", "instruktur": "Siti"}
        ]
        course.db.fetch_all.return_value = expected

        result = course.get_all()

        assert result == expected
        assert len(result) == 2

    def test_get_all_empty(self, course):
        #Test get all courses when none exist
        course.db.fetch_all.return_value = []

        result = course.get_all()

        assert result == []
        assert len(result) == 0

    def test_get_by_id_found(self, course):
        #Test get course by ID when found
        expected = {"id": 1, "nama_kelas": "Python", "instruktur": "Budi"}
        course.db.fetch_one.return_value = expected

        result = course.get_by_id(1)

        assert result == expected
        assert result["id"] == 1

    def test_get_by_id_not_found(self, course):
        #Test get course by ID when not found
        course.db.fetch_one.return_value = None

        result = course.get_by_id(999)

        assert result is None


class TestCourseUpdate:
    #Test Course update method
    
    @pytest.fixture
    def course(self):
        #fixture For Connected Database
        mock_db = MagicMock()
        return Course(mock_db)

    def test_update_success(self, course):
        #Test successful course update
        course.db.execute_query.return_value = True

        result = course.update(
            course_id=5,
            nama_kelas="Updated",
            deskripsi="Updated Desc",
            instruktur="Updated Instruktur"
        )

        assert result is True

        query, params = course.db.execute_query.call_args[0]
        assert "UPDATE courses" in query
        assert params[0] == "Updated"
        assert params[1] == "Updated Desc"
        assert params[2] == "Updated Instruktur"
        assert params[3] == 5  # course_id


class TestCourseDelete:
    #Test Course delete method
    
    @pytest.fixture
    def course(self):
        #fixture For Connected Database
        mock_db = MagicMock()
        return Course(mock_db)

    def test_delete_success(self, course):
        #Test successful course deletion
        course.db.execute_query.return_value = True

        result = course.delete(10)

        assert result is True
        
        # Should call execute_query twice: delete enrollments + delete course
        assert course.db.execute_query.call_count == 2

        first_call_query, _ = course.db.execute_query.call_args_list[0][0]
        second_call_query, _ = course.db.execute_query.call_args_list[1][0]

        assert "DELETE FROM enrollments" in first_call_query
        assert "DELETE FROM courses" in second_call_query
