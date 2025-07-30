from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    """
    Django management command to count the number of entries in each table of the database.
    """
    help = 'Count the number of entries in each table of the database'

    def handle(self, *args, **kwargs):
        # Get all models in the project
        models = apps.get_models()

        self.stdout.write(self.style.SUCCESS("Counting entries in each table..."))

        for model in models:
            # Get the table name and count the entries
            table_name = model._meta.db_table
            count = model.objects.count()
            self.stdout.write(f"{table_name}: {count} entries")

        self.stdout.write(self.style.SUCCESS("Done!"))