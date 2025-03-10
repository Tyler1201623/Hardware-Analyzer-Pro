import platform
import json
import subprocess
import requests
import logging
import logging.handlers
import os
import csv
from datetime import datetime
from typing import Dict, Union, List

try:
    from py3nvml import py3nvml

    nvml_available = True
except ImportError:
    nvml_available = False


class GPU:
    def __init__(self, log_dir: str = "logs"):
        """Initialize GPU monitoring with enhanced features."""
        # Initialize core attributes
        self.log_dir = log_dir
        self.history = []
        self.max_history_size = 100

        # Create log directory
        os.makedirs(log_dir, exist_ok=True)

        # Setup components
        self.setup_logging()
        self.gpus = self._get_gpu_info()
        self.last_update = datetime.now()

    def setup_logging(self):
        """Setup enhanced logging configuration."""
        log_file = os.path.join(self.log_dir, "gpu_manager.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setFormatter(formatter)

        self.logger = logging.getLogger("GPU_Manager")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def _get_gpu_info(self) -> List[Dict[str, str]]:
        """Enhanced GPU detection with detailed information."""
        gpus = []

        if nvml_available:
            gpus.extend(self._get_nvml_gpu_info())

        # Platform-specific detection as fallback
        if not gpus:
            if platform.system() == "Windows":
                gpus.extend(self._get_windows_gpu_info())
            elif platform.system() == "Linux":
                gpus.extend(self._get_linux_gpu_info())
            elif platform.system() == "Darwin":
                gpus.extend(self._get_mac_gpu_info())

        return gpus or [{"name": "No GPU detected", "memory_total": "Unknown"}]

    def _get_windows_gpu_info(self) -> List[Dict[str, str]]:
        """Get GPU information on Windows using multiple methods."""
        gpus = []
        try:
            # Try NVML first for NVIDIA GPUs
            if nvml_available:
                nvidia_gpus = self._get_nvml_gpu_info()
                if nvidia_gpus:
                    return nvidia_gpus

            # Fallback to WMI
            import wmi

            w = wmi.WMI()
            for gpu in w.Win32_VideoController():
                gpu_info = {
                    "name": gpu.Name.strip(),
                    "driver_version": (
                        gpu.DriverVersion.strip() if gpu.DriverVersion else "Unknown"
                    ),
                    "video_processor": (
                        gpu.VideoProcessor.strip() if gpu.VideoProcessor else "Unknown"
                    ),
                }

                # Multi-step memory detection
                memory_str = self._get_gpu_memory_multi_source(gpu)
                gpu_info["memory_total"] = memory_str
                gpus.append(gpu_info)

        except Exception as e:
            self.logger.error(f"Error getting Windows GPU info: {e}")
        return gpus

    def _get_gpu_memory_multi_source(self, gpu_obj) -> str:
        """Get GPU memory using multiple detection methods."""
        try:
            # Method 1: Direct AdapterRAM
            if hasattr(gpu_obj, "AdapterRAM") and gpu_obj.AdapterRAM:
                memory = gpu_obj.AdapterRAM
                if memory > 0:
                    return f"{memory / (1024**3):.2f} GB"

            # Method 2: Registry lookup
            memory_from_reg = self._get_gpu_memory_from_registry(gpu_obj.PNPDeviceID)
            if memory_from_reg != "Memory size unknown":
                return memory_from_reg

            # Method 3: Dedicated video memory from DirectX
            if platform.system() == "Windows":
                try:
                    import ctypes

                    class DXGI_ADAPTER_DESC(ctypes.Structure):
                        _fields_ = [
                            ("Description", ctypes.c_wchar * 128),
                            ("VendorId", ctypes.c_uint),
                            ("DeviceId", ctypes.c_uint),
                            ("SubSysId", ctypes.c_uint),
                            ("Revision", ctypes.c_uint),
                            ("DedicatedVideoMemory", ctypes.c_size_t),
                            ("DedicatedSystemMemory", ctypes.c_size_t),
                            ("SharedSystemMemory", ctypes.c_size_t),
                            ("AdapterLuid", ctypes.c_int64),
                        ]

                    desc = DXGI_ADAPTER_DESC()
                    if hasattr(gpu_obj, "PNPDeviceID"):
                        # Use DXGI to get memory info
                        dxgi = ctypes.windll.dxgi
                        if dxgi and desc.DedicatedVideoMemory > 0:
                            return f"{desc.DedicatedVideoMemory / (1024**3):.2f} GB"
                except:
                    pass

            # Method 4: GPU-specific detection
            if "NVIDIA" in gpu_obj.Name and nvml_available:
                try:
                    py3nvml.nvmlInit()
                    handle = py3nvml.nvmlDeviceGetHandleByIndex(0)
                    memory_info = py3nvml.nvmlDeviceGetMemoryInfo(handle)
                    py3nvml.nvmlShutdown()
                    return f"{memory_info.total / (1024**3):.2f} GB"
                except:
                    pass

            # Last resort: Estimate based on device ID and known models
            if hasattr(gpu_obj, "DeviceID"):
                # Add common GPU memory mappings
                common_gpus = {
                    "RTX 4070": 12,
                    "RTX 3080": 10,
                    "RTX 3070": 8,
                    # Add more mappings as needed
                }
                for gpu_name, memory in common_gpus.items():
                    if gpu_name in gpu_obj.Name:
                        return f"{memory:.2f} GB"

        except Exception as e:
            self.logger.error(f"Error in GPU memory detection: {e}")

        return "Memory size unknown"

    def _get_gpu_memory_from_registry(self, pnp_device_id):
        """Get GPU memory from Windows registry as fallback."""
        try:
            import winreg

            key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{pnp_device_id}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                memory_val = winreg.QueryValueEx(key, "HardwareInformation.MemorySize")[
                    0
                ]
                if isinstance(memory_val, int) and memory_val > 0:
                    return f"{memory_val / (1024**3):.2f} GB"
        except:
            pass
        return "Memory size unknown"

    def _get_linux_gpu_info(self) -> List[Dict[str, str]]:
        """Get GPU information on Linux using lspci."""
        gpus = []
        try:
            output = subprocess.check_output("lspci | grep -i vga", shell=True).decode()
            for line in output.splitlines():
                gpus.append(
                    {
                        "name": line.split(": ")[1] if ": " in line else line,
                        "memory_total": "Unknown",
                    }
                )
        except Exception as e:
            self.logger.error(f"Error getting Linux GPU info: {e}")
        return gpus

    def _get_mac_gpu_info(self) -> List[Dict[str, str]]:
        """Get GPU information on macOS using system_profiler."""
        gpus = []
        try:
            output = subprocess.check_output(
                ["system_profiler", "SPDisplaysDataType"]
            ).decode()
            for line in output.splitlines():
                if "Chipset Model:" in line:
                    gpus.append(
                        {"name": line.split(": ")[1].strip(), "memory_total": "Unknown"}
                    )
        except Exception as e:
            self.logger.error(f"Error getting macOS GPU info: {e}")
        return gpus

    def _get_nvml_gpu_info(self) -> List[Dict[str, str]]:
        """Get NVIDIA GPU information using NVML."""
        gpus = []
        try:
            py3nvml.nvmlInit()
            device_count = py3nvml.nvmlDeviceGetCount()

            for i in range(device_count):
                handle = py3nvml.nvmlDeviceGetHandleByIndex(i)
                memory_info = py3nvml.nvmlDeviceGetMemoryInfo(handle)

                gpus.append(
                    {
                        "name": py3nvml.nvmlDeviceGetName(handle).decode(),
                        "memory_total": f"{memory_info.total / (1024**2):.0f} MB",
                        "memory_used": f"{memory_info.used / (1024**2):.0f} MB",
                        "memory_free": f"{memory_info.free / (1024**2):.0f} MB",
                        "driver_version": py3nvml.nvmlSystemGetDriverVersion().decode(),
                    }
                )

            py3nvml.nvmlShutdown()
        except Exception as e:
            self.logger.error(f"Error getting NVIDIA GPU info: {e}")
        return gpus

    def get_performance_metrics(self) -> Dict[str, Union[str, List[Dict]]]:
        """Get current GPU performance metrics."""
        metrics = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gpus": self.gpus,
        }
        return metrics

    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate a comprehensive GPU report."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"gpu_report_{timestamp}.txt")

        with open(report_path, "w") as f:
            f.write("=== GPU Analysis Report ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for gpu in self.gpus:
                f.write("GPU Information:\n")
                for key, value in gpu.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")

        return report_path

    def export_metrics(self, export_format: str = "json", output_dir: str = "metrics"):
        """Export GPU metrics in specified format."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "json":
            file_path = os.path.join(output_dir, f"gpu_metrics_{timestamp}.json")
            with open(file_path, "w") as f:
                json.dump({"gpus": self.gpus}, f, indent=4)
        elif export_format == "csv":
            file_path = os.path.join(output_dir, f"gpu_metrics_{timestamp}.csv")
            with open(file_path, "w", newline="") as f:
                if self.gpus:
                    writer = csv.DictWriter(f, fieldnames=self.gpus[0].keys())
                    writer.writeheader()
                    writer.writerows(self.gpus)

        return file_path


if __name__ == "__main__":
    try:
        gpu_monitor = GPU()

        # Generate comprehensive report
        report_path = gpu_monitor.generate_report()
        print(f"GPU report generated: {report_path}")

        # Export metrics in different formats
        json_metrics = gpu_monitor.export_metrics(export_format="json")
        csv_metrics = gpu_monitor.export_metrics(export_format="csv")
        print(f"Metrics exported to: {json_metrics} and {csv_metrics}")

    except Exception as e:
        logging.critical(f"Critical error in GPU script: {e}")
        print(f"Critical error: {e}")


def get_detailed_metrics(self):
    """Get comprehensive GPU metrics."""
    return {
        "gpus": self.gpus,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
