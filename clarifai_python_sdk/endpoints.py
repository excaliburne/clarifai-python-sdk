ENDPOINTS = {
    'apps':                               '/v2/users/{user_id}/apps',

    'models__predict':                    '/v2/models/{model_id}/versions/{model_version_id}/outputs',
    'models__predict_without_version_id': '/v2/models/{model_id}/outputs',

    'inputs__post':                       '/v2/inputs',
    'inputs__get':                        '/v2/users/{user_id}/apps/{app_id}/inputs',
    'inputs__stream':                     '/v2/users/me/apps/{app_id}/inputs/stream',

    'concepts__list':                     '/v2/users/me/apps/{app_id}/concepts?page={page}&per_page={per_page}'
}