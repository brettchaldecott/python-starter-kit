from datetime import date
import os
import logging
from flask import Flask, url_for, render_template, request, session, redirect
from flask_session import Session
from functools import wraps
import asyncio
from dotenv import load_dotenv

from kinde_sdk import Configuration, ApiException
from kinde_sdk.kinde_api_client import GrantType, KindeApiClient
from kinde_sdk.apis.tags import users_api
from kinde_sdk.model.user import User
from kinde_sdk.auth.oauth import OAuth

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object("config")
Session(app)

# Initialize Kinde clients
def init_kinde_clients():
    """Initialize Kinde API and OAuth clients."""
    # Get configuration from environment variables or config file
    kinde_issuer_url = app.config.get("KINDE_ISSUER_URL")
    client_id = app.config.get("CLIENT_ID")
    client_secret = app.config.get("CLIENT_SECRET")
    grant_type = app.config.get("GRANT_TYPE")
    callback_url = app.config.get("KINDE_CALLBACK_URL")
    
    # Initialize Kinde API client
    configuration = Configuration(host=kinde_issuer_url)
    kinde_api_client_params = {
        "configuration": configuration,
        "domain": kinde_issuer_url,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "callback_url": callback_url,
    }
    
    # Initialize OAuth client
    oauth = OAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=callback_url,
        host=kinde_issuer_url,
        framework="flask"
    )
    
    return oauth

# Initialize clients
oauth = init_kinde_clients()

# Store user clients in app context
user_clients = {}

# Helper functions
def get_authorized_data(user_details):
    """Extract authorized user data from user details."""
    return {
        "id": user_details.get("id"),
        "user_given_name": user_details.get("given_name"),
        "user_family_name": user_details.get("family_name"),
        "user_email": user_details.get("email"),
        "user_picture": user_details.get("picture"),
    }

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route("/")
def index():
    """Home page route."""
    data = {"current_year": date.today().year}
    template = "logged_out.html"
    
    if session.get("user"):
        kinde_data = user_clients.get(session.get("user"))
        if kinde_data:
            template = "home.html"
            data.update(get_authorized_data(kinde_data))
    
    return render_template(template, **data)

@app.route("/api/auth/login")
def login():
    """Login route."""
    val = asyncio.run(oauth.login())
    logger.info(f"Redirecting to login URL: {val}")
    return redirect(val)

@app.route("/api/auth/register")
def register():
    """Register route."""
    val = asyncio.run(oauth.register())
    logger.info(f"Redirecting to register URL: {val}")
    return redirect(val)

@app.route("/api/auth/kinde_callback")
def callback():
    """OAuth callback route."""
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Generate a unique user ID (in a real app, this would be from your user database)
    user_id = f"user_{os.urandom(8).hex()}"
    
    request_result = asyncio.run(oauth.handle_redirect(code=code, state=state, user_id=user_id))
    logger.info(f"OAuth callback successful for user: {user_id}")
    
    data = {"current_year": date.today().year}
    data.update(request_result["user"])
    data["user_token"] = request_result["tokens"]
    
    session["user"] = data.get("id")
    user_clients[data.get("id")] = data
    
    return redirect(url_for("index"))

@app.route("/api/auth/logout")
def logout():
    """Logout route."""
    user_id = session.get("user")
    if user_id:
        user_clients[user_id] = None
        session["user"] = None
        logger.info(f"User logged out: {user_id}")
    
    return redirect(
        kinde_client.logout(redirect_to=app.config.get("LOGOUT_REDIRECT_URL"))
    )

@app.route("/details")
@login_required
def get_details():
    """User details page route."""
    template = "logged_out.html"
    data = {"current_year": date.today().year}

    if session.get("user"):
        kinde_data = user_clients.get(session.get("user"))

        if kinde_data:
            data = {"current_year": date.today().year}
            data.update(get_authorized_data(kinde_data))
            data["access_token"] = kinde_data.get("user_token", {}).get("access_token")

            # Create management API client if credentials are available
            if app.config.get("MGMT_API_CLIENT_ID") and app.config.get("MGMT_API_CLIENT_SECRET"):
                kinde_mgmt_api_client = KindeApiClient(
                    configuration=Configuration(host=app.config["KINDE_ISSUER_URL"]),
                    domain=app.config["KINDE_ISSUER_URL"],
                    client_id=app.config["MGMT_API_CLIENT_ID"],
                    client_secret=app.config["MGMT_API_CLIENT_SECRET"],
                    callback_url=app.config["KINDE_CALLBACK_URL"],
                    grant_type=GrantType.CLIENT_CREDENTIALS,
                )
                # Uncomment to fetch token
                # kinde_mgmt_api_client.fetch_token()
                # data["management_access_token"] = kinde_mgmt_api_client.configuration.access_token
            
            template = "details.html"

    return render_template(template, **data)

@app.route("/helpers")
@login_required
def get_helper_functions():
    """Helper functions page route."""
    template = "logged_out.html"

    if session.get("user"):
        kinde_data = user_clients.get(session.get("user"))
        data = {"current_year": date.today().year}

        if kinde_data:
            data.update(get_authorized_data(kinde_data))
            
            # Get user token
            user_token = kinde_data.get("user_token", {})
            
            # Create Kinde client for helper functions
            configuration = Configuration(host=app.config["KINDE_ISSUER_URL"])
            kinde_client = KindeApiClient(
                configuration=configuration,
                domain=app.config["KINDE_ISSUER_URL"],
                client_id=app.config["CLIENT_ID"],
                client_secret=app.config["CLIENT_SECRET"],
                callback_url=app.config["KINDE_CALLBACK_URL"],
            )
            
            # Set access token
            if user_token.get("access_token"):
                kinde_client.configuration.access_token = user_token["access_token"]
            
            # Get helper data
            data["claim"] = kinde_client.get_claim("iss")
            data["organization"] = kinde_client.get_organization()
            data["user_organizations"] = kinde_client.get_user_organizations()
            data["flag"] = kinde_client.get_flag("theme", "red")
            data["bool_flag"] = kinde_client.get_boolean_flag("is_dark_mode", False)
            data["str_flag"] = kinde_client.get_string_flag("theme", "red")
            data["int_flag"] = kinde_client.get_integer_flag("competitions_limit", 10)
            
            template = "helpers.html"

    return render_template(template, **data)

@app.route("/api_demo")
@login_required
def get_api_demo():
    """API demo page route."""
    template = "api_demo.html"
    data = {"current_year": date.today().year}

    if session.get("user"):
        kinde_data = user_clients.get(session.get("user"))

        if kinde_data:
            data.update(get_authorized_data(kinde_data))

            # Only attempt API call if management API credentials are available
            if app.config.get("MGMT_API_CLIENT_ID") and app.config.get("MGMT_API_CLIENT_SECRET"):
                try:
                    kinde_mgmt_api_client = KindeApiClient(
                        configuration=Configuration(host=app.config["KINDE_ISSUER_URL"]),
                        domain=app.config["KINDE_ISSUER_URL"],
                        client_id=app.config["MGMT_API_CLIENT_ID"],
                        client_secret=app.config["MGMT_API_CLIENT_SECRET"],
                        audience=f"{app.config['KINDE_ISSUER_URL']}",
                        callback_url=app.config["KINDE_CALLBACK_URL"],
                        grant_type=GrantType.CLIENT_CREDENTIALS,
                    )

                    api_instance = users_api.UsersApi(kinde_mgmt_api_client)
                    api_response = api_instance.get_users()
                    data['users'] = [
                        {
                            'first_name': user.get('first_name', ''),
                            'last_name': user.get('last_name', ''),
                            'total_sign_ins': int(user.get('total_sign_ins', 0))
                        }
                        for user in api_response.body['users']
                    ]
                    data['is_api_call'] = True
                    
                except ApiException as e:
                    data['is_api_call'] = False
                    logger.error(f"Exception when calling UsersApi: {e}")
                except Exception as ex:
                    data['is_api_call'] = False
                    logger.error(f"Management API not setup: {ex}")
            else:
                data['is_api_call'] = False
                logger.warning("Management API credentials not configured")

    return render_template(template, **data)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html', current_year=date.today().year), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html', current_year=date.today().year), 500

# Run the application if this file is executed directly
if __name__ == "__main__":
    app.run(
        host=app.config.get("SITE_HOST", "127.0.0.1"),
        port=int(app.config.get("SITE_PORT", 5000)),
        debug=app.config.get("DEBUG", False)
    )