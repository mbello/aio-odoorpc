from typing import overload, Any, Callable, List, Literal, Optional, Tuple, Union
from aio_odoorpc_base.helpers import execute_kwargs
from aio_odoorpc_base.aio import execute_kw, login
from aio_odoorpc_base.protocols import T_AsyncHttpClient
from aio_odoorpc.helpers import _aio_fields_processor
from aio_odoorpc import helpers
import asyncio


# Domain operators.
DOMAIN_OPERATORS = ('!', '|', '&')
TERM_OPERATORS = ('=', '!=', '<>', '<=', '<', '>', '>=', '=?', '=like', '=ilike', 'like', 'not like', 'ilike',
                  'not ilike', 'in', 'not in', 'child_of', 'parent_of')


T_Domain = List[Union[Literal['!', '|', '&'],
                      Tuple[str, Literal['=', '!=', '<>', '<=', '<', '>', '>=', '=?', '=like',
                                         '=ilike', 'like', 'not like', 'ilike', 'not ilike', 'in',
                                         'not in', 'child_of', 'parent_of'], Any]]]

class AsyncOdooRPC:
    database: str
    username: Optional[str]
    uid: Optional[int]
    password: str
    http_client: T_AsyncHttpClient
    url: Optional[str]
    model_name: Optional[str]
    
    def __init__(self, *,
                 database: str,
                 username_or_uid: Union[str, int],
                 password: str,
                 http_client: Optional[T_AsyncHttpClient] = None,
                 url_jsonrpc_endpoint: Optional[str] = None,
                 default_model_name: Optional[str] = None):
        self.database = database
        self.username = username_or_uid if isinstance(username_or_uid, str) else None
        self.uid = username_or_uid if isinstance(username_or_uid, int) else None
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

    @overload
    def set_format_for_id_fields(self,
                                 type: Literal['int'],
                                 id_only: Literal[True],
                                 value_for_empty_id: Any):
        ...

    @overload
    def set_format_for_id_fields(self,
                                 type: Literal['noop', 'tuple', 'dict', 'list_of_dict'],
                                 id_only: bool,
                                 value_for_empty_id: Any):
        ...
    
    def set_format_for_id_fields(self,
                                 type = 'dict',
                                 id_only = False,
                                 value_for_empty_id = False):
        if not isinstance(type, str) \
           or not isinstance(id_only, bool) \
           or type not in ('noop', 'int', 'tuple', 'dict', 'list_of_dict'):
            raise ValueError('set_format_for_id_fields called with invalid parameters')
        
        if type == 'noop' or (type == 'dict' and id_only == False and value_for_empty_id == False):
            self.setter_for__id_fields = None
            return
        
        if type == 'int':
            self.setter_for__id_fields = lambda x:
        elif type == 'tuple':
            self.setter_for__id_fields = helpers.setter__id_tuple_id()
        elif type == 'dict':
            self.setter_for__id_fields = helpers.setter__id_dict_id
        elif type == 'list_of_dict':
            self.setter_for__id_fields = helpers.setter__id_list_dict_id
        

    async def search_read(self, domain: T_Domain, *,
                          fields: Optional[List[str]] = None,
                          offset: Optional[int] = None,
                          limit: Optional[int] = None,
                          order: Optional[str] = None,
                          setter__id_fields: Optional[Callable[[List], Any]] = None,
                          model_name: Optional[str] = None,
                          http_client: Optional[T_AsyncHttpClient] = None) -> List[dict]:
    
        aw = self.execute_kw(method='search_read',
                             args=domain,
                             kwargs=execute_kwargs(fields=fields, offset=offset, limit=limit, order=order),
                             model_name=model_name,
                             http_client=http_client)

        aw = asyncio.create_task(aw)
        await asyncio.sleep(0)
        return await _aio_fields_processor(awaitable=aw, fields=fields, setter__id_fields=setter__id_fields)

    async def read(self, ids: List[int], *,
                   fields: Optional[List[str]] = None,
                   offset: Optional[int] = None,
                   limit: Optional[int] = None,
                   model_name: Optional[str] = None,
                   http_client: Optional[T_AsyncHttpClient] = None) -> List[dict]:
            
        if not isinstance(ids, list):
            raise ValueError('ids must be a list of ids (list of ints)')
        if len(ids) <= 0:
            return list()
        else:
            if offset:
                if offset >= len(ids):
                    return list()
                else:
                    ids = ids[offset:]
            if limit:
                limit = min(limit, len(ids))
                ids = ids[:limit-1]
            
            aw = self.execute_kw(method='read',
                                 args=ids,
                                 kwargs=execute_kwargs(fields=fields),
                                 model_name=model_name,
                                 http_client=http_client)
            aw = asyncio.create_task(aw)
            await asyncio.sleep(0)
            return await _aio_fields_processor(awaitable=aw, fields=fields,
                                               setter__id_fields=self.setter__id_fields)
            
    async def search(self, domain: T_Domain, *,
                     offset: Optional[int] = None,
                     limit: Optional[int] = None,
                     order: Optional[str] = None,
                     count: Optional[bool] = None,
                     model_name: Optional[str] = None,
                     http_client: Optional[T_AsyncHttpClient] = None) -> List[int]:
    
        return await self.execute_kw(method='search',
                                     args=domain,
                                     kwargs=execute_kwargs(offset=offset, limit=limit, order=order,
                                                                    count=count),
                                     model_name=model_name,
                                     http_client=http_client)

    async def search_count(self, domain: T_Domain, *,
                           model_name: Optional[str] = None,
                           http_client: Optional[T_AsyncHttpClient] = None) -> int:
    
        return await self.execute_kw(method='search_count',
                                     args=domain,
                                     model_name=model_name,
                                     http_client=http_client)


    async def copy_data(self, model_name: Optional[str] = None, *,
                        id: int, http_client: Optional[T_AsyncHttpClient] = None):

    async def write(self, *,
                    model_name: Optional[str] = None,
                    ids: List[int],
                    http_client: Optional[T_AsyncHttpClient] = None):


    def __base_args(self, http_client: Optional[T_AsyncHttpClient] = None) -> Tuple:
        http_client = http_client if http_client is not None else self.http_client
        if http_client is None:
            raise RuntimeError('[aio-odoorpc] Error: no http client has been set.')
        return http_client, self.url

    def __base_kwargs(self, model_name):
        model_name = model_name if model_name else self.model_name
    
        if not self.uid:
            raise RuntimeError(f'[aio-odoorpc] Error: uid has not been set. (did you forget to login?)')
        if not model_name:
            raise RuntimeError(f'[aio-odoorpc] Error: model_name has not been set. '
                               f'Either set default_model_name or pass it in the parameter list.')
    
        return {'db': self.database, 'uid': self.uid, 'password': self.password, 'obj': model_name}

    async def login(self, *, http_client: Optional[T_AsyncHttpClient] = None, force: bool = False) -> int or None:
        # If uid is already set, this method is a noop
        if not force and self.uid is not None:
            return None
    
        if self.username is None:
            raise RuntimeError('[aio-odoorpc] Error: invoked login but username is not set.')
    
        self.uid = await login(*self.__base_args(http_client),
                               db=self.database,
                               login=self.username,
                               password=self.password)
        return self.uid

    async def execute_kw(self,
                         method: str,
                         args: Optional[list] = tuple(),
                         kwargs: Optional[dict] = None, *,
                         model_name: Optional[str] = None,
                         http_client: Optional[T_AsyncHttpClient] = None):
        
        return await execute_kw(*self.__base_args(http_client),
                                **self.__base_kwargs(model_name),
                                method=method,
                                args=args,
                                kw=kwargs)
