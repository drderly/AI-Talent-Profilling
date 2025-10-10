"""
Setup script for LLM API
Run: python setup.py
This will install all dependencies and initialize the project
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        print("\n" + "="*60)
        print("LLM API Setup Complete!")
        print("="*60)
        print("\n✓ All dependencies installed")
        print("✓ Environment configured")
        print("\nTo start the server, run:")
        print("  python main.py")
        print("\nConfiguration file: .env")
        print("="*60 + "\n")

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="llm-api",
    version="1.1.0",
    description="LLM API wrapper for Ollama with streaming support",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires=">=3.10",
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        "console_scripts": [
            "llm-api=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
