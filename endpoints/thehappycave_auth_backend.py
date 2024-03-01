# _______ BACKEND FOR THE HAPPY CAVE AUTHENTICATION _______ #

import sys, os
from fastapi import HTTPException, Request
from fastapi import APIRouter


import firebase_admin
from firebase_admin import auth, credentials

# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


router = APIRouter()


# _______ HANDLING FIREBASE SERVICE _______ #
# Check if Firebase app has already been initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(
            parent_path,
            "config",
            "the-happy-cave-firebase-adminsdk-slai7-89463d7543.json",
        )
    )
    firebase_admin.initialize_app(cred)


@router.post("/create_user/")
async def create_user(request: Request):
    user_data = await request.json()
    name = user_data.get("name")
    email = user_data.get("email")
    password = user_data.get("password")

    if not all([email, password, name]):
        raise HTTPException(status_code=400, detail="Missing email, password, or name")

    try:
        user_record = auth.create_user(
            display_name=name, email=email, password=password
        )

        return {"uid": user_record.uid, "email": user_record.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
