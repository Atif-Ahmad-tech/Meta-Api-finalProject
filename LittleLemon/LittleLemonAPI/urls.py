from django.urls import path
from . import views

urlpatterns = [
    # path('menu-items/', views.menu_item, name='menu-items'),
    #  path('menu-items/', views.MenuItemView.as_view(), name='menu-item'),
    path('menu-items/', views.MenuItemView.as_view({'get': 'list', 'post': 'create'})),
    path('menu-items/<int:id>', views.single_menu_item, name='single-menu-item'),
    path('groups/manager/users/', views.manager_users, name='manager_users'),
    path('groups/manager/users/<int:id>', views.single_manager_view, name='manager_user_detail'), ## DELETE request
    path('groups/delivery-crew/users', views.delivery_crew_view, name='delivery_crew_users'),
    path('groups/delivery-crew/users/<int:id>', views.single_delivery_crew, name='delivery_crew_user_detail'),
    path('cart/menu-items/', views.cart_view, name = 'cart-view'),
    path('orders/', views.user_orders, name = 'user-orders'),
    path('orders/<int:id>', views.single_user_orders, name = 'user-orders')
]
# urlpatterns = [  path('menu-items/',views.MenuItemsViewSet.as_view({'get':'list'})),
#                path('menu-items/<int:pk>',views.MenuItemsViewSet.as_view({'get':'retrieve'})),
# ]