import jwt
import datetime

SECRET_KEY = "IamNick"

def generate_jwt(user_id):

    payload = {
        "user_id": user_id,
        "exp":datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "iat":datetime.datetime.utcnow(),
        "role":"user"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt(token):

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error":"Token has expired"}
    except jwt.InvalidTokenError:
        return {"error":"Invalid token"}
    

if __name__ == "__main__":

    user_id = 12345
    token = generate_jwt(user_id)
    print(f"Generated JWT Token: {token}")

    decoded_data = decode_jwt(token)
    print(f"Decoded Data: {decoded_data}")