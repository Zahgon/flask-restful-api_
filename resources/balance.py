from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from models.balance import BalanceModel
from models.user import UserModel
from resources.parsers import RequestParser, parser_argument
from security import jwt_required

router = APIRouter(tags=["balance"])


class BalanceParser(RequestParser):
    balance: float = parser_argument("This field cannot be left blank!")


@router.get("/balance/{uuid}")
def get_balance(uuid: int, current_identity=Depends(jwt_required)):
    user_balance = BalanceModel.find_by_id(uuid)
    if user_balance:
        return {
            "message": f"User balance is {user_balance.balance}",
            "balance": user_balance.balance,
        }
    return JSONResponse(
        status_code=404,
        content={"message": "Balance not found. Add money for user."},
    )


@router.post("/balance/{uuid}", status_code=201)
def add_balance(
    uuid: int, data: BalanceParser, current_identity=Depends(jwt_required)
):
    user = UserModel.find_by_id(uuid)
    balance = BalanceModel.find_by_id(uuid)
    if not user:
        return JSONResponse(status_code=404, content={"message": "User not found."})
    if balance:
        balance.balance = data.balance + balance.balance
    else:
        balance = BalanceModel(uuid, **data.model_dump())

    try:
        balance.save_to_db()
    except Exception:
        return JSONResponse(
            status_code=500, content={"message": "An error occurred add balance."}
        )
    return {
        "message": f"User balance has been updated. New balance is "
        f"{balance.balance}",
        "balance": balance.balance,
    }
