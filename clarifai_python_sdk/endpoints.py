ENDPOINTS = {
    'apps':                                   '/v2/users/{user_id}/apps',

    'models__predict':                        '/v2/models/{model_id}/versions/{model_version_id}/outputs',
    'models__predict_without_version_id':     '/v2/models/{model_id}/outputs',
    'models__train':                          '/v2/users/me/apps/{app_id}/models/{model_id}/versions',
    'models__list':                           '/v2/users/me/apps/{app_id}/models',
    'models__list_model_types':               '/v2/users/me/apps/{app_id}/models/types',
    'models__get_model_by_id':                '/v2/users/me/apps/{app_id}/models/{model_id}',
    'models__get_model_versions_by_model_id': '/v2/users/me/apps/{app_id}/models/{model_id}/versions',
    'models__get_model_training_inputs':      '/v2/users/me/apps/{app_id}/models/{model_id}/inputs',
    'models__search':                         '/v2/models/searches',

    'inputs__post':                           '/v2/inputs',
    'inputs__get':                            '/v2/users/{user_id}/apps/{app_id}/inputs',
    'inputs__stream':                         '/v2/users/me/apps/{app_id}/inputs/stream',

    'concepts__list':                         '/v2/users/me/apps/{app_id}/concepts?page={page}&per_page={per_page}'
}