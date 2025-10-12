import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { CompositeNavigationProp } from '@react-navigation/native';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { StackNavigationProp } from '@react-navigation/stack';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { RootStackParamList, MainTabParamList, Service, QueueEntry } from '../../types';

type HomeScreenTabProp = BottomTabNavigationProp<MainTabParamList, 'Home'>;
type HomeScreenStackProp = StackNavigationProp<RootStackParamList>;
type HomeScreenNavigationProp = CompositeNavigationProp<HomeScreenTabProp, HomeScreenStackProp>;

const HomeScreen = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const { user } = useAuth();

  const [services, setServices] = useState<Service[]>([]);
  const [recentQueues, setRecentQueues] = useState<QueueEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load services
      const servicesResponse = await apiService.getServices();
      if (servicesResponse.success) {
        setServices(servicesResponse.data || []);
      }

      // Load user's recent queues
      const queuesResponse = await apiService.getUserQueues();
      if (queuesResponse.success) {
        setRecentQueues((queuesResponse.data || []).slice(0, 3)); // Show last 3
      }
    } catch (error) {
      console.error('Error loading home data:', error);
      Alert.alert('Error', 'Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleServicePress = (service: Service) => {
    // Navigate to QueueJoin in the parent stack navigator
    navigation.getParent()?.navigate('QueueJoin', { serviceId: service.id });
  };

  const handleQueuePress = (queue: QueueEntry) => {
    navigation.getParent()?.navigate('QueueStatus', { queueId: queue.id });
  };

  const handleEmergencyPress = () => {
    Alert.alert(
      'Emergency Assistance',
      'This will alert hospital staff for immediate assistance. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Call for Help',
          style: 'destructive',
          onPress: () => {
            // In a real app, this would trigger emergency services
            Alert.alert('Emergency Alert Sent', 'Hospital staff has been notified.');
          }
        }
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.greeting}>Hello, {user?.name || 'Patient'}</Text>
          <Text style={styles.subtitle}>How can we help you today?</Text>
        </View>

        {/* Emergency Button */}
        <TouchableOpacity style={styles.emergencyButton} onPress={handleEmergencyPress}>
          <Text style={styles.emergencyButtonText}>🚨 Emergency Assistance</Text>
          <Text style={styles.emergencyButtonSubtext}>Tap for immediate help</Text>
        </TouchableOpacity>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActions}>
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => navigation.getParent()?.navigate('QueueJoin')}
            >
              <Text style={styles.quickActionIcon}>📋</Text>
              <Text style={styles.quickActionText}>Join Queue</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => navigation.getParent()?.navigate('AppointmentBooking')}
            >
              <Text style={styles.quickActionIcon}>📅</Text>
              <Text style={styles.quickActionText}>Book Appointment</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Services */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Available Services</Text>
          <View style={styles.servicesList}>
            {services.slice(0, 4).map((service) => (
              <TouchableOpacity
                key={service.id}
                style={styles.serviceCard}
                onPress={() => handleServicePress(service)}
              >
                <View style={styles.serviceHeader}>
                  <Text style={styles.serviceName}>{service.name}</Text>
                  <Text style={styles.serviceDepartment}>{service.department}</Text>
                </View>
                <Text style={styles.serviceDescription} numberOfLines={2}>
                  {service.description}
                </Text>
                <View style={styles.serviceFooter}>
                  <Text style={styles.waitTime}>
                    Est. wait: {service.estimated_wait_time}min
                  </Text>
                  <Text style={styles.joinButton}>Join →</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Recent Queues */}
        {recentQueues.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Activity</Text>
            <View style={styles.recentQueues}>
              {recentQueues.map((queue) => (
                <TouchableOpacity
                  key={queue.id}
                  style={styles.queueCard}
                  onPress={() => handleQueuePress(queue)}
                >
                  <View style={styles.queueHeader}>
                    <Text style={styles.queueNumber}>#{queue.queue_number}</Text>
                    <Text style={[styles.queueStatus, getStatusStyle(queue.status)]}>
                      {queue.status}
                    </Text>
                  </View>
                  <Text style={styles.queueService}>{queue.service_name}</Text>
                  <Text style={styles.queueTime}>
                    Position: {queue.position} • Joined: {new Date(queue.joined_at).toLocaleDateString()}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const getStatusStyle = (status: string) => {
  switch (status) {
    case 'waiting':
      return styles.statusWaiting;
    case 'called':
      return styles.statusCalled;
    case 'serving':
      return styles.statusServing;
    case 'completed':
      return styles.statusCompleted;
    default:
      return styles.statusDefault;
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#64748b',
  },
  header: {
    padding: 24,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
  emergencyButton: {
    backgroundColor: '#dc2626',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#dc2626',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  emergencyButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  emergencyButtonSubtext: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.9,
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    backgroundColor: '#ffffff',
    flex: 1,
    marginHorizontal: 4,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  servicesList: {
    gap: 12,
  },
  serviceCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    flex: 1,
  },
  serviceDepartment: {
    fontSize: 12,
    color: '#6b7280',
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  serviceDescription: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 12,
    lineHeight: 20,
  },
  serviceFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  waitTime: {
    fontSize: 12,
    color: '#6b7280',
  },
  joinButton: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2563eb',
  },
  recentQueues: {
    gap: 8,
  },
  queueCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  queueHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  queueNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  queueStatus: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    textTransform: 'uppercase',
  },
  statusWaiting: {
    backgroundColor: '#fef3c7',
    color: '#d97706',
  },
  statusCalled: {
    backgroundColor: '#dbeafe',
    color: '#2563eb',
  },
  statusServing: {
    backgroundColor: '#dcfce7',
    color: '#16a34a',
  },
  statusCompleted: {
    backgroundColor: '#f3f4f6',
    color: '#6b7280',
  },
  statusDefault: {
    backgroundColor: '#f3f4f6',
    color: '#6b7280',
  },
  queueService: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4,
  },
  queueTime: {
    fontSize: 12,
    color: '#6b7280',
  },
});

export default HomeScreen;