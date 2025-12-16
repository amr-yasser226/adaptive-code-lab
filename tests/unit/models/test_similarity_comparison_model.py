import pytest
from core.entities.similarity_comparison import SimilarityComparison


class TestSimilarityComparison:
    """Test suite for SimilarityComparison entity"""

    def test_init(self):
        """Test SimilarityComparison initialization"""
        comp = SimilarityComparison(
            similarity_id=1,
            compared_submission_id=10,
            match_score=0.85,
            note="High similarity",
            match_segments=[{"start": 0, "end": 100}]
        )

        assert comp.get_similarity_id() == 1
        assert comp.get_compared_submission_id() == 10
        assert comp.match_score == 0.85
        assert comp.note == "High similarity"
        assert len(comp.match_segments) == 1

    def test_get_similarity_id(self):
        """Test get_similarity_id getter"""
        comp = SimilarityComparison(
            similarity_id=42, compared_submission_id=1,
            match_score=0.5, note=None, match_segments=None
        )
        assert comp.get_similarity_id() == 42

    def test_get_compared_submission_id(self):
        """Test get_compared_submission_id getter"""
        comp = SimilarityComparison(
            similarity_id=1, compared_submission_id=99,
            match_score=0.5, note=None, match_segments=None
        )
        assert comp.get_compared_submission_id() == 99

    def test_get_match_details(self):
        """Test get_match_details returns complete info"""
        segments = [{"start": 10, "end": 50}]
        comp = SimilarityComparison(
            similarity_id=1, compared_submission_id=2,
            match_score=0.9, note="Match found",
            match_segments=segments
        )

        details = comp.get_match_details()

        assert details["similarity_id"] == 1
        assert details["compared_submission_id"] == 2
        assert details["match_score"] == 0.9
        assert details["note"] == "Match found"
        assert details["match_segments"] == segments

    def test_public_attributes(self):
        """Test public attributes are accessible"""
        comp = SimilarityComparison(
            similarity_id=1, compared_submission_id=2,
            match_score=0.75, note="Moderate match",
            match_segments=None
        )

        assert comp.match_score == 0.75
        assert comp.note == "Moderate match"
        assert comp.match_segments is None
