from typing import Any, Callable, Dict, Iterable, List, Literal, Tuple, Optional, Union


DEFAULT_SERVER_DATE_FORMAT: str = "%Y-%m-%d"
DEFAULT_SERVER_TIME_FORMAT: str = "%H:%M:%S"
DEFAULT_SERVER_DATETIME_FORMAT = f"{DEFAULT_SERVER_DATE_FORMAT} {DEFAULT_SERVER_TIME_FORMAT}"

T_ID_FIELD = Union[Tuple[int, str], Literal[False], None]
T_GETTER_ID = Callable[[T_ID_FIELD],
                       Optional[Union[Tuple[int, str],
                                      Literal[False],
                                      int,
                                      List[int],
                                      Dict[Literal["id"], int],
                                      List[Dict[Literal["id"], int]]]]]


def _fields_processor(data: Union[List[Dict[str, Any]], None],
                      fields: Optional[Iterable[str]] = None,
                      getter_id: Optional[T_GETTER_ID] = None):
    if getter_id is None or not data:
        return data

    fields = data[0].keys if fields is None else fields
    
    if fields:
        id_fields: List[str] = [f for f in fields if f.endswith('_id') or f.endswith('_uid')]
    else:
        return data
        
    for r in data:
        for f in id_fields:
            r[f] = getter_id(r[f])
    
    return data


def getter_id_as_int(id_field: T_ID_FIELD) -> Optional[int]:
    if not id_field:
        return None
    elif isinstance(id_field, list) and isinstance(id_field[0], int):
        return id_field[0]
    elif isinstance(id_field, int):
        return id_field
    else:
        RuntimeError(f'[aio-odoorpc] getter_id_as_int: id of type {type(id_field)}')


def getter_id_as_list_of_int(id_field: T_ID_FIELD) -> Optional[List[int]]:
    return [getter_id_as_int(id_field)] if id_field else None


def getter_id_as_dict(id_field: T_ID_FIELD) -> Optional[Dict[str, int]]:
    return {'id': getter_id_as_int(id_field)} if id_field else None


def getter_id_as_list_of_dict(id_field: T_ID_FIELD) -> Optional[List[Dict[str, int]]]:
    return [getter_id_as_dict(id_field)] if id_field else None


