

# Register your models here.
from django.contrib import admin
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderItem, InventoryTransaction

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone_number')
    search_fields = ('name', 'email')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'current_stock', 'reorder_threshold', 'reorder_needed')
    search_fields = ('name', 'sku')
    list_filter = ('reorder_threshold',)
    readonly_fields = ('reorder_needed',)

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('product', 'ordered_quantity', 'unit_price', 'received_quantity')
    readonly_fields = ('received_quantity',) # received_quantity updated by API, not manually here

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'order_date', 'status', 'total_amount', 'created_by', 'approved_by', 'approval_date')
    list_filter = ('status', 'order_date', 'supplier')
    search_fields = ('po_number', 'supplier__name')
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ('po_number', 'total_amount', 'created_by', 'approved_by', 'approval_date') # These fields are set by system/API

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'Pending': # Once approved, some fields might become read-only
            return self.readonly_fields + ('supplier', 'expected_delivery_date', 'status')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'transaction_date', 'purchase_order_item')
    list_filter = ('transaction_type', 'transaction_date', 'product')
    search_fields = ('product__name',)
    readonly_fields = ('product', 'transaction_type', 'quantity', 'transaction_date', 'purchase_order_item')