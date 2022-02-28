import requests

from ..exceptions import PolyApiException

GET = "GET"
POST = "POST"
DELETE = "DELETE"
PUT = "PUT"

def request(endpoint: str, method:str, headers=None, data=None):
    try:
        resp = requests.request(method=method, url=endpoint, headers=headers, json=data if data else None)
        if resp.status_code != 200:
            raise PolyApiException(resp)
        return resp.json()
    except requests.RequestException:
        raise PolyApiException(error_msg="Request exception!")

def post(endpoint, headers=None, data=None):
    return request(endpoint, POST, headers, data)

def get(endpoint, headers=None, data=None):
    return request(endpoint, GET, headers, data)

def delete(endpoint, headers=None, data=None):
    return request(endpoint, DELETE, headers, data)
