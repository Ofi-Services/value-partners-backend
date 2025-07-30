from django.db import models
from .constants import ACTIVITY_CHOICES, PATTERN_CHOICES
class OCRInvoiceItem(models.Model):
    invoice = models.CharField(max_length=255)
    invoice_no = models.CharField(max_length=255)
    po_number = models.CharField(max_length=255)
    invoice_item = models.PositiveIntegerField()
    material_description = models.CharField(max_length=255)
    supplier = models.CharField(max_length=255)
    supplier_id = models.CharField(max_length=255)
    invoice_qty = models.DecimalField(max_digits=10, decimal_places=2)
    database_qty = models.DecimalField(max_digits=10, decimal_places=2)
    qty_match = models.BooleanField(default=False)
    condition_qty_match = models.CharField(max_length=20, choices=[
        ('equal', 'Equal'),
        ('higher', 'Higher'),
        ('lower', 'Lower')
    ])
    diff_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    database_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_match = models.BooleanField(default=False)
    condition_price_match = models.CharField(max_length=20, choices=[
        ('equal', 'Equal'),
        ('higher', 'Higher'),
        ('lower', 'Lower')
    ])
    diff_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_payment_terms = models.IntegerField()
    database_payment_terms = models.IntegerField()
    payment_terms_match = models.BooleanField(default=False)
    condition_payment_terms = models.CharField(max_length=20, choices=[
        ('equal', 'Equal'),
        ('higher', 'Higher'),
        ('lower', 'Lower')
    ])
    diff_payment_terms = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['invoice', 'invoice_item'], name='unique_invoice_item'),
        ]

    def __str__(self):
        return f"Invoice: {self.invoice} - Item: {self.invoice_item}"


class Supplier(models.Model):
    """
    Model representing a supplier.

    Attributes:
        id (int): The primary key for the supplier.
        name (str): The name of the supplier.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Contract(models.Model):
    """
    Model representing a contract.

    Attributes:
        id (int): The primary key for the contract.
        supplier (Supplier): The supplier associated with the contract.
    """
    id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, related_name='contracts', on_delete=models.CASCADE)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Contract {self.id} with {self.supplier.name}"
    
class CatalogItem(models.Model):
    """
    Model representing catalog items.

    Attributes:
        id (int): The primary key for the catalog item.
        supplier (Supplier): The supplier associated with the catalog item.
        contract (Contract): The contract associated with the catalog item.
        product_code (str): The product code of the catalog item.
        product_name (str): The name of the catalog item.
        unit_price (float): The unit price of the catalog item.
    """
    id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    contract = models.ForeignKey(Contract, related_name='catalog_items', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} ({self.product_code})"
class GoodRecevied(models.Model):
    """
    Model representing goods received.

    Attributes:
        id (int): The primary key for the goods received record.
        order (Case): The order associated with the goods received.
        product_code (str): The product code of the goods received.
        quantity (int): The quantity of goods received.
        unit_price (float): The unit price of the goods received.
    """
    id = models.AutoField(primary_key=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    invoice = models.ForeignKey('Invoice', related_name='goods_received', on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, related_name='goods_received', on_delete=models.CASCADE, null=True, blank=True)
    product_code = models.CharField(max_length=100)

    def __str__(self):
        return f"Goods Received {self.id} for Order {self.order.id}"
    
class Case(models.Model):

    id = models.CharField(max_length=25, primary_key=True)
    order_date = models.DateTimeField()
    employee_id = models.CharField(max_length=25)
    branch = models.CharField(max_length=25)
    supplier = models.ForeignKey('Supplier', null=True, blank=True, on_delete=models.SET_NULL)
    avg_time = models.FloatField(default=0)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivery = models.DateTimeField(null=True, blank=True)
    on_time = models.BooleanField(default=False)
    in_full = models.BooleanField(default=False)
    number_of_items = models.IntegerField()
    ft_items = models.IntegerField()
    total_price = models.IntegerField()


    def __str__(self):
        return f"Case {self.id} - Duration: {self.duration}"

class Activity(models.Model):
    """
    A model representing an activity related to a case.

    Attributes:
        id (int): The primary key for the activity.
        case (Case): The related case of the activity
        timestamp (datetime): The timestamp of the activity.
        name (str): The name of the activity, chosen from ACTIVITY_CHOICES.
        case_index (int): The index of the case, with a default value of 0.
        tpt (float): The time per task of the activity, with a default value of 0.
    """
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, related_name='activities', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=60)
    tpt = models.FloatField(default=0)
    user = models.CharField(max_length=50, default='None')
    user_type = models.CharField(max_length=50, default='None')
    automatic = models.BooleanField(default=False)
    rework = models.BooleanField(default=False)
    case_index = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.case.id} - {self.name} at {self.timestamp}"
    
class Variant(models.Model):
    """
    A model representing a variant.

    Attributes:
        id (int): The primary key for the variant.
        activities (str): The activities of the variant.
        cases (str): The cases of the variant.
        number_cases (int): The amount of cases of the variant.
        percentage (float): The percentage of cases the variant includes.
        avg_time (float): The average time per case of the variant.
    """
    id = models.AutoField(primary_key=True)
    activities = models.TextField()
    cases = models.TextField()
    number_cases = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    avg_time = models.FloatField(default=0)

    def __str__(self):
        return self.name
    

class Inventory(models.Model):
    """
    Inventory model represents the inventory of products in the system.
    Attributes:
        id (AutoField): The primary key for the inventory record.
        product_code (CharField): The code identifying the product. Can be blank or null.
        product_name (CharField): The name of the product.
        current_stock (IntegerField): The current stock level of the product.
        unit_price (IntegerField): The price per unit of the product.
    Methods:
        __str__(): Returns the string representation of the Inventory instance, 
                   which is the product code.
    """
    id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=255)
    current_stock = models.IntegerField()
    unit_price = models.IntegerField()
    new_product = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the string representation of the Inventory instance.
        """
        return f'{self.product_code}'

class OrderItem(models.Model):
    """
    OrderItem represents an item in an order, including details about the material, quantity, pricing, and related inventory suggestions.
    Attributes:
        order (ForeignKey): A reference to the associated Order. Deletes the OrderItem if the Order is deleted.
        material_name (CharField): The name of the material for the order item. Maximum length is 255 characters.
        material_code (CharField): An optional code for the material. Maximum length is 255 characters.
        quantity (IntegerField): The quantity of the material ordered.
        unit_price (IntegerField): The price per unit of the material.
        is_free_text (BooleanField): Indicates whether the material is a free-text entry.
        suggestion (ForeignKey): An optional reference to an Inventory item as a suggestion. Deletes the suggestion if the Inventory item is deleted.
        confidence (FloatField): An optional confidence score for the suggestion.
    Methods:
        __str__(): Returns a string representation of the OrderItem instance, including the material name and quantity.
    """
    order = models.ForeignKey(Case, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=255)
    material_code = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField()
    unit_price = models.IntegerField()
    is_free_text = models.BooleanField()
    suggestion = models.ForeignKey(Inventory, on_delete=models.CASCADE, blank=True, null=True, related_name='suggestion1_order_items')
    confidence = models.FloatField(blank=True, null=True)
    contract_used = models.BooleanField(default=False)


    def __str__(self):
        """
        Returns the string representation of the OrderItem instance.
        """
        return f'{self.material_name} - {self.quantity}'


class Invoice(models.Model):
    """
    Model representing an invoice.

    Attributes:
        reference (str): The unique reference for the invoice.
        date (datetime): The date of the invoice.
        unit_price (decimal): The unit price of the invoice.
        quantity (int): The quantity of the invoice.
        value (decimal): The value of the invoice.
        vendor (str): The name of the vendor without code.
        pattern (str): The pattern type of the invoice.
        open (bool): The status of the invoice, can be open or closed.
        group_id (str): The group ID associated with the invoice.
        confidence (str): The confidence level of the invoice.
        Region (str): The region associated with the invoice.
        Description (str): The description of the invoice.
        Payment_Method (str): The payment method for the invoice.
        Pay_Date (datetime): The payment date of the invoice.
        Special_Instructions (str): Any special instructions for the invoice.
        Accuracy (int): The accuracy of the invoice.
    """
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    case = models.ForeignKey(Case, related_name='invoices', on_delete=models.CASCADE)
    pattern = models.CharField(max_length=50, choices=PATTERN_CHOICES)
    open = models.BooleanField(default=True)
    group_id = models.CharField(max_length=50)
    confidence = models.CharField(max_length=6)
    description = models.CharField(max_length=250, default='No description')
    payment_method = models.CharField(max_length=50, default='Credit Card')
    pay_date = models.DateTimeField(null=True, blank=True)
    special_instructions = models.CharField(max_length=50, blank=True, null=True)
    accuracy = models.IntegerField(default=0)

    def __str__(self):
        return f"Invoice {self.reference} from {self.vendor} on {self.date}"