from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from .import views
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    slug =  serializers.CharField(write_only=True)
    class Meta:
        model= Category
        fields = ['id', 'title', 'slug']
        
    
class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    # catagory = serializers.HyperlinkedRelatedField(queryset = catagory.objects.all(),view_name='catagory_detail')
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured','category', 'category_id']
        ordering_fields = ['price', 'title']
        
        

class CartSerializer(serializers.ModelSerializer):
    # price = serializers.SerializerMethodField(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    
    def validate(self, attrs):
        if(attrs['quantity']<0):
            raise serializers.ValidationError('quantity should not be less than 0')
        if(attrs['unit_price']<0):
            raise serializers.ValidationError('unit_price cannot be negative')
        return super().validate(attrs)
   
    class Meta:
        model = Cart
        fields = ['id','user', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id','unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['id','user', 'delivery_crew', 'status','total', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = ['id','order', 'menuitem', 'quantity', 'unit_price', 'price']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']