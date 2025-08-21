from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .apiview import CurrentUserDetails,Inventroy,Receive,Sales,Profitability,Shop,Item,AccessRequestApi,RegisterAPIView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


router = DefaultRouter()
# Shop Api router
router.register('shop', Shop, basename='shop')
# Item Api router
router.register('item', Item, basename='item')

urlpatterns = [
      
      path('', include(router.urls)),
      # Access Request 
      path('accessrequest/',AccessRequestApi.as_view(),name='access-request'),
      path('accessrequest/<int:pk>',AccessRequestApi.as_view(),name='access-request'),

      # Current User
      path('currentuser/', CurrentUserDetails.as_view(), name='current-user-detail'),      
      # Inventroy Dashboard Api
      path('inventory/', Inventroy, name='inventory-api'),
      # Receive Dashboard Api
      path('receive/', Receive, name='receive-api'),
      # Sales Dashboard Api
      path('sales/', Sales, name='sales-api'),
      # Profitability Dashboard Api
      path('profitability/', Profitability, name='profitability-api'),

      # Jwt auth token
      path('accesstoken/', TokenObtainPairView.as_view(), name='accesstoken'),
      path('refreshtoken/', TokenRefreshView.as_view(), name='refreshtoken'),

      # Register user
      path('register/', RegisterAPIView.as_view(), name='register'),
]
