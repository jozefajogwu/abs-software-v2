from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RecentActivity
from .serializers import RecentActivitySerializer

class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = RecentActivity.objects.all()[:20]  # latest 20 entries
        serializer = RecentActivitySerializer(logs, many=True)
        return Response(serializer.data)
