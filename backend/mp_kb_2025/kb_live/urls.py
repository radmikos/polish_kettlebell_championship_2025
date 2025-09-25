"""URL configuration for the kb_live REST API."""

from rest_framework.routers import DefaultRouter

from kb_live import views


router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("players", views.PlayerViewSet, basename="player")
router.register("clubs", views.SportClubViewSet, basename="club")

urlpatterns = router.urls
