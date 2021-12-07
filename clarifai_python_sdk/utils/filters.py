

class Filters:
    def __init__(self, l: list) -> None:
        self.list = l


    def ids_from_input_objects(self) -> list:
        """Return a list of ids from a list of Clarifai input objects

        - A clarifai input object looks like:

        {
            "id": "51ab80382a26425cb31096c215cadb32",
            "data": {
                "image": {
                    "url": "https://pixabay.com/get/g398b06527ebcc578b8d29622ce467165489ab9f77baab470182fb4c8c5886b62d9d304726553143b8fdcbbf8be8ec2d1c3c5fe36111280ba78ec0d641d85b7eb_1280.jpg",
                    "hosted": {
                        ...
                    },
                    ...
                }
            },
            ...
        },

        Returns:
            (list): List of input ids 
        """
        return list(map(lambda x: x['id'], self.list))