import pytest
import asyncio
from bs4 import BeautifulSoup
import httpx


@pytest.fixture(scope='package')
def url_db_user_pwd():
    
    return ['https://6978260-14-0.runbot39.odoo.com/', '6978260-14-0-all', 'admin', 'admin']
    with httpx.Client() as client:
        resp = client.get(url='http://runbot.odoo.com/runbot')
    print(resp.text)
    soup = BeautifulSoup(resp.text, features='html.parser')
    tags = soup.find_all("div", class_="slot-container")
    
    urls = []
    
    for tag in tags:
        try:
            if tag.div.find('span', class_="btn-success"):
                url = tag.div.find('a', class_='fa-sign-in')['href']
                return [url, 'all', 'demo', 'demo']
                # url_parts = url.split('?db=')
                # if len(url_parts) == 2:
                    # return [url_parts[0], url_parts[1], 'admin', 'admin']
        except:
            pass
    
    return None


@pytest.yield_fixture(scope='package')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.yield_fixture(scope='function')
def aio_benchmark(benchmark):
    import asyncio
    import threading
    
    class Sync2Async:
        def __init__(self, coro, *args, **kwargs):
            self.coro = coro
            self.args = args
            self.kwargs = kwargs
            self.custom_loop = None
            self.thread = None
        
        def start_background_loop(self) -> None:
            asyncio.set_event_loop(self.custom_loop)
            self.custom_loop.run_forever()
        
        def __call__(self):
            evloop = None
            awaitable = self.coro(*self.args, **self.kwargs)
            # breakpoint()
            try:
                evloop = asyncio.get_running_loop()
            except:
                pass
            if evloop is None:
                return asyncio.run(awaitable)
            else:
                if not self.custom_loop or not self.thread or not self.thread.is_alive():
                    self.custom_loop = asyncio.new_event_loop()
                    self.thread = threading.Thread(target=self.start_background_loop, daemon=True)
                    self.thread.start()
                
                return asyncio.run_coroutine_threadsafe(awaitable, self.custom_loop).result()
    
    def _wrapper(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            benchmark(Sync2Async(func, *args, **kwargs))
        else:
            benchmark(func, *args, **kwargs)
    
    return _wrapper
