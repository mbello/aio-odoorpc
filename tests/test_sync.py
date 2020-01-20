import pytest
from aio_odoorpc_base.helpers import odoo_base_url2jsonrpc_endpoint
from aio_odoorpc import OdooRPC
import httpx
import requests
import asyncio


def test_sync_httpx1(url_db_user_pwd: list, benchmark):
    url, db, user, pwd = url_db_user_pwd
    with httpx.Client(base_url=url) as session:
        benchmark(sync_test, '', db, user, pwd, session)


def test_sync_httpx2(url_db_user_pwd: list, benchmark):
    with httpx.Client() as session:
        benchmark(sync_test, *url_db_user_pwd, session)


def test_sync_requests(url_db_user_pwd: list, aio_benchmark):
    with requests.Session() as session:
        aio_benchmark(sync_test, *url_db_user_pwd, session)


def sync_test(url, db, user, pwd, http_client):
    url_json_endpoint = odoo_base_url2jsonrpc_endpoint(odoo_base_url=url)
    odoo = OdooRPC(database=db,
                   username_or_uid=user,
                   password=pwd,
                   http_client=http_client,
                   url_jsonrpc_endpoint=url_json_endpoint)
    odoo.login()
    limit = 10
    fields = ['partner_id', 'date_order', 'amount_total']
    
    kwargs = {
        'model_name': 'sale.order',
        'domain': []}
    
    data1 = odoo.search_read(**kwargs, fields=fields)
    
    count = odoo.search_count(**kwargs)
    
    ids = odoo.search(**kwargs)
    
    del kwargs['domain']
    kwargs['ids'] = ids
    data2 = odoo.read(**kwargs, fields=fields)
    
    assert len(data1) == count
    assert len(ids) == count
    assert len(data2) == count
    
    if 'id' not in fields:
        fields.append('id')
    
    for f in fields:
        for d in data1:
            assert d.get(f)
    
    for f in fields:
        for d in data2:
            assert d.get(f)
    
    ids1 = [d.get('id') for d in data1]
    ids2 = [d.get('id') for d in data2]
    ids.sort()
    ids1.sort()
    ids2.sort()
    
    assert len(ids) == len(ids1) and len(ids) == len(ids2)
    
    data1 = {d.get('id'): d for d in data1}
    data2 = {d.get('id'): d for d in data2}
    
    for i in range(0, len(ids) - 1):
        assert ids[i] == ids1[i] == ids2[i]
        
        for f in fields:
            assert data1[ids[i]][f] == data2[ids[i]][f]
