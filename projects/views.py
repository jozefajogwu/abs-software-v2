from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Project
from .serializers import ProjectSerializer
from users.models import CustomUser

# List and Create Projects
class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

# Retrieve, Update, Delete a Project
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

# Assign Users to a Project
class AssignUsersToProjectView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        user_ids = request.data.get("user_ids", [])
        users = CustomUser.objects.filter(id__in=user_ids)
        project.assigned_team.set(users)
        project.save()

        return Response({"message": "Users assigned successfully"}, status=status.HTTP_200_OK)


# 📊 Project Stats Endpoint
class ProjectStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Project.objects.count()
        active = Project.objects.filter(status="Active").count()
        completed = Project.objects.filter(status="Completed").count()
        delayed = Project.objects.filter(status="On Hold").count()   # mapped to delayed
        cancelled = Project.objects.filter(status="Cancelled").count()
        archived = Project.objects.filter(status="Archived").count()

        return Response({
            "total_projects": total,
            "active_projects": active,
            "completed_projects": completed,
            "delayed_projects": delayed,
            "cancelled_projects": cancelled,
            "archived_projects": archived
        })
