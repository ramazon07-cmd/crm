def create_audit_log(request, action, instance, changes=None):
    """
    Helper to create audit log entries.

    Usage:
        create_audit_log(request, 'CREATE', student_instance)
        create_audit_log(request, 'UPDATE', payment_instance, changes={'status': ['unpaid', 'paid']})
        create_audit_log(request, 'DELETE', teacher_instance)
    """
    from .models import AuditLog

    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
        ip_address=ip,
    )
