# from rest_framework.views import exception_handler

# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)

#     # Customize the authentication error response
#     if response is not None and response.status_code == 401:
#         response.data = {
#             "error": "user not authenticated,invalid credentials"
#         }

#     return response
# from rest_framework.views import exception_handler

# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)

#     if response is not None and isinstance(response.data, dict):
#         if 'detail' in response.data:
#             response.data = {
#                 'error': response.data['detail']
#             }
#         else:
#             # for field or non-field validation errors
#             response.data = {
#                 'error': response.data
#             }

#     return response
# from rest_framework.views import exception_handler

# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)
#     data=response.data
#     if response is not None:
#         # Handle authentication error with custom message
#         if response.status_code == 401:
#             response.data = {
#                 "error": "user not authenticated, invalid credentials"
#             }
#         # Handle other error formats
#         if isinstance(data, (list, str)):
#             clean = data[0] if isinstance(data, list) else data

#         # 2) If it's a dict with 'non_field_errors', pull its first item:
#         elif isinstance(data, dict) and 'non_field_errors' in data:
#             clean = data['non_field_errors'][0]

#         # 3) If it's a dict of field errors, pick the **first** field's first error:
#         elif isinstance(data, dict):
#             # e.g. {"email": ["Invalid"], "password": ["Too short"]}
#             first_field = next(iter(data))
#             errors = data[first_field]
#             clean = errors[0] if isinstance(errors, (list, tuple)) else errors

#         else:
#             # Fallback – dump the whole thing
#             clean = data

#         # Wrap under your single 'error' key
#         response.data = {'error': clean}
#         return response
#     return response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        # Handle the case when DRF returns None (e.g. unhandled exception)
        return Response({
            "error": str(exc) or "An unexpected error occurred.",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        data = response.data

        # Handle authentication error with custom message
        if response.status_code == 401:
            response.data = {
                "error": "User not authenticated, invalid credentials",
                "data": None
            }
            return response

        # Initialize clean message
        clean = None

        # Handle list or string errors
        if isinstance(data, (list, str)):
            clean = data[0] if isinstance(data, list) else data

        # Handle 'non_field_errors'
        elif isinstance(data, dict) and 'non_field_errors' in data:
            clean = data['non_field_errors'][0]

        # Handle field-level errors
        elif isinstance(data, dict):
            first_field = next(iter(data))
            errors = data[first_field]
            clean = errors[0] if isinstance(errors, (list, tuple)) else errors

        else:
            clean = str(data)

        # Return consistent error structure
        response.data = {
            "error": clean,
            "data": None
        }

    except Exception as e:
        # Fallback in case something goes wrong inside the handler
        return Response({
            "error": "An internal error occurred while handling another error.",
            "detail": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
