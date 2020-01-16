from typing import Any, Mapping, Optional, Sequence, Tuple
import random
from aio_odoorpc.protocols import ProtoAsyncHttpClient, ProtoAsyncResponse, ProtoResponse
from asyncio import iscoroutine


async def async_odoo_jsonrpc(*,
                             http_client: ProtoAsyncHttpClient,
                             service: str,
                             method: str,
                             args: Optional[Sequence] = None,
                             kwargs: Optional[Mapping] = None) -> Tuple[ProtoResponse or ProtoAsyncResponse, int]:
    
    req_id = random.randint(0, 1000000000)
    
    data = {'jsonrpc': '2.0',
            'method': 'call',
            'params': {'service': service,
                       'method': method},
            'id': req_id}
    
    if args:
        data['params']['args'] = args
    if kwargs:
        data['params']['kwargs'] = kwargs
    
    resp = await http_client.post(json=data)
    return resp, req_id


async def async_odoo_jsonrpc_result(*,
                                    http_client: ProtoAsyncHttpClient,
                                    service: str,
                                    method: str,
                                    args: Optional[Sequence] = None,
                                    kwargs: Optional[Mapping] = None,
                                    ensure_instance_of: Optional[type] = None) -> Any:
    
    resp, req_id = await async_odoo_jsonrpc(http_client=http_client,
                                            service=service,
                                            method=method,
                                            args=args,
                                            kwargs=kwargs)
    
    data = await resp.json() if iscoroutine(resp.json) else resp.json()
    
    assert data.get('id') == req_id, "[AsyncOdooRPC] Somehow the response id differs from the request id."
    
    if data.get('error'):
        raise RuntimeError(data['error'])
    else:
        retval = data.get('result')
        if retval is None:
            raise RuntimeError('[AsyncOdooRPC] Response with no result.')
        if ensure_instance_of is not None:
            assert isinstance(retval, ensure_instance_of), \
                f'[AsyncOdooRPC] Result of unexpected type. Expecting {type(ensure_instance_of)}, got {type(retval)}.'
        return retval

