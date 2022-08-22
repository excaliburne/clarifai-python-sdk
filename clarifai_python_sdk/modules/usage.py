# SYSTEM
import os
from datetime import datetime
from urllib import response
from dateutil.relativedelta import relativedelta

# PACKAGE
from clarifai_python_sdk.response import ResponseWrapper, BuildResponseSchema
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest

# PACKAGES
from collections import OrderedDict

# OTHERS
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes

# TYPES
from typing import List, Union

# DEV IMPORTS
if os.environ.get('CLARIFAI_PYTHON_SDK__DEV'):
    import pysnooper


DEFAULT_TEMPLATE = 'last_month'
OPS_CATEGORIES_RELATED_TO_MODELS = ('model-predict')


def _ensure_key_is_last(origin_dict: dict, key_to_last: str) -> dict:
    ordered_usage_date_dict = OrderedDict(origin_dict)
    ordered_usage_date_dict.move_to_end(key_to_last)
    
    return ordered_usage_date_dict


class UsageObject:
    """
    A reminder of what a Clarifai usage object looks like...
    {
      'date": '2022-07-22T00:00:00Z",
      'section': 'model_usage',
      'model_id': 'travel-embedding-v1',
      'category_id': 'model-predict',
      'value': 19
    },
    """
    def __init__(self, clarifai_usage_object: dict):
        self.clarifai_usage_object = clarifai_usage_object

        self.value: int = clarifai_usage_object.get('value', 0)
        self.category_id: str = clarifai_usage_object['category_id']
        self.app_id: Union[str, None] = clarifai_usage_object.get('app_id')
        self.model_id: Union[str, None] = clarifai_usage_object.get('model_id')
        self.date: str = clarifai_usage_object['date']


class Usage:
    def __init__(self, params: dict):
        self.params = params
  
    @staticmethod
    def _get_templates(template: str) -> dict:
        template = template or DEFAULT_TEMPLATE

        now             = datetime.today()
        a_day_ago       = now + relativedelta(days=-1)
        a_week_ago      = now + relativedelta(weeks=-1)
        a_month_ago     = now + relativedelta(months=-1)
        three_month_ago = now + relativedelta(months=-3)
        six_month_ago   = now + relativedelta(months=-6)

        end_date_default = {'end_date': 'T'.join(str(now).split(' ')) + 'Z'}

        templates = {
            'last_day': {
                'start_date': 'T'.join(str(a_day_ago).split(' ')) + 'Z',
                **end_date_default
            },
            'last_week': {
                'start_date': 'T'.join(str(a_week_ago).split(' ')) + 'Z',
                **end_date_default
            },
            'last_month': {
                'start_date': 'T'.join(str(a_month_ago).split(' ')) + 'Z',
                **end_date_default
            },
            'last_3_months': {
                'start_date': 'T'.join(str(three_month_ago).split(' ')) + 'Z',
                **end_date_default
            },
            'last_6_months': {
                'start_date': 'T'.join(str(six_month_ago).split(' ')) + 'Z',
                **end_date_default
            },
        }

        return templates[template]

    def _request_historical_usage(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = DEFAULT_TEMPLATE,
        broken_down_per_app: bool = None,
        auth_object: dict = {},
        **kwargs
    ) -> ResponseWrapper:
        """
        Notes:
            - Clarifai API accepts below date formats:
                start_date=2022-07-10T00:00:00Z
                end_date=2022-08-13T00:00:00Z

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional)
            broken_down_per_app (bool, optional)

        Returns:
            (Object) - ResponseWrapper
        """
        template: dict = self._get_templates(template)

        response_object = MakeClarifaiRequest(
            endpoint_index_name="usage__historical",
            method="GET",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
            query_params={
                'start_date': start_date if start_date is not None else template['start_date'],
                'end_date': end_date if end_date is not None else template['end_date'],
                'broken_down_per_app': broken_down_per_app
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    def historical(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = DEFAULT_TEMPLATE,
    ) -> ResponseWrapper:
        """
        Get historical usage (organized data) for specified timeframe.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months

        Returns:
            (Object) - ResponseWrapper

            'status': {
                'code': ...
                ...
            }
            'usage': {
                'by_ops_category': {
                    'stored-input': 18974,
                    'search': 1443,
                    'model-predict': 7118,
                    'model-training-hours': 17
                    ...
                },
                'by_models': {
                    'face-clustering': 94,
                    'face-landmarks': 92,
                    ...
                } # if any models used
            },
            'timeframe': {
                'start_date': '2022-02-20T18:17:01.664646Z',
                'end_date': '2022-08-20T18:17:01.664646Z'
            }
        """
        kwargs: dict = locals()
        kwargs.pop('self')
        
        usage_data_dict = {
            'by_ops_category': {},
            'total_ops': 0
        }

        response_object = self._request_historical_usage(**kwargs).response
        response_schema = BuildResponseSchema()

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            response_schema.update(
                clarifai_status_code=response_object.status_code,
                clarifai_error_description=response_object.details or response_object.description
            )
        else:
            response_schema.update(is_success=True)
            usages: List[dict] = response_object.dict.get('usage')
            
            for usage in usages:
                usage = UsageObject(usage)

                usage_data_dict['by_ops_category'][usage.category_id] = usage.value if not \
                    usage_data_dict['by_ops_category'].get(usage.category_id) \
                        else usage_data_dict['by_ops_category'][usage.category_id] + usage.value
                
                if usage.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                    if not usage_data_dict.get('by_models'): usage_data_dict['by_models'] = {}
                    usage_data_dict['by_models'][usage.model_id] = usage.value if not \
                        usage_data_dict['by_models'].get(usage.model_id) \
                            else usage_data_dict['by_models'][usage.model_id] + usage.value
                
                usage_data_dict['total_ops'] += usage.value

            usage_data_dict: dict = _ensure_key_is_last(usage_data_dict, 'total_ops')

        response_schema.update(
            entries_if_success={
                'usage': usage_data_dict,
                'timeframe': self._get_templates(template) \
                    if start_date is None and end_date is None \
                        else {'start_date': start_date, 'end_date': end_date}
            },
        )

        return ResponseWrapper(self.params, response_dict=response_schema.build())
    
    def historical_feed(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = DEFAULT_TEMPLATE,
        broken_down_per_app: bool = None
    ) -> ResponseWrapper:  
        """
        Get historical feed (unorganized data) usage for specified timeframe.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months
            broken_down_per_app (bool, optional)

        Returns:
            (Object) - ResponseWrapper
        """
        kwargs: dict = locals()
        kwargs.pop('self')
        
        response_object = self._request_historical_usage(**kwargs)

        return response_object

    def historical_by_apps(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = DEFAULT_TEMPLATE
    ) -> ResponseWrapper:
        """
        Get historical usage broken down per app.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months

        Returns:
           (Object) - ResponseWrapper
        """
        kwargs = locals() 
        kwargs.pop('self')

        usage_data_dict = {}

        response_object = self._request_historical_usage(broken_down_per_app=True, **kwargs).response
        response_schema = BuildResponseSchema()

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            response_schema.update(
                clarifai_status_code=response_object.status_code,
                clarifai_error_description=response_object.details or response_object.description
            )
        else:
            response_schema.update(is_success=True)
            usages: List[dict] = response_object.dict['usage']

            for usage in usages:
                usage = UsageObject(usage)

                if usage_data_dict.get(usage.app_id) is None:
                    usage_data_dict[usage.app_id] = {
                        'by_ops_category': {},
                        'total_ops': 0
                    }
                else:
                    app_dict: dict = usage_data_dict[usage.app_id]

                    app_dict['by_ops_category'][usage.category_id] = usage.value \
                        if app_dict['by_ops_category'].get(usage.category_id) is None \
                            else app_dict['by_ops_category'][usage.category_id] + usage.value

                    if usage.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                        app_dict['by_models'] = {} if app_dict.get('by_models') is None else app_dict['by_models']
                        app_dict['by_models'][usage.model_id] = usage.value \
                            if app_dict['by_models'].get(usage.model_id) is None \
                                else app_dict['by_models'][usage.model_id] + usage.value
                    
                    app_dict['total_ops'] = app_dict['total_ops'] + usage.value

                    usage_data_dict[usage.app_id]: dict = _ensure_key_is_last(app_dict, 'total_ops')

        response_schema.update(
            entries_if_success={
                'usage_by_apps': usage_data_dict,
                'timeframe': self._get_templates(template) \
                    if start_date is None and end_date is None \
                        else {'start_date': start_date, 'end_date': end_date}
            }
        )

        return ResponseWrapper(self.params, response_dict=response_schema.build())
    
    def historical_by_apps_and_dates(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = None
    ) -> ResponseWrapper:
        """
        Get historical usage broken down apps then date.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months

        Returns:
           (Object) - ResponseWrapper

            {
                'status': {
                    'code': ...,
                    ...
                },
                'usage_by_apps_and_dates': {
                    "clarifai-toolbox-four": {
                        "2022-07-22T00:00:00Z": {
                            "by_ops_category": {
                                "model-predict": 114,
                                ...
                            },
                            "by_models": {
                                "travel-embedding-v1": 38,
                                "travel-clustering-v1": 38,
                                "travel-recognition-v1": 38,
                                ...
                            },
                            "total_ops": 114
                        },
                        ...
                    },
                    ...
                }
        """

        kwargs = locals() 
        kwargs.pop('self')

        usage_data_dict = {}

        response_object = self._request_historical_usage(broken_down_per_app=True, **kwargs).response
        response_schema = BuildResponseSchema()

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            response_schema.update(
                clarifai_status_code=response_object.status_code,
                clarifai_error_description=response_object.details or response_object.description
            )
        else:
            response_schema.update(is_success=True)
            usages: List[dict] = response_object.dict.get('usage')

            for usage in usages:
                usage = UsageObject(usage)

                if not usage_data_dict.get(usage.app_id):
                    usage_data_dict[usage.app_id] = {}
                
                if not usage_data_dict[usage.app_id].get(usage.date):
                    usage_data_dict[usage.app_id][usage.date] = {}
                
                if not usage_data_dict[usage.app_id][usage.date].get('by_ops_category'):
                    usage_data_dict[usage.app_id][usage.date]['by_ops_category'] = {}

                by_models_dict_exists: Union[dict, None] = usage_data_dict[usage.app_id][usage.date].get('by_models')
                
                if not by_models_dict_exists and usage.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                    usage_data_dict[usage.app_id][usage.date]['by_models'] = {}
                
                if usage.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                    by_models_dict = usage_data_dict[usage.app_id][usage.date]['by_models']
                    by_models_dict[usage.model_id] = usage.value if not by_models_dict.get(usage.model_id) else \
                        by_models_dict[usage.model_id] + usage.value
                
                by_ops_dict = usage_data_dict[usage.app_id][usage.date]['by_ops_category']
                by_ops_dict[usage.category_id] = usage.value if not by_ops_dict.get(usage.category_id) else \
                    by_ops_dict[usage.category_id] + usage.value
                
                usage_data_dict[usage.app_id][usage.date]['total_ops'] = usage.value if not \
                    usage_data_dict[usage.app_id][usage.date].get('total_ops') else \
                        usage_data_dict[usage.app_id][usage.date]['total_ops'] + usage.value
            
        response_schema.update(
            entries_if_success={
                'usage_by_apps_and_dates': usage_data_dict,
                'timeframe': self._get_templates(template) \
                    if start_date is None and end_date is None \
                        else {'start_date': start_date, 'end_date': end_date}
            },
        )

        return ResponseWrapper(self.params, response_dict=response_schema.build())

    def historical_by_date(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = None
    ) -> ResponseWrapper:
        """
        Get historical usage broken down by date.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months

        Returns:
           (Object) - ResponseWrapper

            {
                'status': {
                    'code': ...
                    ...
            },
            "usage_by_date": {
                '2022-07-20T00:00:00Z': {
                    'by_ops_category': {
                        'model-predict': 4
                        ...
                    },
                    'by_models': {
                        'general-image-embedding': 4
                        ...
                    },
                'total_ops': 4
            },
        """
        
        kwargs: dict = locals()
        kwargs.pop('self')
        
        usage_data_dict = {}

        response_object = self._request_historical_usage(**kwargs).response
        response_schema = BuildResponseSchema()

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            response_schema.update(
                clarifai_status_code=response_object.status_code,
                clarifai_error_description=response_object.details or response_object.description
            )
        else:
            response_schema.update(is_success=True)
            usages: List[dict] = response_object.dict.get('usage')

            for usage in usages:
                usage = UsageObject(usage)

                if not usage_data_dict.get(usage.date):
                    usage_data_dict[usage.date] = {
                        'by_ops_category': {usage.category_id: usage.value},
                        **({'by_models': {usage.model_id: usage.value}} if usage.category_id in OPS_CATEGORIES_RELATED_TO_MODELS else {}),
                        'total_ops': 0
                    }
                else:
                    date_dict = usage_data_dict[usage.date]

                    date_dict['by_ops_category'][usage.category_id] = usage.value if not \
                        date_dict['by_ops_category'].get(usage.category_id) \
                            else date_dict['by_ops_category'][usage.category_id] + usage.value

                    if usage.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                        usage_dict_has_model_key: Union[dict, None] = date_dict.get('by_models')

                        if not usage_dict_has_model_key: 
                            date_dict['by_models'] = {}

                        date_dict['by_models'][usage.model_id] = usage.value if not \
                            date_dict.get('by_models', {}).get(usage.model_id) else \
                                date_dict.get('by_models', {})[usage.model_id] + usage.value
                
                usage_data_dict[usage.date]['total_ops'] += usage.value

                usage_data_dict[usage.date] = _ensure_key_is_last(usage_data_dict[usage.date], 'total_ops')

        response_schema.update(
            entries_if_success={
                'usage_by_date': usage_data_dict,
                'timeframe': self._get_templates(template) \
                    if start_date is None and end_date is None \
                        else {'start_date': start_date, 'end_date': end_date}
            }
        )

        return ResponseWrapper(self.params, response_dict=response_schema.build())

    def historical_by_date_and_apps(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = None
    ) -> ResponseWrapper:
        """
        Get historical usage broken down by date then app.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months

        Returns:
           (Object) - ResponseWrapper

            {
                'status': {
                    'code': ...
                    ...
            },
            "usage_by_date_and_apps": {
                "2022-07-21T00:00:00Z": {
                    "FRAlphaFoundDogsV2": {
                        "by_ops_category": {
                            "model-predict": 66
                            ...
                        },
                        "by_models": {
                            "general-image-recognition": 22,
                            "general-image-embedding": 22,
                            "general-clusterering": 22
                            ...
                        }
                    },
                    "clarifai-toolbox-five": {
                        "by_ops_category": {
                            "search": 72
                            ...
                        }
                    }
                    ...
                },
            },
        """
        
        kwargs: dict = locals()
        kwargs.pop('self')
        
        usage_data_dict = {}

        response_object = self._request_historical_usage(broken_down_per_app=True, **kwargs).response
        response_schema = BuildResponseSchema()

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            response_schema.update(
                clarifai_status_code=response_object.status_code,
                clarifai_error_description=response_object.details or response_object.description
            )
        else:
            response_schema.update(is_success=True)
            usages: List[dict] = response_object.dict.get('usage')

            for usage in usages:
                usage_object = UsageObject(usage)

                if not usage_data_dict.get(usage_object.date):
                    usage_data_dict[usage_object.date] = {}
                
                if not usage_data_dict.get(usage_object.date, {}).get(usage_object.app_id):
                    usage_data_dict[usage_object.date][usage_object.app_id] = {}
                
                if not usage_data_dict[usage_object.date][usage_object.app_id].get('by_ops_category'):
                    usage_data_dict[usage_object.date][usage_object.app_id]['by_ops_category'] = {}
                
                by_models_dict_exists: Union[dict, None] = usage_data_dict[usage_object.date][usage_object.app_id].get('by_models')
                    
                if not by_models_dict_exists and usage_object.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                    usage_data_dict[usage_object.date][usage_object.app_id]['by_models'] = {}
        
                by_ops_dict = usage_data_dict[usage_object.date][usage_object.app_id]['by_ops_category']
                by_ops_dict[usage_object.category_id] = usage_object.value if not by_ops_dict.get(usage_object.category_id) else \
                    by_ops_dict.get(usage_object.category_id) + usage_object.value

                if usage_object.category_id in OPS_CATEGORIES_RELATED_TO_MODELS:
                    by_models_dict = usage_data_dict[usage_object.date][usage_object.app_id]['by_models']
                    by_models_dict[usage_object.model_id] = usage_object.value if not by_models_dict.get(usage_object.model_id) else \
                        by_models_dict.get(usage_object.model_id) + usage_object.value

        response_schema.update(
            entries_if_success={
                'usage_by_date_and_apps': usage_data_dict,
                'timeframe': self._get_templates(template) \
                    if None in (start_date, end_date) \
                    else {'start_date': start_date, 'end_date': end_date}
            }
        )

        return ResponseWrapper(self.params, response_dict=response_schema.build())
    
    def total_ops(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = None
    ) -> ResponseWrapper:
        """
        Return the total number of operations used for time period provided.
            - If no start, end_date or template is given, last month usage will be returned.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
                - last_3_months
                - last_6_months

        Returns:
            (Object) - ResponseWrapper
        """

        kwargs = locals()
        kwargs.pop('self')

        response_object = self._request_historical_usage(broken_down_per_app=True, **kwargs).response
        response_schema = BuildResponseSchema()

        total_ops = 0
       
        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            response_schema.update(
                clarifai_status_code=response_object.status_code,
                clarifai_error_description=response_object.details or response_object.description
            )
        else:
            response_schema.update(is_success=True)
            usages = response_object.dict['usage']

            total_ops = sum(map(lambda usage: UsageObject(usage).value, usages))
        
        response_schema.update(
            entries_if_success={
                'total_ops': total_ops,
                'timeframe': self._get_templates(template) \
                    if None in (start_date, end_date) \
                        else {'start_date': start_date, 'end_date': end_date}
            }
        )

        return ResponseWrapper(self.params, response_dict=response_schema.build())