from core.cpu import CPU
from core.ram import RAM
from core.storage import Storage
from core.gpu import GPU
from core.logging_util import get_logger  # Add this import
import json
import requests
import csv
import logging
from datetime import datetime
from typing import Dict, Any, List
import platform
import wmi
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="hardware_manager.log",
    filemode="a",
)


class HardwareManager:
    def __init__(self):
        try:
            # Setup logging with UTF-8 encoding
            self.logger = get_logger("Hardware_Manager", "hardware_manager.log")

            # Initialize components with error handling
            try:
                self.cpu = self._initialize_cpu()
                self.ram = RAM()
                self.storage = Storage()
                self.gpu = GPU()

                self.system_info = self._get_system_info()
                self._setup_refresh_interval()
                self.logger.info("Hardware Manager initialized successfully")
            except Exception as e:
                self.logger.error(f"Component initialization failed: {e}")
                raise

        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Hardware Manager initialization failed: {e}")
            raise RuntimeError(f"Hardware Manager initialization failed: {e}")

    def _initialize_cpu(self) -> CPU:
        """Initialize CPU with enhanced name detection and error handling."""
        try:
            cpu = CPU()
            if platform.system() == "Windows":
                try:
                    w = wmi.WMI()
                    cpu_info = w.Win32_Processor()[0]
                    cpu.name = cpu_info.Name.strip()
                except Exception as e:
                    self.logger.warning(f"WMI CPU detection failed: {e}")
            return cpu
        except Exception as e:
            self.logger.error(f"CPU initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize CPU component: {e}")

    def _get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information."""
        return {
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        }

    def _setup_refresh_interval(self):
        """Setup default refresh intervals."""
        self.refresh_intervals = {
            "fast": 1,  # 1 second for critical metrics
            "normal": 5,  # 5 seconds for regular updates
            "slow": 30,  # 30 seconds for non-critical metrics
        }
        self.current_interval = self.refresh_intervals["normal"]

    def refresh_all(self):
        """Refresh all hardware components with enhanced error handling."""
        results = {"success": False, "cpu": 0.0, "ram": 0.0, "gpu": 0.0, "errors": []}

        try:
            self.cpu.update_metrics()
            results["cpu"] = self.get_cpu_usage()
        except Exception as e:
            self.logger.error(f"CPU refresh failed: {e}")
            results["errors"].append(f"CPU: {str(e)}")

        try:
            self.ram.update_metrics()
            results["ram"] = self.get_ram_usage()
        except Exception as e:
            self.logger.error(f"RAM refresh failed: {e}")
            results["errors"].append(f"RAM: {str(e)}")

        try:
            self.gpu.gpus = self.gpu._get_gpu_info()
            results["gpu"] = self.get_gpu_usage()
        except Exception as e:
            self.logger.error(f"GPU refresh failed: {e}")
            results["errors"].append(f"GPU: {str(e)}")

        results["success"] = not results["errors"]
        return results

    def get_hardware_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive hardware summary with enhanced formatting and error handling."""
        try:
            # Update all components first
            self.cpu.update_metrics()
            self.ram.update_metrics()
            self.gpu.gpus = self.gpu._get_gpu_info()

            summary = {
                "system_info": self._get_system_info(),
                "cpu": self.cpu.get_detailed_metrics(),
                "ram": self.ram.get_detailed_metrics(),
                "storage": self.storage.to_dict(),
                "gpu": {"gpus": self.gpu.gpus},
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Add performance indicators
            try:
                summary["performance_status"] = self._get_performance_status()
            except Exception as e:
                self.logger.error(f"Error getting performance status: {e}")
                summary["performance_status"] = {
                    "cpu_status": "🔴 Error",
                    "ram_status": "🔴 Error",
                    "storage_status": "🔴 Error",
                }

            self.logger.info("✓ Hardware summary generated successfully")
            return summary

        except Exception as e:
            self.logger.error(f"✗ Failed to generate hardware summary: {e}")
            # Return a minimal summary with error information
            return {
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "system_info": self._get_system_info(),
            }

    def _get_performance_status(self) -> Dict[str, str]:
        """Generate detailed performance status indicators with thresholds."""
        try:
            # Get current metrics
            cpu_metrics = self.cpu.get_detailed_metrics()
            ram_metrics = self.ram.get_detailed_metrics()
            storage_metrics = self.storage.to_dict()

            # CPU Status
            cpu_usage = float(cpu_metrics["current_usage"].strip("%"))
            cpu_status = self._get_resource_status(
                cpu_usage,
                warning_threshold=70,
                critical_threshold=85,
                resource_name="CPU",
            )

            # RAM Status
            ram_usage = float(ram_metrics["percent_used"].strip("%"))
            ram_status = self._get_resource_status(
                ram_usage,
                warning_threshold=75,
                critical_threshold=90,
                resource_name="RAM",
            )

            # Storage Status
            storage_status = self._get_aggregate_storage_status(
                storage_metrics["drives"]
            )

            return {
                "cpu_status": cpu_status["message"],
                "cpu_details": cpu_status["details"],
                "ram_status": ram_status["message"],
                "ram_details": ram_status["details"],
                "storage_status": storage_status["message"],
                "storage_details": storage_status["details"],
            }
        except Exception as e:
            self.logger.error(f"Error getting performance status: {e}")
            return {
                "cpu_status": "Error",
                "ram_status": "Error",
                "storage_status": "Error",
            }

    def _get_resource_status(
        self,
        usage: float,
        warning_threshold: float,
        critical_threshold: float,
        resource_name: str,
    ) -> Dict[str, str]:
        """Get detailed status for a resource with specific thresholds."""
        if usage >= critical_threshold:
            return {
                "message": f"🔴 Critical {resource_name} Usage",
                "details": f"{resource_name} usage at {usage:.1f}% - Performance severely impacted",
            }
        elif usage >= warning_threshold:
            return {
                "message": f"🟡 High {resource_name} Load",
                "details": f"{resource_name} usage at {usage:.1f}% - Monitor for performance impact",
            }
        else:
            return {
                "message": f"🟢 {resource_name} Optimal",
                "details": f"{resource_name} usage at {usage:.1f}% - Operating normally",
            }

    def _get_aggregate_storage_status(self, drives: List[Dict]) -> Dict[str, str]:
        """Get aggregated storage status across all drives."""
        critical_drives = []
        warning_drives = []

        for drive in drives:
            usage = float(drive["percent_used"].strip("%"))
            if usage > 90:
                critical_drives.append(drive["device"])
            elif usage > 80:
                warning_drives.append(drive["device"])

        if critical_drives:
            return {
                "message": "🔴 Critical Storage Space",
                "details": f"Critical space on drives: {', '.join(critical_drives)}",
            }
        elif warning_drives:
            return {
                "message": "🟡 Storage Space Warning",
                "details": f"Low space on drives: {', '.join(warning_drives)}",
            }
        return {
            "message": "🟢 Storage Optimal",
            "details": "All drives have adequate free space",
        }

    def to_json(self, pretty: bool = True) -> str:
        """Convert hardware summary to formatted JSON."""
        return json.dumps(self.get_hardware_summary(), indent=4 if pretty else None)

    def export_to_web(self, api_url: str, timeout: int = 10) -> None:
        """Export hardware summary to web API with enhanced error handling."""
        try:
            response = requests.post(
                api_url, json=self.get_hardware_summary(), timeout=timeout
            )
            response.raise_for_status()
            logging.info("✓ Hardware summary exported to web successfully")
        except requests.exceptions.RequestException as e:
            logging.error(f"✗ Web export failed: {e}")
            raise

    def save_to_file(self, file_path: str, format: str = "json") -> None:
        """Save hardware summary to file with format options."""
        try:
            if format.lower() == "json":
                with open(file_path, "w") as f:
                    f.write(self.to_json())
            elif format.lower() == "csv":
                summary = self.get_hardware_summary()
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    for section, data in summary.items():
                        writer.writerow([section.upper()])
                        if isinstance(data, dict):
                            for key, value in data.items():
                                writer.writerow([key, value])
                        writer.writerow([])
            logging.info(f"✓ Hardware summary saved to {file_path}")
        except Exception as e:
            logging.error(f"✗ File save failed: {e}")
            raise

    def export_to_mobile(self, mobile_api_url):
        """Send hardware summary to a mobile app API."""
        try:
            summary = self.get_hardware_summary()
            response = requests.post(mobile_api_url, json=summary, timeout=10)
            response.raise_for_status()
            logging.info("Hardware summary successfully sent to the mobile app.")
            print("Hardware summary successfully sent to the mobile app.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending hardware summary to mobile app: {e}")
            print(f"Error sending hardware summary to mobile app: {e}")

    def log_to_file(self, log_file_path):
        """Append hardware summary to a log file."""
        try:
            with open(log_file_path, "a") as log_file:
                log_file.write(self.to_json() + "\n")
            logging.info(f"Hardware summary logged to: {log_file_path}")
            print(f"Hardware summary logged to: {log_file_path}")
        except Exception as e:
            logging.error(f"Error logging hardware summary to file: {e}")
            print(f"Error logging hardware summary to file: {e}")

    def get_cpu_usage(self):
        """Get current CPU usage with error handling."""
        try:
            return float(self.cpu.get_detailed_metrics()["current_usage"].strip("%"))
        except Exception:
            return 0.0

    def get_ram_usage(self):
        """Get current RAM usage with error handling."""
        try:
            return float(self.ram.get_detailed_metrics()["percent_used"].strip("%"))
        except Exception:
            return 0.0

    def get_gpu_usage(self):
        """Get current GPU usage with error handling."""
        try:
            if self.gpu.gpus and "memory_used" in self.gpu.gpus[0]:
                total = float(self.gpu.gpus[0]["memory_total"].split()[0])
                used = float(self.gpu.gpus[0]["memory_used"].split()[0])
                return (used / total) * 100
            return 0.0
        except Exception:
            return 0.0

    def cleanup(self):
        """Cleanup resources properly."""
        try:
            # Close any open handlers
            for handler in self.logger.handlers[:]:
                try:
                    handler.close()
                    self.logger.removeHandler(handler)
                except Exception as e:
                    self.logger.error(f"Error closing handler: {e}")

            # Cleanup components with error handling
            components = ["gpu", "cpu", "ram", "storage"]
            for component_name in components:
                component = getattr(self, component_name, None)
                if component and hasattr(component, "cleanup"):
                    try:
                        component.cleanup()
                    except Exception as e:
                        self.logger.error(f"Error cleaning up {component_name}: {e}")

            self.logger.info("Hardware Manager cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def __str__(self):
        """String representation of hardware summary."""
        return self.to_json()

    def get_formatted_summary(self) -> str:
        """Get pre-formatted hardware summary for display."""
        try:
            summary = self.get_hardware_summary()
            sections = []

            # Headers with improved formatting
            headers = {
                "SYSTEM": "💻 SYSTEM INFORMATION",
                "CPU": "⚡ CPU INFORMATION",
                "MEMORY": "🧮 MEMORY STATUS",
                "GPU": "🎮 GPU INFORMATION",
                "STORAGE": "💾 STORAGE DEVICES",
                "STATUS": "📊 SYSTEM STATUS",
            }

            # Format each section with caching for performance
            sections.extend(
                self._format_system_section(summary["system_info"], headers["SYSTEM"])
            )
            sections.extend(self._format_cpu_section(summary["cpu"], headers["CPU"]))
            sections.extend(
                self._format_memory_section(summary["ram"], headers["MEMORY"])
            )
            sections.extend(self._format_gpu_section(summary["gpu"], headers["GPU"]))
            sections.extend(
                self._format_storage_section(summary["storage"], headers["STORAGE"])
            )
            sections.extend(
                self._format_status_section(
                    summary["performance_status"], headers["STATUS"]
                )
            )

            # Add timestamp with icon
            sections.append(f"\n⏰ Last Updated: {summary['timestamp']}")

            return "\n".join(sections)

        except Exception as e:
            self.logger.error(f"Error formatting summary: {e}")
            return "Error generating formatted summary"

    def _format_system_section(self, system_info: dict, header: str) -> List[str]:
        """Format system information section."""
        sections = []
        sections.append("╔════════════════ " + header + " ════════════════╗")
        for key, value in system_info.items():
            sections.append(f"║  {key.replace('_', ' ').title():<15}: {value:<35} ║")
        sections.append("╚══════════════════════════════════════════════════╝")
        return sections

    def _format_cpu_section(self, cpu_info: dict, header: str) -> List[str]:
        """Format CPU information section with error handling."""
        sections = []
        sections.append("\n╔════════════════ " + header + " ════════════════╗")
        try:
            # Handle potentially missing or None values with defaults
            model = cpu_info.get("name", "Unknown")
            cores = cpu_info.get("cores", "?")
            threads = cpu_info.get("threads", "?")
            freq = cpu_info.get("frequency", "Unknown")
            usage = cpu_info.get("current_usage", "0%")

            # Strip '%' and convert to float, with error handling
            try:
                usage_value = float(
                    usage.strip("%") if isinstance(usage, str) else usage
                )
            except (ValueError, AttributeError):
                usage_value = 0.0

            # Format the sections with proper padding
            sections.append(f"║  Model      : {str(model):<35} ║")
            sections.append(f"║  Cores      : {cores} Physical, {threads} Logical ║")
            sections.append(f"║  Frequency  : {str(freq):<35} ║")
            sections.append(
                f"║  Usage      : {self._get_status_indicator(usage_value):<35} ║"
            )

        except Exception as e:
            self.logger.error(f"Error formatting CPU section: {e}")
            sections.append(f"║  Error: Could not retrieve CPU information        ║")

        sections.append("╚══════════════════════════════════════════════════╝")
        return sections

    def _format_memory_section(self, ram_info: dict, header: str) -> List[str]:
        """Format memory information section."""
        sections = []
        sections.append("\n╔════════════════ " + header + " ════════════════╗")
        total = float(ram_info["total"].split()[0])
        used = float(ram_info["used"].split()[0])
        percent = float(ram_info["percent_used"].strip("%"))
        sections.append(
            f"║  Total      : {total:>6.2f} GB {self._get_memory_bar(percent)} ║"
        )
        sections.append(f"║  Used       : {used:>6.2f} GB ({percent}%) ║")
        sections.append(
            f"║  Available  : {float(ram_info['available'].split()[0]):>6.2f} GB ║"
        )
        sections.append("╚══════════════════════════════════════════════════╝")
        return sections

    def _format_gpu_section(self, gpu_info: dict, header: str) -> List[str]:
        """Format GPU information section with accurate memory reporting."""
        sections = []
        sections.append("\n╔════════════════ " + header + " ════════════════╗")
        for gpu in gpu_info["gpus"]:
            sections.append(f"║  Model      : {gpu['name']:<35} ║")
            memory = gpu.get("memory_total", "Memory size unknown")
            if memory != "Memory size unknown" and not isinstance(memory, str):
                memory = f"{memory / (1024**3):.2f} GB"
            sections.append(f"║  Memory     : {memory:<35} ║")
            sections.append(f"║  Driver     : {gpu['driver_version']:<35} ║")
        sections.append("╚══════════════════════════════════════════════════╝")
        return sections

    def _format_storage_section(self, storage_info: dict, header: str) -> List[str]:
        """Format storage information section."""
        sections = []
        sections.append("\n╔════════════════ " + header + " ════════════════╗")
        for drive in storage_info["drives"]:
            percent = float(drive["percent_used"].strip("%"))
            label = f"{drive['device']} ({drive['type']})"
            sections.append(f"║  {label:<44} ║")
            sections.append(f"║  {self._get_storage_bar(percent)} [{percent:>5.1f}%] ║")
            sections.append(
                f"║  Total: {drive['total']:<10} Used: {drive['used']:<10} Free: {drive['free']:<10} ║"
            )
            sections.append("║──────────────────────────────────────────────────║")
        sections.append("╚══════════════════════════════════════════════════╝")
        return sections

    def _format_status_section(self, status: dict, header: str) -> List[str]:
        """Format system status section."""
        sections = []
        sections.append("\n╔════════════════ " + header + " ════════════════╗")
        sections.append(f"║  CPU Status    : {status['cpu_status']:<35} ║")
        sections.append(f"║  RAM Status    : {status['ram_status']:<35} ║")
        sections.append(f"║  Storage Status: {status['storage_status']:<35} ║")
        sections.append("╚══════════════════════════════════════════════════╝")
        return sections

    def _get_memory_bar(self, percent: float) -> str:
        """Generate memory usage bar."""
        width = 20
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _get_storage_bar(self, percent: float) -> str:
        """Generate storage usage bar."""
        width = 40
        filled = int(width * percent / 100)
        if percent < 60:
            bar = "█" * filled + "░" * (width - filled)
        elif percent < 80:
            bar = "▒" * filled + "░" * (width - filled)
        else:
            bar = "▓" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _format_hardware_summary(self, summary):
        """Format hardware summary for display with error handling."""
        sections = []

        try:
            # CPU Section
            cpu_info = summary.get("cpu", {})
            sections.append("\n╔════════════════ CPU INFORMATION ════════════════╗")
            sections.append(f"║  Model      : {cpu_info.get('name', 'Unknown'):<35} ║")
            sections.append(
                f"║  Cores      : {cpu_info.get('cores', '?')} Physical, {cpu_info.get('threads', '?')} Logical ║"
            )
            sections.append(
                f"║  Frequency  : {cpu_info.get('frequency', 'Unknown'):<35} ║"
            )
            usage = cpu_info.get("current_usage", "0%")
            if isinstance(usage, str):
                usage = float(usage.strip("%"))
            sections.append(
                f"║  Usage      : {self._get_status_indicator(usage):<35} ║"
            )
            sections.append("╚══════════════════════════════════════════════════╝")

            # ...rest of existing code...

        except Exception as e:
            self.logger.error(f"Error formatting hardware summary: {e}")
            return "Error formatting hardware information"

    def generate_performance_graphs(self):
        """Generate performance graphs for CPU, RAM, and GPU usage."""
        if not hasattr(self, "performance_history") or not self.performance_history:
            return None

        try:
            # Extract data
            timestamps = [entry["timestamp"] for entry in self.performance_history]
            cpu_usage = [
                entry["metrics"].get("cpu", {}).get("usage", 0)
                for entry in self.performance_history
            ]
            ram_usage = [
                entry["metrics"].get("ram", {}).get("usage", 0)
                for entry in self.performance_history
            ]
            gpu_usage = [
                entry["metrics"].get("gpu", {}).get("usage", 0)
                for entry in self.performance_history
            ]

            # Create figure with subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
            fig.suptitle("System Performance History")

            # CPU Usage
            ax1.plot(timestamps, cpu_usage, "b-", label="CPU")
            ax1.set_ylabel("CPU Usage %")
            ax1.grid(True)
            ax1.legend()

            # RAM Usage
            ax2.plot(timestamps, ram_usage, "g-", label="RAM")
            ax2.set_ylabel("RAM Usage %")
            ax2.grid(True)
            ax2.legend()

            # GPU Usage
            ax3.plot(timestamps, gpu_usage, "r-", label="GPU")
            ax3.set_ylabel("GPU Usage %")
            ax3.grid(True)
            ax3.legend()

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Convert plot to base64 string
            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            buf.seek(0)
            plt.close()

            return base64.b64encode(buf.getvalue()).decode("utf-8")

        except Exception as e:
            self.logger.error(f"Error generating performance graphs: {e}")
            return None

    def export_performance_report(self, file_path, format="pdf"):
        """Export comprehensive performance report."""
        try:
            if format == "pdf":
                self._export_pdf_report(file_path)
            elif format == "html":
                self._export_html_report(file_path)
            elif format == "csv":
                self._export_csv_report(file_path)

            self.logger.info(f"Performance report exported to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting performance report: {e}")
            return False

    def _export_pdf_report(self, file_path):
        """Export report as PDF."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
            )
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Add title
            elements.append(Paragraph("System Performance Report", styles["Title"]))

            # Add current metrics
            summary = self.get_hardware_summary()

            # Create tables for each section
            for section, data in summary.items():
                elements.append(Paragraph(section.upper(), styles["Heading1"]))
                if isinstance(data, dict):
                    table_data = [[k, str(v)] for k, v in data.items()]
                    t = Table(table_data)
                    t.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                                ("FONTSIZE", (0, 0), (-1, -1), 10),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ]
                        )
                    )
                    elements.append(t)

            # Generate and add performance graphs
            graph_data = self.generate_performance_graphs()
            if graph_data:
                # Add performance graphs to PDF
                img_data = base64.b64decode(graph_data)
                img_path = "temp_graph.png"
                with open(img_path, "wb") as f:
                    f.write(img_data)
                elements.append(Paragraph("Performance Graphs", styles["Heading1"]))
                elements.append(Image(img_path))
                os.remove(img_path)

            doc.build(elements)

        except Exception as e:
            self.logger.error(f"Error creating PDF report: {e}")
            raise


# Example usage
if __name__ == "__main__":
    try:
        manager = HardwareManager()

        # Print hardware summary
        print("Hardware Summary:")
        print(manager)

        # Save hardware summary to JSON
        manager.save_to_file("hardware_summary.json")

        # Log hardware summary to a log file
        manager.log_to_file("hardware_summary.log")

        # Export to web
        web_api_url = "http://httpbin.org/post"  # Use httpbin for testing
        manager.export_to_web(web_api_url)

        # Export to mobile
        mobile_api_url = "http://httpbin.org/post"  # Use httpbin for testing
        manager.export_to_mobile(mobile_api_url)

    except Exception as e:
        print(f"Critical error in hardware manager script: {e}")
        logging.critical(f"Critical error in hardware manager script: {e}")
    finally:
        manager.cleanup()
