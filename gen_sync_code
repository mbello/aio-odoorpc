#! /usr/bin/env python3

from typing import List, Tuple
import os

files = [('aio_odoorpc/async_odoorpc.py', 'aio_odoorpc/odoorpc.py'),
         ('aio_odoorpc/async_jsonrpc.py', 'aio_odoorpc/jsonrpc.py')]

repl = [('async def', 'def'),
        ('await ', ''),
        ('async with httpx.AsyncClient', 'with httpx.Client'),
        ('AsyncOdooRPC', 'OdooRPC'),
        ('async_jsonrpc', 'jsonrpc')]


def convert_async_to_sync(filename_async: str, filename_sync: str, repl: List[Tuple]):
    with open(filename_async, 'r') as f:
        f_async = f.read()
    
    f_sync = f_async

    for t in repl:
        f_sync = f_sync.replace(t[0], t[1])

    with open(filename_sync, 'w') as f:
        f.write(f_sync)


for f in files:
    convert_async_to_sync(f[0], f[1], repl)
    os.system(f'autopep8 -i {f[1]}')
