# SYSTEM IMPORTS
from datetime import datetime
from dateutil.relativedelta import relativedelta

# PACKAGE
from clarifai_python_sdk.response import ResponseWrapper
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler

# PACKAGES
from collections import OrderedDict

# OTHERS
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes


DEFAULT_TEMPLATE = 'last_month'

class Usage:
    def __init__(self, params):
        self.params = params

    
    @staticmethod
    def _get_templates(template: str):
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
        auth_object: dict = {}
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
        template = self._get_templates(template)

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
        broken_down_per_app: bool = None
    ) -> ResponseWrapper:  
        """
        Get historical usage for specified timeframe.
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
            (Object): ResponseWrapper
        """
        args = locals()
        args.pop('self')
        
        response_object = self._request_historical_usage(**args)

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
           (Object): ResponseWrapper
        """
        args = locals() 
        args.pop('self')

        response = self._request_historical_usage(**args, broken_down_per_app=True).response.dict

        OPS_CATEGORY_RELATED_TO_MODELS = ('model-predict')
        clarifai_error_description = None
        clarifai_status_code       = None
        is_success = False
        per_apps   = {}
       
        if response['status']['code'] != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code = response['status']['code']
            clarifai_error_description = response['status'].get('details') or response['status']['description']

        else:
            is_success = True
            usages = response['usage']

            for usage in usages:
                app_id      = usage['app_id']
                category_id = usage['category_id']
                value       = usage.get('value') or 0

                if per_apps.get(app_id) is None:
                    per_apps[app_id] = {
                        'by_ops_category': {},
                        'total_ops': 0
                    }
                else:
                    app_dict = per_apps[app_id]

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
            (Object): ResponseWrapper
        """

        args = locals()
        del args['self']
        response = self._request_historical_usage(**args, broken_down_per_app=True).response.dict

        clarifai_error_description = None
        clarifai_status_code       = None
        is_success = False
        total_ops  = 0
       
        if response['status']['code'] != ClarifaiStatusCodes.SUCCESS:
            is_success = False
            clarifai_status_code = response['status']['code']
            clarifai_error_description = response['status'].get('details') or response['status']['description']

        else:
            is_success = True,
            usages = response['usage']

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
                if start_date is None and end_date is None \
                    else {'start_date': start_date, 'end_date': end_date}} \
                        if is_success else {}
            )
        }

        return ResponseWrapper(self.params, response_dict=response_schema)