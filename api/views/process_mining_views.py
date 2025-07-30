from rest_framework.views import APIView
from rest_framework.response import Response

class Alerts(APIView):
    """
    API view to return a mock alert about process mining.
    """
    def get(self, request, format=None):
        # Mock alert message
        message = (
            "Process mining analysis has identified inefficiencies in the order fulfillment process. "
            "The average processing time has increased by 15%, and bottlenecks were detected in the approval stage. "
            "Consider reviewing the workflow to optimize performance."
        )

        # Return the mock alert
        return Response(
            {
                "Alert": {
                    "type": "process-mining",
                    "message": message,
                }
            }
        )