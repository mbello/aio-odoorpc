import pytest
from aio_odoorpc_base.helpers import odoo_base_url2jsonrpc_endpoint
from aio_odoorpc import AsyncOdooRPC
import httpx
import aiohttp
import asyncio


@pytest.mark.asyncio
async def test_async_httpx1(url_db_user_pwd: list, aio_benchmark):
    url, db, user, pwd = url_db_user_pwd
    async with httpx.AsyncClient(base_url=url) as session:
        await async_test('', db, user, pwd, session)
        # aio_benchmark(async_test, '', db, user, pwd, session)


@pytest.mark.asyncio
async def test_async_httpx2(url_db_user_pwd: list, aio_benchmark):
    async with httpx.AsyncClient() as session:
        await async_test(*url_db_user_pwd, session)
        # aio_benchmark(async_test, *url_db_user_pwd, session)


@pytest.mark.asyncio
async def _test_async_aiohttp(url_db_user_pwd: list):
    async with aiohttp.ClientSession() as session:
        await async_test(*url_db_user_pwd, session)


@pytest.mark.asyncio
async def test_async_readme1(url_db_user_pwd: list):
    url, db, user, pwd = url_db_user_pwd

    url_json_endpoint = odoo_base_url2jsonrpc_endpoint(odoo_base_url=url)

    async with httpx.AsyncClient(base_url=url) as session:
        odoo = AsyncOdooRPC(database=db, username_or_uid=user, password=pwd, http_client=session,
                            url_jsonrpc_endpoint=url_json_endpoint)
        await odoo.login()
        try:
            # A default model name has not been set a instantiation time so we should
            # pass the model_name on every invocation. Here it should throw an exception.
            await odoo.search_read()
        except RuntimeError:
            pass
        else:
            assert False, 'Expected an exception to be raised'
        
        # Now with model_name set it should work. Not passing a list of ids
        # turns the read call into a search_read call with an empty domain
        # A missing 'fields' parameter means 'fetch all fields'.
        # Hence this call is very expensive, it fetches all fields for all
        # 'sale.order' records
        all_orders_all_fields = await odoo.search_read(model_name='sale.order', limit=10)
        
        # creates a copy of odoo obj setting default_model_name to 'sale.order'
        sale_order = odoo.new_for_model('sale.order')
        
        # now we do not need to pass model_name and it works!
        all_orders_all_fields2 = await sale_order.search_read(limit=10)
        
        large_orders = sale_order.search_read(domain=[['amount_total', '>', 10000]],
                                              fields=['partner_id', 'amount_total', 'date_order'])


@pytest.mark.asyncio
async def test_bug_return_none(url_db_user_pwd: list):
    url, db, user, pwd = url_db_user_pwd
    url_json_endpoint = odoo_base_url2jsonrpc_endpoint(odoo_base_url=url)
    
    async with httpx.AsyncClient(base_url=url) as session:
        odoo = AsyncOdooRPC(database=db, username_or_uid=user, password=pwd, http_client=session,
                            url_jsonrpc_endpoint=url_json_endpoint)
        await odoo.login()
        
        odoo.set_format_for_id_fields('int')
        test = await odoo.search_read(model_name='sale.order', domain=[], fields=[])
        assert test is not None

    
async def async_test(url, db, user, pwd, http_client):
    url_json_endpoint = odoo_base_url2jsonrpc_endpoint(odoo_base_url=url)
    
    odoo = AsyncOdooRPC(database=db,
                        username_or_uid=user,
                        password=pwd,
                        http_client=http_client,
                        url_jsonrpc_endpoint=url_json_endpoint,
                        default_model_name='sale.order')
    await odoo.login()
    limit = 10
    fields = ['partner_id', 'date_order', 'amount_total']
    
    kwargs = {'domain': []}
    
    data1 = asyncio.create_task(odoo.search_read(**kwargs, fields=fields))
    
    count = asyncio.create_task(odoo.search_count(**kwargs))
    
    ids = asyncio.create_task(odoo.search(**kwargs))
    
    ids = await ids
    del kwargs['domain']
    kwargs['ids'] = ids
    data2 = asyncio.create_task(odoo.read(**kwargs, fields=fields))
    
    count = await count
    data1 = await data1
    data2 = await data2
    
    assert len(data1) == count
    assert len(ids) == count
    assert len(data2) == count
    
    if 'id' not in fields:
        fields.append('id')
    
    for f in fields:
        for d in data1:
            assert f in d
    
    for f in fields:
        for d in data2:
            assert f in d
    
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


@pytest.mark.asyncio
async def test_write(url_db_user_pwd: list):
    url, db, user, pwd = url_db_user_pwd
    url_json_endpoint = odoo_base_url2jsonrpc_endpoint(odoo_base_url=url)
    
    async with httpx.AsyncClient(base_url=url) as session:
        odoo = AsyncOdooRPC(database=db, username_or_uid=user, password=pwd, http_client=session,
                            url_jsonrpc_endpoint=url_json_endpoint, default_model_name='product.template')
        await odoo.login()
        odoo.set_format_for_id_fields('int')
        products = await odoo.search_read(domain=[], fields=['list_price'], limit=10)
    
        new_price = 6.66
    
        await odoo.write(products[0]['id'], {'list_price': new_price})
    
        test = await odoo.read(products[0]['id'], fields=['list_price'])
        assert test[0]['list_price'] == new_price
        
        ids = [p['id'] for p in products]
        
        print(ids)
        
        await odoo.write(ids, {'list_price': new_price})
    
        products = await odoo.read(ids=ids, fields=['list_price'])
        
        assert len(products) == len(ids)
        for p in products:
            assert p['list_price'] == new_price
            
        await odoo.write(ids, {'standard_price': new_price, 'weight': new_price})

        products = await odoo.read(ids=ids, fields=['standard_price', 'weight'])
        assert len(products) == len(ids)
        for p in products:
            assert p['standard_price'] == new_price
            assert p['weight'] == new_price
        