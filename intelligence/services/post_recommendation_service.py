class PostRecommendationService:

    @staticmethod
    def on_comment_added(comment):
        post = comment.post
        # TODO: add recommendation logic here
        print(f"Recommender triggered for Post {post.id} due to new comment {comment.id}")

    @staticmethod
    def on_new_like(comment):
        post = comment.post
        # TODO: add recommendation logic here
        print(f"Recommender triggered for Post {post.id} due to new comment {comment.id}")

    @staticmethod
    def on_successfull_onboarding(user, topics):
        # TODO: add recommendation logic here
        ...