# SYSTEM IMPORTS
from datetime import datetime

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Usage:
    def __init__(self, params):
        self.params = params
    

    def historical(
        self,
        start_date: str = None,
        end_date: str = None,
        template: str = None,
        broken_down_per_app: bool = None
    ) -> str or dict:  
        """
        Get historical usage for specified timeframe.
        
        If no start, end_date or template is given, this function will return usage
        from last month.

        Args:
            start_date (str, optional)
            end_date (str, optional)
            template (str, optional): Options are...
                - last_day
                - last_week
                - last_month
            broken_down_per_app (bool, optional)

        Returns:
            (json or dict)
        """

        now         = 'T'.join(str(datetime.today()).split(' ')) + 'Z'
        a_month_ago = 'T'.join(str(datetime.today().replace(month=datetime.today().month - 1)).split(' ')) + 'Z'
        
        endpoint = UrlHandler().build(
            'usage__historical', 
            path_variables={**self.params['user_data_object']},
            query_params={
                'start_date': start_date if start_date is not None else a_month_ago,
                'end_date': end_date if end_date is not None else now,
                'broken_down_per_app': broken_down_per_app
            }
        )

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint,
        )

        return self.params['response_object'].returns(response)


