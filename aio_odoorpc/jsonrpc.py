from typing import Any, Mapping, Optional, Sequence, Tuple
import random
from aio_odoorpc.protocols import ProtoHttpClient, ProtoResponse
# from asyncio import iscoroutine


def odoo_jsonrpc(*,
                 http_client: ProtoHttpClient,
                 service: str,
                 method: str,
                 args: Optional[Sequence] = None,
                 kwargs: Optional[Mapping] = None) -> Tuple[ProtoResponse, int]:

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

    resp = http_client.post(json=data)
    return resp, req_id


def odoo_jsonrpc_result(*,
                        http_client: ProtoHttpClient,
                        service: str,
                        method: str,
                        args: Optional[Sequence] = None,
                        kwargs: Optional[Mapping] = None,
                        ensure_instance_of: Optional[type] = None) -> Any:

    resp, req_id = odoo_jsonrpc(http_client=http_client,
                                service=service,
                                method=method,
                                args=args,
                                kwargs=kwargs)

    data = resp.json()

    assert data.get(
        'id') == req_id, "[OdooRPC] Somehow the response id differs from the request id."

    if data.get('error'):
        raise RuntimeError(data['error'])
    else:
        retval = data.get('result')
        if retval is None:
            raise RuntimeError('[OdooRPC] Response with no result.')
        if ensure_instance_of is not None:
            assert isinstance(retval, ensure_instance_of), \
                f'[OdooRPC] Result of unexpected type. Expecting {type(ensure_instance_of)}, got {type(retval)}.'
        return retval
