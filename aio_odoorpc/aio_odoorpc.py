from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from aio_odoorpc_base.helpers import execute_kwargs
from aio_odoorpc_base.aio import execute_kw, login
from aio_odoorpc_base.protocols import T_AsyncHttpClient
from .helpers import _fields_processor
from aio_odoorpc import helpers

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
    getter_id_fields: Optional[helpers.T_GETTER_ID] = None
    _context: Optional[dict] = None
    _forced_context: Optional[dict] = None
    
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
    
    @property
    def context(self) -> Union[Dict[str, Any], None]:
        return self._context
    
    @context.setter
    def context(self, ctx: Union[Dict[str, Any], None]):
        self.context = ctx
    
    @property
    def forced_context(self) -> Union[Dict[str, Any], None]:
        return self._forced_context
    
    @forced_context.setter
    def forced_context(self, ctx: Union[Dict[str, Any], None]):
        self._forced_context = ctx
    
    def set_format_for_id_fields(self,
                                 fmt: Literal["noop", "int", "dict", "list_of_int",
                                              "list_of_dict", None, False]):
        
        fmt = 'noop' if fmt is False or fmt is None else fmt
        
        opts = {'noop': None,
                'int': helpers.getter_id_as_int,
                'dict': helpers.getter_id_as_dict,
                'list_of_int': helpers.getter_id_as_list_of_int,
                'list_of_dict': helpers.getter_id_as_list_of_dict}
        
        self.getter_id_fields = opts[fmt]

    async def search(self, domain: Optional[T_Domain] = None, *,
                     offset: Optional[int] = None,
                     limit: Optional[int] = None,
                     order: Optional[str] = None,
                     count: Optional[bool] = None,
                     model_name: Optional[str] = None,
                     http_client: Optional[T_AsyncHttpClient] = None) -> List[int]:
    
        return await self.execute_kw(method='search',
                                     args=domain,
                                     kwargs=execute_kwargs(offset=offset, limit=limit,
                                                           order=order, count=count),
                                     model_name=model_name,
                                     http_client=http_client)

    async def search_count(self, domain: Optional[T_Domain] = None, *,
                           model_name: Optional[str] = None,
                           http_client: Optional[T_AsyncHttpClient] = None) -> int:
    
        return await self.execute_kw(method='search_count',
                                     args=domain,
                                     model_name=model_name,
                                     http_client=http_client)

    async def search_read(self, domain: Optional[T_Domain] = None, *,
                          fields: Optional[List[str]] = None,
                          offset: Optional[int] = None,
                          limit: Optional[int] = None,
                          order: Optional[str] = None,
                          model_name: Optional[str] = None,
                          http_client: Optional[T_AsyncHttpClient] = None) -> List[dict]:
        
        data = await self.execute_kw(method='search_read',
                                     args=domain,
                                     kwargs=execute_kwargs(fields=fields, offset=offset, limit=limit, order=order),
                                     model_name=model_name,
                                     http_client=http_client)
        
        return _fields_processor(data=data, fields=fields, getter_id=self.getter_id_fields)
    
    async def read(self, ids: Union[int, List[int]], *,
                   fields: Optional[List[str]] = None,
                   offset: Optional[int] = None,
                   limit: Optional[int] = None,
                   model_name: Optional[str] = None,
                   http_client: Optional[T_AsyncHttpClient] = None) -> List[dict]:
        
        ids = [ids] if isinstance(ids, int) else ids
        
        if not ids:
            return list()
        else:
            if offset:
                if offset >= len(ids):
                    return list()
                else:
                    ids = ids[offset:]
            if limit:
                limit = min(limit, len(ids))
                ids = ids[:limit - 1]
            
            data = await self.execute_kw(method='read',
                                         args=ids,
                                         kwargs=execute_kwargs(fields=fields),
                                         model_name=model_name,
                                         http_client=http_client)
            
            return _fields_processor(data=data, fields=fields, getter_id=self.getter_id_fields)
        
    async def copy_data(self, id: Union[List[int], int], *,
                        default: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
                        model_name: Optional[str] = None,
                        http_client: Optional[T_AsyncHttpClient] = None):
        id = [id] if isinstance(id, int) else id
        default = [default] if isinstance(default, dict) else default
        
        return await self.execute_kw(method='copy_data',
                                     args=id,
                                     kwargs={'default': default},
                                     model_name=model_name,
                                     http_client=http_client)
    
    async def write(self, ids: Union[int, List[int]], vals: Dict[str, Any], *,
                    model_name: Optional[str] = None,
                    http_client: Optional[T_AsyncHttpClient] = None):
        
        ids = [ids] if isinstance(ids, int) else ids
        return await self.execute_kw(method='write',
                                     args=ids,
                                     kwargs={'vals': vals},
                                     model_name=model_name,
                                     http_client=http_client)
    
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
    
    async def login(self, *, http_client: Optional[T_AsyncHttpClient] = None, force: bool = False) -> Optional[int]:
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
        
        if self.forced_context or (self.context and 'context' not in kwargs):
            ctx = kwargs.get('context', self.context)
            ctx = self.forced_context if ctx is None else ctx.update(self.forced_context or {})
            kwargs['context'] = ctx
        
        return await execute_kw(*self.__base_args(http_client),
                                **self.__base_kwargs(model_name),
                                method=method,
                                args=args,
                                kw=kwargs)
