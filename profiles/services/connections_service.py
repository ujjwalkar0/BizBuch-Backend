from profiles.models import ProfileFollow, Profile


class ConnectionsService:
    """
    Service for handling user connections.
    """

    @staticmethod
    def get_connections(user):
        """
        Get all connections for a user (followers + following).
        
        Returns:
            QuerySet of Profile objects representing all connections
        """
        # Get user IDs of followers
        follower_ids = ProfileFollow.objects.filter(
            following=user
        ).values_list('follower_id', flat=True)
        
        # Get user IDs of users being followed
        following_ids = ProfileFollow.objects.filter(
            follower=user
        ).values_list('following_id', flat=True)
        
        # Combine both sets and get unique profiles
        connection_ids = set(follower_ids) | set(following_ids)
        
        # Return empty queryset if no connections
        if not connection_ids:
            return Profile.objects.none()
        
        return Profile.objects.filter(user_id__in=connection_ids)
