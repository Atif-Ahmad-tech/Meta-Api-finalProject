from django.shortcuts import render
from rest_framework import status,viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework.permissions import  IsAuthenticated
from rest_framework.decorators import api_view, renderer_classes, permission_classes, throttle_classes
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer,UserSerializer, CartSerializer, OrderSerializer
from .permissions import IsMemberOfManagerGroup
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
class MenuItemPagination(PageNumberPagination):
    page_size = 2

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return f'{url}&page={page_number}'
class MenuItemView(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    queryset = MenuItem.objects.select_related('category').all()
    throttle_classes = [UserRateThrottle]
    filter_backends = [OrderingFilter]
    ordering_fields=['price','title']
    pagination_class = PageNumberPagination
    def list(self, request, *args, **kwargs):
        items = self.get_queryset().select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        per_page = request.query_params.get('perpage', default=2)
        ordering = request.query_params.get('ordering')
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_params = ordering.split(',')
            items = items.order_by(*ordering_params)
        if per_page:
            self.pagination_class.page_size = int(per_page)
        items = self.paginate_queryset(items)
        serializer = self.get_serializer(items, many=True)
        response = {
            'next': self.paginator.get_next_link(),
            'results': serializer.data
            }
        return Response(response, status=status.HTTP_200_OK)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                items = self.get_queryset().select_related('category').all()
                category_name = request.query_params.get('category')
                to_price = request.query_params.get('to_price')
                search = request.query_params.get('search')
                per_page = request.query_params.get('perpage', default=2)
                ordering = request.query_params.get('ordering')
                if category_name:
                    items = items.filter(category__title=category_name)
                if to_price:
                    items = items.filter(price__lte=to_price)
                if search:
                    items = items.filter(title__icontains=search)
                if ordering:
                    ordering_params = ordering.split(',')
                    items = items.order_by(*ordering_params)
                if per_page:
                    self.pagination_class.page_size = int(per_page)
                items = self.paginate_queryset(items)
                serializer = self.get_serializer(items, many=True)
                response = {
                'next': self.paginator.get_next_link(),
                'results': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
                # return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


##################################################
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_menu_item(request, id):
    user = request.user
    try:
        items = MenuItem.objects.get(pk=id)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = MenuItemSerializer(items)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        if user.groups.filter(name='Manager').exists():
            serializer = MenuItemSerializer(items, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'PATCH':
        if user.groups.filter(name='Manager').exists():
            serializer = MenuItemSerializer(items, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        if user.groups.filter(name='Manager').exists():
            items.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
##################################################


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsMemberOfManagerGroup]) ## only access by user with manager Group
def manager_users(request):
    manager_group = Group.objects.get(name='Manager')
    if request.method == 'GET':                         
        managers = manager_group.user_set.all()
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':                  ### add username in the payload  to manager group
            user_name = request.data.get('username')
            try:
                user = User.objects.get(username=user_name)
                manager_group.user_set.add(user)
                manager_group = manager_group.user_set.all()
                serializer = UserSerializer(manager_group, many=True)
                return Response("message : user added to the manager group", status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
    
##################################################
          
            
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsMemberOfManagerGroup])
def single_manager_view(request, id):
    if request.method == 'DELETE':
        manager_group = Group.objects.get(name='Manager')
        try:
            user = User.objects.get(pk=id)
            manager_group.user_set.remove(user)
            manager_group = manager_group.user_set.all()
            serializer = UserSerializer(manager_group, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
##################################################

@api_view(['GET', 'POST', ])
@permission_classes([IsAuthenticated,IsMemberOfManagerGroup])
def delivery_crew_view(request):
    delivery_crew_group = Group.objects.get(name='Delivery Crew')
    if request.method == 'GET':
        delivery_crew = delivery_crew_group.user_set.all()
        serializer = UserSerializer(delivery_crew, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        
            user_name = request.data.get('username')
            try:
                user = User.objects.get(username=user_name)
                delivery_crew_group.user_set.add(user)
                delivery_crew = delivery_crew_group.user_set.all()
                serializer = UserSerializer(delivery_crew, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)#  
    
##################################################
    
@api_view([ 'DELETE'])
@permission_classes([IsAuthenticated,IsMemberOfManagerGroup])      
def single_delivery_crew(request, id):
    delivery_crew_group = Group.objects.get(name='Delivery Crew')     
    if request.method == 'DELETE':
        try:
            user = User.objects.get(pk=id)
            delivery_crew_group.user_set.remove(user)
            delivery_crew = delivery_crew_group.user_set.all()
            serializer = UserSerializer(delivery_crew, many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
#######################################

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if request.method == 'GET':
        # Get current user's cart items
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Add menu item to cart for current user
        menu_item_id = request.data.get('id')
        quantity = request.data.get('quantity')
        try:
            menu_item = MenuItem.objects.get(pk=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item = Cart.objects.create(
            user=request.user,
            menuitem=menu_item,
            quantity=quantity,
            unit_price=menu_item.price,
            
        )
        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        # Delete current user's cart items
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
##################################################
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_orders(request):
   
    if not request.user.groups.exists() or request.user.groups.filter(name__in=['manager', 'delivery crew']).exists():
        if request.method =='GET':
            orders = Order.objects.filter(user=request.user)
            to_price = request.query_params.get('to_total')
            search = request.query_params.get('search')
            perpage = request.query_params.get('perpage', default=2)   
            page = request.query_params.get('page', default=1)
            if to_price:
                items= orders.filter(total__lte=to_price)
            if search:
                items= orders.filter(user=search)
            paginator = Paginator(orders, per_page=perpage)
            try:                                 
                orders = paginator.page(page)      
            except EmptyPage:                        
                    []
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        elif request.method== 'POST':
            cart_items = Cart.objects.filter(user=request.user).select_related('menuitem').values()
            for cart_item in cart_items:
                user = cart_item['user_id']
                menuitem = cart_item['menuitem']
                quantity = cart_item['quantity']
                unit_price = cart_item['unit_price']
                price = cart_item['price']
            if not cart_items:
                return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            order_item = OrderItem.objects.bulk_create(user=user,menuitem=menuitem,quantity=quantity,unit_price=unit_price,price=price)
            cart_items.delete()
            return Response({"message: added to order items"}, status=status.HTTP_201_CREATED)
    elif request.user.groups.filter(name='Manager').exists():
        if request.method=='GET':
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
@api_view(['GET'])
def single_user_orders(request, id):
    order = get_object_or_404(Order, id=id)
    if order.user != request.user:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(order)
    return Response(serializer.data)



