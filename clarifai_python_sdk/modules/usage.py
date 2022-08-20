# SYSTEM
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

# PACKAGE
from clarifai_python_sdk.response import ResponseWrapper
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest

# PACKAGES
from collections import OrderedDict

# OTHERS
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes

# TYPES
from typing import List, Union

from tests import data

# DEV IMPORTS
if os.environ.get('CLARIFAI_PYTHON_SDK__DEV'):
    import pysnooper


DEFAULT_TEMPLATE = 'last_month'
OPS_CATEGORY_RELATED_TO_MODELS = ('model-predict')


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
    ):
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
        
        is_success = False
        clarifai_status_code = None
        clarifai_error_description = None
        usage_data_dict = {
            'by_ops_category': {},
            'total_ops': 0
        }

        response_object = self._request_historical_usage(**kwargs).response

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code: int = response_object.status_code
            clarifai_error_description: str = response_object.details or response_object.description
        
        else:
            is_success = True
            usages: List[dict] = response_object.dict.get('usage')
            
            for usage in usages:
                category_id: str = usage['category_id']
                value: int       = usage.get('value') or 0

                usage_data_dict['by_ops_category'][category_id] = value if not usage_data_dict['by_ops_category'].get(category_id) \
                    else usage_data_dict['by_ops_category'][category_id] + value
                
                if category_id in OPS_CATEGORY_RELATED_TO_MODELS:
                    if not usage_data_dict.get('by_models'): usage_data_dict['by_models'] = {}
                    model_id: str = usage.get('model_id')
                    usage_data_dict['by_models'][model_id] = value if not usage_data_dict['by_models'].get(model_id) \
                        else usage_data_dict['by_models'][model_id] + value
                
                usage_data_dict['total_ops'] += value

            ordered_usage_date_dict = OrderedDict(usage_data_dict)
            ordered_usage_date_dict.move_to_end('total_ops')
            usage_data_dict = ordered_usage_date_dict

        response_schema = {
            'status': {
                'code': clarifai_status_code if clarifai_status_code is not None else ClarifaiStatusCodes.SUCCESS,
                **({'description': clarifai_error_description} if clarifai_error_description is not None else {})
            },
            **({'usage': usage_data_dict} if is_success else {}),
            **({'timeframe': self._get_templates(template) \
                if start_date is None and end_date is None \
                    else {'start_date': start_date, 'end_date': end_date}} \
                        if is_success else {}
            )
        }

        return ResponseWrapper(self.params, response_dict=response_schema)
    
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

    def historical_usage_per_apps(
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

        clarifai_error_description = None
        clarifai_status_code       = None
        is_success = False
        per_apps   = {}

        response_object: ResponseWrapper = self._request_historical_usage(broken_down_per_app=True, **kwargs).response

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code = response_object.status_code
            clarifai_error_description = response_object.details or response_object.description

        else:
            is_success = True
            usages: List[dict] = response_object.dict['usage']

            for usage in usages:
                app_id: str      = usage['app_id']
                category_id: str = usage['category_id']
                value            = usage.get('value') or 0

                if per_apps.get(app_id) is None:
                    per_apps[app_id] = {
                        'by_ops_category': {},
                        'total_ops': 0
                    }
                else:
                    app_dict: dict = per_apps[app_id]

                    app_dict['by_ops_category'][category_id] = value \
                        if app_dict['by_ops_category'].get(category_id) is None \
                            else app_dict['by_ops_category'][category_id] + value

                    if category_id in OPS_CATEGORY_RELATED_TO_MODELS:
                        model_id = usage['model_id']

                        app_dict['by_models'] = {} if app_dict.get('by_models') is None else app_dict['by_models']
                        app_dict['by_models'][model_id] = value \
                            if app_dict['by_models'].get(model_id) is None \
                                else app_dict['by_models'][model_id] + value
                    
                    app_dict['total_ops'] = app_dict['total_ops'] + value

                    # Putting "total_ops" keys at the end of each app_id dict
                    ordered_app_dict = OrderedDict(app_dict)
                    ordered_app_dict.move_to_end('total_ops')
                    per_apps[app_id] = ordered_app_dict

        response_schema = {
            'status': {
                'code': clarifai_status_code if clarifai_status_code is not None else ClarifaiStatusCodes.SUCCESS,
                **({'description': clarifai_error_description} if clarifai_error_description is not None else {})
            },
            **({'usage_per_apps': per_apps} if is_success else {}),
            **({'timeframe': self._get_templates(template) \
                if start_date is None and end_date is None \
                    else {'start_date': start_date, 'end_date': end_date}} \
                        if is_success else {}
            )
        }

        return ResponseWrapper(self.params, response_dict=response_schema)

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
        
        is_success = False
        clarifai_status_code = None
        clarifai_error_description = None
        usage_data_dict = {}

        response_object = self._request_historical_usage(**kwargs).response

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code: int = response_object.status_code
            clarifai_error_description: str = response_object.details or response_object.description
        
        else:
            is_success = True
            usages: List[dict] = response_object.dict.get('usage')

            for usage in usages:
                date: str        = usage['date']
                category_id: str = usage['category_id']
                model_id: Union[str, None] = usage.get('model_id')
                value            = usage.get('value') or 0

                if not usage_data_dict.get(date):
                    usage_data_dict[date] = {
                        'by_ops_category': {category_id: value},
                        **({'by_models': {model_id: value}} if category_id in OPS_CATEGORY_RELATED_TO_MODELS else {}),
                        'total_ops': 0
                    }
                else:
                    date_dict = usage_data_dict[date]

                    date_dict['by_ops_category'][category_id] = value if not date_dict['by_ops_category'].get(category_id) \
                        else date_dict['by_ops_category'].get(category_id) + value

                    if category_id in OPS_CATEGORY_RELATED_TO_MODELS:
                        usage_dict_has_model_key: Union[dict, None] = date_dict.get('by_models')

                        if not usage_dict_has_model_key: 
                            date_dict['by_models'] = {}

                        date_dict['by_models'][model_id] = value if not date_dict.get('by_models', {}).get(model_id) else date_dict.get('by_models', {}).get(model_id) + value
                
                usage_data_dict[date]['total_ops'] += value
                # ensure "total_ops" is always the last key of each date_dict
                ordered_usage_data_dict = OrderedDict(usage_data_dict[date])
                ordered_usage_data_dict.move_to_end('total_ops')
                usage_data_dict[date] = ordered_usage_data_dict

        response_schema = {
            'status': {
                'code': clarifai_status_code if clarifai_status_code is not None else ClarifaiStatusCodes.SUCCESS,
                **({'description': clarifai_error_description} if clarifai_error_description is not None else {})
            },
            **({'usage_by_date': usage_data_dict} if is_success else {}),
            **({'timeframe': self._get_templates(template) \
                if start_date is None and end_date is None \
                    else {'start_date': start_date, 'end_date': end_date}} \
                        if is_success else {}
            )
        }

        return ResponseWrapper(self.params, response_dict=response_schema)

    def historical_by_date_and_apps(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = None
    ) -> ResponseWrapper:
        """
        Get historical usage broken down by date and app.
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
        
        is_success = False
        clarifai_status_code = None
        clarifai_error_description = None
        usage_data_dict = {}

        response_object = self._request_historical_usage(broken_down_per_app=True, **kwargs).response

        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code: int = response_object.status_code
            clarifai_error_description: str = response_object.details or response_object.description
        
        else:
            is_success = True
            usages: List[dict] = response_object.dict.get('usage')

            for usage in usages:
                date: str        = usage['date']
                category_id: str = usage['category_id']
                model_id: Union[str, None] = usage.get('model_id')
                app_id: str      = usage.get('app_id')
                value: int       = usage.get('value') or 0

                if not usage_data_dict.get(date):
                    usage_data_dict[date] = {}
                
                if not usage_data_dict.get(date, {}).get(app_id):
                    usage_data_dict[date][app_id] = {}
                
                if not usage_data_dict[date][app_id].get('by_ops_category'):
                    usage_data_dict[date][app_id]['by_ops_category'] = {}
                    
                if not usage_data_dict[date][app_id].get('by_models') and category_id in OPS_CATEGORY_RELATED_TO_MODELS:
                    usage_data_dict[date][app_id]['by_models'] = {}
        
                by_ops_dict = usage_data_dict[date][app_id]['by_ops_category']
                by_ops_dict[category_id] = value if not by_ops_dict.get(category_id) else by_ops_dict.get(category_id) + value

                if category_id in OPS_CATEGORY_RELATED_TO_MODELS:
                    by_models_dict = usage_data_dict[date][app_id]['by_models']
                    by_models_dict[model_id] = value if not by_models_dict.get(model_id) else by_models_dict.get(model_id) + value

        response_schema = {
            'status': {
                'code': clarifai_status_code if clarifai_status_code is not None else ClarifaiStatusCodes.SUCCESS,
                **({'description': clarifai_error_description} if clarifai_error_description is not None else {})
            },
            **({'usage_by_date_and_apps': usage_data_dict} if is_success else {}),
            **({'timeframe': self._get_templates(template) \
                    if None in (start_date, end_date) \
                    else {'start_date': start_date, 'end_date': end_date}
                } if is_success else {}
            )
        }

        return ResponseWrapper(self.params, response_dict=response_schema)
    
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

        clarifai_error_description = None
        clarifai_status_code       = None
        is_success = False
        total_ops  = 0
       
        if response_object.status_code != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code = response_object.status_code
            clarifai_error_description = response_object.details or response_object.description

        else:
            is_success = True,
            usages = response_object.dict['usage']

            for usage in usages:
                value = usage.get('value') or 0
                total_ops += value

        response_schema = {
            'status': {
                'code': clarifai_status_code if clarifai_status_code is not None else ClarifaiStatusCodes.SUCCESS,
                **({'description': clarifai_error_description} if clarifai_error_description is not None else {})
            },
            **({'total_ops': total_ops} if is_success else {}),
            **({'timeframe': self._get_templates(template) \
                    if None in (start_date, end_date) \
                    else {'start_date': start_date, 'end_date': end_date}
                } if is_success else {}
            )
        }

        return ResponseWrapper(self.params, response_dict=response_schema)