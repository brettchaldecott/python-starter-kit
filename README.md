# Kinde Python Starter Kit

A Flask application demonstrating integration with Kinde Authentication and Management API.

## Features

- User authentication (login, register, logout)
- User profile management
- Organization management
- Feature flags
- Management API integration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Kinde account and application

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd python-starter-kit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Kinde configuration:
```env
# Site Configuration
SITE_HOST=127.0.0.1
SITE_PORT=5000

# Kinde Configuration
KINDE_ISSUER_URL=https://your-subdomain.kinde.com
KINDE_CLIENT_ID=your-client-id
KINDE_CLIENT_SECRET=your-client-secret
KINDE_GRANT_TYPE=authorization_code
KINDE_CODE_VERIFIER=your-code-verifier

# Management API Configuration
KINDE_MGMT_API_CLIENT_ID=your-management-api-client-id
KINDE_MGMT_API_CLIENT_SECRET=your-management-api-client-secret

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=True
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

## Configuration

### Environment Variables

- `SITE_HOST`: Host address for the Flask application
- `SITE_PORT`: Port number for the Flask application
- `KINDE_ISSUER_URL`: Your Kinde domain URL
- `KINDE_CLIENT_ID`: Your Kinde application client ID
- `KINDE_CLIENT_SECRET`: Your Kinde application client secret
- `KINDE_GRANT_TYPE`: OAuth grant type (authorization_code or authorization_code_with_pkce)
- `KINDE_CODE_VERIFIER`: Code verifier for PKCE (required if using PKCE)
- `KINDE_MGMT_API_CLIENT_ID`: Kinde Management API client ID
- `KINDE_MGMT_API_CLIENT_SECRET`: Kinde Management API client secret
- `FLASK_SECRET_KEY`: Secret key for Flask session encryption
- `FLASK_DEBUG`: Enable/disable Flask debug mode

## Project Structure

```
python-starter-kit/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── templates/         # HTML templates
    ├── home.html
    ├── details.html
    ├── helpers.html
    ├── api_demo.html
    └── errors/
        ├── 404.html
        └── 500.html
```

## Security Considerations

- Never commit the `.env` file to version control
- Keep your client secrets secure
- Use HTTPS in production
- Regularly update dependencies
- Follow security best practices for session management

## License

This project is licensed under the MIT License - see the LICENSE file for details.
