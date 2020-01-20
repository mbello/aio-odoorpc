from typing import List, Optional, Tuple, Union
from aio_odoorpc_base.helpers import build_execute_kw_kwargs
from aio_odoorpc_base import execute_kw, login
from aio_odoorpc_base.protocols import T_HttpClient


class OdooRPC:
    database: str
    username: Optional[str]
    uid: Optional[int]
    password: str
    http_client: T_HttpClient
    model_name: Optional[str]

    def __init__(self, *,
                 database: str,
                 username_or_uid: Union[str, int],
                 password: str,
                 http_client: Optional[T_HttpClient] = None,
                 url_jsonrpc_endpoint: Optional[str] = None,
                 default_model_name: Optional[str] = None):
        self.database = database
        self.username = username_or_uid if isinstance(
            username_or_uid, str) else None
        self.uid = username_or_uid if isinstance(
            username_or_uid, int) else None
        self.password = password
        self.http_client = http_client
        self.url = url_jsonrpc_endpoint if url_jsonrpc_endpoint is not None else ''
        self.model_name = default_model_name

    def __copy__(self):
        username_or_uid = self.uid if self.uid else self.username
        new = type(self)(database=self.database, username_or_uid=username_or_uid,
                         password=self.password, http_client=self.http_client,
                         url_jsonrpc_endpoint=self.url, default_model_name=self.model_name)
        new.username = self.username
        return new

    def new_for_model(self, default_model_name: str):
        new = self.__copy__()
        new.model_name = default_model_name
        return new

    def __base_args(self, http_client: Optional[T_HttpClient] = None) -> Tuple:
        http_client = http_client if http_client is not None else self.http_client
        if http_client is None:
            raise RuntimeError(
                '[aio-aio_odoorpc] Error: no http client has been set.')
        return http_client, self.url

    def __base_kwargs(self, model_name):
        model_name = model_name if model_name else self.model_name

        if not self.uid:
            raise RuntimeError(f'[aio-aio_odoorpc] Error: uid has not been set. (did you forget to login?)')
        if not model_name:
            raise RuntimeError(f'[aio-aio_odoorpc] Error: model_name has not been set. '
                               f'Either set default_model_name or pass it in the parameter list.')

        return {'database': self.database, 'uid': self.uid, 'password': self.password, 'model_name': model_name}

    def login(self, *, http_client: Optional[T_HttpClient] = None, force: bool = False) -> int or None:
        # If uid is already set, this method is a noop
        if not force and self.uid is not None:
            return None

        if self.username is None:
            raise RuntimeError(
                '[aio-aio_odoorpc] Error: invoked login but username is not set.')

        self.uid = login(*self.__base_args(http_client),
                         database=self.database,
                         username=self.username,
                         password=self.password)
        return self.uid

    def read(self, *,
             model_name: Optional[str] = None,
             ids: Optional[List[int]] = None,
             fields: Optional[List[str]] = None,
             order: Optional[int] = None,
             http_client: Optional[T_HttpClient] = None) -> List[dict]:

        if ids is None:
            return self.search_read(model_name=model_name,
                                    fields=fields,
                                    order=order,
                                    http_client=http_client)
        elif not ids:
            return list()
        else:
            return execute_kw(*self.__base_args(http_client),
                              **self.__base_kwargs(model_name),
                              method='read',
                              domain_or_ids=ids,
                              kwargs=build_execute_kw_kwargs(fields=fields))

    def search(self, *,
               model_name: Optional[str] = None,
               domain: list = tuple(),
               offset: Optional[int] = None,
               limit: Optional[int] = None,
               order: Optional[str] = None,
               http_client: Optional[T_HttpClient] = None) -> List[int]:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(model_name),
                          method='search',
                          domain_or_ids=domain,
                          kwargs=build_execute_kw_kwargs(offset=offset, limit=limit, order=order))

    def search_read(self, *,
                    model_name: Optional[str] = None,
                    domain: list = tuple(),
                    fields: Optional[List[str]] = None,
                    offset: Optional[int] = None,
                    limit: Optional[int] = None,
                    order: Optional[str] = None,
                    http_client: Optional[T_HttpClient] = None) -> List[dict]:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(model_name),
                          method='search_read',
                          domain_or_ids=domain,
                          kwargs=build_execute_kw_kwargs(fields=fields, offset=offset,
                                                         limit=limit, order=order))

    def search_count(self, *,
                     model_name: Optional[str] = None,
                     domain: list = tuple(),
                     http_client: Optional[T_HttpClient] = None) -> int:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(model_name),
                          method='search_count',
                          domain_or_ids=domain)
