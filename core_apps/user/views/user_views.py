import urllib.parse
import uuid

from django.contrib.auth import authenticate

from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Concat
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from common.base_permission import IsAdmin, IsConsultantManager, IsConsultant
from common.base_view import custom_exception_handler, BaseView
from common.crud_mixin import CRUDMixin
from core_apps.user.func.email_func import send_forget_password_email
from core_apps.user.models import User, CoWorker, Organization
from core_apps.user.serializers.common_serializers import UserIdNameSerializer, OrganizationIdNameSerializer
from core_apps.user.serializers.consultant_serializers import ConsultantSerializer
from core_apps.user.serializers.login_serializer import LoginSerializer
from core_apps.user.serializers.password_serializer import PasswordSerializer
from core_apps.user.serializers.register_serializers import RegisterSerializer
from core_apps.user.serializers.user_serializers import UserSerializer, UserSummarySerializer


class RegisterView(CRUDMixin):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    model = User


class UserView(CRUDMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    model = User

    @custom_exception_handler
    def get(self, request, object_id=None):
        if not object_id:
            user_id = request.user.id
        elif request.user.has_role(User.ADMIN_ROLE) or request.user.has_role(User.CONSULTANT_MANAGER_ROLE):
            user_id = object_id
        else:
            raise Exception("User is not authorized to view this page")

        try:
            user = User.objects.get(id=user_id, is_delete=False)
        except User.DoesNotExist:
            raise ValidationError("User not found")

        serializer = self.serializer_class(user)

        return Response(serializer.data)

    @custom_exception_handler
    def put(self, request, object_id=None):
        with transaction.atomic():
            if object_id is None:
                user_id = request.user.id
            else:
                user_id = object_id

            user = self.get_object(self.model, user_id)
            serializer = self.serializer_class(user, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"message": "Successfully updated"})


@api_view(['POST'])
@transaction.atomic
@custom_exception_handler
def update_password(request, user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'message': 'Authorization header is missing'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = PasswordSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(id=user_id, is_delete=False)

            if not auth_header == user.reset_token or user.is_res_tok_valid is False:
                return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

            user.update_password(serializer.validated_data['password'])

            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@transaction.atomic
@custom_exception_handler
def forget_password(request):
    email = request.data.get('email')
    if not email:
        raise ValidationError("Email is required")
    try:
        user = User.objects.get(email=email, is_delete=False)

        if user.is_locked:
            raise ValidationError("Account locked.")

        if not user.is_verified:
            raise ValidationError("Account not verified.")

        if not user.is_active:
            raise ValidationError("Account is not active.")

        user.set_password_reset_token()
        send_forget_password_email(user)

        return Response({'message': 'Reset password email sent successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        raise ValidationError("User not found")


class LoginView(APIView):
    @custom_exception_handler
    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(username=email, password=password)
            if not user:
                self.handle_invalid_login(email)
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            if user.is_locked:
                return Response({'error': 'Account locked'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_verified:
                return Response({'error': 'Account not verified'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.chat_id:
                user.chat_id = uuid.uuid4()
                user.save()

            data = self.compose_data(user)
            return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def handle_invalid_login(email):
        try:
            user = User.objects.get(email=email)
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.is_locked = True
                user.description = "Account locked due to multiple login attempts"
            user.save()
        except User.DoesNotExist:
            pass

    @staticmethod
    def compose_data(user):
        refresh = RefreshToken.for_user(user)
        user_data = UserSummarySerializer(user).data
        return {
            "message": "Successfully logged in",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": user_data
        }


class GetAllUserView(BaseView):
    permission_classes = [IsAuthenticated, IsConsultantManager]
    serializer_class = UserSummarySerializer

    @custom_exception_handler
    def get(self, request):
        if not request.user.has_organization:
            raise Exception("User is not authorized to view this page")

        if not request.user.organization:
            raise Exception("Complete organization info before proceeding")

        if request.user.has_role(User.ADMIN_ROLE):
            manager = request.query_params.get('manager')
            if manager:
                user_ids = CoWorker.objects.filter(organization_id=request.user.organization_id,
                                                   manager_id=manager).values_list('user_id',
                                                                                   flat=True)
            else:
                user_ids = CoWorker.objects.filter(organization_id=request.user.organization_id).values_list('user_id',
                                                                                                             flat=True)
            users = User.objects.filter(id__in=user_ids, is_delete=False)

        elif request.user.has_role(User.CONSULTANT_MANAGER_ROLE):
            user_ids = CoWorker.objects.filter(manager_id=request.user.id,
                                               organization_id=request.user.organization_id).values_list('user_id',
                                                                                                         flat=True)
            users = User.objects.filter(id__in=user_ids, is_delete=False)
        else:
            raise Exception("User is not authorized to view this page")

        name = request.query_params.get('name')
        if name:
            users = users.annotate(
                full_name=Concat('first_name', Value(' '), 'last_name')
            ).filter(Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(full_name__icontains=name))

        email = request.query_params.get('email')
        if email:
            users = users.filter(email__icontains=email)

        role = request.query_params.get('role')
        if role:
            users = users.filter(roles__name=role)

        u_status = request.query_params.get('status')
        if u_status:
            users = users.filter(is_active=u_status)

        page = self.paginate_queryset(users, request)
        serializer = self.serializer_class(page, many=True)

        return Response(serializer.data)


class GetExternalConsultantsView(BaseView):
    permission_classes = [IsAuthenticated, (IsAdmin | IsConsultantManager)]
    serializer_class = UserIdNameSerializer

    @custom_exception_handler
    def get(self, request):
        if not request.user.has_organization:
            raise Exception("User is not authorized to view this page")

        if request.user.has_role(User.ADMIN_ROLE):
            users = User.objects.filter(
                roles__name__in=[User.GIG_WORKER_ROLE, User.OVER_EMPLOYEE_ROLE],
                is_delete=False
            )
            existing_coworkers = CoWorker.objects.filter(
                organization=request.user.organization
            ).values_list('user_id', flat=True)

            users = users.exclude(id__in=existing_coworkers)
        else:
            raise Exception("User is not authorized to view this page")

        keyword = request.query_params.get('keyword')
        email = request.query_params.get('email')
        print(email)
        if keyword:
            users = users.annotate(
                full_name=Concat('first_name', Value(' '), 'last_name')
            ).filter(
                Q(first_name__icontains=keyword) |
                Q(last_name__icontains=keyword) |
                Q(full_name__icontains=keyword) |
                Q(email__icontains=keyword)
            )

        if email:
            users = users.filter(
                email__icontains=email
            )

        page = self.paginate_queryset(users, request)
        serializer = self.serializer_class(page, many=True)

        return Response(serializer.data)


class GetOrganizationView(BaseView):
    permission_classes = [IsAuthenticated, IsConsultant]
    serializer_class = OrganizationIdNameSerializer

    @custom_exception_handler
    def get(self, request):
        if not request.user.has_organization:
            raise Exception("User is not authorized to view this page")

        organizations = Organization.objects.exclude(id=request.user.organization_id)

        keyword = request.query_params.get('keyword')
        if keyword:
            organizations = organizations.filter(
                Q(name__icontains=keyword)
            )

        page = self.paginate_queryset(organizations, request)
        serializer = self.serializer_class(page, many=True)

        return Response(serializer.data)


class GetAllUserSummaryView(BaseView):
    permission_classes = [IsAuthenticated, IsConsultantManager]
    serializer_class = UserSummarySerializer

    @custom_exception_handler
    def get(self, request):
        if not request.user.has_organization:
            raise Exception("User is not authorized to view this page")

        if not request.user.organization:
            raise Exception("Complete organization info before proceeding")

        if request.user.has_role(User.ADMIN_ROLE):
            user_ids = CoWorker.objects.filter(organization_id=request.user.organization_id).values_list('user_id',
                                                                                                         flat=True)
            users = User.objects.filter(id__in=user_ids, is_delete=False)

        elif request.user.has_role(User.CONSULTANT_MANAGER_ROLE):
            user_ids = CoWorker.objects.filter(manager_id=request.user.id).values_list('user_id', flat=True)
            users = User.objects.filter(id__in=user_ids, is_delete=False)
        else:
            raise Exception("User is not authorized to view this page")

        all_workers = users.count()
        active_workers = users.filter(is_active=True).count()
        inactive_workers = users.filter(is_active=False).count()
        role_counts = {
            role: users.filter(roles__name=role).count()
            for role in User.ORG_ROLES
        }

        data = {
            "all_workers": all_workers,
            "active_workers": active_workers,
            "inactive_workers": inactive_workers,
            **role_counts
        }
        return Response(data)


class ConsultantView(CRUDMixin):
    permission_classes = [IsAuthenticated, (IsAdmin | IsConsultantManager)]
    serializer_class = ConsultantSerializer
    model = CoWorker


@api_view(['POST'])
@transaction.atomic
@custom_exception_handler
def connection_accept(request, conn_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'message': 'Authorization header is missing'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        coworker = CoWorker.objects.get(id=conn_id, is_delete=False)

        if not auth_header == coworker.token or coworker.is_token_valid is False:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        coworker.is_accepted = True
        coworker.is_token_valid = False
        coworker.save()

        return Response({'message': 'Connection accepted successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': 'Connection not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserByRoleView(BaseView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserIdNameSerializer

    @custom_exception_handler
    def get(self, request):
        if not request.user.has_organization:
            raise Exception("User is not authorized to view this page")

        if request.user.has_any_role([User.ADMIN_ROLE, User.SALES_ROLE, User.CONSULTANT_MANAGER_ROLE]):
            role = request.query_params.get('role')
            if not role:
                raise Exception("Role parameter is required")

            users = User.objects.filter(
                organization=request.user.organization,
                roles__name=role,
                is_delete=False
            )

            page = self.paginate_queryset(users, request)
            serializer = self.serializer_class(page, many=True)

            return Response(serializer.data)
        else:
            raise Exception("User is not authorized to view this page")


@api_view(['GET'])
@transaction.atomic
@custom_exception_handler
def get_user_status(request):
    email = request.GET.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email, is_delete=False)
    except User.DoesNotExist:
        return Response({'user_status': 'not_exist', 'user_id': None})

    requesting_user = request.user

    if user.has_organization:
        user_status = 'internal' if user.organization == requesting_user.organization else 'exist'
    else:
        is_coworker = CoWorker.objects.filter(
            user=user, organization=requesting_user.organization, is_delete=False
        ).exists()
        user_status = 'internal' if is_coworker else 'external'

    return Response({'user_status': user_status, 'user_id': user.id})
