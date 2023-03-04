from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from decimal import Decimal

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)
    
class MenuItem(models.Model):
    title=models.CharField(max_length=255, db_index=True)
    price= models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('menuitem', 'user')
        
@receiver(pre_save, sender=Cart)
def cart_pre_save(sender, instance, **kwargs):
    menuitem = instance.menuitem
    instance.unit_price = menuitem.price
    instance.price = Decimal(instance.quantity) * instance.unit_price     

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(db_index = True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add = True, db_index=True)
    
class OrderItem(models.Model):
    order = models.ForeignKey(User, on_delete = models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def save(self, *args, **kwargs):
        super(OrderItem, self).save(*args, **kwargs)
    class Meta:
        unique_together = ('order', 'menuitem')
        
@receiver(pre_save, sender=OrderItem)
def cart_pre_save(sender, instance, **kwargs):
    menuitem = instance.menuitem
    instance.unit_price = menuitem.price
    instance.price = Decimal(instance.quantity) * instance.unit_price   