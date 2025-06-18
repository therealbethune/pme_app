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
    python_requires=">=3.9",
    # Backend designed for 3.9-3.12, but allow 3.13 for local dev
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.22.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "scipy>=1.10.0",
        "numpy-financial>=1.0.0",
        "openpyxl>=3.1.0",
        "xlsxwriter>=3.0.0",
        "xlrd>=2.0.0",
        "plotly>=5.17.0",
        "kaleido>=0.2.1",
        "python-multipart>=0.0.6",
        "pydantic>=2.0.0",
        "psutil>=5.9.0",
        "requests>=2.28.0",
        "redis>=5.0.0",
        "reportlab>=4.0.8",
        "orjson>=3.8.0",
        "ujson>=5.7.0",
        "mplcursors",
        "ttkbootstrap",
        "structlog>=23.0.0",
        "polars>=0.20.0",
        "pyarrow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "black",
            "mypy==1.10.0",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "ruff",
            "tox>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            # Entry point for web application
            "pme-web = main:main",
        ],
    },
)
