"""
PME Calculator Backend Package
Professional Private Market Equivalent Calculator
"""

__version__ = "1.0.0"
__author__ = "PME Calculator Team"
__description__ = "Professional Private Market Equivalent Calculator Backend"

# Import main components - handling missing imports gracefully
try:
    from .math_engine import MathEngine
except ImportError:
    MathEngine = None

__all__ = [
    "__version__",
]

# Add available components to __all__
if MathEngine is not None:
    __all__.append("MathEngine")
