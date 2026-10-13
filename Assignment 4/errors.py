"""Single error shape — RFC 7807 style problem helper."""
from flask import jsonify

def problem(*, type_: str, title: str, status: int, detail: str):
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
    }
    resp = jsonify(body)
    resp.status_code = status
    return resp

# Convenience wrappers
def bad_request(detail: str):
    return problem(type_="https://campuseats.example.com/problems/bad-request",
                   title="Bad Request", status=400, detail=detail)

def not_found(detail: str):
    return problem(type_="https://campuseats.example.com/problems/not-found",
                   title="Not Found", status=404, detail=detail)

def conflict(detail: str):
    return problem(type_="https://campuseats.example.com/problems/conflict",
                   title="Conflict", status=409, detail=detail)

def unprocessable(detail: str):
    return problem(type_="https://campuseats.example.com/problems/unprocessable",
                   title="Unprocessable Entity", status=422, detail=detail)

def bad_gateway(detail: str):
    return problem(type_="https://campuseats.example.com/problems/bad-gateway",
                   title="Bad Gateway", status=502, detail=detail)
