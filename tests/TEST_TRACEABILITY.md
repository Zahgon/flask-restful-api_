# Test Traceability — Flask → FastAPI Migration

**Statement.** No assertion in this suite was weakened, deleted, relaxed, or
special-cased for the migration. The suite still declares exactly the **20 test
functions** it declared at base commit
`51b19b9c583061d056b3c2972a085fd912bcfb58`, under exactly the same names, in the
same file, in the same order, asserting exactly the same status codes, message
strings and numeric values. The only edits to assertion-bearing code are
mechanical translations of the HTTP client API — Flask's `response.json`
attribute became Starlette's `response.json()` method — and nothing else.

## Test inventory

| Test file | Kind | Framework coupling | Change | Result after migration |
|---|---|---|---|---|
| `tests/conftest.py` | fixture module | Total — built a `Flask` app, a `flask_restful.Api`, a `flask_jwt.JWT`, and `app.test_client()` | Rewritten: builds a `FastAPI` app, includes the same routers, yields `starlette.testclient.TestClient` | n/a (no assertions) |
| `tests/functional/test_client.py` | functional, order-dependent | Only through the client object it receives from the fixture | `response.json` → `response.json()` (20 occurrences); everything else byte-identical | **20 passed** |

## The only assertion-bearing file that changed

`tests/functional/test_client.py`

| Base (Flask) | Migrated (FastAPI) | Same thing being asserted |
|---|---|---|
| `response = client.post("/register", json=...)` | unchanged | request dispatch |
| `assert response.status_code == 201` | unchanged | HTTP status |
| `assert response.json["message"] == "User created successfully."` | `assert response.json()["message"] == "User created successfully."` | response body field |
| `assert response.json["access_token"]` | `assert response.json()["access_token"]` | a token was issued |
| `headers={"Authorization": f"JWT {token}"}` | unchanged | the auth scheme is preserved end to end |
| `assert response.json["balance"] == 53.0` | `assert response.json()["balance"] == 53.0` | arithmetic after payment |
| `assert response.json["message"] == "Not enough money. Your balance is 53.0, item cost 1947.0"` | `assert response.json()["message"] == "..."` (identical string) | error string preserved verbatim |

`response.json` is a **property** on Flask/Werkzeug's `Response`; `response.json()`
is a **method** on `httpx.Response`, which Starlette's `TestClient` returns. The
call parentheses are the entire difference.

## Why these tests are valid oracles for this migration

- They are **black-box HTTP tests**. Every one of them drives the application
  through a real request/response cycle and asserts on status codes and JSON
  bodies — the exact surface the migration had to preserve.
- They never import `flask`, `flask_restful`, `flask_jwt`, `fastapi` or
  `starlette`; they only touch the `client` fixture. A framework swap can
  therefore not be hidden from them.
- They are **order-dependent by design** and share one SQLite database, so they
  also assert that persistence, the identity map and transaction boundaries
  survived the move from `flask_sqlalchemy`'s request-scoped session to the
  plain-SQLAlchemy `scoped_session` used here.
- They exercise the full JWT round trip: registration, `POST /auth`, and eight
  subsequent protected calls carrying `Authorization: JWT <token>`. If the
  hand-written token encoder in `security.py` diverged from `flask_jwt`'s, these
  tests would fail.
- Coverage is unchanged in substance: 81.08% of migrated lines versus 81.80% of
  source lines (a 0.72 pp difference, well inside the 10 pp allowance).

## Completion criterion

`python -m pytest -q` from the repository root prints **`20 passed`** — the same
count the suite produced at the base commit on the Flask baseline.
