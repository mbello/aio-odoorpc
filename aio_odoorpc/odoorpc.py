from typing import Any, Callable, List, Optional
from aio_odoorpc.helpers import build_execute_kw_kwargs
from aio_odoorpc.jsonrpc import odoo_jsonrpc, odoo_jsonrpc_result
from aio_odoorpc.protocols import ProtoHttpClient
# from typing import Awaitable
# from inspect import isawaitable


class OdooRPC:
    database: str
    username: Optional[str]
    uid: Optional[int]
    password: str
    _http_client: Optional[Callable or ProtoHttpClient]

    def __init__(self, *,
                 database: str,
                 username_or_uid: str or int,
                 password: str,
                 http_client: Optional[Callable] = None):
        self.database = database
        self.password = password
        self._http_client = http_client

        if isinstance(username_or_uid, str):
            self.username = username_or_uid
            self.uid = None
        elif isinstance(username_or_uid, int):
            self.uid = username_or_uid
            self.username = None

    def set_http_client(self, http_client: Optional[ProtoHttpClient] = None):
        self._http_client = http_client

    def get_http_client(self, http_client: Optional[ProtoHttpClient] = None) -> ProtoHttpClient:
        if http_client:
            return http_client
        if self._http_client:
            return self._http_client()
        else:
            raise RuntimeError(
                '[OdooRPC] get_http_client: no http_client callable or awaitable has been set.')

    def login(self, *, http_client: Optional[ProtoHttpClient] = None) -> int or None:
        # If uid is already set, this method is a noop
        if self.uid is not None:
            return None

        self.uid = odoo_jsonrpc_result(http_client=self.get_http_client(http_client),
                                       service='common',
                                       method='login',
                                       args=[self.database,
                                             self.username, self.password],
                                       ensure_instance_of=int)
        self.username = None
        return self.uid

    def read(self, *,
             model_name: str,
             ids: List[int],
             fields: Optional[List[str]] = None,
             http_client: Optional[ProtoHttpClient] = None) -> List[dict]:

        http_client = self.get_http_client(http_client)

        return self.execute_kw(method='read',
                               model_name=model_name,
                               ids=[ids],
                               kwargs=build_execute_kw_kwargs(fields=fields),
                               http_client=http_client,
                               ensure_instance_of=list)

    def search(self, *,
               model_name: str,
               domain: list,
               offset: Optional[int] = None,
               limit: Optional[int] = None,
               order: Optional[str] = None,
               http_client: Optional[ProtoHttpClient] = None) -> List[int]:

        return self.execute_kw(method='search',
                               model_name=model_name,
                               domain=[domain],
                               kwargs=build_execute_kw_kwargs(
                                   offset=offset, limit=limit, order=order),
                               http_client=http_client,
                               ensure_instance_of=list)

    def search_read(self, *,
                    model_name: str,
                    domain: list,
                    fields: Optional[List[str]] = None,
                    offset: Optional[int] = None,
                    limit: Optional[int] = None,
                    order: Optional[str] = None,
                    http_client: Optional[ProtoHttpClient] = None) -> List[dict]:

        return \
            self.execute_kw(method='search_read',
                            model_name=model_name,
                            domain=[domain],
                            kwargs=build_execute_kw_kwargs(
                                fields=fields, offset=offset, limit=limit, order=order),
                            http_client=http_client,
                            ensure_instance_of=list)

    def search_count(self, *,
                     model_name: str,
                     domain: list,
                     http_client: Optional[ProtoHttpClient] = None) -> int:

        return self.execute_kw(method='search_count',
                               model_name=model_name,
                               domain=[domain],
                               http_client=http_client,
                               ensure_instance_of=int)

    def execute_kw(self, *,
                   method: str,
                   model_name: str,
                   domain: Optional[list] = None,
                   ids: Optional[List[List[int]]] = None,
                   kwargs: Optional[dict] = None,
                   http_client: Optional[ProtoHttpClient] = None,
                   ensure_instance_of: Optional[bool or type] = None) -> Any:

        http_client = self.get_http_client(http_client)

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

        if ensure_instance_of is not None:
            if ensure_instance_of is True:
                ensure_instance_of = None

            return odoo_jsonrpc_result(http_client=http_client,
                                       service='object',
                                       method='execute_kw',
                                       args=args,
                                       ensure_instance_of=ensure_instance_of)
        else:
            return odoo_jsonrpc(http_client=http_client,
                                service='object',
                                method='execute_kw',
                                args=args)
