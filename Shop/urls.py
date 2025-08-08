from django.urls import path
from .views import Items,AddItem,EditItem,Shops,Profile,get_shops,get_items,DeleteItem,AddShop,EditShop,DeleteShop,Dashboard,kpi,ChartApi,Table,Inventroy,Receive,Sales,Profitability
from .authview import UserLogin,UserLogout,RequestAccess
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [    
    # landing Page
    path('landing/', TemplateView.as_view(template_name='Auth/landing.html'), name='landing'),
    
    # Request Access
    path('requestaccess',RequestAccess,name='requestaccess'),
    # Login and Logout    
    path('login/',UserLogin,name='login'),
    path('logout/',UserLogout,name='logout'),


    # Password 
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='Password/password_reset_form.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='Password/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='Password/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='Password/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='Password/password_change_form.html'
    ), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='Password/password_change_done.html'
    ), name='password_change_done'),


   
    # items     
    path('items/', Items, name='items'), # List
    path('items/add/', AddItem, name='add_item'), # add 
    path('items/edit/<int:item_id>/', EditItem, name='edit_item'), # edit
    path('items/delete/<int:item_id>/', DeleteItem, name='delete_item'), # delete
    # item api
    path('api/items/', get_items, name='get_items'),
    # shop
    path('shops/',Shops, name='shops'), # list
    path('shops/add/',AddShop, name='add_shop'), # add
    path('shops/edit/<int:shop_id>/',EditShop, name='edit_shop'), # edit
    path('shops/delete/<int:shop_id>/',DeleteShop, name='delete_shop'), # delete
    # shop api
    path('api/shops/',get_shops),
    # profile
    path('profile/',Profile,name='profile'),

    # Dashboard's
    path('', Dashboard, name='dashboard'), 
    # Inventroy Report
    path('inventroy/', Inventroy, name='inventroy'),
    # Receive Report
    path('receive/', Receive, name='receive'),
    # Sales Report
    path('sales/', Sales, name='sales'),
    # Profitability Report
    path('profitability/', Profitability , name='profitability'),

    # Dashboard API
    path('api/kpi/', kpi, name='kpi'),
    path('api/chartapi/', ChartApi, name='chartapi'),
    path('api/table/', Table, name='table'),
  
]
