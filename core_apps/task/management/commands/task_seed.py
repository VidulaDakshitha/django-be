from django.core.management.base import BaseCommand

from core_apps.user.models import User


class Command(BaseCommand):
    help = 'Seeds the database with User data'

    def handle(self, *args, **kwargs):
        tasks_data = [
            {"title": "Test Task 1",
             "description": "test",
             "budget": 100.50,
             "currency": "USD",
             "bid_type": "open",
             "bid_deadline": "2025-04-25",
             "task_deadline": "2025-04-25",
             "acceptance_criteria": "test"},

            {"title": "Test Task 2",
             "description": "test",
             "budget": 200.50,
             "currency": "USD",
             "bid_type": "open",
             "bid_deadline": "2025-04-25",
             "task_deadline": "2025-04-25",
             "acceptance_criteria": "test"},

            {"title": "Test Task 3",
             "description": "test",
             "budget": 300.50,
             "currency": "USD",
             "bid_type": "closed",
             "bid_deadline": "2025-04-25",
             "task_deadline": "2025-04-25",
             "acceptance_criteria": "test"}
        ]

        for user_data in tasks_data:
            pass

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with tasks'))
