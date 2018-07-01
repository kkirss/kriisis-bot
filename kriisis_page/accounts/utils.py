from rest_framework_jwt.utils import jwt_payload_handler


def hashid_jwt_payload_handler(user):
    payload = jwt_payload_handler(user)
    if "user_id" in payload:
        if type(payload["user_id"]) not in (str, int):
            payload["user_id"] = str(payload["user_id"])
    return payload
