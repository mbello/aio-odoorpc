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

    def __init__(self, *,
                 database: str,
                 username_or_uid: Union[str, int],
                 password: str,
                 http_client: Optional[T_HttpClient] = None,
                 url_jsonrpc_endpoint: Optional[str] = None):
        self.database = database
        self.username = username_or_uid if isinstance(
            username_or_uid, str) else None
        self.uid = username_or_uid if isinstance(
            username_or_uid, int) else None
        self.password = password
        self.http_client = http_client
        self.url = url_jsonrpc_endpoint if url_jsonrpc_endpoint is not None else ''

    def __base_args(self, http_client: Optional[T_HttpClient] = None) -> Tuple:
        http_client = http_client if http_client is not None else self.http_client
        if http_client is None:
            raise RuntimeError(
                '[aio-aio_odoorpc] Error: no http client has been set.')
        return http_client, self.url

    def __base_kwargs(self):
        if self.uid:
            return {'database': self.database, 'uid': self.uid, 'password': self.password}
        else:
            raise RuntimeError(f'[aio-aio_odoorpc] Error: uid has not been set. (did you forget to login?)')

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
             model_name: str,
             ids: List[int],
             fields: Optional[List[str]] = None,
             http_client: Optional[T_HttpClient] = None) -> List[dict]:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(),
                          model_name=model_name,
                          method='read',
                          domain_or_ids=ids,
                          kwargs=build_execute_kw_kwargs(fields=fields))

    def search(self, *,
               model_name: str,
               domain: list,
               offset: Optional[int] = None,
               limit: Optional[int] = None,
               order: Optional[str] = None,
               http_client: Optional[T_HttpClient] = None) -> List[int]:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(),
                          method='search',
                          model_name=model_name,
                          domain_or_ids=domain,
                          kwargs=build_execute_kw_kwargs(offset=offset, limit=limit, order=order))

    def search_read(self, *,
                    model_name: str,
                    domain: list,
                    fields: Optional[List[str]] = None,
                    offset: Optional[int] = None,
                    limit: Optional[int] = None,
                    order: Optional[str] = None,
                    http_client: Optional[T_HttpClient] = None) -> List[dict]:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(),
                          method='search_read',
                          model_name=model_name,
                          domain_or_ids=domain,
                          kwargs=build_execute_kw_kwargs(fields=fields, offset=offset,
                                                         limit=limit, order=order))

    def search_count(self, *,
                     model_name: str,
                     domain: list,
                     http_client: Optional[T_HttpClient] = None) -> int:

        return execute_kw(*self.__base_args(http_client),
                          **self.__base_kwargs(),
                          method='search_count',
                          model_name=model_name,
                          domain_or_ids=domain)
