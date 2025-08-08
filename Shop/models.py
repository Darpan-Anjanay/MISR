from django.db import models
from django.contrib.auth.models import User


class AccessRequest(models.Model):
    full_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    email = models.CharField(max_length=254)
    contact_number = models.CharField(max_length=20, blank=False, null=False)
    message = models.TextField(blank=False, null=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'access_request'


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='Profile', default='Profile/shopee.svg')

    class Meta:
        managed = False
        db_table = 'company_profile'
    # def __str__(self):
    #     return self.company_name





class ShopMaster(models.Model):
    name = models.CharField(unique=True, max_length=255)
    active_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    shop_id = models.CharField(max_length=255, blank=True, null=True)
    profile_company_id = models.ForeignKey(CompanyProfile, models.DO_NOTHING, db_column='profile_company_id', blank=True, null=True)


    shared_email = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop_master'
    
    def __str__(self):
        return self.name



class ItemMaster(models.Model):
    name = models.CharField(unique=True, max_length=255)
    status = models.BooleanField(default=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    profile_company_id = models.ForeignKey(CompanyProfile, models.DO_NOTHING, db_column='profile_company_id', blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'item_master'

    def __str__(self):
        return self.name
    
    
class ReceiveLog(models.Model):
    shop = models.ForeignKey('ShopMaster', models.DO_NOTHING)
    item = models.ForeignKey(ItemMaster, models.DO_NOTHING)
    qty = models.IntegerField()
    rate = models.FloatField()
    date = models.DateField()

    class Meta:
        managed = False
        db_table = 'receive_log'

    
    def __str__(self):
        return self.item.name

    



class InventorySummary(models.Model):
    shop = models.ForeignKey('ShopMaster', models.DO_NOTHING)
    item = models.ForeignKey('ItemMaster', models.DO_NOTHING)
    received_qty = models.IntegerField(blank=True, null=True)
    received_total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sold_qty = models.IntegerField(blank=True, null=True)
    available_qty = models.IntegerField(blank=True, null=True)
    avg_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)        

    class Meta: 
        managed = False
        db_table = 'inventory_summary'
        unique_together = (('shop', 'item'))        



class SalesSummary(models.Model):
    invoice_no = models.CharField(max_length=50)
    shop = models.ForeignKey('ShopMaster', models.DO_NOTHING)
    item = models.ForeignKey('ItemMaster', models.DO_NOTHING)
    cost_rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_status = models.CharField(max_length=50, blank=True, null=True)
    qty_sold = models.IntegerField()
    sale_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField()
    total_amt = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, blank=True, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sales_summary'
        unique_together = (('invoice_no', 'item'),)