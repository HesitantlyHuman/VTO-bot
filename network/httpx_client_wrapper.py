#A wrapper of the httpx client allowing for more flexible cookie set parameters (such as secure = True, which is necesssary for the wfm interface)
import httpx
from http.cookiejar import Cookie

class FlexableCookies(httpx.Cookies):
    _default_cookie_params = {
        "version": 0,
        "port": None,
        "port_specified": False,
        "secure": False,
        "expires": None,
        "discard": True,
        "comment": None,
        "comment_url": None,
        "rest": {"HttpOnly": None},
        "rfc2109": False,
    }

    def __init__(self, **kwargs):
        super(FlexableCookies, self).__init__(**kwargs)

    def set(self, name: str, value: str, domain: str = "", path: str = "/", **kwargs) -> None:
        """
        Set a cookie value by name. May optionally include domain and path as well as additional kwargs as approprate.
        """
        cookie_arguments = {
            'name' : name,
            'value' : value,
            'domain' : domain,
            'domain': domain,
            'domain_specified': bool(domain),
            'domain_initial_dot': domain.startswith("."),
            'path': path,
            'path_specified': bool(path),
        }

        cookie_arguments.update(FlexableCookies._default_cookie_params)
        cookie_arguments.update(kwargs)

        cookie = Cookie(**cookie_arguments)
        self.jar.set_cookie(cookie)

class FlexableCookiesClient(httpx.Client):
    def __init__(self, **kwargs):
        super(FlexableCookiesClient, self).__init__(**kwargs)
        self._cookies = FlexableCookies()
