from typing import List, Tuple, Optional
from httpx import Response, AsyncClient
from aio_odoorpc.helper import helper_build_kwargs
from aio_odoorpc.async_jsonrpc import jsonrpc, jsonrpc_postprocessing


class AsyncOdooRPC:
    url: str
    database: str
    username: Optional[str]
    uid: Optional[int]
    password: str
    ssl_verify: bool
    
    def __init__(self, url: str, database: str, username_or_uid: str or int, password: str, ssl_verify: bool = True):
        self.url = url
        self.database = database
        self.password = password
        self.ssl_verify = ssl_verify
        
        if isinstance(username_or_uid, str):
            self.username = username_or_uid
            self.uid = None
        elif isinstance(username_or_uid, int):
            self.uid = username_or_uid
            self.username = None
    
    @classmethod
    async def from_cfg(cls, *,
                       host: str,
                       database: str,
                       username_or_uid: str or int,
                       password: str, port: int = None,
                       ssl: bool = True,
                       ssl_verify: bool = True,
                       base_url: str = None) -> 'AsyncOdooRPC':
        
        url_protocol = 'https' if ssl else 'http'
        if port is None:
            port = 443 if ssl else 80
        
        if (port == 80 and not ssl) or (port == 443 and ssl):
            url_port = ""
        else:
            url_port = f":{port}"
        
        if not base_url:
            base_url = ""
        
        url = f'{host}{url_port}/{base_url}/'.replace('//', '/')
        url = f'{url_protocol}://{url}'
        
        ssl_verify = (ssl and ssl_verify)
        
        self = cls(url=url, database=database, username_or_uid=username_or_uid,
                   password=password, ssl_verify=ssl_verify)
        
        if self.uid is not None:
            await self.login()
        
        return self

    async def login(self, *, http_client: Optional[AsyncClient] = None) -> int or None:
        # If uid is already set, this method is a noop
        if self.uid is not None:
            return None
    
        resp, data = await jsonrpc(base_url=self.url,
                                   service='common',
                                   method='login',
                                   ssl_verify=self.ssl_verify,
                                   args=[self.database, self.username, self.password],
                                   http_client=http_client)
    
        self.uid = await jsonrpc_postprocessing(resp, data, int)
        self.username = None
        return self.uid

    async def read(self, *,
                   model_name: str,
                   ids: List[int],
                   fields: Optional[List[str]] = None,
                   http_client: Optional[AsyncClient] = None) -> List[dict]:
        r, d = await self.execute_kw(method='read',
                                     model_name=model_name,
                                     ids=[ids],
                                     kwargs=helper_build_kwargs(fields=fields),
                                     http_client=http_client)
        return await jsonrpc_postprocessing(r, d, list)
    
    async def search(self, *,
                     model_name: str,
                     domain: list,
                     offset: Optional[int] = None,
                     limit: Optional[int] = None,
                     order: Optional[str] = None,
                     http_client: Optional[AsyncClient] = None) -> List[int]:
        
        r, d = await self.execute_kw(method='search',
                                     model_name=model_name,
                                     domain=[domain],
                                     kwargs=helper_build_kwargs(offset=offset, limit=limit, order=order),
                                     http_client=http_client)
        return await jsonrpc_postprocessing(r, d, list)
    
    async def search_read(self, *,
                          model_name: str,
                          domain: list,
                          fields: Optional[List[str]] = None,
                          offset: Optional[int] = None,
                          limit: Optional[int] = None,
                          order: Optional[str] = None,
                          http_client: Optional[AsyncClient] = None) -> List[dict]:
        
        r, d = \
            await self.execute_kw(method='search_read',
                                  model_name=model_name,
                                  domain=[domain],
                                  kwargs=helper_build_kwargs(fields=fields, offset=offset, limit=limit, order=order),
                                  http_client=http_client)
        
        return await jsonrpc_postprocessing(r, d, list)
    
    async def search_count(self, *,
                           model_name: str,
                           domain: list,
                           http_client: Optional[AsyncClient] = None) -> int:
        
        r, d = await self.execute_kw(method='search_count',
                                     model_name=model_name,
                                     domain=[domain],
                                     http_client=http_client)
        
        return await jsonrpc_postprocessing(r, d, int)
    
    async def execute_kw(self, *,
                         method: str,
                         model_name: str,
                         domain: Optional[list] = None,
                         ids: Optional[List[List[int]]] = None,
                         kwargs: Optional[dict] = None,
                         http_client: Optional[AsyncClient] = None) -> Tuple[Response, dict]:
        
        assert self.uid, '[OdooRPC] Error: uid is not set. Did you forget to call the login() method?'
        
        if (domain is None and ids is None) or (domain is not None and ids is not None):
            raise ValueError(f'[OdooRPC] execute_kw,{model_name},{method}: Either domain or ids *must* be set.')
        
        args = [self.database, self.uid, self.password, model_name, method]
        
        if domain is not None:
            args.append(domain)
        elif ids is not None:
            args.append(ids)
        
        if kwargs:
            args.append(kwargs)
        
        r, d = await jsonrpc(base_url=self.url,
                             service='object',
                             method='execute_kw',
                             ssl_verify=self.ssl_verify,
                             args=args,
                             http_client=http_client)
        
        return r, d
