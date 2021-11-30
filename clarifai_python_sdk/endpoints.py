ENDPOINTS = {
    'apps': {
        'list': lambda user_id: f'/v2/users/{user_id}/apps'
    },

    'models': {
        'predict': lambda model: model['model_version_id'] and '/v2/models/' + model['model_id'] + '/versions/{version_id}/outputs' or '/v2/models/' + model['model_id'] + '/outputs'
    }
}