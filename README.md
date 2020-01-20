# aio-odoorpc: an async Odoo RPC client

This package builds upon the lower-level [aio-odoorpc-base](https://github.com/mbello/aio-odoorpc-base) 
adding a AsyncOdooRPC/OdooRPC class as a thin layer that makes for a friendlier interface.

AsyncOdooRPC is asynchronous code, OdooRPC is synchronous.

This package does not intend to implement all the functionality of other odoo rpc modules
like ERPpeek and odoorpc. This is meant to be simpler but equally easy to work with without
trying to be too smart. One of the motivations of this package was to have an alternative to odoorpc
which started getting in my way. For instance, just instantiating a new object in odoorpc may result
in a roundtrip to the remote Odoo server. These unnecessary RPC calls quickly add up and it becomes
too difficult to develop fast software. Also, odoorpc offers no asynchronous interface which
is a huge lost opportunity for code that spends a lot of time waiting on blocking network calls.

## Why use this instead of aio-odoorpc-base

With this interface you can instantiate an object once and then make simpler invocations to remote
methods like `login, read, search, search_read and search_count`. With aio-odoorpc-base, you get only
the lower level `execute_kw` call and must pass a long list of parameters on every invocation.

Also, aio-odoorpc let's you simulate behavior of odoorpc by instantiating the AsyncOdooRPC class with
a `default_model_name` so then all method calls do not need to pass a `model_name`. In this way, you can
easily replace the usage of odoorpc with this object (I know because I migrated a lot of code away 
from odoorpc). Of course, if you are migrating from odoorpc you should take the opportunity to
migrate to async code as well.

## Limitations

Right now there are built-in helper functions only for getting info out (read, search, search_read,
search_count), nothing to help creating new records or updating field values. Those are coming soon.

## Things to know about this module:
- Asyncio is a python3 thing, so no python2 support;

- Type hints are used everywhere;

- This package uses jsonrpc only (no xmlrpc);

- You need to manage the http client yourself. Code is tested with requests (sync),
  httpx (sync and async) and aiohttp (async). See 'Usage' for examples;

- I am willing to take patches and to add other contributors to this project. Feel free to get in touch,
  the github page is the best place to interact with the project and the project's author;
  
- The synchronous version of the code is generated automatically from the asynchronous code, so at
  least for now the effort to maintain both is minimal. Both versions are unit tested.

## Things to know about Odoo's API:
- The `login()` call is really only a lookup of the uid (an int) of the user given a
  database, username and password. If you are using this RPC client over and over in your code,
  maybe even calling from a stateless cloud service, you should consider finding out the user id (uid)
  of the user and pass the uid instead of the username to the constructor of AsyncOdooRPC. This way, 
  you do not need to call the `login()` method after instantiating the class, saving a RPC call;

- The uid mentioned above is not a session-like id. It is really only the database id of the user
  and it never expires. There is really no 'login' step required to access the Odoo RPC API if you
  know the uid from the beginning;

- You will need the url of your Odoo's jsonrpc endpoint. Usually, you will just need to add 'jsonrpc' to
  your odoo url. Example: Odoo web GUI on 'https://acme.odoo.com', JSONRPC will be on 'https://acme.odoo.com/jsonrpc'. 
  However, you may alternatively use one of the three helper methods offered by aio-odoorpc-base.helpers 
  to build the correct url:

```python
def build_odoo_base_url(*, host: str, port: Optional[int] = None, ssl: bool = True, base_url: str = '') -> str:
    ...

def build_odoo_jsonrpc_endpoint_url(*, host: str, port: Optional[int] = None, ssl: bool = True,
                                    base_url: str = '', custom_odoo_jsonrpc_suffix: Optional[str] = None) -> str:
    ...

def odoo_base_url2jsonrpc_endpoint(odoo_base_url: str = '', custom_odoo_jsonrpc_suffix: Optional[str] = None) -> str:
    ...
```
   To import them use
```
from aio_odoorpc_base.helpers import build_odoo_base_url, build_odoo_jsonrpc_endpoint_url, odoo_base_url2jsonrpc_endpoint
```
   Examples:
```python
build_odoo_base_url(host='acme.odoo.com', base_url='testing')
>>>> https://acme.odoo.com/testing
build_odoo_jsonrpc_endpoint_url(host='acme.odoo.com', base_url='testing')
>>>> https://acme.odoo.com/testing/jsonrpc
odoo_base_url2jsonrpc_endpoint('https://acme.odoo.com/testing')
>>>> https://acme.odoo.com/testing/jsonrpc
```

# Usage

#### Note: check the tests folder for more examples

I will omit the event_loop logic I assume that if you want an async module you already have
that sorted out yourself or through a framework like FastAPI.
All examples below could also be called using the synchronous OdooRPC object, but without the
'await' syntax.

```python
from aio_odoorpc import AsyncOdooRPC
import httpx

# If the http_client you are using does not support a 'base_url' parameter like
# httpx does, you will need to pass the 'url_jsonrpc_endpoint' parameter when
# instantiating the AsyncOdooRPC object.
async with httpx.AsyncClient(base_url='https://acme.odoo.com/jsonrpc') as session:
    odoo = AsyncOdooRPC(database='acme_db', username_or_uid='demo',
                        password='demo', http_client=session)
    await odoo.login()

    try:
        # A default model name has not been set a instantiation time so we should
        # pass the model_name on every invocation. Here it should throw an exception.
        await odoo.read()
    except RuntimeError:
        pass
    else:
        assert False, 'Expected an exception to be raised'
    
    # Now with model_name set it should work. Not passing a list of ids
    # turns the read call into a search_read call with an empty domain (so it matches all)
    # A missing 'fields' parameter means 'fetch all fields'.
    # Hence this call is very expensive, it fetches all fields for all
    # 'sale.order' records
    all_orders_all_fields = await odoo.read(model_name='sale.order')
    
    # creates a copy of odoo obj setting default_model_name to 'sale.order'
    sale_order = odoo.new_for_model('sale.order')
    
    # now we do not need to pass model_name and it works!
    all_orders_all_fields2 = await sale_order.read()

    large_orders = sale_order.search_read(domain=[['amount_total', '>', 10000]],
                                          fields=['partner_id', 'amount_total', 'date_order'])
```

# Object instantiation

**The AsyncOdooRPC/OdooRPC object takes these parameters:**
- **database**: string, required. The name of the odoo database
- **username_or_id**: string or int, required. If you pass username (a string), an invocation of the
  method 'login()' will be required to fetch the uid (an int). The uid is what is really needed, 
  if you know both username and uid pass the uid and avoid a login() call which costs a roundtrip
  to the Odoo server;
- **password**: string, required. The user's password. Unfortunately, Odoo's jsonrpc API requires the
  password to be sent on every call. There is no session or token mechanism available as an alternative
  authentication method.
- **http_client**: an http client, optional. If an http client is not set, you will need to pass the
  http_client parameter on every method invocation (when available). Some http clients (e.g. httpx) 
  let you create a session setting the appropriate url as in
  `async with httpx.AsyncClient(base_url='https://acme.odoo.com/jsonrpc as session`
  if you do that on a supporting client, you do not need to pass url, it is already set on the
  http_client. Otherwise, you will need to pass `url_jsonrpc_endpoint` to the constructor.
- **url_jsonrpc_endpoint**: string, optional. The url for your Odoo's server jsonrpc endpoint. You should
  always pass it unless your http_client already knows to which url it should point to.
  You may use aio-odoorpc-base helper methods `build_odoo_base_url, build_odoo_jsonrpc_endpoint_url,
  odoo_base_url2jsonrpc_endpoint` that were described earlier in this README to build this url.
  In short, the jsonrpc endpoint is your odoo instance's base url with a 'jsonrpc' suffix:
  https://acme.odoo.com/jsonrpc
- **default_model_name**: str, optional. This parameter sets the default model_name for all method
  invocations that take an optional method_name parameter. If you set 'model_name' on a method
  invocation it will override this default and follow your order. When you have an instance of
  AsyncOdooRPC/OdooRPC you can create a copy with a different default method_name calling the
  method new_for_model('sale.order.line'). You can use this style to mimic odoorpc's way where
  you can call search, read, search_read on a specific model. 
```python
odoo = AsyncOdooRPC(...)
sale_order = odoo.new_for_model('sale.order')
sale_order_line = odoo.new_for_model('sale.order.line')
partner = sale_order.new_for_model('partner')
```
  Just remember that new_for_method is nothing special, it only sets a default model name on a
  copy of an instance. Making copies of copies is perfectly ok. 

# Dependencies

This package depends on [aio-odoorpc-base](https://github.com/mbello/aio-odoorpc-base) which has no dependency itself.