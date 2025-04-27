from rest_framework.response import Response
from rest_framework import status

def create_response(
    success=True,
    message="",
    data=None,
    errors=None,
    status_code=status.HTTP_200_OK
):
    if data is None:
        data = []
    if errors is None:
        errors = []
    
    response_data = {
        "status": success,
        "message": message,
        "data": data,
        "errors": errors
    }
    
    return Response(response_data, status=status_code)