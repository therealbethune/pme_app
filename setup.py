from setuptools import setup, find_packages

setup(
    name="pme_app",
    version="0.1.0",
    description="PME Calculator Core Libraries",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(include=["pme_app", "pme_app.*"]),
    python_requires=">=3.7",
    install_requires=["numpy", "pandas", "matplotlib", "numpy_financial", "scipy"],
    extras_require={
        "dev": ["black", "ruff", "pytest", "pytest-asyncio", "polars"]
    },
    entry_points={
        "console_scripts": [
            # Entry point for web application
            "pme-web = main:main",
        ],
    },
)
