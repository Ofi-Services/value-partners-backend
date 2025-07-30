from rest_framework.views import APIView
from rest_framework.response import Response

class Alerts(APIView):
    """
    API view to return a plain text response.
    """
    def get(self, request, format=None):
        return Response(
            {
                "Alert": {
                    "content": {
                        "new_invoices": 54,
                        "new_duplicate_invoices": 12,
                    },
                    "type": "duplicated",
                    "message": "The Canada Customs & Revenue Agency has 9 new invoices with a high confidence level of being duplicated. I recommend reviewing these invoices.",
                    "UUID": "173cc4a2d7b9fc54dc35b9951cc28a7308b9b394bc09fc7544134a0f015d19e6",
                },
            }
        )