# SYSTEM IMPORTS
import base64, requests


class Data:

    @staticmethod
    def image_url_to_base_64(image_url: str) -> str:
        """Converts an image_url to base64 string

        Args:
            image_url (str)

        Returns:
            (string): base64
        """
        return base64.b64encode(requests.get(image_url).content).decode('ascii')
    

