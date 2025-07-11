from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg import openapi as oa
from drf_yasg.utils import swagger_auto_schema

# models and serializers
from modules.manager.serializers.user import *
from modules.manager.models.user import User

# viewser base
from modules.common.views import BaseModelViewSet


class UserViewSet(BaseModelViewSet):
    """
    API endpoints for management of users.
    """

    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return UserListSerializer
        if self.action in ["create"]:
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description="List all active users.",
        manual_parameters=[
            oa.Parameter(
                name="Authorization",
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(
                description="List of users", schema=UserListSerializer(many=True)
            ),
            403: oa.Response(
                description="Forbidden",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            404: oa.Response(
                description="Not found",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific user.",
        manual_parameters=[
            oa.Parameter(
                name="Authorization",
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description="User details", schema=UserListSerializer),
            403: oa.Response(
                description="Forbidden",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            404: oa.Response(
                description="User not found",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new user.",
        request_body=UserCreateSerializer,
        manual_parameters=[
            oa.Parameter(
                name="Authorization",
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            201: oa.Response(
                description="User created successfully", schema=UserListSerializer
            ),
            400: oa.Response(
                description="Bad request",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={
                        "message": oa.Schema(type=oa.TYPE_STRING),
                        "error": oa.Schema(type=oa.TYPE_OBJECT),
                    },
                ),
            ),
            403: oa.Response(
                description="Forbidden",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "User could not be created", "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_description="Update a user.",
        request_body=UserUpdateSerializer,
        manual_parameters=[
            oa.Parameter(
                name="Authorization",
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(
                description="User updated successfully", schema=UserListSerializer
            ),
            400: oa.Response(
                description="Bad request",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={
                        "message": oa.Schema(type=oa.TYPE_STRING),
                        "error": oa.Schema(type=oa.TYPE_OBJECT),
                    },
                ),
            ),
            403: oa.Response(
                description="Forbidden",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            404: oa.Response(
                description="User not found",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "User could not be updated", "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_description="Delete a user (soft delete: is_active=False).",
        manual_parameters=[
            oa.Parameter(
                name="Authorization",
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(
                description="User deleted successfully",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"message": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            403: oa.Response(
                description="Forbidden",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            404: oa.Response(
                description="User not found",
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_200_OK
        )
