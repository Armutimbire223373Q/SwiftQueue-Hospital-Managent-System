import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { toast } from './ui/use-toast';
import apiClient from '../services/apiClient';
import { format } from 'date-fns';
import { Bell, Check, Trash2, AlertCircle, Info, CheckCircle } from 'lucide-react';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await apiClient.get('/notifications');
      setNotifications(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load notifications',
        variant: 'destructive',
      });
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await apiClient.put(`/notifications/${notificationId}/read`);
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId ? { ...notif, is_read: true } : notif
        )
      );
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to mark notification as read',
        variant: 'destructive',
      });
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      await apiClient.delete(`/notifications/${notificationId}`);
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
      toast({
        title: 'Success',
        description: 'Notification deleted',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete notification',
        variant: 'destructive',
      });
    }
  };

  const markAllAsRead = async () => {
    setLoading(true);
    try {
      // Mark all unread notifications as read
      const unreadNotifications = notifications.filter(n => !n.is_read);
      await Promise.all(
        unreadNotifications.map(notif => apiClient.put(`/notifications/${notif.id}/read`))
      );

      setNotifications(prev =>
        prev.map(notif => ({ ...notif, is_read: true }))
      );

      toast({
        title: 'Success',
        description: 'All notifications marked as read',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to mark all notifications as read',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Info className="h-4 w-4 text-blue-500" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'error': return 'border-red-200 bg-red-50';
      case 'success': return 'border-green-200 bg-green-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      default: return 'border-blue-200 bg-blue-50';
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Notifications</span>
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount}
              </Badge>
            )}
          </CardTitle>
          {unreadCount > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={markAllAsRead}
              disabled={loading}
            >
              <Check className="h-4 w-4 mr-1" />
              Mark All Read
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          {notifications.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No notifications yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notification) => (
                <Card
                  key={notification.id}
                  className={`p-4 ${getNotificationColor(notification.type)} ${
                    !notification.is_read ? 'border-l-4' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center space-x-2">
                        {getNotificationIcon(notification.type)}
                        <h4 className={`font-medium ${!notification.is_read ? 'font-semibold' : ''}`}>
                          {notification.title}
                        </h4>
                        {!notification.is_read && (
                          <Badge variant="secondary" className="text-xs">
                            New
                          </Badge>
                        )}
                      </div>

                      <p className="text-sm text-gray-700">{notification.message}</p>

                      <p className="text-xs text-gray-500">
                        {format(new Date(notification.created_at), 'PPp')}
                      </p>
                    </div>

                    <div className="flex space-x-1 ml-4">
                      {!notification.is_read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => markAsRead(notification.id)}
                          className="h-8 w-8 p-0"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                      )}

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteNotification(notification.id)}
                        className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default NotificationCenter;