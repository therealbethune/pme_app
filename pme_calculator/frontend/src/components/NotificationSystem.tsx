import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import {
  Snackbar,
  IconButton,
  Box,
  Typography,
  Slide,
  SlideProps,
  Stack,
  LinearProgress,
  Paper,
} from '@mui/material';
import {
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  Info,
  Close
} from '@mui/icons-material';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  progress?: number;
  timestamp: number;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  updateNotification: (id: string, updates: Partial<Notification>) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

const NotificationItem: React.FC<{
  notification: Notification;
  onClose: (id: string) => void;
}> = ({ notification, onClose }) => {
  const [open, setOpen] = useState(true);

  const handleClose = useCallback(() => {
    setOpen(false);
    setTimeout(() => onClose(notification.id), 300);
  }, [notification.id, onClose]);

  useEffect(() => {
    if (!notification.persistent && notification.duration !== 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, notification.duration || 5000);

      return () => clearTimeout(timer);
    }
  }, [notification.duration, notification.persistent, handleClose]);



      return (
      <Slide direction="left" in={open} timeout={300}>
        <Paper
          elevation={3}
          sx={{
            p: 2,
          mb: 2,
          width: '100%',
          backgroundColor: notification.type === 'error' ? 'error.main' : notification.type === 'warning' ? 'warning.main' : notification.type === 'success' ? 'success.main' : 'info.main',
          color: 'white',
          borderRadius: 4,
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" spacing={1} alignItems="center">
            <IconButton
              size="small"
              aria-label="close"
              color="inherit"
              onClick={handleClose}
            >
              <Close />
            </IconButton>
          </Stack>
          <Typography variant="h6">{notification.title}</Typography>
          {notification.action && (
            <IconButton
              size="small"
              aria-label="action"
              color="inherit"
              onClick={notification.action.onClick}
            >
              {notification.action.label}
            </IconButton>
          )}
        </Stack>
        <Typography variant="body1">{notification.message}</Typography>
        {typeof notification.progress === 'number' && (
          <Box sx={{ mt: 1 }}>
            <LinearProgress 
              variant="determinate" 
              value={notification.progress} 
              sx={{ height: 6, borderRadius: 3 }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
              <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>
                {notification.progress.toFixed(0)}% Complete
              </span>
              <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>
                {new Date(notification.timestamp).toLocaleTimeString()}
              </span>
            </Box>
          </Box>
                  )}
        </Paper>
      </Slide>
    );
};

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const notification: Notification = {
      ...notificationData,
      id,
      timestamp: Date.now(),
    };

    setNotifications(prev => [notification, ...prev]);
    return id;
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const updateNotification = useCallback((id: string, updates: Partial<Notification>) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, ...updates }
          : notification
      )
    );
  }, []);

  return (
    <NotificationContext.Provider value={{
      notifications,
      addNotification,
      removeNotification,
      clearAll,
      updateNotification
    }}>
      {children}
      
      {/* Notification Display */}
      <Box
        sx={{
          position: 'fixed',
          top: 80,
          right: 20,
          zIndex: 9999,
          maxWidth: 400,
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
        }}
      >
        <Stack spacing={1}>
          {notifications.slice(0, 5).map(notification => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onClose={removeNotification}
            />
          ))}
        </Stack>
      </Box>
    </NotificationContext.Provider>
  );
};

// Utility hooks for common notification patterns
export const useNotificationHelpers = () => {
  const { addNotification, updateNotification } = useNotifications();

  const showSuccess = useCallback((title: string, message?: string) => {
    return addNotification({
      type: 'success',
      title,
      message,
      duration: 4000
    });
  }, [addNotification]);

  const showError = useCallback((title: string, message?: string, persistent = true) => {
    return addNotification({
      type: 'error',
      title,
      message,
      persistent,
      duration: persistent ? 0 : 8000
    });
  }, [addNotification]);

  const showWarning = useCallback((title: string, message?: string) => {
    return addNotification({
      type: 'warning',
      title,
      message,
      duration: 6000
    });
  }, [addNotification]);

  const showInfo = useCallback((title: string, message?: string) => {
    return addNotification({
      type: 'info',
      title,
      message,
      duration: 5000
    });
  }, [addNotification]);

  const showProgress = useCallback((title: string, message?: string) => {
    return addNotification({
      type: 'info',
      title,
      message,
      persistent: true,
      progress: 0
    });
  }, [addNotification]);

  const updateProgress = useCallback((id: string, progress: number, message?: string) => {
    updateNotification(id, { 
      progress,
      ...(message && { message })
    });
  }, [updateNotification]);

  const completeProgress = useCallback((id: string, title?: string) => {
    updateNotification(id, {
      type: 'success',
      title: title || 'Completed!',
      progress: 100,
      persistent: false,
      duration: 3000
    });
  }, [updateNotification]);

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showProgress,
    updateProgress,
    completeProgress
  };
};

export const NotificationManager = {
  success: (message: string) => {
    console.log('Success:', message);
    // Add toast notification logic here if needed
  },
  error: (message: string) => {
    console.error('Error:', message);
    // Add toast notification logic here if needed
  },
  info: (message: string) => {
    console.log('Info:', message);
    // Add toast notification logic here if needed
  }
}; 