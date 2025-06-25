from django.urls import path
from .views import AnnouncementListView, EventListView, FeedListView, LikeView, CommentView, AcknowledgePostView, AcknowledgeAnnouncementView, PostdeptView, approve_feeds, reject_feeds
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('announcements/', AnnouncementListView.as_view(), name='announcements'),
    path('post/dept/', PostdeptView.as_view(), name='announcement'),
    path('events/', EventListView.as_view(), name='events'),
    path('feeds/', FeedListView.as_view(), name='feeds'),
    path('feeds/<int:postid>/like/', LikeView.as_view(), name='like'),
    path('feeds/<int:postid>/comment/', CommentView.as_view(), name='comment'),
    path('posts/<int:post_id>/acknowledge/', AcknowledgePostView.as_view(), name='acknowledge-post'),
    path('announcements/<int:pk>/acknowledge/', AcknowledgeAnnouncementView.as_view(), name='acknowledge-announcement'),
    path('posts/approve/<int:pk>/', approve_feeds, name='approve-post'),
    path('posts/reject/<int:pk>/', reject_feeds, name='reject-post'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

