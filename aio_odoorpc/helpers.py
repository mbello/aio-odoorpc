from typing import Awaitable, Callable, Dict, Iterable, List, Mapping, Optional, Union
import asyncio


# from Odoo sources
DEFAULT_SERVER_DATE_FORMAT: str = "%Y-%m-%d"
DEFAULT_SERVER_TIME_FORMAT: str = "%H:%M:%S"
DEFAULT_SERVER_DATETIME_FORMAT = f"{DEFAULT_SERVER_DATE_FORMAT} {DEFAULT_SERVER_TIME_FORMAT}"


async def _aio_fields_processor(awaitable: Awaitable,
                                fields: Optional[Iterable] = None,
                                setter__id_fields: Optional[Callable] = None):
    if setter__id_fields is None:
        return await awaitable
    
    id_fields = None
    
    if fields:
        id_fields = [f for f in fields if f.endswith('_id') or f.endswith('_uid')]
        if len(id_fields) == 0:
            return await awaitable
    
    data = await awaitable
    
    if not data:
        return data
    else:
        if not id_fields:
            id_fields = [f for f in data[0].keys() if f.endswith('_id') or f.endswith('_uid')]
            if len(id_fields) == 0:
                return data
    
    for r in data:
        for f in id_fields:
            r[f] = setter__id_fields(r[f])

    return data


def _fields_processor(data: Mapping,
                      fields: Optional[Iterable] = None,
                      setter__id_fields: Optional[Callable] = None):
    if setter__id_fields is None or not data:
        return data
    
    if fields:
        id_fields = [f for f in fields if f.endswith('_id') or f.endswith('_uid')]
        if len(id_fields) == 0:
            return data
    else:
        id_fields = [f for f in data[0].keys() if f.endswith('_id') or f.endswith('_uid')]
        if len(id_fields) == 0:
            return data
    
    for r in data:
        for f in id_fields:
            r[f] = setter__id_fields(r[f])
    
    return data


def setter__id_id_as_int(id: Optional[Union[list, bool]] = None) -> Optional[int]:
    if not id:
        return None
    if isinstance(id, list) and list:
        return id[0] if id else None
    elif isinstance(id, int):
        return id
    else:
        RuntimeError(f'[aio-odoorpc] setter__id_as_int: id of type {type(id)}')


def setter__id_list_of_int(id: Optional[Union[list, bool]] = None) -> Optional[List[int]]:
    return list(id[0]) if id else None


def setter__id_dict_id(id: Optional[Union[list, bool]] = None) -> Optional[Dict[str, int]]:
    return {'id': id[0]} if id else None


def setter__id_list_dict_id(id: Optional[Union[list, bool]] = None) -> Optional[List[Dict[str, int]]]:
    return [{'id': id[0]}] if id else None


