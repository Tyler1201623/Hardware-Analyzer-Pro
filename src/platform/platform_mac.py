import platform
import subprocess
import json


class PlatformMac:
    def __init__(self):
        self.os_info = self._get_os_info()
        self.kernel_version = self._get_kernel_version()
        self.architecture = platform.architecture()[0]

    def _get_os_info(self):
        """Retrieve macOS version information."""
        try:
            mac_version = platform.mac_ver()
            return {
                "os_name": "macOS",
                "version": mac_version[0],
                "build": mac_version[2],
            }
        except Exception as e:
            return {"error": f"Failed to fetch macOS info: {e}"}

    def _get_kernel_version(self):
        """Retrieve the macOS kernel version."""
        try:
            return platform.uname().release
        except Exception as e:
            return f"Failed to fetch kernel version: {e}"

    def get_hardware_info(self):
        """Retrieve hardware-specific information using system profiler."""
        try:
            output = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType"], text=True
            )
            hardware_info = {}
            for line in output.splitlines():
                if ": " in line:
                    key, value = line.split(": ", 1)
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
    platform_mac = PlatformMac()

    # Print platform details
    print("Mac Platform Details:")
    print(platform_mac)

    # Save to JSON
    try:
        with open("platform_mac_details.json", "w") as file:
            file.write(platform_mac.to_json())
        print("Platform details saved to platform_mac_details.json")
    except Exception as e:
        print(f"Error saving platform details: {e}")
