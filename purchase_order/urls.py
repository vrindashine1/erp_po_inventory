
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, ProductViewSet, PurchaseOrderViewSet, InventoryTransactionViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'inventory-transactions', InventoryTransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
