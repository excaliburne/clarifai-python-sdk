def get_dict_by_key_or_return_empty(dictt: dict, key: str):
    dict_to_return = {}
    
    if key in dictt:
        dict_to_return = {
            key: dictt[key]
        }
    
    return dict_to_return


def get_existing_dicts_from_keys(dictt: dict, keys: list):
    dict_to_return = {}

    for key in keys:
        if key in dictt:
            dict_to_return[key] = dictt[key]
    
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