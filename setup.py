from setuptools import find_packages, setup

setup(
    name="pme_app",
    version="0.1.0",
    description="PME Calculator Core Libraries",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(
        include=["pme_app", "pme_app.*", "pme_calculator", "pme_calculator.*"]
    ),
    python_requires=">=3.11",
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "numpy_financial",
        "scipy",
        "mplcursors",
        "ttkbootstrap",
        "fastapi>=0.111,<1.0",
    ],
    extras_require={
        "dev": [
            "black",
            "mypy==1.10.0",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "polars",
            "ruff",
            "uvicorn[standard]>=0.30",
        ]
    },
    entry_points={
        "console_scripts": [
            # Entry point for web application
            "pme-web = main:main",
        ],
    },
)
