import csv
from django.core.management.base import BaseCommand

from core_apps.task.models import Skill
from core_apps.user.models import User


class Command(BaseCommand):
    help = 'Seeds the database with Skill data (limited to 100 skills)'

    def handle(self, *args, **kwargs):
        # Path to the CSV file
        csv_file_path = 'core_apps/task/management/commands/skills.csv'

        # Open and read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                if count >= 100:  # Limit to 100 skills
                    break
                skill_name = row['Skills']  # Adjust this according to your CSV column name
                Skill.objects.get_or_create(skill=skill_name)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded the database with {count} skills'))
