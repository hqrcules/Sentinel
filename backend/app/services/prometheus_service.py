import httpx
from typing import Dict, Any, Optional
from ..core import settings


class PrometheusService:
    def __init__(self):
        self.base_url = settings.PROMETHEUS_URL

    async def query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a PromQL query and return results.
        """
        url = f"{self.base_url}/api/v1/query"
        params = {"query": query}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "success":
                    return data.get("data")
                return None
        except Exception as e:
            print(f"Error querying Prometheus: {e}")
            return None

    async def query_range(
        self,
        query: str,
        start: str,
        end: str,
        step: str = "15s"
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a PromQL range query.
        """
        url = f"{self.base_url}/api/v1/query_range"
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "success":
                    return data.get("data")
                return None
        except Exception as e:
            print(f"Error querying Prometheus range: {e}")
            return None

    async def get_server_metrics(self, job_name: str, instance: str) -> Dict[str, Any]:
        """
        Get common metrics for a server.
        """
        metrics = {}

        # CPU usage
        cpu_query = f'100 - (avg by(instance) (irate(node_cpu_seconds_total{{mode="idle",job="{job_name}",instance="{instance}"}}[5m])) * 100)'
        cpu_result = await self.query(cpu_query)
        if cpu_result and cpu_result.get("result"):
            metrics["cpu_usage_percent"] = float(cpu_result["result"][0]["value"][1])

        # Memory usage
        memory_query = f'(1 - (node_memory_MemAvailable_bytes{{job="{job_name}",instance="{instance}"}} / node_memory_MemTotal_bytes{{job="{job_name}",instance="{instance}"}})) * 100'
        memory_result = await self.query(memory_query)
        if memory_result and memory_result.get("result"):
            metrics["memory_usage_percent"] = float(memory_result["result"][0]["value"][1])

        # Disk usage
        disk_query = f'100 - ((node_filesystem_avail_bytes{{job="{job_name}",instance="{instance}",mountpoint="/",fstype!="rootfs"}} * 100) / node_filesystem_size_bytes{{job="{job_name}",instance="{instance}",mountpoint="/",fstype!="rootfs"}})'
        disk_result = await self.query(disk_query)
        if disk_result and disk_result.get("result"):
            metrics["disk_usage_percent"] = float(disk_result["result"][0]["value"][1])

        # Network bytes received
        network_rx_query = f'rate(node_network_receive_bytes_total{{job="{job_name}",instance="{instance}"}}[5m])'
        network_rx_result = await self.query(network_rx_query)
        if network_rx_result and network_rx_result.get("result"):
            metrics["network_rx_bytes_per_sec"] = float(network_rx_result["result"][0]["value"][1])

        # Network bytes transmitted
        network_tx_query = f'rate(node_network_transmit_bytes_total{{job="{job_name}",instance="{instance}"}}[5m])'
        network_tx_result = await self.query(network_tx_query)
        if network_tx_result and network_tx_result.get("result"):
            metrics["network_tx_bytes_per_sec"] = float(network_tx_result["result"][0]["value"][1])

        return metrics


prometheus_service = PrometheusService()
