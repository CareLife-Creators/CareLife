from decimal import Decimal
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

        result = self._request_json(
            "POST",
            "/tokenized/checkout/token/grant",
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
            "/tokenized/checkout/create",
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
            "/tokenized/checkout/execute",
            headers=self._authorized_headers(),
            payload={
                "paymentID": bkash_payment_id,
            },
        )

    def query_payment(
        self,
        bkash_payment_id: str,
    ) -> dict[str, Any]:
        return self._request_json(
            "GET",
            "/tokenized/checkout/payment/status",
            headers=self._authorized_headers(),
            params={
                "paymentID": bkash_payment_id,
            },
        )