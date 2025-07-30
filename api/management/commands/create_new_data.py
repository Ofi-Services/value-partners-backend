import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Case, Activity, Variant, Inventory, OrderItem, Supplier, CatalogItems, Invoice, Contract

from ..constants import NAMES, BRANCHES, SUPPLIERS
import json




class Command(BaseCommand):
    """
    Django management command to add data to the database from a CSV file.
    """
    help = 'Add data to the database from CSV file'

    def create_suppliers(self):
        """
        Create suppliers in the database.
        """
        for supplier in SUPPLIERS:
            supplier_obj, created = Supplier.objects.get_or_create(name=supplier)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Supplier {supplier} created.'))
            else:
                self.stdout.write(self.style.WARNING(f'Supplier {supplier} already exists.'))

    def create_catalogue(self):
        """
        Create catalogue items in the database.
        """
         # Path to the CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'Inventory.csv')

        # Read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                product_code = row['Product Code']
                name = row['Product Name']

                
                CatalogItems.objects.get_or_create(
                    product_code=product_code,
                    product_name=name,
                )
                self.stdout.write(self.style.SUCCESS(f'Catalogue item {name} created.'))

        self.stdout.write(self.style.SUCCESS('Catalogue data added successfully'))

    def create_goods(self):
        """
        Create goods in the database.
        """
        invoices = Invoice.objects.all()
        for invoice in invoices:
            #Get the case for the invoice
            Supplier = Supplier.objects.get(id=invoice.case.supplier.id)

        self.stdout.write(self.style.SUCCESS('Goods data added successfully'))

    
    def create_contracts(self, supplier: Supplier):
        """
        Create contracts in the database.
        """
        # Create the contract
        contract = Contract.objects.create(
            supplier=supplier,
        )

        self.stdout.write(self.style.SUCCESS(f'Contract {contract.id} created.'))

    def handle(self, *args, **kwargs):
        """
        Handle the command to add data to the database from the CSV file.
        """
        #self.create_suppliers()
        self.create_catalogue()