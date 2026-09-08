from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db import session
from models.item import ItemModel
from resources.parsers import RequestParser, parser_argument
from security import jwt_required

router = APIRouter(tags=["item"])
welcome_router = APIRouter(tags=["welcome"])


class ItemParser(RequestParser):
    price: float = parser_argument("This field cannot be left blank!")
    store_id: int = parser_argument("Every item needs a store_id.")
    description: Optional[str] = parser_argument("Item description.", default=None)
    image: Optional[str] = parser_argument("Link to image.", default=None)


@router.get("/item/{name}")
def get_item(name: str, current_identity=Depends(jwt_required)):
    item = ItemModel.find_by_name(name)
    if item:
        return item.json(item.id)
    return JSONResponse(status_code=404, content={"message": "Item not found"})


@router.post("/item/{name}", status_code=201)
def create_item(name: str, data: ItemParser, current_identity=Depends(jwt_required)):
    if ItemModel.find_by_name(name):
        return JSONResponse(
            status_code=400,
            content={"message": "An item with name {} already exists.".format(name)},
        )
    item = ItemModel(name, **data.model_dump())
    try:
        item.save_to_db()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "An error occurred inserting the item."},
        )
    item_id = item.find_by_name(name).id
    return item.json(item_id)


@router.delete("/item/{name}")
def delete_item(name: str, current_identity=Depends(jwt_required)):
    item = ItemModel.find_by_name(name)
    if item:
        item.delete_from_db()
        return {"message": "Item deleted."}
    return JSONResponse(status_code=404, content={"message": "Item not found."})


@router.put("/item/{name}")
def upsert_item(name: str, data: ItemParser, current_identity=Depends(jwt_required)):
    item = ItemModel.find_by_name(name)
    if item:
        item.price = data.price
    else:
        item = ItemModel(name, **data.model_dump())
    item.save_to_db()
    item_id = item.find_by_name(name).id
    return item.json(item_id)


@router.get("/items")
def list_items():
    return {
        "items": list(map(lambda x: x.json(x.id), session.query(ItemModel).all()))
    }


@welcome_router.get("/")
def welcome():
    return {
        "GitHub": "https://github.com/berpress/flask-restful-api",
        "swagger": "https://app.swaggerhub.com/apis-docs/berpress/flask-rest-"
        "api/1.0.0",
    }
