"""
Utils
"""

import requests


def get_airbus_access_token(api_key: str) -> str:
  """
  Get Airbus access token

  Returns:
    str: access token
  """
  headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
  }

  data = [
    ('apikey', api_key),
    ('grant_type', 'api_key'),
    ('client_id', 'IDP'),
  ]

  response = requests.post('https://authenticate.foundation.api.oneatlas.airbus.com/auth/realms/IDP/protocol/openid-connect/token', headers=headers, data=data)

  access_token = response.json()['access_token']

  return access_token
