
# Create your models here.
from django.db import models
from django.conf import settings # For AUTH_USER_MODEL

class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True) # Stock Keeping Unit
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reorder_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=10.00) # Threshold to trigger reorder flag

    @property
    def reorder_needed(self):
        return self.current_stock < self.reorder_threshold

    def __str__(self):
        return f"{self.name} ({self.sku})"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Partially Delivered', 'Partially Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'), # Added for completeness, though not explicitly in instructions
    )

    po_number = models.CharField(max_length=50, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_pos')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    approval_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            # Generate a simple PO number, could be more sophisticated
            last_po = PurchaseOrder.objects.all().order_by('id').last()
            if last_po:
                last_id = last_po.id
                self.po_number = f"PO-{last_id + 1:05d}"
            else:
                self.po_number = "PO-00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PO-{self.po_number} ({self.supplier.name})"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    ordered_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.ordered_quantity * self.unit_price

    class Meta:
        unique_together = ('purchase_order', 'product')

    def __str__(self):
        return f"{self.product.name} - {self.ordered_quantity} in PO {self.purchase_order.po_number}"

class InventoryTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('In', 'In'),
        ('Out', 'Out'),
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    # Could add source/destination fields if needed

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} of {self.product.name} on {self.transaction_date.strftime('%Y-%m-%d %H:%M')}"
    
    