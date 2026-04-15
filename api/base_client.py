"""Базовый API клиент."""

import httpx
from typing import Optional, Any, Dict
from config import settings


class BaseAPIClient:
    """Базовый класс для API клиентов."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = base_url or settings.API_BASE_URL
        self.timeout = timeout or settings.API_TIMEOUT
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )
        self._auth_token: Optional[str] = None

    def set_auth_token(self, token: str):
        """Установка токена авторизации."""
        self._auth_token = token
        self.client.headers["Authorization"] = f"Bearer {token}"

    def clear_auth_token(self):
        """Очистка токена авторизации."""
        self._auth_token = None
        self.client.headers.pop("Authorization", None)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Выполнение HTTP запроса."""
        request_headers = headers or {}
        if self._auth_token and "Authorization" not in request_headers:
            request_headers["Authorization"] = f"Bearer {self._auth_token}"

        response = self.client.request(
            method=method,
            url=endpoint,
            json=data,
            params=params,
            headers=request_headers,
        )
        return response

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """GET запрос."""
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """POST запрос."""
        return self._request("POST", endpoint, data=data, headers=headers)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """PUT запрос."""
        return self._request("PUT", endpoint, data=data)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """PATCH запрос."""
        return self._request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> httpx.Response:
        """DELETE запрос."""
        return self._request("DELETE", endpoint)

    def close(self):
        """Закрытие клиента."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
