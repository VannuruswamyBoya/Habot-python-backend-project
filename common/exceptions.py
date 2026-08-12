from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats errors uniformly.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize DRF exceptions
        error_code = getattr(exc, 'default_code', 'error').upper()
        
        # If it's a validation error, the data is usually a dict of fields and lists of errors
        if isinstance(response.data, dict) and 'detail' not in response.data:
            error_code = 'VALIDATION_ERROR'
            message = response.data
        else:
            message = response.data.get('detail', str(exc))

        response.data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }
    else:
        # Handle non-DRF exceptions (e.g. unhandled 500s)
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred."
                }
            },
            status=500
        )

    return response
