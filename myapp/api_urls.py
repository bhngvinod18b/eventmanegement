from rest_framework.routers import DefaultRouter
from .views import MyeventViewSet, LiketViewSet, FollowViewSet, Saved_eventViewSet, BookeventViewSet

router = DefaultRouter()
router.register(r'event', MyeventViewSet, basename='event')
router.register(r'likes', LiketViewSet, basename='like')
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'saved_event', Saved_eventViewSet, basename='saved_event')
router.register(r'bookevent', BookeventViewSet, basename='bookevent')

urlpatterns = router.urls