import platform
import subprocess
import json


class PlatformLinux:
    def __init__(self):
        self.os_info = self._get_os_info()
        self.kernel_version = self._get_kernel_version()
        self.architecture = platform.architecture()[0]

    def _get_os_info(self):
        """Retrieve Linux distribution information."""
        try:
            with open("/etc/os-release", "r") as file:
                os_info = {}
                for line in file:
                    key, value = line.strip().split("=")
                    os_info[key] = value.strip('"')
                return os_info
        except Exception as e:
            return {"error": f"Failed to fetch OS info: {e}"}

    def _get_kernel_version(self):
        """Retrieve the Linux kernel version."""
        try:
            return platform.uname().release
        except Exception as e:
            return f"Failed to fetch kernel version: {e}"

    def get_hardware_info(self):
        """Retrieve hardware-specific information using lscpu."""
        try:
            output = subprocess.check_output("lscpu", shell=True).decode("utf-8")
            hardware_info = {}
            for line in output.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    hardware_info[key.strip()] = value.strip()
            return hardware_info
        except Exception as e:
            return {"error": f"Failed to fetch hardware info: {e}"}

    def to_dict(self):
        """Convert platform details to a dictionary."""
        return {
            "os_info": self.os_info,
            "kernel_version": self.kernel_version,
            "architecture": self.architecture,
            "hardware_info": self.get_hardware_info(),
        }

    def to_json(self):
        """Convert platform details to JSON."""
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        """String representation of platform details."""
        return self.to_json()


# Example usage
if __name__ == "__main__":
    platform_linux = PlatformLinux()

    # Print platform details
    print("Linux Platform Details:")
    print(platform_linux)

    # Save to JSON
    try:
        with open("platform_linux_details.json", "w") as file:
            file.write(platform_linux.to_json())
        print("Platform details saved to platform_linux_details.json")
    except Exception as e:
        print(f"Error saving platform details: {e}")
