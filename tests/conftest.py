import os
import sys
import pytest

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def hardware_manager():
    """Fixture to provide a HardwareManager instance."""
    from src.core.hardware_manager import HardwareManager
    return HardwareManager()

@pytest.fixture
def network_manager():
    """Fixture to provide a Network instance."""
    from src.core.network import Network
    return Network()
