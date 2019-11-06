import requests as _requests

try:  # Python 3.5+
    from http import HTTPStatus as _StatusCodes
except ImportError:
    try:  # Python 3
        from http import client as _StatusCodes
    except ImportError:  # Python 2
        import httplib as _StatusCodes

# These response keys are defined in https://tools.ietf.org/id/draft-ietf-oauth-discovery-08.html.
_authorization_endpoint_key = "authorization_endpoint"
_token_endpoint_key = "token_endpoint"


class AuthorizationEndpoints(object):
    """
    A simple wrapper around commonly discovered endpoints used for the PKCE auth flow.
    """
    def __init__(self, auth_endpoint=None, token_endpoint=None):
        self._auth_endpoint = auth_endpoint
        self._token_endpoint = token_endpoint

    @property
    def auth_endpoint(self):
        return self._auth_endpoint

    @property
    def token_endpoint(self):
        return self._token_endpoint


class DiscoveryClient(object):
    """
    Discovers well known OpenID configuration and parses out authorization endpoints required for initiating the PKCE
    auth flow.
    """

    def __init__(self, discovery_url=None):
        self._discovery_url = discovery_url
        self._authorization_endpoints = None

    @property
    def authorization_endpoints(self):
        """
        :rtype: flytekit.clis.auth.discovery.AuthorizationEndpoints:
        """
        return self._authorization_endpoints

    def get_authorization_endpoints(self):
        if self.authorization_endpoints is not None:
            return self.authorization_endpoints
        resp = _requests.get(
            url=self._discovery_url,
        )
        # Follow at most one redirect.
        if resp.status_code == _StatusCodes.FOUND:
            redirect_location = resp.headers['Location']
            if redirect_location is None:
                raise ValueError('Received a 302 but no follow up location was provided in headers')
            resp = _requests.get(
                url=redirect_location,
            )

        response_body = resp.json()
        if response_body[_authorization_endpoint_key] is None:
            raise ValueError('Unable to discover authorization endpoint')

        if response_body[_token_endpoint_key] is None:
            raise ValueError('Unable to discover token endpoint')

        self._authorization_endpoints = AuthorizationEndpoints(auth_endpoint=response_body[_authorization_endpoint_key],
                                                               token_endpoint=response_body[_token_endpoint_key])
        return self.authorization_endpoints