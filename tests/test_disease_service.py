"""
tests/test_disease_service.py — Unit tests for DiseaseService

Validates that:
  1. All 50 disease classes are registered
  2. Class indices exactly match model/classes.json alphabetical ordering
  3. Critical healthy vs disease labels are correct
  4. All treatment lists are properly formed
  5. Lookup by index works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.services.disease_service import DiseaseService


class TestDiseaseServiceCount:
    def test_exactly_134_diseases(self):
        """All 134 pathology classes must be registered."""
        assert DiseaseService.get_class_count() == 134

    def test_indices_are_zero_to_133(self):
        """Indices must form a contiguous 0..133 range."""
        indices = [d.class_idx for d in DiseaseService.DISEASES]
        assert indices == list(range(134)), "Indices must be 0..133 in order"


class TestDiseaseServiceOrdering:
    """
    Verify the canonical ordering matching model/classes.json (134 classes across 11 crops).
    """

    @pytest.mark.parametrize("idx,expected_healthy", [
        (11,  True),   # Banana healthy
        (1,   False),  # Banana Black Sigatoka
        (22,  True),   # Corn healthy
        (16,  False),  # Corn Northern Leaf Blight
        (37,  True),   # Cotton healthy
        (24,  False),  # Cotton Bacterial blight
        (50,  True),   # Orange healthy
        (68,  True),   # Potato healthy
        (60,  False),  # Potato Late blight
        (79,  True),   # Rice healthy
        (90,  True),   # Soybean healthy
        (102, True),   # Sugarcane healthy
        (100, False),  # Sugarcane Red rot
        (112, True),   # Tomato healthy
        (105, False),  # Tomato Late blight
        (122, True),   # Turmeric healthy
        (133, True),   # Wheat healthy
    ])
    def test_healthy_disease_ordering(self, idx, expected_healthy):
        d = DiseaseService.get_by_index(idx)
        assert d is not None, f"No disease at index {idx}"
        assert d.is_healthy == expected_healthy, (
            f"Index {idx}: expected is_healthy={expected_healthy}, "
            f"got is_healthy={d.is_healthy} — name='{d.name}'"
        )

    def test_banana_indices_0_to_11(self):
        for idx in range(0, 12):
            d = DiseaseService.get_by_index(idx)
            assert d is not None
            assert d.crop == "Banana"
        assert DiseaseService.get_by_index(11).is_healthy is True

    def test_orange_at_50(self):
        d = DiseaseService.get_by_index(50)
        assert d is not None
        assert d.crop == "Orange"
        assert d.is_healthy is True

    def test_potato_healthy_and_late_blight(self):
        healthy     = DiseaseService.get_by_index(68)
        late_blight = DiseaseService.get_by_index(60)
        assert healthy.is_healthy is True,  "idx 68 must be Potato Healthy"
        assert late_blight.is_healthy is False, "idx 60 must be Potato Late Blight"
        assert "blight" in late_blight.name.lower()
        assert late_blight.severity == "Critical"

    def test_tomato_healthy_and_late_blight(self):
        healthy     = DiseaseService.get_by_index(112)
        late_blight = DiseaseService.get_by_index(105)
        assert healthy.is_healthy is True,  "idx 112 must be Tomato Healthy"
        assert late_blight.is_healthy is False, "idx 105 must be Tomato Late Blight"
        assert "blight" in late_blight.name.lower()
        assert late_blight.severity == "Critical"

    def test_wheat_indices_123_to_133(self):
        for idx in range(123, 134):
            d = DiseaseService.get_by_index(idx)
            assert d is not None
            assert d.crop == "Wheat"
        assert DiseaseService.get_by_index(133).is_healthy is True


class TestDiseaseServiceLookup:
    def test_get_by_index_valid(self):
        d = DiseaseService.get_by_index(0)
        assert d is not None
        assert d.class_idx == 0

    def test_get_by_index_invalid(self):
        d = DiseaseService.get_by_index(999)
        assert d is None

    def test_get_all_names_length(self):
        names = DiseaseService.get_all_names()
        assert len(names) == 134

    def test_all_healthy_classes_have_no_treatments(self):
        """Healthy classes should have empty treatment lists."""
        for d in DiseaseService.DISEASES:
            if d.is_healthy:
                assert d.chemical_treatment == [], f"{d.name} healthy but has chemical treatments"
                assert d.organic_treatment == [],  f"{d.name} healthy but has organic treatments"

    def test_critical_diseases_have_treatments(self):
        """Critical diseases must have at least 1 chemical and 1 organic treatment."""
        for d in DiseaseService.DISEASES:
            if d.severity == "Critical":
                assert len(d.chemical_treatment) > 0, f"{d.name} critical but no chemical treatment"
                assert len(d.organic_treatment) > 0,  f"{d.name} critical but no organic treatment"

    def test_healthy_class_severity_is_none(self):
        for d in DiseaseService.DISEASES:
            if d.is_healthy:
                assert d.severity == "None", f"{d.name} should have severity='None'"
