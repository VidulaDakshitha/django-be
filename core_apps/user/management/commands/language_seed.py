import csv

from django.core.management.base import BaseCommand

from core_apps.user.models import Locale


class Command(BaseCommand):
    help = 'Seeds the database with Language data'

    def handle(self, *args, **kwargs):
        # Path to the CSV file
        csv_file_path = 'core_apps/user/management/commands/languages.csv'

        # Open and read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                if count >= 100:  # Limit to 100 languages
                    break
                language = row['Language']
                symbol = row['Code']
                Locale.objects.get_or_create(language=language, symbol=symbol)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded the database with {count} languages'))
