from decimal import Decimal
from threading import Lock
from time import monotonic
from typing import Any

import httpx
from pydantic import SecretStr

from app.application.interfaces.payment_gateway import (
    PaymentGatewayError,
)


class BkashGatewayClient:
    """Server-side client for bKash Checkout."""

    def __init__(self, settings):
        self.settings = settings
        self.base_url = settings.bkash_api_base_url.rstrip("/")
        self._token_lock = Lock()
        self._access_token: str | None = None
        self._token_expires_at = 0.0

    @staticmethod
    def _secret_value(value: SecretStr | None) -> str | None:
        if value is None:
            return None

        secret = value.get_secret_value().strip()
        return secret or None

    def _require_configuration(self) -> tuple[str, str, str, str]:
        username = self.settings.bkash_username
        password = self._secret_value(self.settings.bkash_password)
        app_key = self._secret_value(self.settings.bkash_app_key)
        app_secret = self._secret_value(self.settings.bkash_app_secret)

        if not all((username, password, app_key, app_secret)):
            raise PaymentGatewayError(
                "bKash payment is not configured on the server."
            )

        return username, password, app_key, app_secret

    def validate_configuration(self) -> None:
        """Fail before creating a payment row when credentials are missing."""
        self._require_configuration()

    def _request_json(
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        try:
            response = httpx.request(
                method,
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=headers,
                json=payload,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise PaymentGatewayError(
                "The bKash gateway could not complete the request."
            ) from exc

        if not isinstance(data, dict):
            raise PaymentGatewayError(
                "The bKash gateway returned an unexpected response."
            )

        code = data.get("statusCode")
        if code is not None and str(code) not in {"0000"}:
            raise PaymentGatewayError(
                "The bKash gateway did not accept the request."
            )

        return data

    def _get_token(self) -> tuple[str, str]:
        username, password, app_key, app_secret = (
            self._require_configuration()
        )

        with self._token_lock:
            if (
                self._access_token
                and monotonic() < self._token_expires_at
            ):
                return self._access_token, app_key

            result = self._request_json(
                "POST",
                "/auth/grant-token",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "username": username,
                    "password": password,
                },
                payload={
                    "app_key": app_key,
                    "app_secret": app_secret,
                },
            )

            token = result.get("id_token")
            if not isinstance(token, str) or not token:
                raise PaymentGatewayError(
                    "The bKash gateway did not issue an access token."
                )

            try:
                expires_in = int(result.get("expires_in", 3600))
            except (TypeError, ValueError):
                expires_in = 3600
            self._access_token = token
            self._token_expires_at = monotonic() + max(
                60,
                expires_in - 60,
            )

        return token, app_key

    def _authorized_headers(self) -> dict[str, str]:
        token, app_key = self._get_token()

        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": token,
            "X-APP-Key": app_key,
        }

    def create_payment(
        self,
        amount: Decimal,
        currency: str,
        merchant_invoice_number: str,
        callback_url: str,
        payer_reference: str,
    ) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/payment/create",
            headers=self._authorized_headers(),
            payload={
                "mode": "0011",
                "payerReference": payer_reference,
                "callbackURL": callback_url,
                "amount": f"{amount:.2f}",
                "currency": currency,
                "intent": "sale",
                "merchantInvoiceNumber": merchant_invoice_number,
            },
        )

    def execute_payment(
        self,
        bkash_payment_id: str,
    ) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/payment/execute",
            headers=self._authorized_headers(),
            payload={
                "paymentId": bkash_payment_id,
            },
        )

    def query_payment(
        self,
        bkash_payment_id: str,
    ) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/query/payment",
            headers=self._authorized_headers(),
            payload={
                "paymentId": bkash_payment_id,
            },
        )
