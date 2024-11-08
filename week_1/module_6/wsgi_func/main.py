import requests
from typing import Callable, Optional

CURRENCY = "USD"


def fetch_currency(currency: str) -> tuple[str, Optional[bytes]]:
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    resp = requests.get(url)

    if resp.status_code < 300:
        response_body = resp.content
    else:
        response_body = None

    return f"{resp.status_code} {resp.reason}", response_body


def currency_app(environ: dict[str, str], start_response: Callable) -> Optional[bytes]:
    currency = environ.get("PATH_INFO", "/").split("/")[-1]
    response_status, response_body = fetch_currency(currency)

    status = response_status
    response_headers = [("Content-type", "text/html")]
    start_response(status, response_headers)

    return response_body


def run_wsgi_app(app: Callable, environ: dict[str, str]) -> list[bytes]:
    status_line = "200 OK"
    headers = [("Content-type", "text/html")]

    def start_response(status: str, response_headers: list[tuple[str]]) -> None:
        nonlocal status_line, headers
        status_line = status
        headers = response_headers

    response_body = app(environ, start_response)

    response = [f"HTTP/1.1 {status_line}".encode()]
    for header in headers:
        response.append(f"{header[0]}: {header[1]}".encode())

    if response_body:
        response.append(b'')
        response.append(response_body)

    return response


if __name__ == "__main__":
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": f"/{CURRENCY}",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    response = run_wsgi_app(currency_app, environ)
    print(b'\r\n'.join(response).decode())
