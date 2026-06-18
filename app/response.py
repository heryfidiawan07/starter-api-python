from fastapi.responses import JSONResponse


def _body(success: bool, message: str, data=None, meta=None, errors=None) -> dict:
    result: dict = {"success": success, "message": message}
    if data is not None:
        result["data"] = data
    if meta is not None:
        result["meta"] = meta
    if errors is not None:
        result["errors"] = errors
    return result


def ok(message: str, data=None) -> JSONResponse:
    return JSONResponse(content=_body(True, message, data=data), status_code=200)


def ok_paged(message: str, data, meta: dict) -> JSONResponse:
    return JSONResponse(content=_body(True, message, data=data, meta=meta), status_code=200)


def created(message: str, data=None) -> JSONResponse:
    return JSONResponse(content=_body(True, message, data=data), status_code=201)


def bad_request(message: str, errors=None) -> JSONResponse:
    return JSONResponse(content=_body(False, message, errors=errors), status_code=400)


def unauthorized(message: str) -> JSONResponse:
    return JSONResponse(content=_body(False, message), status_code=401)


def forbidden(message: str) -> JSONResponse:
    return JSONResponse(content=_body(False, message), status_code=403)


def not_found(message: str) -> JSONResponse:
    return JSONResponse(content=_body(False, message), status_code=404)


def unprocessable(message: str, errors=None) -> JSONResponse:
    return JSONResponse(content=_body(False, message, errors=errors), status_code=422)


def server_error(message: str) -> JSONResponse:
    return JSONResponse(content=_body(False, message), status_code=500)
