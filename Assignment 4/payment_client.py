"""Hardened outbound call to Payments service — timeout, retry with backoff+jitter."""
import os
import time
import random
import requests

def get_payments_base() -> str:
    url = os.getenv("PAYMENTS_SERVICE_URL", "http://localhost:5000")
    return url.rstrip("/")

def call_payments_create_order(*, order_id: str, amount: float, idempotency_key: str,
                                timeout: float = 2.0, max_retries: int = 3) -> dict:
    """POST /api/payment/order with retry. Never retries 4xx. Carries idempotency key."""
    url = f"{get_payments_base()}/api/payment/order"
    headers = {"Idempotency-Key": idempotency_key, "Content-Type": "application/json"}
    payload = {"amount": amount, "order_id": order_id}

    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
            # 4xx is not retryable
            if 400 <= resp.status_code < 500:
                # Surface as-is — caller maps to problem()
                resp.raise_for_status()
            if resp.status_code < 300:
                return resp.json()
            # 5xx -> retryable
            if 500 <= resp.status_code < 600 and attempt < max_retries:
                _sleep_backoff(attempt)
                continue
            resp.raise_for_status()
        except requests.exceptions.Timeout as e:
            last_exc = e
            if attempt < max_retries:
                _sleep_backoff(attempt)
                continue
            raise
        except requests.exceptions.ConnectionError as e:
            last_exc = e
            if attempt < max_retries:
                _sleep_backoff(attempt)
                continue
            raise
        except requests.exceptions.HTTPError:
            # 4xx already raised; do not swallow
            raise
        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                _sleep_backoff(attempt)
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("Payments call exhausted retries")

def _sleep_backoff(attempt: int) -> None:
    base = 0.2 * (2 ** attempt)  # 0.2s, 0.4s, 0.8s
    jitter = random.uniform(0, base * 0.2)
    time.sleep(base + jitter)
