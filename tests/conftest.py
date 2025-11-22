import pytest
import os
import mysql.connector


@pytest.fixture
def clean_test_db():
    """
    Clean tables BEFORE & AFTER each test.
    Provides DatabaseConnection instance.
    """
    db = DatabaseConnection(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "skillhub_test")
    )

    db.connect()

    # cleanup before test
    for table in ["enrollments", "participants", "courses"]:
        try:
            db.execute_query(f"DELETE FROM {table}")
        except Exception:
            pass

    yield db

    # cleanup after test
    for table in ["enrollments", "participants", "courses"]:
        try:
            db.execute_query(f"DELETE FROM {table}")
        except Exception:
            pass

    db.disconnect()
