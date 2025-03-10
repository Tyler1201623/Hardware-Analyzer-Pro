import os
import sys
import subprocess
from pathlib import Path

def create_venv_config():
    """Create pyvenv.cfg file with proper configuration."""
    python_path = sys.executable
    python_home = os.path.dirname(python_path)
    
    config_content = f"""home = {python_home}
implementation = CPython
version_info = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
virtualenv = 20.24.5
include-system-site-packages = true
base-prefix = {python_home}
base-exec-prefix = {python_home}
base-executable = {python_path}
"""
    
    with open("pyvenv.cfg", "w") as f:
        f.write(config_content)
    print("✓ Created pyvenv.cfg")

def setup_environment():
    """Setup the environment."""
    try:
        # Create pyvenv.cfg first
        create_venv_config()
        
        # Create necessary directories
        dirs = ['logs', 'src/logs', 'src/core/logs', 'reports', 'results']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        print("✓ Directory structure created")
        
        # Install dependencies with improved error handling
        try:
            # First upgrade pip
            subprocess.check_call([
                sys.executable, "-m", "pip", 
                "install", "--upgrade", "pip"
            ])
            
            # Then install setuptools first
            subprocess.check_call([
                sys.executable, "-m", "pip", 
                "install", "--upgrade", "setuptools>=61.0.0"
            ])
            
            # Finally install other requirements
            subprocess.check_call([
                sys.executable, "-m", "pip", 
                "install", "-r", "requirements.txt"
            ])
            print("✓ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            raise
            
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment()

from setuptools import setup, find_packages
import os

def read_requirements():
    """Read the requirements.txt file."""
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="hardware_analyzer",
    version="1.0.0",
    description="Professional hardware monitoring and analysis tool",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'hardware-analyzer=src.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Monitoring",
    ],
    python_requires='>=3.8',
)
