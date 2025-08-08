from django.contrib import admin
from .models import ItemMaster, ShopMaster, ReceiveLog ,InventorySummary,SalesSummary,CompanyProfile,AccessRequest

# Readonly Class
class ReadOnlyAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]




# Shop Admin
class ShopMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'active_status']
    search_fields = ['name']
    list_display_links = ['name']
    list_filter = ['profile_company_id','active_status'] 


admin.site.register(ShopMaster, ShopMasterAdmin)

# Item Admin
class ItemMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']
    list_display_links = ['name']
    search_fields = ['name']
    list_filter = ['status']  


admin.site.register(ItemMaster, ItemMasterAdmin)

# Rececie Admin
class ReceiveLogAdmin(ReadOnlyAdmin):
    list_display = ['shop', 'item', 'qty', 'rate', 'date']
    list_display_links = ['item']
    search_fields = ['shop__name', 'item__name']  
    list_filter = ['shop', 'date']


admin.site.register(ReceiveLog, ReceiveLogAdmin)


# Inventory Summary Admin
class InventorySummaryAdmin(ReadOnlyAdmin):
    list_display = [
        'shop', 'item', 'received_qty', 'received_total_cost',
        'sold_qty', 'available_qty', 'avg_rate', 'stock_value'
    ]
    list_filter = ['shop']
    search_fields = ['shop__name','item__name']  
    readonly_fields = ['avg_rate', 'stock_value']

admin.site.register(InventorySummary, InventorySummaryAdmin)    

# Sales Summary Admin
class SalesSummaryAdmin(ReadOnlyAdmin):
    list_display = (
        'invoice_no', 'shop', 'item', 'qty_sold', 'sale_rate', 'sale_date',
        'total_amt', 'payment_type', 'profit'
    )
    list_filter = ('shop', 'sale_date', 'payment_type')
    search_fields = ('invoice_no', 'item__name', 'shop__name')  
    date_hierarchy = 'sale_date'
    ordering = ('-sale_date',)

    readonly_fields = ('created_at',) 

admin.site.register(SalesSummary,SalesSummaryAdmin)


# Company Profile Admin
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')
    search_fields = ('user__username', 'company_name')
    list_filter = ('company_name',)
   



# Access Request Admin
@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company_name', 'email', 'contact_number', 'submitted_at', 'status')
    list_filter = ('status', 'submitted_at')
    search_fields = ('full_name', 'email', 'company_name', 'contact_number')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
