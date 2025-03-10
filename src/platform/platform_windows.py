import platform
import subprocess
import json
import wmi  # Install using `pip install WMI`
import psutil
import win32com.client


class PlatformWindows:
    def __init__(self):
        self.os_info = self._get_os_info()
        self.kernel_version = self._get_kernel_version()
        self.architecture = platform.architecture()[0]
        self.hardware_info = self._get_hardware_info()

    def _get_os_info(self):
        """Retrieve Windows OS version information."""
        try:
            system_info = platform.uname()
            return {
                "system": system_info.system,
                "node_name": system_info.node,
                "release": system_info.release,
                "version": system_info.version,
                "machine": system_info.machine,
            }
        except Exception as e:
            return {"error": f"Failed to fetch OS info: {e}"}

    def _get_kernel_version(self):
        """Retrieve the Windows kernel version."""
        try:
            return platform.uname().release
        except Exception as e:
            return f"Failed to fetch kernel version: {e}"

    def _get_hardware_info(self):
        """Retrieve detailed hardware information using WMI."""
        try:
            w = wmi.WMI()
            cpu = w.Win32_Processor()[0]
            memory = w.Win32_PhysicalMemory()
            system = w.Win32_ComputerSystem()[0]

            memory_info = {
                "total_memory": f"{sum(int(mem.Capacity) for mem in memory) / (1024 ** 3):.2f} GB"
            }

            return {
                "cpu": {
                    "name": cpu.Name,
                    "cores": cpu.NumberOfCores,
                    "threads": cpu.NumberOfLogicalProcessors,
                    "architecture": platform.architecture()[0],
                },
                "memory": memory_info,
                "system": {
                    "manufacturer": system.Manufacturer,
                    "model": system.Model,
                },
            }
        except Exception as e:
            return {"error": f"Failed to fetch hardware info: {e}"}

    def to_dict(self):
        """Convert platform details to a dictionary."""
        return {
            "os_info": self.os_info,
            "kernel_version": self.kernel_version,
            "architecture": self.architecture,
            "hardware_info": self.hardware_info,
        }

    def to_json(self):
        """Convert platform details to JSON."""
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        """String representation of platform details."""
        return self.to_json()


class WindowsPlatform:
    @staticmethod
    def get_cpu_info():
        w = wmi.WMI()
        cpu = w.Win32_Processor()[0]
        return {
            "name": cpu.Name.strip(),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "architecture": cpu.Architecture,
            "max_clock_speed": f"{cpu.MaxClockSpeed} MHz",
        }

    @staticmethod
    def get_gpu_info():
        w = wmi.WMI()
        return [
            {
                "name": gpu.Name,
                "memory_total": f"{getattr(gpu, 'AdapterRAM', 0) / (1024**2):.0f} MB",
                "driver_version": getattr(gpu, "DriverVersion", "Unknown"),
            }
            for gpu in w.Win32_VideoController()
        ]


# Example usage
if __name__ == "__main__":
    platform_windows = PlatformWindows()

    # Print platform details
    print("Windows Platform Details:")
    print(platform_windows)

    # Save to JSON
    try:
        with open("platform_windows_details.json", "w") as file:
            file.write(platform_windows.to_json())
        print("Platform details saved to platform_windows_details.json")
    except Exception as e:
        print(f"Error saving platform details: {e}")
