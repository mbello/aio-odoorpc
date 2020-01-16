from typing import Optional, Tuple
import random
import httpx


async def jsonrpc(*,
                  base_url: str,
                  service: str,
                  method: str,
                  ssl_verify: bool,
                  args: Optional[list] = None,
                  kwargs: Optional[dict] = None,
                  jsonrpc_url: str = "jsonrpc",
                  http_client: httpx.AsyncClient = None) -> Tuple[httpx.Response, dict]:
    
    req_id = random.randint(0, 1000000000)
    
    rpc_params = {'service': service,
                  'method': method}
    if args:
        rpc_params['args'] = args
    if kwargs:
        rpc_params['kwargs'] = kwargs
    
    data = {'jsonrpc': '2.0',
            'method': 'call',
            'params': rpc_params,
            'id': req_id}
    
    post_params = {'url': jsonrpc_url, 'json': data}
    
    if http_client:
        resp = await http_client.post(**post_params)
    else:
        async with httpx.AsyncClient(base_url=base_url, verify=ssl_verify) as http_client:
            resp = await http_client.post(**post_params)
    
    data = resp.json()
    assert data['id'] == req_id, "[AsyncOdooRPC] Somehow the response id differs from the request id."
    
    return resp, data


async def jsonrpc_postprocessing(resp: httpx.Response, data: dict, instance_of: Optional[type] = None):
    if data.get('error'):
        raise RuntimeError(data['error'])
    else:
        retval = data.get('result')
        if retval is None:
            raise RuntimeError('[AsyncOdooRPC] Response with no result.')
        if instance_of is not None:
            assert isinstance(retval, instance_of)
        return retval
