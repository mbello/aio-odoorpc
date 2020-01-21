from typing import Awaitable, Callable, Dict, Iterable, List, Mapping, Optional, Union
import asyncio


async def _aio_fields_processor(awaitable: Awaitable,
                                fields: Optional[Iterable] = None,
                                setter__id_fields: Optional[Callable] = None):
    if setter__id_fields is None:
        return await awaitable
    
    id_fields = None
    
    if fields:
        id_fields = [f for f in fields if f.endswith('_id')]
        if len(id_fields) == 0:
            return await awaitable
    
    res = await awaitable
    
    if not res:
        return res
    else:
        if not id_fields:
            id_fields = [f for f in res[0].keys() if f.endswith('_id')]
            if len(id_fields) == 0:
                return res
    
    for r in res:
        for f in id_fields:
            r[f] = setter__id_fields(r[f])


def _fields_processor(data: Mapping,
                      fields: Optional[Iterable] = None,
                      setter__id_fields: Optional[Callable] = None):
    if setter__id_fields is None or not data:
        return data
    
    if fields:
        id_fields = [f for f in fields if f.endswith('_id')]
        if len(id_fields) == 0:
            return data
    else:
        id_fields = [f for f in data[0].keys() if f.endswith('_id')]
        if len(id_fields) == 0:
            return data
    
    for r in data:
        for f in id_fields:
            r[f] = setter__id_fields(r[f])


def setter__id_id_as_int(id: Optional[Union[list, bool]] = None) -> Optional[int]:
    return id[0] if id else None


def setter__id_list_of_int(id: Optional[Union[list, bool]] = None) -> Optional[List[int]]:
    return list(id[0]) if id else None


def setter__id_dict_id(id: Optional[Union[list, bool]] = None) -> Optional[Dict[str, int]]:
    return {'id': id[0]} if id else None


def setter__id_list_dict_id(id: Optional[Union[list, bool]] = None) -> Optional[List[Dict[str, int]]]:
    return [{'id': id[0]}] if id else None


