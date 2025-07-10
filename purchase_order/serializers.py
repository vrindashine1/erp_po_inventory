from rest_framework import serializers
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderItem, InventoryTransaction

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    reorder_needed = serializers.ReadOnlyField() # Add this to expose the property

    class Meta:
        model = Product
        fields = '__all__'

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product', 'product_name', 'ordered_quantity', 'received_quantity', 'unit_price', 'subtotal']
        read_only_fields = ['received_quantity', 'subtotal']

class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_delivery_date', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        total_amount = 0
        for item_data in items_data:
            item = PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
            total_amount += item.subtotal
        purchase_order.total_amount = total_amount
        purchase_order.save()
        return purchase_order

class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username')
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier', 'supplier_name', 'order_date',
            'expected_delivery_date', 'status', 'total_amount',
            'created_by', 'created_by_username', 'approved_by', 'approved_by_username',
            'approval_date', 'items_count'
        ]

    def get_items_count(self, obj):
        return obj.items.count()

class PurchaseOrderDetailSerializer(PurchaseOrderListSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta(PurchaseOrderListSerializer.Meta):
        fields = PurchaseOrderListSerializer.Meta.fields + ['items']

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ['transaction_date']