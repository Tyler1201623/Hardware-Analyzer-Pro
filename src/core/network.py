"""
Network-related utilities.
"""

import psutil
import json
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, List, Any
import socket
import requests


class Network:
    def __init__(self, log_dir: str = "logs"):
        """Initialize Network monitoring with enhanced features."""
        self.log_dir = log_dir
        self.history = []
        self.max_history_size = 100

        # Create log directory
        os.makedirs(log_dir, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Initialize metrics
        self.update_metrics()

    def setup_logging(self):
        """Setup enhanced logging configuration."""
        log_file = os.path.join(self.log_dir, "network_manager.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setFormatter(formatter)

        self.logger = logging.getLogger("Network_Manager")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def update_metrics(self):
        """Update network metrics."""
        try:
            self.interfaces = self._get_network_interfaces()
            self.connections = self._get_network_connections()
            self.io_counters = self._get_io_counters()
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._update_history()
            self.logger.info("Network metrics updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating network metrics: {e}")
            raise

    def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get detailed network interface information."""
        interfaces = []

        # Get addresses for all interfaces
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        for interface_name, addresses in net_if_addrs.items():
            interface_info = {
                "name": interface_name,
                "addresses": [],
                "status": "Down",
                "speed": None,
                "mtu": None,
            }

            # Get interface statistics
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_info.update(
                    {
                        "status": "Up" if stats.isup else "Down",
                        "speed": (
                            f"{stats.speed} Mbps" if stats.speed > 0 else "Unknown"
                        ),
                        "mtu": stats.mtu,
                    }
                )

            # Get IP addresses
            for addr in addresses:
                addr_info = {
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask if hasattr(addr, "netmask") else None,
                    "broadcast": addr.broadcast if hasattr(addr, "broadcast") else None,
                }
                interface_info["addresses"].append(addr_info)

            interfaces.append(interface_info)

        return interfaces

    def _get_network_connections(self) -> List[Dict[str, Any]]:
        """Get active network connections."""
        connections = []

        try:
            for conn in psutil.net_connections(kind="inet"):
                connection_info = {
                    "type": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                    "local_address": (
                        f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                    ),
                    "remote_address": (
                        f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                    ),
                    "status": conn.status,
                    "pid": conn.pid,
                }
                connections.append(connection_info)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            self.logger.warning("Access denied when fetching network connections")

        return connections

    def _get_io_counters(self) -> Dict[str, Any]:
        """Get network I/O statistics."""
        try:
            counters = psutil.net_io_counters()
            return {
                "bytes_sent": counters.bytes_sent,
                "bytes_recv": counters.bytes_recv,
                "packets_sent": counters.packets_sent,
                "packets_recv": counters.packets_recv,
                "errin": counters.errin,
                "errout": counters.errout,
                "dropin": counters.dropin,
                "dropout": counters.dropout,
            }
        except Exception as e:
            self.logger.error(f"Error getting I/O counters: {e}")
            return {}

    def _update_history(self):
        """Maintain historical network usage data."""
        current_metrics = {"timestamp": self.timestamp, "io_counters": self.io_counters}

        self.history.append(current_metrics)
        if len(self.history) > self.max_history_size:
            self.history.pop(0)

    def get_network_summary(self) -> dict:
        """Get comprehensive network summary."""
        try:
            self.update_metrics()

            stats = psutil.net_io_counters()
            net_if_stats = psutil.net_if_stats()
            net_if_addrs = psutil.net_if_addrs()

            interfaces = []
            for name, addrs in net_if_addrs.items():
                interface = {
                    "name": name,
                    "status": "Up" if net_if_stats[name].isup else "Down",
                    "speed": (
                        f"{net_if_stats[name].speed} Mbps"
                        if net_if_stats[name].speed > 0
                        else "Unknown"
                    ),
                    "mtu": net_if_stats[name].mtu,
                    "addresses": [],
                }

                for addr in addrs:
                    addr_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": getattr(addr, "netmask", None),
                        "broadcast": getattr(addr, "broadcast", None),
                    }
                    interface["addresses"].append(addr_info)

                interfaces.append(interface)

            return {
                "interfaces": interfaces,
                "io_stats": {
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errin": stats.errin,
                    "errout": stats.errout,
                },
                "connectivity": self.test_internet_connection(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            self.logger.error(f"Error getting network summary: {e}")
            return {"error": str(e), "connectivity": {"connected": False}}

    def _get_interfaces_info(self) -> list:
        """Get detailed network interface information."""
        interfaces = []
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for name, stat in stats.items():
            interface = {
                "name": name,
                "status": "Up" if stat.isup else "Down",
                "speed": f"{stat.speed} Mbps" if stat.speed > 0 else "Unknown",
                "mtu": stat.mtu,
                "addresses": [],
            }

            if name in addrs:
                for addr in addrs[name]:
                    address_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": getattr(addr, "netmask", None),
                        "broadcast": getattr(addr, "broadcast", None),
                    }
                    interface["addresses"].append(address_info)

            interfaces.append(interface)

        return interfaces

    def _get_active_connections(self) -> list:
        """Get list of active network connections."""
        connections = []
        try:
            for conn in psutil.net_connections(kind="inet"):
                connection = {
                    "type": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                    "local_addr": (
                        f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                    ),
                    "remote_addr": (
                        f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                    ),
                    "status": conn.status,
                }
                connections.append(connection)
        except:
            pass
        return connections

    def test_internet_connection(self) -> Dict[str, Any]:
        """Test internet connectivity with better error handling."""
        result = {
            "connected": False,
            "latency": None,
            "external_ip": None,
            "error": None,
        }

        try:
            # Test basic connectivity (with timeout)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            result["connected"] = True

            try:
                # Get external IP (with timeout)
                response = requests.get("https://api.ipify.org?format=json", timeout=5)
                if response.status_code == 200:
                    result["external_ip"] = response.json()["ip"]
                    result["latency"] = response.elapsed.total_seconds() * 1000
            except Exception as e:
                result["error"] = f"IP lookup failed: {str(e)}"

        except Exception as e:
            result["error"] = f"Connection test failed: {str(e)}"

        return result

    def export_metrics(self, export_format: str = "json", output_dir: str = "metrics"):
        """Export network metrics in specified format."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            if export_format == "json":
                file_path = os.path.join(
                    output_dir, f"network_metrics_{timestamp}.json"
                )
                with open(file_path, "w") as f:
                    json.dump(self.get_network_summary(), f, indent=4)
            return file_path
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            raise

    def cleanup(self):
        """Cleanup network resources."""
        try:
            # Close any open handlers
            if hasattr(self, "logger") and self.logger:
                for handler in self.logger.handlers[:]:
                    try:
                        handler.close()
                        self.logger.removeHandler(handler)
                    except Exception as e:
                        print(f"Error closing network handler: {e}")
        except Exception as e:
            print(f"Error during network cleanup: {e}")


if __name__ == "__main__":
    try:
        network = Network()
        print("Network Summary:")
        print(json.dumps(network.get_network_summary(), indent=4))

        print("\nInternet Connection Test:")
        print(json.dumps(network.test_internet_connection(), indent=4))

    except Exception as e:
        print(f"Error: {e}")
