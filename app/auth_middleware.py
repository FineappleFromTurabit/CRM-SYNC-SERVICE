from functools import wraps
# from flask import request, jsonify
from fastapi import Request,HTTPException
import jwt
import os
from dotenv import load_dotenv
from .config import SECRET_KEY
load_dotenv()



ALGORITHM = "HS256"

def auth_required(route_func):

    @wraps(route_func)
    async def wrapper(*args, **kwargs):

        # Get Request instance
        request: Request = kwargs.get("request")

        if request is None:
            # fallback: search in args
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            raise HTTPException(status_code=500, detail="Request not found")

        auth = request.headers.get("Authorization")

        if not auth:
            raise HTTPException(status_code=401, detail="Missing token")

        # Validate Bearer format
        parts = auth.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid auth format")

        token = parts[1]

        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = user  # attach user
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await route_func(*args, **kwargs)

    return wrapper


# def admin_required(f):
#     def wrapper(*args, **kwargs):
#         auth = request.headers.get("Authorization")
#         if not auth:
#             return jsonify({"error": "Missing token"}), 401

#         token = auth.replace("Bearer ", "")
#         print('------------------------------------------------------------------')
#         print('------------------------------------------------------------------')
#         print('------------------------------------------------------------------')
#         print('------------------------------------------------------------------')
#         print("Decoded token:", token)  # Debugging line
#         try:
#             user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#             if user["role"] != "admin" :
#                 return jsonify({"error": "Admin only"}), 403
#             request.user = user
#         except:
#             return jsonify({"error": "Invalid or expired token"}), 401

#         return f(*args, **kwargs)

#     wrapper.__name__ = f.__name__
#     return wrapper