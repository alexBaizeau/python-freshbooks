import json

from authlib.integrations.httpx_client import AsyncOAuth2Client

from freshbooks import BaseClient


class AsyncClient(BaseClient):
    @property
    def authlib_integration_client(self):
        return AsyncOAuth2Client

    def token_payload(self, grant_type, secret_key, secret_value):
        payload = {
            "grant_type": grant_type,
            "client_secret": self.client_secret,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        payload[secret_key] = secret_value
        return payload

    async def fetch_access_token(self, authorization_response):
        return await self.session.fetch_token(
            self.token_endpoint, authorization_response=authorization_response
        )

    async def refresh_access_token(self):
        return await self.session.refresh_token(
            self.token_endpoint, refresh_token=self.refresh_token
        )

    async def get(self, url, params={}):
        response = await self.session.get(f"{self.base_url}{url}", params=params)
        self.handle_errors(response)
        return response.json()

    async def post(self, url, payload):
        response = await self.session.post(url, data=json.dumps(payload))
        self.handle_errors(response)
        return response.json()

    async def load_current_user(self):
        result = (await self.get("/auth/api/v1/users/me?exclude_groups=1"))["response"]
        self.current_user = self.build_identity(result)
        return self.current_user

    async def set_active_business(self, business_uuid):
        if not self.current_user:
            await self.load_current_user()
        self.set_active_business_and_roles_id(self.current_user, business_uuid)

    async def get_currencies(self):
        return (
            await (
                self.get(
                    f"/accounting/account/{self.active_account_id}/systems/currencies"
                )
            )
        )["response"]["result"]["currencies"]["currency_codes"]

