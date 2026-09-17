import os
import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient
from dotenv import load_dotenv


load_dotenv()


# --------------------------------------------------
# Entra ID Configuration
# --------------------------------------------------

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_ENTRA_CLIENT_ID")

ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

JWKS_URL = (
    f"https://login.microsoftonline.com/{TENANT_ID}"
    "/discovery/v2.0/keys"
)

EXPECTED_SCOPE = "access_as_user"


# --------------------------------------------------
# Security
# --------------------------------------------------

security = HTTPBearer()

jwks_client = PyJWKClient(JWKS_URL)


# --------------------------------------------------
# Validate Entra Access Token
# --------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=ISSUER
        )

        scopes = payload.get("scp", "").split()

        if EXPECTED_SCOPE not in scopes:
            raise HTTPException(
                status_code=403,
                detail="Required API scope is missing."
            )

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token has expired."
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Entra ID access token."
        )


# --------------------------------------------------
# Check Application Role
# --------------------------------------------------

def require_role(required_role):

    def check_role(
        user=Depends(get_current_user)
    ):

        roles = user.get("roles", [])

        if required_role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"{required_role} role is required."
            )

        return user

    return check_role