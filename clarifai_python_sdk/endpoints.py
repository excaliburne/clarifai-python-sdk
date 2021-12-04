def build_advanced_url(*args):
    return ''.join(args)


ENDPOINTS = {
    'apps': {
        'list': lambda user_id: f'/v2/users/{user_id}/apps'
    },

    'models': {
        'predict': lambda model: model['model_version_id'] and '/v2/models/' + model['model_id'] + '/versions/{version_id}/outputs' or '/v2/models/' + model['model_id'] + '/outputs'
    },

    'inputs': {
        'post': '/v2/inputs',
        'get': lambda user_data_object: '/v2/users/' + user_data_object['user_id'] + '/apps/' + user_data_object['app_id'] + '/inputs'
    },

    'concepts': {
        'list': lambda user_data_object: build_advanced_url('/v2/users/', user_data_object['user_id'], '/apps/', user_data_object['app_id'], '/concepts?page=1&per_page=500')
    }
    
}