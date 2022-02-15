import os
from datetime import datetime, timedelta

import jwt


def generate_invitation_jwt_token(organization):
    dt = datetime.now() + timedelta(hours=12)
    org_uuid_str = organization.get('org_uuid').__str__()
    token = jwt.encode(
        {
            "org_uuid": org_uuid_str,
            "exp": int(dt.strftime("%s")),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256")

    return token


def generate_password_reset_token(email):
    dt = datetime.now() + timedelta(hours=6)
    token = jwt.encode(
        {
            "email": email,
            "exp": int(dt.strftime("%s")),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256")
    return token


def generate_email_verification_token(email):
    dt = datetime.now() + timedelta(hours=6)
    token = jwt.encode(
        {
            "email": email,
            "exp": int(dt.strftime("%s")),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256")
    return token


def decode_token(encoded_jwt):
    return jwt.decode(encoded_jwt, os.getenv('SECRET_KEY'), algorithms=["HS256"])
