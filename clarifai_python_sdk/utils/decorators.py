# SYSTEM
from functools import wraps
from subprocess import call

# ERRORS
from clarifai_python_sdk.errors import UserError


def handle_exception(fn: callable) -> callable:

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return e.message

    return wrapper


def set_limits(limits: dict) -> callable:
    """
    Decorator that wraps a class function attribute to check if limits of arguments passed to the
    function has been respected.

    Args:
        limits (dict) Should look like...
            {'inputs': (128, 1), 'per_page': (10, 2)}  
    """

    def inner(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            for limit_key, limit_value in limits.items():
                limit_key_is_kwargs = kwargs.get(limit_key, False)
                
                if limit_key_is_kwargs:
                    retrieved_arg_value = limit_key_is_kwargs
                else:
                    retrieved_arg_value = args[limit_value[1]]

                if len(retrieved_arg_value) > limit_value[0]:
                    raise UserError(f'Endpoints limits exceed "{limit_key}" length should be less or equal than {limit_value[0]}')

            return fn(*args, **kwargs)

        return wrapper
    return inner