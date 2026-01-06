"""Polls the remote Streamlit deployment to verify health."""

import argparse
import sys
import time

import requests


def verify_health(url: str, timeout: int = 60, interval: int = 5):
    """Polls the Streamlit health endpoint or main page to verify deployment."""
    print(f"Checking health for: {url}")
    start_time = time.time()

    health_endpoint = f"{url.rstrip('/')}/_stcore/health"

    while time.time() - start_time < timeout:
        try:
            # Check standard Streamlit health endpoint
            resp = requests.get(health_endpoint, timeout=5)
            if resp.status_code == 200 and resp.text == "ok":
                print("SUCCESS: Streamlit health check passed (200 OK).")
                return 0

            # Fallback: check main page if health endpoint is hidden/different
            resp_main = requests.get(url, timeout=5)
            if resp_main.status_code == 200:
                print("SUCCESS: Main page returned 200 OK.")
                if "NHRA" in resp_main.text or "Streamlit" in resp_main.text:
                    print(" Verified content appears correct.")
                return 0

        except requests.RequestException as e:
            print(f"Polling... ({e})")

        time.sleep(interval)

    print("FAILURE: Timed out waiting for 200 OK.")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://gameofnhra.streamlit.app")
    parser.add_argument("--timeout", type=int, default=300)  # 5 mins max wait
    args = parser.parse_args()

    sys.exit(verify_health(args.url, args.timeout))
