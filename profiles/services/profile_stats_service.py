from django.db.models import Count, Q
from posts.models import Post
from profiles.models import ProfileFollow


class ProfileStatsService:
    """
    Service for calculating profile statistics.
    Follows Single Responsibility Principle - handles only stats calculation.
    """

    @staticmethod
    def get_connections_count(user):
        """Get total connections count (followers + following)"""
        followers = ProfileFollow.objects.filter(following=user).count()
        following = ProfileFollow.objects.filter(follower=user).count()
        return followers + following

    @staticmethod
    def get_followers_count(user):
        """Get followers count"""
        return ProfileFollow.objects.filter(following=user).count()

    @staticmethod
    def get_following_count(user):
        """Get following count"""
        return ProfileFollow.objects.filter(follower=user).count()

    @staticmethod
    def get_posts_count(user):
        """Get user's posts count"""
        return Post.objects.filter(author=user).count()

    @staticmethod
    def is_connected(user, other_user):
        """Check if two users are connected (mutual follow or one follows the other)"""
        if user == other_user:
            return False
        return ProfileFollow.objects.filter(
            Q(follower=user, following=other_user) |
            Q(follower=other_user, following=user)
        ).exists()

    @staticmethod
    def is_following(user, other_user):
        """Check if user is following another user"""
        if user == other_user:
            return False
        return ProfileFollow.objects.filter(
            follower=user, following=other_user
        ).exists()

    @staticmethod
    def get_mutual_connections_count(user, other_user):
        """Get count of mutual connections between two users"""
        if user == other_user:
            return 0
        
        user_followers = set(
            ProfileFollow.objects.filter(following=user).values_list('follower_id', flat=True)
        )
        other_followers = set(
            ProfileFollow.objects.filter(following=other_user).values_list('follower_id', flat=True)
        )
        
        return len(user_followers & other_followers)

    @classmethod
    def get_all_stats(cls, user, viewing_user=None):
        """
        Get all stats for a user profile.
        
        Args:
            user: User to get stats for
            viewing_user: User viewing the profile (for connection status)
        
        Returns:
            Dictionary with all stats
        """
        stats = {
            'connections_count': cls.get_connections_count(user),
            'followers_count': cls.get_followers_count(user),
            'following_count': cls.get_following_count(user),
            'posts_count': cls.get_posts_count(user),
        }
        
        if viewing_user and viewing_user != user:
            stats.update({
                'is_connected': cls.is_connected(viewing_user, user),
                'is_following': cls.is_following(viewing_user, user),
                'mutual_connections_count': cls.get_mutual_connections_count(viewing_user, user),
            })
        
        return stats
