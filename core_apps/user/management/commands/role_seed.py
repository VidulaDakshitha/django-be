from django.core.management.base import BaseCommand
from core_apps.user.models import User, Role


class Command(BaseCommand):
    help = 'Seeds the database with Roles data'

    def handle(self, *args, **kwargs):
        roles_data = [
            {"name": User.ADMIN_ROLE, "description": "Admin permission"},
            {"name": User.CUSTOMER_ROLE, "description": "Customer permission"},
            {"name": User.CONSULTANT_MANAGER_ROLE, "description": "Consultant manager permission"},
            {"name": User.CONSULTANT_ROLE, "description": "Consultant permission"},
            {"name": User.BILLING_ROLE, "description": "Billing permission"},
            {"name": User.SALES_ROLE, "description": "Sales permission"},
            {"name": User.GIG_WORKER_ROLE, "description": "Gig worker permission"},
            {"name": User.OVER_EMPLOYEE_ROLE, "description": "Over employee permission"},
            {"name": User.TASK_MANAGER_ROLE, "description": "Over employee permission"},
        ]

        for role_data in roles_data:
            role = {
                "name": role_data['name'],
                "description": role_data['description']
            }
            Role.objects.create(**role)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with roles'))
