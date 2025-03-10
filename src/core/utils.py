import os
import sys
import json
import logging
import csv
from datetime import datetime


def setup_logging():
    """Setup application logging with UTF-8 encoding."""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Configure logging with UTF-8 encoding
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler("logs/hardware_analyzer.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup complete.")


def format_size(size_bytes):
    """Format byte sizes in a human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def format_percentage(value):
    """Format percentage with consistent styling."""
    return f"{value:.1f}%"


def get_status_emoji(value):
    """Get status emoji based on value."""
    if value < 60:
        return "🟢"  # Green circle for good
    elif value < 80:
        return "🟡"  # Yellow circle for warning
    else:
        return "🔴"  # Red circle for critical


def save_to_json(file_path, data):
    """Save data to a JSON file."""
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        logging.info(f"Data successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data to JSON file: {e}")
        raise


def save_to_csv(file_path, data, fieldnames=None):
    """Save data to a CSV file."""
    try:
        with open(file_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames or data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Data successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data to CSV file: {e}")
        raise


def generate_timestamped_filename(base_name, extension):
    """Generate a filename with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


def validate_writable_path(file_path):
    """Validate if the file path is writable."""
    try:
        with open(file_path, "w") as file:
            pass
        logging.info(f"Path is writable: {file_path}")
    except Exception as e:
        logging.error(f"Path is not writable: {file_path} - {e}")
        raise


# Load data from a JSON file
def load_from_json(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        logging.info(f"Data successfully loaded from {file_path}")
        return data
    except Exception as e:
        logging.error(f"Error loading data from JSON file: {e}")
        raise


# Check disk space for a given path
def check_disk_space(path="."):
    """Check the available disk space for a given path."""
    try:
        statvfs = os.statvfs(path)
        total = statvfs.f_blocks * statvfs.f_frsize
        available = statvfs.f_bavail * statvfs.f_frsize
        logging.info(f"Disk space check complete for path: {path}")
        return {
            "total_space": total,
            "available_space": available,
            "used_space": total - available,
        }
    except Exception as e:
        logging.error(f"Error checking disk space for path {path}: {e}")
        raise


# Example usage of the utilities
if __name__ == "__main__":
    # Setup logging
    setup_logging()

    # Test JSON save and load
    test_data = {"name": "Test", "value": 42}
    json_file = "test_data.json"
    save_to_json(json_file, test_data)
    loaded_data = load_from_json(json_file)
    print("Loaded JSON Data:", loaded_data)

    # Test CSV save
    csv_file = "test_data.csv"
    test_csv_data = [
        {"name": "CPU", "value": 80},
        {"name": "RAM", "value": 70},
    ]
    save_to_csv(csv_file, test_csv_data)

    # Generate a timestamped filename
    print("Generated Filename:", generate_timestamped_filename("report", "json"))

    # Check disk space
    print("Disk Space:", check_disk_space())

    # Validate writable path
    validate_writable_path("writable_test.txt")
