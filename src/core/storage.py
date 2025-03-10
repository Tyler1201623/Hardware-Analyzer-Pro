import psutil
import json
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="storage_manager.log",
    filemode="a",
)


class Storage:
    def __init__(self):
        """Initialize the storage details."""
        try:
            self.drives = self._get_storage_info()
            logging.info("Storage details initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing storage details: {e}")
            self.drives = []

    def _get_storage_info(self):
        """Retrieve storage details from all partitions."""
        storage_details = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                storage_details.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "type": partition.fstype,
                        "total": f"{usage.total / (1024 ** 3):.2f} GB",  # Convert bytes to GB
                        "used": f"{usage.used / (1024 ** 3):.2f} GB",  # Convert bytes to GB
                        "free": f"{usage.free / (1024 ** 3):.2f} GB",  # Convert bytes to GB
                        "percent_used": f"{usage.percent:.1f}%",
                    }
                )
                logging.info(
                    f"Retrieved storage details for device: {partition.device}"
                )
            except PermissionError:
                # Skip inaccessible partitions
                logging.warning(f"Permission denied for device: {partition.device}")
                storage_details.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "type": partition.fstype,
                        "error": "Permission denied",
                    }
                )
            except Exception as e:
                logging.error(
                    f"Error retrieving storage details for device {partition.device}: {e}"
                )
                storage_details.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "type": partition.fstype,
                        "error": str(e),
                    }
                )
        return storage_details

    def to_dict(self):
        """Convert storage details to a dictionary."""
        try:
            return {"drives": self.drives}  # Updated key to 'drives'
        except Exception as e:
            logging.error(f"Error converting storage details to dictionary: {e}")
            return {"error": "Failed to convert storage details to dictionary"}

    def to_json(self):
        """Convert storage details to JSON."""
        try:
            return json.dumps(self.to_dict(), indent=4)
        except Exception as e:
            logging.error(f"Error converting storage details to JSON: {e}")
            return json.dumps({"error": "Failed to convert storage details to JSON"})

    def export_to_web(self, api_url):
        """Send storage details to a web API."""
        try:
            response = requests.post(api_url, json=self.to_dict(), timeout=10)
            response.raise_for_status()
            logging.info("Storage details successfully sent to the web server.")
            print("Storage details successfully sent to the web server.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending storage details to web server: {e}")
            print(f"Error sending storage details to web server: {e}")

    def export_to_mobile(self, mobile_api_url):
        """Send storage details to a mobile app API."""
        try:
            response = requests.post(mobile_api_url, json=self.to_dict(), timeout=10)
            response.raise_for_status()
            logging.info("Storage details successfully sent to the mobile app.")
            print("Storage details successfully sent to the mobile app.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending storage details to mobile app: {e}")
            print(f"Error sending storage details to mobile app: {e}")

    def save_to_file(self, file_path):
        """Save storage details to a JSON file."""
        try:
            with open(file_path, "w") as file:
                file.write(self.to_json())
            logging.info(f"Storage details saved to: {file_path}")
            print(f"Storage details saved to: {file_path}")
        except Exception as e:
            logging.error(f"Error saving storage details to file: {e}")
            print(f"Error saving storage details to file: {e}")

    def log_to_file(self, log_file_path):
        """Append storage details to a log file."""
        try:
            with open(log_file_path, "a") as log_file:
                log_file.write(self.to_json() + "\n")
            logging.info(f"Storage details logged to: {log_file_path}")
            print(f"Storage details logged to: {log_file_path}")
        except Exception as e:
            logging.error(f"Error logging storage details to file: {e}")
            print(f"Error logging storage details to file: {e}")

    def get_drive_health_status(self, drive_info):
        """Get detailed health status for a drive."""
        try:
            used_percent = float(drive_info["percent_used"].strip("%"))
            total_gb = float(drive_info["total"].split()[0])
            free_gb = float(drive_info["free"].split()[0])

            status = {"status": "optimal", "warnings": [], "recommendations": []}

            # Space warnings
            if used_percent > 90:
                status["status"] = "critical"
                status["warnings"].append("Critical: Drive is nearly full")
                status["recommendations"].append(
                    f"Immediate action required: Only {free_gb:.1f} GB remaining"
                )
            elif used_percent > 80:
                status["status"] = "warning"
                status["warnings"].append("Warning: Drive space running low")
                status["recommendations"].append(
                    "Consider cleaning temporary files and moving large files"
                )

            # Size-based recommendations
            if total_gb > 200 and used_percent > 75:
                status["recommendations"].append(
                    f"Large drive ({total_gb:.0f} GB) running low on space. Consider:"
                    "\n- Running disk cleanup"
                    "\n- Moving old files to external storage"
                    "\n- Uninstalling unused applications"
                )

            # System drive specific checks
            if drive_info["device"].split(":")[0] == "C":
                if free_gb < 50:
                    status["warnings"].append(
                        "System drive space critical for optimal performance"
                    )
                    status["recommendations"].append(
                        "Maintain at least 50GB free on system drive for performance"
                    )

            return status

        except Exception as e:
            self.logger.error(f"Error getting drive health status: {e}")
            return {"status": "unknown", "warnings": [], "recommendations": []}

    def __str__(self):
        """String representation of storage details."""
        return self.to_json()


# Example usage
if __name__ == "__main__":
    try:
        storage = Storage()

        # Print storage details
        print("Storage Details:")
        print(storage)

        # Save storage details to JSON
        storage.save_to_file("storage_details.json")

        # Log storage details to a log file
        storage.log_to_file("storage_details.log")

        # Export to web
        web_api_url = "http://httpbin.org/post"  # Use httpbin for testing
        storage.export_to_web(web_api_url)

        # Export to mobile
        mobile_api_url = "http://httpbin.org/post"  # Use httpbin for testing
        storage.export_to_mobile(mobile_api_url)

    except Exception as e:
        print(f"Critical error in storage script: {e}")
        logging.critical(f"Critical error in storage script: {e}")
