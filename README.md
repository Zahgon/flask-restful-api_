# Rest API on FastAPI

[![Tests](https://github.com/berpress/flask-restful-api/actions/workflows/tests.yml/badge.svg)](https://github.com/berpress/flask-restful-api/actions/workflows/tests.yml)
![coverage](badges/succeeded.svg)

A small shop API: users register, authenticate with a JWT, describe themselves,
create stores and items, top up a balance and buy things.

The project uses python 3.12, [FastAPI](https://fastapi.tiangolo.com/),
[SQLAlchemy](https://www.sqlalchemy.org/), [PyJWT](https://pyjwt.readthedocs.io/)
and pytest.

Swagger documentation:
<https://app.swaggerhub.com/apis-docs/berpress/flask-rest-api/1.0.0>

FastAPI also serves the generated OpenAPI schema at `/openapi.json` and an
interactive UI at `/docs`.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
make start
# or
python -m uvicorn run:app --host 0.0.0.0 --port 5000
```

`run:app` is the serving entry point: it imports the application and creates the
SQLite schema (`data.db`) before the first request, exactly like the original
`before_first_request` hook did.

## Test

```bash
make test
# or
pytest tests -q
```

## Docker

```bash
./start.sh
```

## API

All authenticated endpoints expect the header `Authorization: JWT <access_token>`.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | no | Links to the repository and the swagger docs |
| POST | `/register` | no | Create a user |
| POST | `/auth` | no | Exchange username/password for an `access_token` |
| GET | `/user_info/{uuid}` | yes | Read a user's address, phone and email |
| POST | `/user_info/{uuid}` | yes | Create a user's information |
| PUT | `/user_info/{uuid}` | yes | Update a user's information |
| DELETE | `/user_info/{uuid}` | yes | Delete a user's information |
| GET | `/stores` | no | List every store |
| GET | `/store/{name}` | yes | Read one store |
| POST | `/store/{name}` | yes | Create a store |
| DELETE | `/store/{name}` | yes | Delete a store |
| GET | `/items` | no | List every item |
| GET | `/item/{name}` | yes | Read one item |
| POST | `/item/{name}` | yes | Create an item |
| PUT | `/item/{name}` | yes | Create an item, or update its price |
| DELETE | `/item/{name}` | yes | Delete an item |
| GET | `/balance/{uuid}` | yes | Read a user's balance |
| POST | `/balance/{uuid}` | yes | Add money to a user's balance |
| POST | `/pay/{uuid}` | yes | Buy an item with the user's balance |

### Order of operations

Entities depend on each other, so create them in this order:

1. `POST /register` — `{"username": "test", "password": "test"}`
2. `POST /auth` — `{"username": "test", "password": "test"}` returns
   `{"access_token": "..."}`
3. `POST /user_info/1` — `{"address": {"street": "Main", "city": "Boston",
   "home_number": 1}, "phone": "+100000000", "email": "test@test.com"}`
4. `POST /store/cars` — creates the store
5. `POST /item/bmw` — `{"price": 2000.0, "store_id": 1, "description": "car",
   "image": "https://example.com/bmw.png"}`
6. `POST /balance/1` — `{"balance": 2000.0}`
7. `POST /pay/1` — `{"itemId": 1}`
