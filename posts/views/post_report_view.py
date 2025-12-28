from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from posts.serializers.post_report_serializer import PostReportSerializer
from posts.models import PostReport
from posts.services.post_report_service import PostReportService
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Reports"])
class PostReportListCreateView(generics.CreateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PostReport.objects.filter(post_id=self.kwargs["post_id"]).order_by("-created_at")

    def perform_create(self, serializer):
        try:
            report = PostReportService.report_post(self.request.user, self.kwargs["post_id"], serializer.validated_data)
            serializer.instance = report
        except ValueError as e:
            raise ValidationError({"detail": str(e)})
