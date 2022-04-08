import requests

from py_clob_client.clob_types import FilterParams

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

def build_query_params(url: str, param: str, val: str)->str:
    url_with_params = url
    last = url_with_params[-1]
    # if last character in url string == "?", append the param directly: api.com?param=value
    if last == "?":
        url_with_params = "{}{}={}".format(url_with_params, param, val)
    else:
        # else add "&", then append the param
        url_with_params = "{}&{}={}".format(url_with_params, param, val)
    return url_with_params

def add_query_params(base_url: str, params: FilterParams=None)->str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.market:
            url = build_query_params(url, "market", params.market)
        if params.max:
            url = build_query_params(url, "max", params.max)
        if params.start_ts:
            url = build_query_params(url, "startTs", params.start_ts)
        if params.end_ts:
            url = build_query_params(url, "endTs", params.end_ts)
    return url

