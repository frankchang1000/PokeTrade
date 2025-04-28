from marketplace.models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        unread_notifications = []
        all_notifications = []
    return {
        'unread_notifications': unread_notifications,
        'all_notifications': all_notifications,
    }