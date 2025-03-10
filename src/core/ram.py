import psutil
import json
import requests
import logging
import logging.handlers
import os
import csv
from datetime import datetime
from typing import Dict, Union, List


class RAM:
    def __init__(self, log_dir: str = "logs"):
        """Initialize RAM monitoring with enhanced features."""
        # Initialize core attributes
        self.log_dir = log_dir
        self.history = []
        self.max_history_size = 100

        # Create log directory
        os.makedirs(log_dir, exist_ok=True)

        # Setup components
        self.setup_logging()
        self.update_metrics()

    def setup_logging(self):
        """Setup enhanced logging configuration."""
        log_file = os.path.join(self.log_dir, "ram_manager.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setFormatter(formatter)

        self.logger = logging.getLogger("RAM_Manager")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def update_metrics(self):
        """Update RAM metrics with real-time information."""
        try:
            # Set timestamp first
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Get real memory information from system
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Real RAM usage in GB
            self.total = mem.total / (1024**3)
            self.used = mem.used / (1024**3)
            self.available = mem.available / (1024**3)
            self.percent = mem.percent

            # Initialize cached and buffers
            self.cached = getattr(mem, "cached", 0) / (1024**3)
            self.buffers = getattr(mem, "buffers", 0) / (1024**3)

            # Real swap memory usage
            self.swap_total = swap.total / (1024**3)
            self.swap_used = swap.used / (1024**3)
            self.swap_free = swap.free / (1024**3)
            self.swap_percent = swap.percent

            self._update_history()
            self.logger.info("RAM metrics updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating RAM metrics: {e}")
            raise

    def _update_history(self):
        """Maintain historical RAM usage data."""
        try:
            current_metrics = {
                "timestamp": self.timestamp,
                "used_percent": self.percent,
                "available_gb": self.available,
                "swap_percent": self.swap_percent,
            }

            self.history.append(current_metrics)
            if len(self.history) > self.max_history_size:
                self.history.pop(0)
        except Exception as e:
            self.logger.error(f"Error updating history: {e}")
            raise

    def get_detailed_metrics(self) -> Dict[str, Union[str, float]]:
        """Get comprehensive RAM metrics."""
        return {
            "total": f"{self.total:.2f} GB",
            "used": f"{self.used:.2f} GB",
            "available": f"{self.available:.2f} GB",
            "percent_used": f"{self.percent:.1f}%",
            "cached": f"{self.cached:.2f} GB",
            "buffers": f"{self.buffers:.2f} GB",
            "swap_total": f"{self.swap_total:.2f} GB",
            "swap_used": f"{self.swap_used:.2f} GB",
            "swap_free": f"{self.swap_free:.2f} GB",
            "swap_percent": f"{self.swap_percent:.1f}%",
            "timestamp": self.timestamp,
        }

    def get_usage_alerts(self) -> List[str]:
        """Generate RAM usage alerts based on thresholds."""
        alerts = []
        if self.percent > 90:
            alerts.append("CRITICAL: RAM usage above 90%")
        elif self.percent > 80:
            alerts.append("WARNING: RAM usage above 80%")

        if self.swap_percent > 50:
            alerts.append("WARNING: High swap usage detected")

        return alerts

    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate a comprehensive RAM usage report."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"ram_report_{timestamp}.txt")

        with open(report_path, "w") as f:
            f.write("=== RAM Usage Report ===\n")
            f.write(f"Generated: {self.timestamp}\n\n")

            # Current metrics
            f.write("Current RAM Metrics:\n")
            for key, value in self.get_detailed_metrics().items():
                f.write(f"{key}: {value}\n")

            # Usage alerts
            f.write("\nAlerts:\n")
            for alert in self.get_usage_alerts():
                f.write(f"- {alert}\n")

            # Usage history
            f.write("\nUsage History:\n")
            for entry in self.history[-10:]:
                f.write(f"{entry['timestamp']}: {entry['used_percent']}% used\n")

        return report_path

    def export_metrics(self, export_format: str = "json", output_dir: str = "metrics"):
        """Export RAM metrics in specified format."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "json":
            file_path = os.path.join(output_dir, f"ram_metrics_{timestamp}.json")
            with open(file_path, "w") as f:
                json.dump(self.get_detailed_metrics(), f, indent=4)
        elif export_format == "csv":
            file_path = os.path.join(output_dir, f"ram_metrics_{timestamp}.csv")
            metrics = self.get_detailed_metrics()
            with open(file_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=metrics.keys())
                writer.writeheader()
                writer.writerow(metrics)

        return file_path


if __name__ == "__main__":
    try:
        ram_monitor = RAM()

        # Generate comprehensive report
        report_path = ram_monitor.generate_report()
        print(f"RAM report generated: {report_path}")

        # Export metrics in different formats
        json_metrics = ram_monitor.export_metrics(export_format="json")
        csv_metrics = ram_monitor.export_metrics(export_format="csv")
        print(f"Metrics exported to: {json_metrics} and {csv_metrics}")

        # Check for alerts
        alerts = ram_monitor.get_usage_alerts()
        if alerts:
            print("RAM Usage Alerts:", "\n".join(alerts))

    except Exception as e:
        logging.critical(f"Critical error in RAM script: {e}")
        print(f"Critical error: {e}")
