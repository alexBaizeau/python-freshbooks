import requests
import json
from freshbooks.model.identity import Identity

class Client(object):

    def __init__(self, client_id, client_secret, redirect_uri, bearer_token=None, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.freshbooks.com"
        self.authorization_url = "https://my.freshbooks.com/service/auth/oauth/authorize"
        self.token_url = "https://api.freshbooks.com/auth/oauth/token"
        self.redirect_uri =  redirect_uri
        self.bearer_token = bearer_token
        self.refresh_token = refresh_token
        self.current_user = None,
        self.active_business_uuid = None,
        self.active_business_id = None,
        self.active_system_id = None,
        self.actvie_account_id = None
        self.active_role = None,


    @property
    def headers(self):
        headers = {
            'Api-Version': 'alpha',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        return headers

    def token_payload(self, grant_type, secret_key, secret_value):
        payload = {
            'grant_type': grant_type,
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        payload[secret_key] = secret_value
        return payload

    def fetch_access_token(self, code):
        payload = self.token_payload('authorization_code', 'code', code)
        self.authenticate(self.token_url, payload)
        return self.bearer_token, self.refresh_token

    def refresh_access_token(self):
        payload = self.token_payload('refresh_token', 'refresh_token', self.refresh_token)
        return self.authenticate(self.token_url, payload)

    def authenticate(self, url, payload):
        response = self.post(url, payload)
        self.bearer_token = response['access_token']
        self.refresh_token = response['refresh_token']
        return self.bearer_token, self.refresh_token

    def get(self, url, params={}):
        return requests.get(f'{self.base_url}{url}', headers=self.headers, params=params, verify=False).json()

    def post(self, url, payload):
        return requests.post(
            url,
            data=json.dumps(payload),
            headers=self.headers,
            verify=False
        ).json()

    def load_current_user(self):
        result = self.get('/auth/api/v1/users/me?exclude_groups=1')["response"]
        self.current_user = Identity(self, result["id"], result["email"], result["first_name"], result["last_name"], result["business_memberships"], result["roles"])
        return self.current_user

    def set_active_business(self, business_uuid):
        if not self.current_user:
            self.load_current_user()
        business_memberships = self.current_user.business_memberships
        business_membership = next(bm for bm in business_memberships if bm["business"]["business_uuid"] == business_uuid)

        roles = self.current_user.roles
        active_role = next(role for role in roles if role["accountid"] == business_membership["business"]["account_id"])

        self.active_role = active_role
        self.active_business_id = business_membership["business"]["id"]
        self.active_account_id = self.active_role["accountid"]
        self.active_system_id = self.active_role["systemid"]
        self.active_business_uuid = business_uuid

    def get_currencies(self):
        return self.get(f"/accounting/account/{self.active_account_id}/systems/currencies")["response"]["result"]["currencies"]["currency_codes"]

    def get_invoice_details_report(self, params={}):
        return self.get(f"/accounting/account/{self.active_account_id}/reports/accounting/invoice_details", params)

    def get_expense_report(self, params={}):
        return self.get(f"/accounting/account/{self.active_account_id}/reports/accounting/expense_details", params)

    def get_autocomplete_clients(self, params={}):
        return self.get(f"/search/account/{self.active_account_id}/autocomplete_clients_v2", params)

    def get_clients(self, params={}):
        return self.get(f"/accounting/account/{self.active_account_id}/users/clients", params)
