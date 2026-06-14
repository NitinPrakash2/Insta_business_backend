import json
from types import SimpleNamespace
from typing import Any, Optional
from starlette.datastructures import Headers, QueryParams
from starlette.datastructures import URL


class fake_req_obj:
    """
    A fully functional fake FastAPI/Starlette Request object for testing and background use.
    Behaves just like `fastapi.Request`, but runs entirely in memory.
    """

    def __init__(
        self,
        method: str = "GET",
        url: str = "http://testserver/fake",
        headers: Optional[dict[str, str]] = None,
        query_params: Optional[dict[str, str]] = None,
        path_params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        body: Optional[bytes] = None,
        state: Optional[dict[str, Any]] = None,
    ):
        self.method = method
        self.url = URL(url)
        self.headers = Headers(headers or {})
        self.query_params = QueryParams(query_params or {})
        self.path_params = path_params or {}
        self.state = SimpleNamespace(**(state or {}))

        # Store body
        if body is not None:
            self._body = body
        elif json_data is not None:
            self._body = json.dumps(json_data).encode("utf-8")
        else:
            self._body = b""

    # ---- Methods that mimic Starlette Request ----
    async def body(self) -> bytes:
        return self._body

    async def json(self) -> Any:
        if not self._body:
            return None
        try:
            return json.loads(self._body.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    async def form(self):
        """Optionally support multipart/form-data style"""
        from starlette.datastructures import FormData
        return FormData({})

    async def stream(self):
        """Simulate request.stream()"""
        yield self._body

    def __repr__(self):
        return f"<fake_req_obj method={self.method!r} url={self.url!s}>"


"""
==USAGE==
await get_data(fake_req_obj(json_data={"a": 1}, query={"q": "search"}))

# Create fake request
req = fake_req_obj(
    method="POST",
    url="http://localhost/api/items?limit=10",
    headers={"x-api-key": "abc123"},
    query_params={"limit": "10"},
    path_params={"item_id": 42},
    json_data={"name": "T-shirt", "price": 19.99},
    state={"user": "Alice"}
)

"""