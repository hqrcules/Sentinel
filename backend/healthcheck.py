"""
Simple health check script for Vigil.
Can be used in Docker or Kubernetes health probes.
"""
import sys
import httpx


def check_health():
    """
    Check if the API is healthy.
    """
    try:
        response = httpx.get("http://localhost:8000/api/v1/health/liveness", timeout=5.0)
        if response.status_code == 200:
            print("Health check passed")
            return 0
        else:
            print(f"Health check failed with status code: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(check_health())
