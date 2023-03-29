import requests
from requests.sessions import HTTPAdapter
from requests.adapters import Retry


def create_http_session(max_retry: int = 3, interval: float = 0.5):
    """
    retry기능이 추가된 http session

    args:
        max_retry: 최대 반복할 횟수
        interval: 반복 사이의 간격(시간) -> interval * (2 ** (시도 횟수-1))
    """

    http_ = requests.Session()

    retry_ = Retry(total=max_retry, backoff_factor=interval, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_)
    http_.mount('http://', adapter)
    http_.mount('https://', adapter)

    return http_

# 429: Too many Requests
# 500: Internal Server Error
# 502: Bad Gateway
# 503: Service Unavailable
# 504: Gateway Timeout