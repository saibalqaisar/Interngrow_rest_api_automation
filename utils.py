"""Shared helpers: logging + safe HTTP GET with retries and error handling."""
import logging
import time
import requests

logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("task4")


def safe_get(url, params=None, retries=3, timeout=10):
    """GET request that retries and handles every common API error.
    Returns the Response, or None if all attempts fail."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout,
                                headers={"User-Agent": "InternGrow-Task4/1.0"})
            resp.raise_for_status()          # raises on 4xx / 5xx
            log.info("GET %s -> %s", url, resp.status_code)
            return resp
        except requests.exceptions.Timeout:
            log.warning("Timeout (%s/%s): %s", attempt, retries, url)
        except requests.exceptions.ConnectionError:
            log.warning("Connection error (%s/%s): %s", attempt, retries, url)
        except requests.exceptions.HTTPError as e:
            log.error("HTTP error: %s", e)
            if e.response is not None and e.response.status_code < 500:
                break                         # client error: retrying won't help
        except requests.exceptions.RequestException as e:
            log.error("Request failed: %s", e)
        time.sleep(2 * attempt)               # back off before retrying
    return None
