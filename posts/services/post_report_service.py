from django.shortcuts import get_object_or_404
from posts.models import PostReport, Post

class PostReportService:
    @staticmethod
    def report_post(user, post_id, validated_data):
        post = get_object_or_404(Post, id=post_id)

        if PostReport.objects.filter(post=post, reported_by=user).exists():
            raise ValueError("You have already reported this post.")

        report = PostReport.objects.create(
            post=post,
            reported_by=user,
            reason=validated_data.get("reason", "")
        )

        return report
