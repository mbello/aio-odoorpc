from typing import Optional, Tuple
import random
import httpx


def jsonrpc(base_url: str, service: str, method: str, ssl_verify: bool,
            args: Optional[list] = None, kwargs: Optional[dict] = None) -> Tuple[httpx.Response, dict]:
    req_id = random.randint(0, 1000000000)

    params = {'service': service,
              'method': method}
    if args:
        params['args'] = args
    if kwargs:
        params['kwargs'] = kwargs

    data = {'jsonrpc': '2.0',
            'method': 'call',
            'params': params,
            'id': req_id}

    with httpx.Client(base_url=base_url,
                      verify=ssl_verify) as client:
        resp = client.post(url="jsonrpc", json=data)
        data = resp.json()
        assert data['id'] == req_id, "[OdooRPC] Somehow the response id differs from the request id."

    return resp, data


def jsonrpc_postprocessing(resp: httpx.Response, data: dict, instance_of: Optional[type] = None):
    if data.get('error'):
        raise RuntimeError(data['error'])
    else:
        retval = data.get('result')
        if retval is None:
            raise RuntimeError('[aioOdooRPC] Response with no result.')
        if instance_of is not None:
            assert isinstance(retval, instance_of)
        return retval
