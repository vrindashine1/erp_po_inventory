from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderItem, InventoryTransaction
from .serializers import (
    SupplierSerializer, ProductSerializer,
    PurchaseOrderCreateSerializer, PurchaseOrderListSerializer,
    PurchaseOrderDetailSerializer, InventoryTransactionSerializer
)
from .permissions import IsManager, IsCreatorOrManager

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsManager] # Only managers can CRUD suppliers

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManager] # Only managers can CRUD products

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-order_date', '-id')

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        elif self.action == 'retrieve':
            return PurchaseOrderDetailSerializer
        return PurchaseOrderListSerializer

    def get_permissions(self):
        if self.action in ['approve', 'receive_goods']:
            self.permission_classes = [IsManager]
        elif self.action == 'destroy':
            self.permission_classes = [IsCreatorOrManager]
        else:
            self.permission_classes = [] # Default to IsAuthenticated for others, handled by global setting
        return super().get_permissions()

    def perform_create(self, serializer):
        # Business Rule: Once a PO is created, its status should be "Pending".
        # This is the default in the model, but explicitly set if needed.
        serializer.save(created_by=self.request.user, status='Pending')

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approves a Purchase Order.
        Business Rule: Only users with the "Manager" role can approve.
        """
        po = self.get_object()

        if po.status != 'Pending':
            return Response(
                {"detail": f"PO status is {po.status}. Only 'Pending' POs can be approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        po.status = 'Approved'
        po.approved_by = request.user
        po.approval_date = timezone.now()
        po.save()
        serializer = self.get_serializer(po)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def receive_goods(self, request, pk=None):
        """
        Receives goods for a Purchase Order, updates inventory.
        Business Rule: Updates received_quantity, PO status, and inventory stock.
        """
        po = self.get_object()
        received_items_data = request.data.get('items', []) # Expects a list of {'item_id': X, 'received_qty': Y}

        if po.status not in ['Approved', 'Partially Delivered']:
            return Response(
                {"detail": "Goods can only be received for 'Approved' or 'Partially Delivered' POs."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not received_items_data:
            return Response(
                {"detail": "No items provided for receiving."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            all_items_received = True
            for item_data in received_items_data:
                item_id = item_data.get('item_id')
                received_qty = item_data.get('received_qty')

                if not item_id or received_qty is None:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": "Invalid item data. Each item must have 'item_id' and 'received_qty'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    po_item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=po)
                except PurchaseOrderItem.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": f"Purchase Order Item with id {item_id} not found in this PO."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                if received_qty <= 0:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": f"Received quantity for item {po_item.product.name} must be positive."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Prevent receiving more than ordered
                if po_item.received_quantity + received_qty > po_item.ordered_quantity:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": f"Cannot receive more than ordered for item {po_item.product.name}. Ordered: {po_item.ordered_quantity}, Already received: {po_item.received_quantity}, Attempting to receive: {received_qty}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update received quantity for the PO item
                po_item.received_quantity += received_qty
                po_item.save()

                # Update inventory stock for received products
                product = po_item.product
                product.current_stock += received_qty
                product.save()

                # Log inventory transaction
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type='In',
                    quantity=received_qty,
                    purchase_order_item=po_item
                )

                if po_item.received_quantity < po_item.ordered_quantity:
                    all_items_received = False

            # Update PO status based on received items
            if all_items_received:
                po.status = 'Completed'
            else:
                po.status = 'Partially Delivered'
            po.save()

        serializer = self.get_serializer(po)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Deletes a Purchase Order.
        Business Rule: Only "Pending" orders can be deleted.
        """
        po = self.get_object()
        
        # Permission check already handled by IsCreatorOrManager, but an extra check
        if po.status != 'Pending':
            return Response(
                {"detail": "Only 'Pending' purchase orders can be deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, pk)

class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.all().order_by('-transaction_date')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsManager] # Only managers can view inventory transactions