from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from models.user import UserModel
from models.user_info import UserInfoModel
from resources.parsers import RequestParser, parser_argument
from security import jwt_required

router = APIRouter(tags=["user_info"])


class UserInfoParser(RequestParser):
    address: Optional[dict] = parser_argument(
        "This field cannot be left blank!", default=None
    )
    phone: Optional[str] = parser_argument(
        "This field cannot be left blank!", default=None
    )
    email: Optional[str] = parser_argument(
        "This field cannot be left blank!", default=None
    )


@router.get("/user_info/{uuid}")
def get_user_info(uuid: int, current_identity=Depends(jwt_required)):
    info = UserInfoModel.find_by_id(uuid)
    if info:
        return info.json(info.id)
    return JSONResponse(status_code=404, content={"message": "User info not found"})


@router.post("/user_info/{uuid}")
def create_user_info(
    uuid: int, data: UserInfoParser, current_identity=Depends(jwt_required)
):
    if not UserModel.find_by_id(uuid):
        return JSONResponse(status_code=404, content={"message": "User not found"})
    info = UserInfoModel.find_by_id(uuid)
    if info:
        return JSONResponse(
            status_code=400, content={"message": "User info already exists"}
        )
    info = UserInfoModel(uuid, **data.model_dump())
    try:
        info.save_to_db()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "An error occurred inserting user info."},
        )
    return {"message": "User info created successfully."}


@router.delete("/user_info/{uuid}")
def delete_user_info(uuid: int, current_identity=Depends(jwt_required)):
    info = UserInfoModel.find_by_id(uuid)
    if info:
        info.delete_from_db()
        return {"message": "User info deleted."}
    return JSONResponse(status_code=404, content={"message": "User info not found."})


@router.put("/user_info/{uuid}")
def update_user_info(
    uuid: int, data: UserInfoParser, current_identity=Depends(jwt_required)
):
    info = UserInfoModel.find_by_id(uuid)
    if info:
        info.street = data.address["street"]
        info.city = data.address["city"]
        info.home_number = data.address["home_number"]
        info.phone = data.phone
        info.email = data.email
    else:
        return JSONResponse(
            status_code=404, content={"message": "User info not found."}
        )
    info.save_to_db()
    return {"message": "User info updated successfully."}
