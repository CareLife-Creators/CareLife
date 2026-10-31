import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pydantic import SecretStr

from app.infrastructure.gateways.bkash import BkashGatewayClient


class BkashGatewayClientTests(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(
            bkash_api_base_url=(
                "https://tokenized.sandbox.bka.sh/v2/tokenized-checkout"
            ),
            bkash_username="sandbox-user",
            bkash_password=SecretStr("sandbox-password"),
            bkash_app_key=SecretStr("sandbox-app-key"),
            bkash_app_secret=SecretStr("sandbox-app-secret"),
        )
        self.client = BkashGatewayClient(self.settings)

    @patch("app.infrastructure.gateways.bkash.httpx.request")
    def test_query_uses_documented_tokenized_v2_endpoint(self, request):
        token_response = Mock()
        token_response.json.return_value = {"id_token": "test-token"}
        query_response = Mock()
        query_response.json.return_value = {
            "paymentId": "bkash-payment-1",
            "transactionStatus": "Initiated",
        }
        request.side_effect = [token_response, query_response]

        result = self.client.query_payment("bkash-payment-1")

        self.assertEqual(result["transactionStatus"], "Initiated")
        self.assertEqual(
            request.call_args_list[0].args[:2],
            (
                "POST",
                "https://tokenized.sandbox.bka.sh/v2/tokenized-checkout/auth/grant-token",
            ),
        )
        self.assertEqual(
            request.call_args_list[1].args[:2],
            (
                "POST",
                "https://tokenized.sandbox.bka.sh/v2/tokenized-checkout/query/payment",
            ),
        )
        self.assertEqual(
            request.call_args_list[1].kwargs["json"],
            {"paymentId": "bkash-payment-1"},
        )

    @patch("app.infrastructure.gateways.bkash.httpx.request")
    def test_access_token_is_reused_for_follow_up_gateway_calls(self, request):
        token_response = Mock()
        token_response.json.return_value = {
            "id_token": "test-token",
            "expires_in": "3600",
        }
        query_response = Mock()
        query_response.json.return_value = {
            "transactionStatus": "Initiated",
        }
        execute_response = Mock()
        execute_response.json.return_value = {
            "transactionStatus": "Completed",
        }
        request.side_effect = [
            token_response,
            query_response,
            execute_response,
        ]

        self.client.query_payment("bkash-payment-1")
        self.client.execute_payment("bkash-payment-1")

        self.assertEqual(request.call_count, 3)
        self.assertEqual(
            request.call_args_list[2].args[:2],
            (
                "POST",
                "https://tokenized.sandbox.bka.sh/v2/tokenized-checkout/payment/execute",
            ),
        )
        self.assertEqual(
            request.call_args_list[2].kwargs["json"],
            {"paymentId": "bkash-payment-1"},
        )


if __name__ == "__main__":
    unittest.main()
