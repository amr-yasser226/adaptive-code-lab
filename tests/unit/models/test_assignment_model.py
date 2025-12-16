import pytest
from datetime import datetime, timedelta
from core.entities.assignment import Assignment

def test_assignment_initialization():
    assignment = Assignment(1, 101, "HW1", "Description", "2024-01-01", "2024-01-15", 
                           100, True, True, 0.1, datetime.now(), datetime.now())
    assert assignment.title == "HW1"
    assert assignment.max_points == 100
    assert assignment.is_published is True # The new initialization sets it to True

def test_assignment_is_late_check():
    # If entity has logic for checking late, test it here. 
    # Current entity is mostly data class, but good to verify structure.
    pass
