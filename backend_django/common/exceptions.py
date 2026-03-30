from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(response.data, dict) and "detail" in response.data:
        return response

    if isinstance(response.data, dict):
        first_value = next(iter(response.data.values()), "API error")
        if isinstance(first_value, list) and first_value:
            first_value = first_value[0]
        response.data = {"detail": str(first_value)}
        return response

    response.data = {"detail": str(response.data)}
    return response
