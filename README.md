# Async Odoo RPC client (aio-odoorpc)

This is a fast, simple Odoo RPC client that offers two versions of the same API:
1. AsyncOdooRPC: asynchronous version;
2. OdooRPC: the 'normal', synchronous version.

This package does not intend to implement all the functionality of other odoo rpc modules
like erpeek and odoorpc, because in my experience all higher-level stuff that odoorpc and erppeek
offer, like model instantiation and automatic updates on model field assignment for instance,
always lead to very slow code due to the high number of remote procedure calls that result.

Over time, I felt that it was better to control myself all the RPC invocations and hence I started
to use only the lower level odoorpc methods (execute_kw, read, search, search_read).
Then I wanted it to go even faster and missed an async API to work with the Odoo RPC API. Then
aio-odoorpc was born! ;)

I will keep adding functionality over the coming weeks, right now there are built-in helper functions
only for getting info out (read, search, search_read, search_count), nothing to help creating new
records or updating field values.

## Things to know about this module:
- Asyncio is a python3 thing, so no python2 support;

- Type hints are used everywhere;

- This package uses jsonrpc only (no xmlrpc);

- I chose to base this on httpx instead of aiohttp. If you feel strongly that aiohttp is a better
  option, let's talk about it;

- I am willing to take patches and to add other contributors to this project. Feel free to get in touch,
  the github page is the best place to interact with the project and the project's author;
  
- The synchronous version of the code is generated automatically from the asynchronous code, so at
  least for now the effort to maintain both is minimal.

## Things to know about Odoo RPC API:
- The 'login' call is really only a lookup of the user_id (an int) of the user given a
  database, username and password. If you are using this RPC client over and over in your code,
  maybe even calling from a stateless cloud service, you should consider finding out the user id (uid)
  of the user and pass the uid instead of the username to the constructor of AsyncOdooRPC. This way, 
  you do not need to call the login() method after instantiating the class, saving a RPC call;

- The uid mentioned above is not a session-like id. It is really only the database id of the user
  and it never expires. There is really no 'login' step required to access the Odoo RPC API if you
  know the uid from the beginning;

# Usage

Ok, so let's start with some examples. I will omit the event_loop logic I assume that if you want
an async module you already have that sorted out yourself or through a framework like FastAPI.

All examples below could also be called using the synchronous OdooRPC object, but without the
'await' syntax.

## Class instantiation
```
from aio_odoorpc import AsyncOdooRPC

# if server is listening on default http/https ports, there is no need to specify the port
# in the url. Otherwise, url could be "https://acme.odoo.com:8069" to specify the port number.
# Remember, the method __init__ is never a coroutine, so no await here. But we make no blocking
# calls on the __init__ method.

client = AsyncOdooRPC(url = "https://acme.odoo.com",
                      database = "acme",
                      username_or_uid = "joe@acme.com",
                      password = "my super-difficult-to-guess password")

# login is only required because the client was instantiated with a username rather than a
# user id (uid).
await client.login()

# or we can instantiate the class using a helper. With the helper, there is no need to 
# call the login() method, it takes care of it for you if necessary.
client = await AsyncOdooRPC.from_cfg(host = "acme.odoo.com",
                                     database = "acme",
                                     username = "joe@acme.com",
                                     password = "my super-difficult-to-guess password",
                                     port = 8069,
                                     ssl = True,
                                     ssl_verify = True)
```

## Ok, so now that you have a class instance, let's use it! 

```
    data = await client.search_read(model_name='sale.order',
                                    domain=[['date_confirmed', '>=', '2019-01-01]],
                                    fields=['number, date_confirmed, order_total'],
                                    limit=500)
```
