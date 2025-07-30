from rest_framework.views import APIView
from rest_framework.response import Response
import random

class Alerts(APIView):
    """
    API view to return a mock alert about purchase orders that used free text instead of the catalog.
    """
    def get(self, request, format=None):
        # Mock data for purchase orders
        total_purchase_orders = random.randint(50, 100)  # Random total purchase orders
        free_text_orders = random.randint(10, total_purchase_orders)  # Random free text orders
        catalog_orders = total_purchase_orders - free_text_orders  # Calculate catalog orders

        # Generate the alert message
        if free_text_orders > catalog_orders:
            message = f"There are {free_text_orders} purchase orders that used free text, which is higher than the {catalog_orders} that used the catalog."
            alert_type = "free-text-dominant"
        else:
            message = f"There are {catalog_orders} purchase orders that used the catalog, which is higher than the {free_text_orders} that used free text."
            alert_type = "catalog-dominant"

        # Mock UUID for the alert
        alert_uuid = "mock-uuid-" + str(random.randint(1000, 9999))

        # Return the mock alert
        return Response(
            {
                "Alert": {
                    "content": {
                        "total_purchase_orders": total_purchase_orders,
                        "free_text_orders": free_text_orders,
                        "catalog_orders": catalog_orders,
                    },
                    "type": alert_type,
                    "message": message,
                    "UUID": alert_uuid,
                },
            }
        )