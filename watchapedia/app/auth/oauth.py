from authlib.integrations.starlette_client import OAuth
from watchapedia.app.auth.settings import OAUTH_SETTINGS

oauth = OAuth()

oauth.register(
    name='google',
    client_id=OAUTH_SETTINGS.client_id,
    client_secret=OAUTH_SETTINGS.client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)