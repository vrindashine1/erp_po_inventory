
from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow 'Manager' role users to perform actions.
    """
    def has_permission(self, request, view):
        # Allow read-only access for anyone authenticated, but only managers for write methods
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'Manager'

    def has_object_permission(self, request, view, obj):
        # For object-level permissions, e.g., deleting or approving a specific PO
        if request.method in permissions.SAFE_METHODS:
            return True # Read-only access allowed for all authenticated users
        
        return request.user and request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'Manager'

class IsCreatorOrManager(permissions.BasePermission):
    """
    Custom permission to allow the creator of a PO or a Manager to delete it if pending.
    """
    def has_object_permission(self, request, view, obj):
        # Allow manager to delete
        if request.user.is_authenticated and request.user.is_manager():
            return True
        
        # Allow creator to delete if the PO is Pending
        if request.method == 'DELETE':
            return obj.created_by == request.user and obj.status == 'Pending'
        
        return False # Deny all other write operations for non-managers