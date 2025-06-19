"""
Minimal smoke test to ensure coverage threshold is met.
Tests basic imports and functionality without complex dependencies.
"""

import pytest


def test_import_pme_calculator_backend() -> None:
    """Test that we can import the pme_calculator.backend package."""
    import pme_calculator.backend

    assert pme_calculator.backend is not None


def test_import_pme_math() -> None:
    """Test that we can import the pme_math package."""
    import pme_calculator.backend.pme_math

    assert pme_calculator.backend.pme_math is not None


def test_basic_math_engine_import() -> None:
    """Test that we can import basic math functionality."""
    from pme_calculator.backend.math_engine import MathEngine

    assert MathEngine is not None

    # Test basic functionality
    engine = MathEngine()
    tvpi = engine.calculate_tvpi(1000, 500, 600)
    assert isinstance(tvpi, float)
    assert tvpi == 1.1  # (500 + 600) / 1000


def test_pme_math_metrics() -> None:
    """Test PME math metrics module."""
    from pme_calculator.backend.pme_math.metrics import xirr_wrapper, direct_alpha

    assert xirr_wrapper is not None
    assert direct_alpha is not None

    # Test direct_alpha calculation
    alpha = direct_alpha(0.15, 0.10)
    assert isinstance(alpha, float)
    expected = (1 + 0.15) / (1 + 0.10) - 1
    assert abs(alpha - expected) < 0.001
