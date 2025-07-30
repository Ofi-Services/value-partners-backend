
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ofi_dashboard_backend.settings')
django.setup()
import random
from api.models import OrderItem, CatalogItem

# Get all product codes that have a contract
contract_product_codes = set(CatalogItem.objects.exclude(contract_id=None).values_list('product_code', flat=True))

# Get all order items that could use a contract
orderitems_with_contract = OrderItem.objects.filter(material_code__in=contract_product_codes)

used_count = 0
not_used_count = 0

for item in orderitems_with_contract:
    if random.random() < 0.8:
        item.contract_used = True
        used_count += 1
    else:
        item.contract_used = False
        not_used_count += 1
    item.save()

print(f"Updated {orderitems_with_contract.count()} order items: {used_count} used, {not_used_count} not used.")
