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