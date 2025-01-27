from django.core.management.base import BaseCommand
from django.db import transaction

from core_apps.user.models import User, Organization, CoWorker
from utils.custom_datetime import get_formatted_current_time


class Command(BaseCommand):
    help = 'Seeds the database with User data'

    def handle(self, *args, **kwargs):
        # Create organizations first
        organizations_data = [
            {
                "name": "Organization Alpha",
                "url": "https://alpha.com",
                "address_line1": "123 Alpha Street",
                "city": "Alpha City",
                "country": "USA",
                "description": "Alpha Organization Description"
            },
            {
                "name": "Organization Beta",
                "url": "https://beta.com",
                "address_line1": "456 Beta Street",
                "city": "Beta City",
                "country": "USA",
                "description": "Beta Organization Description"
            }
        ]

        organizations = []
        for org_data in organizations_data:
            org = Organization.objects.create(**org_data)
            organizations.append(org)

        # Create users with different roles
        users_data = [
            # Admin users for Organization Alpha
            {
                "first_name": "Admin",
                "last_name": "One",
                "email": "admin1@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.ADMIN_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "Admin",
                "last_name": "Two",
                "email": "admin2@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.ADMIN_ROLE, User.CUSTOMER_ROLE]
            },
            # Admin users for Organization Beta
            {
                "first_name": "Admin",
                "last_name": "Three",
                "email": "admin1@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.ADMIN_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "Admin",
                "last_name": "Four",
                "email": "admin2@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.ADMIN_ROLE, User.CUSTOMER_ROLE]
            },
            # Customer users
            {
                "first_name": "Customer",
                "last_name": "One",
                "email": "customer1@test.com",
                "password": "Abcd@123",
                "country": "USA",
                "roles": [User.CUSTOMER_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "Customer",
                "last_name": "Two",
                "email": "customer2@test.com",
                "password": "Abcd@123",
                "country": "USA",
                "roles": [User.CUSTOMER_ROLE, User.CUSTOMER_ROLE]
            },
            # Gig Worker users
            {
                "first_name": "GigWorker",
                "last_name": "One",
                "email": "gigworker1@test.com",
                "password": "Abcd@123",
                "country": "USA",
                "roles": [User.GIG_WORKER_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "GigWorker",
                "last_name": "Two",
                "email": "gigworker2@test.com",
                "password": "Abcd@123",
                "country": "USA",
                "roles": [User.GIG_WORKER_ROLE, User.CUSTOMER_ROLE]
            },
            # Over Employee users
            {
                "first_name": "OverEmployee",
                "last_name": "One",
                "email": "overemployee1@test.com",
                "password": "Abcd@123",
                "country": "USA",
                "roles": [User.OVER_EMPLOYEE_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "OverEmployee",
                "last_name": "Two",
                "email": "overemployee2@test.com",
                "password": "Abcd@123",
                "country": "USA",
                "roles": [User.OVER_EMPLOYEE_ROLE, User.CUSTOMER_ROLE]
            },
            # Consultant Manager users for Organization Alpha
            {
                "first_name": "ConsultManager",
                "last_name": "Alpha1",
                "email": "cm1@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.CONSULTANT_MANAGER_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "ConsultManager",
                "last_name": "Alpha2",
                "email": "cm2@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.CONSULTANT_MANAGER_ROLE, User.CUSTOMER_ROLE]
            },
            # Consultant Manager users for Organization Beta
            {
                "first_name": "ConsultManager",
                "last_name": "Beta1",
                "email": "cm1@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.CONSULTANT_MANAGER_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "ConsultManager",
                "last_name": "Beta2",
                "email": "cm2@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.CONSULTANT_MANAGER_ROLE, User.CUSTOMER_ROLE]
            },
            # Task Manager users for both organizations
            {
                "first_name": "TaskManager",
                "last_name": "Alpha1",
                "email": "tm1@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.TASK_MANAGER_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "TaskManager",
                "last_name": "Beta1",
                "email": "tm1@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.TASK_MANAGER_ROLE, User.CUSTOMER_ROLE]
            },
            # Consultant users for both organizations
            {
                "first_name": "Consultant",
                "last_name": "Alpha1",
                "email": "consultant1@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.CONSULTANT_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "Consultant",
                "last_name": "Beta1",
                "email": "consultant1@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.CONSULTANT_ROLE, User.CUSTOMER_ROLE]
            },
            # Billing users for both organizations
            {
                "first_name": "Billing",
                "last_name": "Alpha1",
                "email": "billing1@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.BILLING_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "Billing",
                "last_name": "Beta1",
                "email": "billing1@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.BILLING_ROLE, User.CUSTOMER_ROLE]
            },
            # Sales users for both organizations
            {
                "first_name": "Sales",
                "last_name": "Alpha1",
                "email": "sales1@alpha.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[0],
                "roles": [User.SALES_ROLE, User.CUSTOMER_ROLE]
            },
            {
                "first_name": "Sales",
                "last_name": "Beta1",
                "email": "sales1@beta.com",
                "password": "Abcd@123",
                "country": "USA",
                "has_organization": True,
                "organization": organizations[1],
                "roles": [User.SALES_ROLE, User.CUSTOMER_ROLE]
            }
        ]

        with transaction.atomic():
            for user_data in users_data:
                # Extract roles and organization before creating user
                roles = user_data.pop('roles')
                organization = user_data.pop('organization', None)
                password = user_data.pop('password')

                # Create user
                user = User.objects.create(**user_data)
                user.set_password(password)
                user.created_on = get_formatted_current_time()
                user.is_verified = True
                user.organization = organization
                user.save()

                # Set roles
                user.set_roles(roles)

                # Create CoWorker entry for organization members
                if organization:
                    CoWorker.objects.create(
                        user=user,
                        organization=organization,
                        is_accepted=True,
                        is_external=False
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with users'))
