def get_dict_by_key_or_return_empty(_dict: dict, key: str) -> dict:
    dict_to_return = {}
    
    if key in _dict:
        dict_to_return = {
            key: _dict[key]
        }
    
    return dict_to_return


def get_existing_dicts_from_keys(_dict: dict, keys: list) -> dict:
    dict_to_return = {}

    for key in keys:
        if key in _dict:
            dict_to_return[key] = dic_dicttt[key]
    
    return dict_to_return


def delete_keys_from_dict(d, to_delete):
    if isinstance(to_delete, str):
        to_delete = [to_delete]
    if isinstance(d, dict):
        for single_to_delete in set(to_delete):
            if single_to_delete in d:
                del d[single_to_delete]
        for k, v in d.items():
            delete_keys_from_dict(v, to_delete)
    elif isinstance(d, list):
        for i in d:
            delete_keys_from_dict(i, to_delete)
    return d


def delete_none_values(_dict: dict) -> dict:
    """Delete None values recursively from all of the dictionaries"""
    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            delete_none_values(value)
        elif value is None:
            del _dict[key]
        elif isinstance(value, list):
            for v_i in value:
                if isinstance(v_i, dict):
                    delete_none_values(v_i)

    return _dict