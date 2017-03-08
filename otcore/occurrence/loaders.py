from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class BaseLoader:
    def load_source(self, source):
        """
        Hook for returning the loaded source based on the loader type.
        Meant to be overridden for different source types.
        """
        return source

    def validate_source(self, source):
        pass


class URLLoader(BaseLoader):
    """
    URL Loader uses the request library for fetching the source and returns
    the page content.

    It also validates that the source is a valid URL
    """
    def load_source(self, source):
        import requests

        page = requests.get(source)

        return page.content


    def validate_source(self, source):
        validator = URLValidator()
        try:
            validator(source)
        except ValidationError:
            raise ValidationError(
                "{} Requires a valid URL as its source. "
                "{} is not a valid URL"
                .format(self.__class__.__name__, source)
            )

class URLLoaderWithErrorTracking(BaseLoader):
    """
    URL Loader uses the request library for fetching the source and returns
    the page content.

    It also validates that the source is a valid URL
    """

    def load_source(self, source):
        import requests
        from requests import exceptions

        try:
            # page = requests.get(source, allow_redirects=False)
            page = requests.get(source)
        except exceptions.SSLError:
            print("ERROR SSL [Certificate]. For: {}".format(source))
            return ''
        except exceptions.TooManyRedirects:
            print('ERROR: Too Many Redirects. For: {}'.format(source))
            return ''

        return page.content


    def validate_source(self, source):
        validator = URLValidator()
        try:
            validator(source)
        except ValidationError:
            raise ValidationError(
                "{} Requires a valid URL as its source. "
                "{} is not a valid URL"
                .format(self.__class__.__name__, source)
            )



class FileLoader(BaseLoader):
    """
    File loads a source from a file, assuming that it is text based
    For a Byte based file, use the ByteLoader
    """
    def load_source(self, source):
        with open(source, 'r') as f:
            content = f.read()

        return content


class ByteLoader(BaseLoader):
    """
    Similar to the FileLoader, but opens as bytes instead of a string
    """
    def load_source(self, source):
        with open(source, 'rb') as f:
            content = f.read()

        return content
