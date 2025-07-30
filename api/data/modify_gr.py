import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ofi_dashboard_backend.settings')
django.setup()

from api.models import GoodRecevied  # Adjust model name if needed

updated_count = 0

for gr in GoodRecevied.objects.all():
    if gr.unit_price is not None and random.random() < 0.2:  # 20% chance
        variance = Decimal(str(random.uniform(-0.1, 0.1)))  # -10% to +10% as Decimal
        original_price = gr.unit_price
        gr.unit_price = round(original_price * (Decimal('1') + variance), 2)
        gr.save()
        updated_count += 1

print(f"Updated {updated_count} GoodReceived records with ±10% unit price variance.")
