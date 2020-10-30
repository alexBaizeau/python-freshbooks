import requests
import json


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
        self.authenticate(self.token_url, payload)

    def authenticate(self, url, payload):
        response = self.post(url, payload)
        self.bearer_token = response['access_token']
        self.refresh_token = response['refresh_token']
        return self.bearer_token, self.refresh_token

    def get(self, url):
        return requests.get(f'{self.base_url}{url}', headers=self.headers, verify=False).json()

    def post(self, url, payload):
        return requests.post(
            url,
            data=json.dumps(payload),
            headers=self.headers,
            verify=False
        ).json()

    def get_current_user(self):
        return self.get('/api/v1/users/me')
