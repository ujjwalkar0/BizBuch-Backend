from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException

import logging

logger = logging.getLogger(__name__)

class AppException(APIException):
    def __init__(self, error, status_code=400):
        self.status_code = status_code

        if hasattr(error, "code") and hasattr(error, "message"):
            self.detail = {
                "code": error.code,
                "message": error.message
            }
        else:
            self.detail = error

def custom_exception_handler(exc, context):

    # ✅ FIX: handle AppException FIRST (ADD THIS BLOCK)
    if isinstance(exc, AppException):
        return Response({
            "success": False,
            "data": None,
            "error": exc.detail,
            "meta": None
        }, status=exc.status_code)

    # 🔽 KEEP YOUR EXISTING CODE BELOW
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data

        # Case 1: Standard DRF error with "detail"
        if isinstance(errors, dict) and "detail" in errors:
            detail = errors["detail"]
            code = getattr(detail, "code", "ERROR").upper()
            message = str(detail)

            return Response({
                "success": False,
                "data": None,
                "error": {
                    "code": code,
                    "message": message
                },
                "meta": None
            }, status=response.status_code)

        # Case 2: Validation errors (KEEP STRUCTURE)
        if isinstance(errors, dict):
            return Response({
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": errors
                },
                "meta": None
            }, status=response.status_code)

        # Case 3: Fallback
        return Response({
            "success": False,
            "data": None,
            "error": {
                "code": "ERROR",
                "message": str(errors)
            },
            "meta": None
        }, status=response.status_code)

    # 🚨 Unhandled exceptions (500)
    logger.exception("Unhandled exception", exc_info=exc)

    return Response({
        "success": False,
        "data": None,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        },
        "meta": None
    }, status=500)

# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)

#     if response is not None:
#         errors = response.data

#         # Case 1: Standard DRF error with "detail"
#         if isinstance(errors, dict) and "detail" in errors:
#             detail = errors["detail"]
#             code = getattr(detail, "code", "ERROR").upper()
#             message = str(detail)

#             return Response({
#                 "success": False,
#                 "data": None,
#                 "error": {
#                     "code": code,
#                     "message": message
#                 },
#                 "meta": None
#             }, status=response.status_code)

#         # Case 2: Validation errors (KEEP STRUCTURE)
#         if isinstance(errors, dict):
#             return Response({
#                 "success": False,
#                 "data": None,
#                 "error": {
#                     "code": "VALIDATION_ERROR",
#                     "message": errors
#                 },
#                 "meta": None
#             }, status=response.status_code)

#         # Case 3: Fallback
#         return Response({
#             "success": False,
#             "data": None,
#             "error": {
#                 "code": "ERROR",
#                 "message": str(errors)
#             },
#             "meta": None
#         }, status=response.status_code)

#     # 🚨 Unhandled exceptions (500)
#     logger.exception("Unhandled exception", exc_info=exc)

#     return Response({
#         "success": False,
#         "data": None,
#         "error": {
#             "code": "INTERNAL_SERVER_ERROR",
#             "message": "An unexpected error occurred. Please try again later."
#         },
#         "meta": None
#     }, status=500)