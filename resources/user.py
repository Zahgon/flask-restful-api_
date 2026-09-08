from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.user import UserModel
from resources.parsers import RequestParser, parser_argument

router = APIRouter(tags=["user"])


class UserRegisterParser(RequestParser):
    username: str = parser_argument("This field cannot be blank.")
    password: str = parser_argument("This field cannot be blank.")


@router.post("/register", status_code=201)
def register_user(data: UserRegisterParser):
    if data.username is None or data.password is None:
        return JSONResponse(
            status_code=400,
            content={"message": "Username and password are required fields"},
        )

    find_user = UserModel.find_by_username(data.username)

    if find_user:
        return JSONResponse(
            status_code=400,
            content={
                "message": "A user with that username already exists",
                "uuid": find_user.id,
            },
        )

    user = UserModel(data.username, data.password)
    user.save_to_db()
    user_id = user.find_by_username(data.username).id

    return {"message": "User created successfully.", "uuid": user_id}
