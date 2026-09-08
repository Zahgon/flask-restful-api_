from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from models.balance import BalanceModel
from models.item import ItemModel
from models.user import UserModel
from resources.parsers import RequestParser, parser_argument
from security import jwt_required

router = APIRouter(tags=["pay"])


class PayParser(RequestParser):
    itemId: int = parser_argument("Every item needs a store_id.")


@router.post("/pay/{uuid}")
def pay(uuid: int, data: PayParser, current_identity=Depends(jwt_required)):
    user = UserModel.find_by_id(uuid)
    item = ItemModel.find_by_id(data.itemId)
    balance = BalanceModel.find_by_id(uuid)
    if not user:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    if not item:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    new_balance = balance.balance - item.price
    if new_balance < 0:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Not enough money. Your balance is {balance.balance}, "
                f"item cost {item.price}"
            },
        )
    else:
        balance.balance = balance.balance - item.price
    try:
        balance.save_to_db()
    except Exception:
        return JSONResponse(
            status_code=500, content={"message": "An error occurred buy item"}
        )
    return {
        "message": "Payment was successful",
        "balance": balance.balance,
        "name": item.name,
        "price": item.price,
    }
