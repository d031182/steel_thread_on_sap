"""
Minimal setup.py for pytest import compatibility
Makes project modules importable without manual PYTHONPATH manipulation
"""
from setuptools import setup, find_packages

setup(
    name="steel-thread-on-sap",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies already in app/requirements.txt
        # This setup.py is ONLY for pytest import resolution
    ],
)