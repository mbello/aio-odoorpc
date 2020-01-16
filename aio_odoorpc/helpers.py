from typing import Optional


def build_execute_kw_kwargs(*, fields=None, limit=None, offset=None, order=None) -> dict or None:
    kwargs = dict()
    if offset is not None:
        kwargs['offset'] = offset
    if limit is not None:
        kwargs['limit'] = limit
    if order is not None:
        kwargs['order'] = order
    if fields is not None:
        kwargs['fields'] = fields
    return kwargs if kwargs else None


def build_odoo_jsonrpc_endpoint_url(*,
                                    host: str,
                                    port: Optional[int] = None,
                                    ssl: bool = True,
                                    base_url: str = '',
                                    custom_odoo_jsonrpc_suffix: Optional[str] = None) -> str:
    url = build_odoo_base_url(host=host, port=port, ssl=ssl, base_url=base_url)
    return odoo_base_url2jsonrpc_endpoint(url, custom_odoo_jsonrpc_suffix)


def build_odoo_base_url(*,
                        host: str,
                        port: Optional[int] = None,
                        ssl: bool = True,
                        base_url: str = '') -> str:
    
    url_protocol = 'https' if ssl else 'http'
    
    if port is None:
        port = 443 if ssl else 80
    
    url_port = '' if (port == 80 and not ssl) or (port == 443 and ssl) else f':{port}'
    
    url = f'{host}{url_port}/{base_url}/'.replace('//', '/')
    url = f'{url_protocol}://{url}'
    return url


def odoo_base_url2jsonrpc_endpoint(odoo_base_url: str = '', custom_odoo_jsonrpc_suffix: Optional[str] = None) -> str:
    sep = '/' if odoo_base_url and not odoo_base_url.endswith('/') else ''
    suffix = 'jsonrpc' if custom_odoo_jsonrpc_suffix is None else custom_odoo_jsonrpc_suffix
    return f'{odoo_base_url}{sep}{suffix}'


