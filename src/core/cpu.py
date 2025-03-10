import psutil
import platform
import subprocess
import json
import requests
import logging
import logging.handlers
import os
import csv
from datetime import datetime
from typing import Dict, Union, List


class CPU:
    def __init__(self, log_dir: str = "logs"):
        """Initialize CPU monitoring with enhanced features."""
        try:
            # Initialize core attributes
            self.log_dir = log_dir
            self.history = []
            self.max_history_size = 100

            # Initialize default values
            self.name = "Unknown"
            self.cores = 0
            self.threads = 0
            self.frequency = 0
            self.architecture = "Unknown"
            self.current_usage = 0
            self.temperature = "Not available"
            self.hyperthreading = False  # Add missing attribute
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create log directory
            os.makedirs(log_dir, exist_ok=True)

            # Setup logging
            self.setup_logging()

            # Update metrics
            self.update_metrics()

        except Exception as e:
            print(f"Error initializing CPU: {e}")
            raise

    def setup_logging(self):
        """Setup enhanced logging configuration."""
        log_file = os.path.join(self.log_dir, "cpu_manager.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setFormatter(formatter)

        self.logger = logging.getLogger("CPU_Manager")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def update_metrics(self):
        """Update CPU metrics with real-time information."""
        try:
            # Get real CPU information
            self.name = self.get_cpu_name()
            self.cores = psutil.cpu_count(logical=False) or 0
            self.threads = psutil.cpu_count(logical=True) or 0
            self.hyperthreading = self.threads > self.cores if self.cores else False

            # Get frequency
            cpu_freq = psutil.cpu_freq()
            self.frequency = cpu_freq.current if cpu_freq else 0

            # Get architecture and usage
            self.architecture = platform.architecture()[0]
            self.current_usage = psutil.cpu_percent(interval=1)
            self.temperature = self.get_cpu_temperature()

            # Update timestamp and history
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._update_history()

            self.logger.info("CPU metrics updated successfully")

        except Exception as e:
            self.logger.error(f"Error updating CPU metrics: {e}")
            raise

    def get_cpu_name(self) -> str:
        """Get detailed CPU name based on platform with better error handling."""
        try:
            if platform.system() == "Windows":
                try:
                    import wmi

                    w = wmi.WMI(timeout=3)  # Add timeout to prevent hanging
                    for proc in w.Win32_Processor():
                        return proc.Name.strip()
                except Exception:
                    # Fallback to platform info if WMI fails
                    return platform.processor()

            elif platform.system() == "Darwin":  # macOS
                try:
                    return (
                        subprocess.check_output(
                            ["sysctl", "-n", "machdep.cpu.brand_string"], timeout=1
                        )
                        .decode()
                        .strip()
                    )
                except Exception:
                    return platform.processor()

            elif platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo") as f:
                        for line in f:
                            if "model name" in line:
                                return line.split(":")[1].strip()
                    return platform.processor()
                except Exception:
                    return platform.processor()

            # Default fallback
            return platform.processor() or "Unknown CPU"

        except Exception as e:
            self.logger.error(f"Error getting CPU name: {e}")
            return "Unknown CPU"

    def get_cpu_temperature(self) -> Union[float, str]:
        """Get CPU temperature if available."""
        try:
            if platform.system() == "Linux":
                temp = psutil.sensors_temperatures().get("coretemp", [])
                if temp:
                    return temp[0].current
            return "Not available"
        except:
            return "Not available"

    def _update_history(self):
        """Maintain historical CPU usage data."""
        current_metrics = {
            "timestamp": self.timestamp,
            "usage_percent": self.current_usage,
            "frequency": self.frequency,
            "temperature": self.temperature,
        }

        self.history.append(current_metrics)
        if len(self.history) > self.max_history_size:
            self.history.pop(0)

    def get_detailed_metrics(self) -> Dict[str, Union[str, float, bool]]:
        """Get comprehensive CPU metrics."""
        return {
            "name": self.name,
            "cores": self.cores,
            "threads": self.threads,
            "frequency": f"{self.frequency:.2f} MHz" if self.frequency else "Unknown",
            "architecture": self.architecture,
            "hyperthreading": self.hyperthreading,
            "current_usage": f"{self.current_usage:.1f}%",
            "temperature": (
                f"{self.temperature}°C"
                if isinstance(self.temperature, (int, float))
                else self.temperature
            ),
            "timestamp": self.timestamp,
        }

    def get_performance_alerts(self) -> List[str]:
        """Generate CPU performance alerts based on thresholds."""
        alerts = []
        if self.current_usage > 90:
            alerts.append("CRITICAL: CPU usage above 90%")
        elif self.current_usage > 80:
            alerts.append("WARNING: CPU usage above 80%")

        if isinstance(self.temperature, (int, float)) and self.temperature > 80:
            alerts.append("WARNING: High CPU temperature detected")

        return alerts

    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate a comprehensive CPU usage report."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"cpu_report_{timestamp}.txt")

        with open(report_path, "w") as f:
            f.write("=== CPU Performance Report ===\n")
            f.write(f"Generated: {self.timestamp}\n\n")

            # Current metrics
            f.write("Current CPU Metrics:\n")
            for key, value in self.get_detailed_metrics().items():
                f.write(f"{key}: {value}\n")

            # Performance alerts
            f.write("\nAlerts:\n")
            for alert in self.get_performance_alerts():
                f.write(f"- {alert}\n")

            # Usage history
            f.write("\nRecent Usage History:\n")
            for entry in self.history[-10:]:
                f.write(f"{entry['timestamp']}: {entry['usage_percent']}% CPU usage\n")

        return report_path

    def export_metrics(self, export_format: str = "json", output_dir: str = "metrics"):
        """Export CPU metrics in specified format."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "json":
            file_path = os.path.join(output_dir, f"cpu_metrics_{timestamp}.json")
            with open(file_path, "w") as f:
                json.dump(self.get_detailed_metrics(), f, indent=4)
        elif export_format == "csv":
            file_path = os.path.join(output_dir, f"cpu_metrics_{timestamp}.csv")
            metrics = self.get_detailed_metrics()
            with open(file_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=metrics.keys())
                writer.writeheader()
                writer.writerow(metrics)

        return file_path


if __name__ == "__main__":
    try:
        cpu_monitor = CPU()

        # Generate comprehensive report
        report_path = cpu_monitor.generate_report()
        print(f"CPU report generated: {report_path}")

        # Export metrics in different formats
        json_metrics = cpu_monitor.export_metrics(export_format="json")
        csv_metrics = cpu_monitor.export_metrics(export_format="csv")
        print(f"Metrics exported to: {json_metrics} and {csv_metrics}")

        # Check for performance alerts
        alerts = cpu_monitor.get_performance_alerts()
        if alerts:
            print("CPU Performance Alerts:", "\n".join(alerts))

    except Exception as e:
        logging.critical(f"Critical error in CPU script: {e}")
        print(f"Critical error: {e}")
