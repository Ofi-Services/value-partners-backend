from django.core.management.base import BaseCommand
from api.models import OCRInvoiceItem
import random

SUPPLIERS = ["Colanta", "Alpina", "Parmalat", "Nestle"]
MATERIALS = ["Leche", "Queso", "Parmesano", "Mantequilla", "Cuajada"]
CONDITIONS = ["equal", "higher", "lower"]

class Command(BaseCommand):
    help = 'Reset and insert mock OCRInvoiceItem data with more matching invoices'

    def handle(self, *args, **kwargs):
        num_items = 991

        # 1. Reset the table
        OCRInvoiceItem.objects.all().delete()
        self.stdout.write(self.style.WARNING("All OCRInvoiceItem records deleted."))

        # 2. Insert new mock data
        for i in range(num_items):
            supplier = random.choice(SUPPLIERS)
            material = random.choice(MATERIALS)
            invoice_no = f"{random.randint(10000, 99999)}"
            po_number = f"PO{random.randint(1000, 9999)}"
            invoice_item = random.randint(1, 10)
            supplier_id = f"{random.randint(600000000, 699999999)}"

            # 70% chance to be a perfect match
            if random.random() < 0.7:
                qty = db_qty = random.randint(10, 100)
                qty_match = True
                price = db_price = random.randint(1000, 20000)
                unit_price_match = True
                payment_terms = db_payment_terms = random.choice([15, 20, 30, 45])
                payment_terms_match = True
            else:
                qty = random.randint(10, 100)
                db_qty = qty + random.choice([-5, 5])
                qty_match = False
                price = random.randint(1000, 20000)
                db_price = price + random.choice([-500, 500])
                unit_price_match = False
                payment_terms = random.choice([15, 20, 30, 45])
                db_payment_terms = payment_terms + random.choice([-5, 5])
                payment_terms_match = False

            OCRInvoiceItem.objects.create(
                invoice=invoice_no,
                invoice_no=invoice_no,
                po_number=po_number,
                invoice_item=invoice_item,
                material_description=material,
                supplier=supplier,
                supplier_id=supplier_id,
                invoice_qty=qty,
                database_qty=db_qty,
                qty_match=qty_match,
                condition_qty_match=random.choice(CONDITIONS),
                diff_qty=qty - db_qty,
                invoice_unit_price=price,
                database_unit_price=db_price,
                unit_price_match=unit_price_match,
                condition_price_match=random.choice(CONDITIONS),
                diff_unit_price=price - db_price,
                invoice_payment_terms=payment_terms,
                database_payment_terms=db_payment_terms,
                payment_terms_match=payment_terms_match,
                condition_payment_terms=random.choice(CONDITIONS),
                diff_payment_terms=payment_terms - db_payment_terms,
            )
        self.stdout.write(self.style.SUCCESS(f"Created {num_items} mock OCRInvoiceItem records (70% matching)."))