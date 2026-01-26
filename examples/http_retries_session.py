import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_retry_session(total_retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


if __name__ == "__main__":
    s = build_retry_session()
    r = s.get("https://clob.polymarket.com/")
    print("Status:", r.status_code)
