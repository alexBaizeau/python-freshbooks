import json

from authlib.integrations.requests_client import OAuth2Session

from freshbooks import BaseClient
from freshbooks.exceptions import FreshBooksUnauthenticatedError, FreshBooksPaymentRequiredError


class Client(BaseClient):
    @property
    def authlib_integration_client(self):
        return OAuth2Session

    def fetch_access_token(self, authorization_response):
        return self.session.fetch_token(
            self.token_endpoint, authorization_response=authorization_response
        )

    def refresh_access_token(self):
        return self.session.refresh_token(
            self.token_endpoint, refresh_token=self.refresh_token
        )

    def get(self, url, params={}):
        response = self.session.get(f"{self.base_url}{url}", params=params)
        self.handle_errors(response)
        return response.json()

    def post(self, url, payload):
        response = self.session.post(url, data=json.dumps(payload))
        self.handle_errors(response)
        return response.json()

    def handle_errors(self, response):
        if response.status_code == 401:
            raise FreshBooksUnauthenticatedError()

        if response.status_code == 402:
            raise FreshBooksPaymentRequiredError()

        response.raise_for_status()

    def load_current_user(self):
        result = self.get("/auth/api/v1/users/me?exclude_groups=1")["response"]
        self.current_user = self.build_identity(result)
        return self.current_user

    def set_active_business(self, business_uuid):
        if not self.current_user:
            self.load_current_user()
        self.set_active_business_and_roles_id(self.current_user, business_uuid)

    def get_currencies(self):
        return self.get(
            f"/accounting/account/{self.active_account_id}/systems/currencies"
        )["response"]["result"]["currencies"]["currency_codes"]
