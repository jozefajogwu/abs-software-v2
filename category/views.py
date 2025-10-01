from django.shortcuts import render

from rest_framework import generics
from .models import UserCategory
from .serializers import UserCategorySerializer
from rest_framework.permissions import IsAuthenticated

class UserCategoryListCreateView(generics.ListCreateAPIView):
    queryset = UserCategory.objects.all()
    serializer_class = UserCategorySerializer
    permission_classes = [IsAuthenticated]

class UserCategoryUpdateView(generics.UpdateAPIView):
    queryset = UserCategory.objects.all()
    serializer_class = UserCategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class UserCategoryDeleteView(generics.DestroyAPIView):
    queryset = UserCategory.objects.all()
    serializer_class = UserCategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

