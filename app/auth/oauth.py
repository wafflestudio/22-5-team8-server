from authlib.integrations.starlette_client import OAuth
from app.auth.settings import OAUTH_SETTINGS

oauth = OAuth()

oauth.register(
    name='google',
    client_id=OAUTH_SETTINGS.google_oauth_client_id,
    client_secret=OAUTH_SETTINGS.google_oauth_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)