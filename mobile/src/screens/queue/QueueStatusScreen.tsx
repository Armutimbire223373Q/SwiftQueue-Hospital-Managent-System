import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList, QueueEntry } from '../../types';
import { apiService } from '../../services/api';

type QueueStatusScreenNavigationProp = StackNavigationProp<RootStackParamList, 'QueueStatus'>;
type QueueStatusScreenRouteProp = RouteProp<RootStackParamList, 'QueueStatus'>;

const QueueStatusScreen = () => {
  const navigation = useNavigation<QueueStatusScreenNavigationProp>();
  const route = useRoute<QueueStatusScreenRouteProp>();
  const { queueId } = route.params;

  const [queueEntry, setQueueEntry] = useState<QueueEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadQueueStatus();

    // Set up polling for real-time updates every 30 seconds
    const interval = setInterval(loadQueueStatus, 30000);
    return () => clearInterval(interval);
  }, [queueId]);

  const loadQueueStatus = async () => {
    try {
      setRefreshing(true);
      const response = await apiService.getQueueStatus(queueId);

      if (response.success && response.data) {
        setQueueEntry(response.data);
      } else {
        Alert.alert('Error', 'Failed to load queue status. Please try again.');
      }
    } catch (error) {
      console.error('Error loading queue status:', error);
      Alert.alert('Error', 'Network error. Please check your connection.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadQueueStatus();
  };

  const handleLeaveQueue = () => {
    Alert.alert(
      'Leave Queue',
      'Are you sure you want to leave the queue? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Leave Queue',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await apiService.leaveQueue(queueId);
              if (response.success) {
                Alert.alert('Success', 'You have left the queue.', [
                  { text: 'OK', onPress: () => navigation.goBack() }
                ]);
              } else {
                Alert.alert('Error', 'Failed to leave queue. Please try again.');
              }
            } catch (error) {
              Alert.alert('Error', 'Network error. Please try again.');
            }
          }
        }
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'waiting': return '#f59e0b';
      case 'called': return '#3b82f6';
      case 'serving': return '#10b981';
      case 'completed': return '#6b7280';
      case 'cancelled': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'waiting': return 'Waiting in Queue';
      case 'called': return 'Your Turn!';
      case 'serving': return 'Being Served';
      case 'completed': return 'Completed';
      case 'cancelled': return 'Cancelled';
      default: return 'Unknown Status';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'waiting': return '⏳';
      case 'called': return '📢';
      case 'serving': return '👨‍⚕️';
      case 'completed': return '✅';
      case 'cancelled': return '❌';
      default: return '❓';
    }
  };

  const getEstimatedWaitTime = () => {
    if (!queueEntry) return 'N/A';

    const position = queueEntry.position;
    const avgServiceTime = 15; // Assume 15 minutes per patient
    const estimatedMinutes = position * avgServiceTime;

    if (estimatedMinutes < 60) {
      return `${estimatedMinutes} minutes`;
    } else {
      const hours = Math.floor(estimatedMinutes / 60);
      const minutes = estimatedMinutes % 60;
      return `${hours}h ${minutes}m`;
    }
  };

  const getTimeElapsed = () => {
    if (!queueEntry?.joined_at) return 'N/A';

    const joinedTime = new Date(queueEntry.joined_at);
    const now = new Date();
    const elapsedMs = now.getTime() - joinedTime.getTime();
    const elapsedMinutes = Math.floor(elapsedMs / (1000 * 60));

    if (elapsedMinutes < 60) {
      return `${elapsedMinutes} minutes ago`;
    } else {
      const hours = Math.floor(elapsedMinutes / 60);
      const minutes = elapsedMinutes % 60;
      return `${hours}h ${minutes}m ago`;
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563eb" />
          <Text style={styles.loadingText}>Loading queue status...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!queueEntry) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>Queue entry not found</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => navigation.goBack()}>
            <Text style={styles.retryButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Queue Status</Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={handleRefresh}
          disabled={refreshing}
        >
          <Text style={styles.refreshButtonText}>
            {refreshing ? '⟳' : '🔄'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        {/* Status Card */}
        <View style={styles.statusCard}>
          <View style={styles.statusHeader}>
            <Text style={[styles.statusIcon, { color: getStatusColor(queueEntry.status) }]}>
              {getStatusIcon(queueEntry.status)}
            </Text>
            <View style={styles.statusInfo}>
              <Text style={styles.queueNumber}>#{queueEntry.queue_number}</Text>
              <Text style={[styles.statusText, { color: getStatusColor(queueEntry.status) }]}>
                {getStatusText(queueEntry.status)}
              </Text>
            </View>
          </View>

          {queueEntry.status === 'called' && (
            <View style={styles.alertCard}>
              <Text style={styles.alertText}>
                🎉 It's your turn! Please proceed to {queueEntry.service_name}.
              </Text>
            </View>
          )}
        </View>

        {/* Queue Information */}
        <View style={styles.infoCard}>
          <Text style={styles.cardTitle}>Queue Information</Text>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Service:</Text>
            <Text style={styles.infoValue}>{queueEntry.service_name}</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Current Position:</Text>
            <Text style={styles.infoValue}>#{queueEntry.position}</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Priority:</Text>
            <Text style={[styles.infoValue, styles.priorityText]}>
              {queueEntry.priority.charAt(0).toUpperCase() + queueEntry.priority.slice(1)}
            </Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Joined:</Text>
            <Text style={styles.infoValue}>{getTimeElapsed()}</Text>
          </View>

          {queueEntry.status === 'waiting' && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Estimated Wait:</Text>
              <Text style={styles.infoValue}>{getEstimatedWaitTime()}</Text>
            </View>
          )}
        </View>

        {/* Instructions */}
        <View style={styles.instructionsCard}>
          <Text style={styles.cardTitle}>Instructions</Text>

          {queueEntry.status === 'waiting' && (
            <Text style={styles.instructionsText}>
              • Stay in the waiting area{'\n'}
              • Monitor your position regularly{'\n'}
              • You will be called when it's your turn{'\n'}
              • Please be patient and maintain social distancing
            </Text>
          )}

          {queueEntry.status === 'called' && (
            <Text style={styles.instructionsText}>
              • Proceed immediately to {queueEntry.service_name}{'\n'}
              • Show your queue number to the staff{'\n'}
              • If you miss your turn, you may need to rejoin the queue
            </Text>
          )}

          {queueEntry.status === 'serving' && (
            <Text style={styles.instructionsText}>
              • You are currently being served{'\n'}
              • Please wait for the healthcare provider{'\n'}
              • Follow all instructions from medical staff
            </Text>
          )}

          {queueEntry.status === 'completed' && (
            <Text style={styles.instructionsText}>
              • Your visit has been completed{'\n'}
              • Thank you for choosing our healthcare services{'\n'}
              • Please don't forget to collect any reports or medications
            </Text>
          )}
        </View>

        {/* Actions */}
        {queueEntry.status === 'waiting' && (
          <View style={styles.actionsCard}>
            <TouchableOpacity style={styles.leaveButton} onPress={handleLeaveQueue}>
              <Text style={styles.leaveButtonText}>Leave Queue</Text>
            </TouchableOpacity>
          </View>
        )}

        {queueEntry.status === 'completed' && (
          <View style={styles.actionsCard}>
            <TouchableOpacity
              style={styles.doneButton}
              onPress={() => navigation.popToTop()}
            >
              <Text style={styles.doneButtonText}>Done</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  refreshButton: {
    padding: 8,
  },
  refreshButtonText: {
    fontSize: 18,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  errorText: {
    fontSize: 18,
    color: '#6b7280',
    marginBottom: 24,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#2563eb',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  statusCard: {
    backgroundColor: '#ffffff',
    padding: 24,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    fontSize: 48,
    marginRight: 16,
  },
  statusInfo: {
    flex: 1,
  },
  queueNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
  },
  alertCard: {
    backgroundColor: '#fef3c7',
    padding: 16,
    borderRadius: 8,
    marginTop: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b',
  },
  alertText: {
    fontSize: 16,
    color: '#92400e',
    fontWeight: '600',
  },
  infoCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  infoLabel: {
    fontSize: 16,
    color: '#6b7280',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 16,
    color: '#1f2937',
    fontWeight: '600',
  },
  priorityText: {
    textTransform: 'capitalize',
  },
  instructionsCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instructionsText: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
  },
  actionsCard: {
    padding: 16,
  },
  leaveButton: {
    backgroundColor: '#dc2626',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  leaveButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  doneButton: {
    backgroundColor: '#16a34a',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  doneButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default QueueStatusScreen;