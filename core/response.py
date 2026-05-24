from rest_framework.response import Response
from core.errors import AppError

def success_response(data=None, meta=None, status=200):
    return Response({
        "success": True,
        "data": data,
        "error": None,
        "meta": meta,
    }, status=status)


def error_response(code=None, message=None, status=400):
    return Response({
        "success": False,
        "data": None,
        "error": {"code": code, "message": message},
        "meta": None,
    }, status=status)


def validation_error_response(errors, status=400):
    if "non_field_errors" in errors:
        error = errors["non_field_errors"][0]
    else:
        error = {"code": AppError.VALIDATION_ERROR["code"], "message": errors}

    return error_response(
        code=error["code"],
        message=error["message"],
        status=status
    )