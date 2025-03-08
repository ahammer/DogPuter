#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="dogputer",
    version="0.1.0",
    description="DogPuter - Interactive interface for dogs",
    author="DogPuter Team",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "pygame",
        "moviepy",
        "pyttsx3",
        "numpy",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-timeout",
        ],
    },
)
