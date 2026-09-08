from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db import session
from models.store import StoreModel
from security import jwt_required

router = APIRouter(tags=["store"])


@router.get("/store/{name}")
def get_store(name: str, current_identity=Depends(jwt_required)):
    store = StoreModel.find_by_name(name)
    if store:
        return store.json()
    return JSONResponse(status_code=404, content={"message": "Store not found"})


@router.post("/store/{name}", status_code=201)
def create_store(name: str, current_identity=Depends(jwt_required)):
    if StoreModel.find_by_name(name):
        return JSONResponse(
            status_code=400,
            content={"message": "A store with name '{}' already exists.".format(name)},
        )

    store = StoreModel(name)
    try:
        store.save_to_db()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "An error occurred creating the store."},
        )
    return store.json()


@router.delete("/store/{name}")
def delete_store(name: str, current_identity=Depends(jwt_required)):
    store = StoreModel.find_by_name(name)
    if store:
        store.delete_from_db()

    return {"message": "Store deleted"}


@router.get("/stores")
def list_stores():
    return {"stores": list(map(lambda x: x.json(), session.query(StoreModel).all()))}
