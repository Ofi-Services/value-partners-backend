from rest_framework import serializers
from .models import Case, Activity, Variant, Inventory, OrderItem, Invoice, OCRInvoiceItem



class CaseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Case model.

    This serializer converts Case instances to native Python datatypes
    that can be easily rendered into JSON, XML or other content types.

    Meta:
        model (Case): The model to be serialized.
        fields (str): All fields of the model.
    """
    class Meta:
        model = Case
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Activity model.

    This serializer converts Activity instances to native Python datatypes
    that can be easily rendered into JSON, XML or other content types.

    Meta:
        model (Activity): The model to be serialized.
        fields (list): The fields of the model to be serialized.
    """
    case = CaseSerializer()

    class Meta:
        model = Activity
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the Variant model.
    This serializer converts Variant model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the variant.
    - activities: The activities associated with the variant.
    - cases: The cases related to the variant.
    - number_cases: The number of cases for the variant.
    - percentage: The percentage representation of the variant.
    - avg_time: The average time associated with the variant.
    """

    class Meta:
        model = Variant
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Inventory model.
    This serializer converts Inventory model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the inventory item.
    - product_code: The code identifying the product.
    - product_name: The name of the product.
    - current_stock: The current stock level of the product.
    - unit_price: The price per unit of the product.
    """
    class Meta:
        model = Inventory
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.

    Converts OrderItem model instances to native Python datatypes that can be easily rendered into JSON, XML, or other content types.

    Meta:
        model (OrderItem): The model that is being serialized.
        fields (list): The list of fields to be included in the serialized output.
    """

    #add order serializer
    order = CaseSerializer()
    suggestion = InventorySerializer()
    class Meta:
        model = OrderItem
        fields = ['order', 'material_name', 'material_code', 'quantity', 'unit_price', 'is_free_text', 'suggestion', 'confidence']

class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Invoice model.
    This serializer converts Invoice model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the invoice.
    - date: The date of the invoice.
    - unit_price: The unit price of the invoice item.
    - quantity: The quantity of the invoice item.
    - value: The total value of the invoice item.
    - case: The case associated with the invoice item.
    - pattern: The pattern associated with the invoice item.
    - open: Indicates if the invoice is open or closed.
    - group_id: The group identifier for the invoice item.
    """

    case = CaseSerializer()
    class Meta:
        model = Invoice
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Inventory model.
    This serializer converts Inventory model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the inventory item.
    - product_code: The code identifying the product.
    - product_name: The name of the product.
    - current_stock: The current stock level of the product.
    - unit_price: The price per unit of the product.
    """
    class Meta:
        model = Inventory
        fields = '__all__'

class OCRInvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OCRInvoiceItem model.
    Converts OCRInvoiceItem model instances to native Python datatypes for rendering into JSON, XML, or other content types.
    """
    class Meta:
        model = OCRInvoiceItem
        fields = '__all__'

