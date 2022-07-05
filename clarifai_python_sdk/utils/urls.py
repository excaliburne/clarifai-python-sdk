# SYSTEM IMPORTS
import base64, requests, zlib, re 

# UTILS
from clarifai_python_sdk.utils.dicts import delete_keys_from_dict



class Urls:

    def image_url_to_base_64(self, image_url):
        """Converts an image_url to base64 string

        Args:
            image_url (str)

        Returns:
            (string): base64
        """
        return base64.b64encode(requests.get(image_url).content).decode('ascii')
    

    def input_object_to_base64(self, input_object):
        input_url = input_object['data']['image']['url']
        new_dict = delete_keys_from_dict(input_object, 'url')
        new_dict['data']['image']['base64'] = self.image_url_to_base_64(input_url)

        return new_dict