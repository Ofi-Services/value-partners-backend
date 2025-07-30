from rest_framework.views import APIView
from rest_framework.response import Response
import random

class Alerts(APIView):
    """
    API view to return a mock alert about orders that are not OTIF (On Time In Full).
    """
    def get(self, request, format=None):
        # Mock data for orders
        total_orders = random.randint(50, 100)  # Random total orders
        otif_orders = random.randint(20, total_orders)  # Random OTIF orders
        non_otif_orders = total_orders - otif_orders  # Calculate non-OTIF orders

        # Generate the alert message
        if non_otif_orders > 0:
            message = f"There are {non_otif_orders} orders that are not OTIF out of {total_orders} total orders."
            alert_type = "non-otif"
        else:
            message = f"All {total_orders} orders are OTIF."
            alert_type = "all-otif"

        # Mock UUID for the alert
        alert_uuid = "mock-uuid-" + str(random.randint(1000, 9999))

        # Return the mock alert
        return Response(
            {
                "Alert": {
                    "content": {
                        "total_orders": total_orders,
                        "otif_orders": otif_orders,
                        "non_otif_orders": non_otif_orders,
                    },
                    "type": alert_type,
                    "message": message,
                    "UUID": alert_uuid,
                },
            }
        )