import json

from authlib.common.urls import url_decode

from freshbooks.exceptions import FreshBooksUnauthenticateddError
from freshbooks.model.identity import Identity


def build_auth_client_secret_freshbooks(redirect_uri):
    def auth_client_secret_freshbooks(client, method, uri, headers, body):
        try:
            # When using the httpx client body is "b" bytes string, not sure why
            body = body.decode()
        except (UnicodeDecodeError, AttributeError):
            pass

        body = dict(url_decode(body))
        body["client_id"] = client.client_id
        body["client_secret"] = client.client_secret
        body["redirect_uri"] = redirect_uri
        headers["Content-Type"] = "application/json"
        return uri, headers, json.dumps(body)

    return auth_client_secret_freshbooks


class BaseClient(object):
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        update_token=None,
        token=None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.freshbooks.com"
        self.authorization_url = (
            "https://my.freshbooks.com/service/auth/oauth/authorize"
        )
        self.token_endpoint = "https://api.freshbooks.com/auth/oauth/token"
        self.update_token = update_token
        self.redirect_uri = redirect_uri
        self.session = self.authlib_integration_client(
            client_id,
            client_secret,
            update_token=update_token,
            token=token,
            token_endpoint_auth_method="client_secret_freshbooks",
            token_endpoint=self.token_endpoint,
        )
        self.session.register_client_auth_method(
            (
                "client_secret_freshbooks",
                build_auth_client_secret_freshbooks(redirect_uri),
            )
        )

        self.current_user = None
        self.active_business_uuid = None
        self.active_business_id = None
        self.active_system_id = None
        self.active_account_id = None
        self.active_role = None
        self.active_business_membership = None

    @property
    def authlib_integration_client(self):
        raise NotImplementedError

    @property
    def headers(self):
        headers = {
            "Api-Version": "alpha",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        }
        return headers

    def token_payload(self, grant_type, secret_key, secret_value):
        payload = {
            "grant_type": grant_type,
            "client_secret": self.client_secret,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        payload[secret_key] = secret_value
        return payload

    def handle_errors(self, response):
        if response.status_code == 401:
            raise FreshBooksUnauthenticateddError()

        response.raise_for_status()

    def build_identity(self, result):
        return Identity(
            self,
            result["id"],
            result["email"],
            result["first_name"],
            result["last_name"],
            result["business_memberships"],
            result["roles"],
        )

    def set_active_business_and_roles_id(self, user, business_uuid):
        business_memberships = user.business_memberships
        business_membership = next(
            bm
            for bm in business_memberships
            if bm["business"]["business_uuid"] == str(business_uuid)
        )

        roles = self.current_user.roles
        active_role = next(
            role
            for role in roles
            if role["accountid"] == business_membership["business"]["account_id"]
        )

        self.active_role = active_role
        self.active_business_membership = business_membership
        self.active_business_id = business_membership["business"]["id"]
        self.active_account_id = self.active_role["accountid"]
        self.active_system_id = self.active_role["systemid"]
        self.active_business_uuid = business_uuid

    def get_invoice_details_report(self, params={}):
        return self.get(
            f"/accounting/account/{self.active_account_id}/reports/accounting/invoice_details",
            params,
        )

    def get_expense_report(self, params={}):
        return self.get(
            f"/accounting/account/{self.active_account_id}/reports/accounting/expense_details",
            params,
        )

    def get_profit_loss_report(self, params={}):
        return self.get(
            f"/accounting/account/{self.active_account_id}/reports/accounting/profitloss_entity",
            params,
        )

    def get_autocomplete_clients(self, params={}):
        return self.get(
            f"/search/account/{self.active_account_id}/autocomplete_clients_v2", params
        )

    def get_clients(self, params={}):
        return self.get(
            f"/accounting/account/{self.active_account_id}/users/clients", params
        )
