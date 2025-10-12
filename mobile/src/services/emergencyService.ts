import * as Location from 'expo-location';
import { Alert, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from './apiService';
import { notificationService } from './notificationService';

export interface EmergencyContact {
  id: string;
  name: string;
  phone: string;
  relationship: string;
}

export interface EmergencyData {
  type: 'medical' | 'accident' | 'fire' | 'crime' | 'other';
  description: string;
  location?: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  severity: 'low' | 'medium' | 'high' | 'critical';
  symptoms?: string[];
  medicalConditions?: string[];
}

class EmergencyService {
  private emergencyContacts: EmergencyContact[] = [];
  private isEmergencyActive = false;

  constructor() {
    this.loadEmergencyContacts();
  }

  // Load emergency contacts from storage
  async loadEmergencyContacts(): Promise<void> {
    try {
      const contacts = await AsyncStorage.getItem('emergencyContacts');
      if (contacts) {
        this.emergencyContacts = JSON.parse(contacts);
      }
    } catch (error) {
      console.error('Error loading emergency contacts:', error);
    }
  }

  // Save emergency contacts to storage
  async saveEmergencyContacts(): Promise<void> {
    try {
      await AsyncStorage.setItem('emergencyContacts', JSON.stringify(this.emergencyContacts));
    } catch (error) {
      console.error('Error saving emergency contacts:', error);
    }
  }

  // Add emergency contact
  async addEmergencyContact(contact: Omit<EmergencyContact, 'id'>): Promise<void> {
    const newContact: EmergencyContact = {
      ...contact,
      id: Date.now().toString(),
    };

    this.emergencyContacts.push(newContact);
    await this.saveEmergencyContacts();
  }

  // Remove emergency contact
  async removeEmergencyContact(contactId: string): Promise<void> {
    this.emergencyContacts = this.emergencyContacts.filter(c => c.id !== contactId);
    await this.saveEmergencyContacts();
  }

  // Get all emergency contacts
  getEmergencyContacts(): EmergencyContact[] {
    return this.emergencyContacts;
  }

  // Get current location
  async getCurrentLocation(): Promise<{latitude: number; longitude: number; address?: string} | null> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Location permission is required for emergency services');
        return null;
      }

      const location = await Location.getCurrentPositionAsync({});
      const { latitude, longitude } = location.coords;

      // Try to get address
      let address: string | undefined;
      try {
        const addresses = await Location.reverseGeocodeAsync({ latitude, longitude });
        if (addresses.length > 0) {
          const addr = addresses[0];
          address = `${addr.street || ''} ${addr.city || ''} ${addr.region || ''} ${addr.postalCode || ''}`.trim();
        }
      } catch (error) {
        console.warn('Could not reverse geocode location:', error);
      }

      return { latitude, longitude, address };
    } catch (error) {
      console.error('Error getting location:', error);
      return null;
    }
  }

  // Trigger emergency SOS
  async triggerEmergencySOS(emergencyData: EmergencyData): Promise<boolean> {
    try {
      if (this.isEmergencyActive) {
        Alert.alert('Emergency Already Active', 'An emergency alert is already in progress.');
        return false;
      }

      this.isEmergencyActive = true;

      // Get current location
      const location = await this.getCurrentLocation();

      const fullEmergencyData = {
        ...emergencyData,
        location: location || undefined,
        timestamp: new Date().toISOString(),
        deviceInfo: {
          platform: Platform.OS,
          version: Platform.Version,
        }
      };

      // Send emergency alert to backend
      const response = await apiService.post('/api/emergency/sos', fullEmergencyData);

      if (response.success) {
        // Send local notification
        await notificationService.sendLocalNotification({
          type: 'emergency_alert',
          title: '🚨 EMERGENCY ALERT SENT',
          message: 'Emergency services have been notified. Help is on the way.',
          data: fullEmergencyData,
          priority: 'max'
        });

        // Send SMS to emergency contacts if configured
        await this.notifyEmergencyContacts(fullEmergencyData);

        Alert.alert(
          'Emergency Alert Sent',
          'Emergency services have been notified. Stay calm and follow any instructions provided.',
          [{ text: 'OK' }]
        );

        return true;
      } else {
        throw new Error(response.error || 'Failed to send emergency alert');
      }

    } catch (error) {
      console.error('Emergency SOS failed:', error);
      Alert.alert(
        'Emergency Alert Failed',
        'Could not send emergency alert. Please call emergency services directly: 911/112',
        [{ text: 'Call Now', onPress: () => this.callEmergencyServices() }]
      );
      return false;
    } finally {
      this.isEmergencyActive = false;
    }
  }

  // Notify emergency contacts via SMS
  private async notifyEmergencyContacts(emergencyData: any): Promise<void> {
    if (this.emergencyContacts.length === 0) return;

    const message = `EMERGENCY ALERT: ${emergencyData.description}. Location: ${emergencyData.location?.address || 'Unknown'}. Please contact immediately.`;

    for (const contact of this.emergencyContacts) {
      try {
        await apiService.post('/api/emergency/sms/send', {
          phone_number: contact.phone,
          message: `URGENT: ${contact.name}, ${message}`,
          priority: 'high'
        });
      } catch (error) {
        console.error(`Failed to notify ${contact.name}:`, error);
      }
    }
  }

  // Call emergency services directly
  callEmergencyServices(): void {
    const emergencyNumber = Platform.OS === 'ios' ? 'tel:911' : 'tel:112';

    // Note: In a real app, you'd use Linking.openURL(emergencyNumber)
    // For demo purposes, we'll show an alert
    Alert.alert(
      'Call Emergency Services',
      'Dial 911 (US) or 112 (Europe) immediately',
      [
        { text: 'Cancel' },
        {
          text: 'Call Now',
          onPress: () => {
            // In production: Linking.openURL(emergencyNumber)
            console.log('Calling emergency services:', emergencyNumber);
          }
        }
      ]
    );
  }

  // Get first aid recommendations
  async getFirstAidRecommendations(emergencyType: string, symptoms: string): Promise<any> {
    try {
      const response = await apiService.post('/api/ai/emergency/first-aid', {
        emergency_type: emergencyType,
        symptoms: symptoms,
        use_network_ai: true // Use network AI when available
      });

      if (response.success) {
        return response.first_aid_procedures;
      } else {
        throw new Error(response.error || 'Failed to get first aid recommendations');
      }
    } catch (error) {
      console.error('Error getting first aid recommendations:', error);
      return this.getOfflineFirstAid(emergencyType);
    }
  }

  // Offline first aid fallback
  private getOfflineFirstAid(emergencyType: string): any {
    const offlineAdvice: Record<string, any> = {
      cardiac_arrest: {
        immediate_actions: [
          "Call emergency services immediately (911/112)",
          "Start CPR if trained: 30 compressions, 2 breaths",
          "Use AED if available"
        ],
        do_not: [
          "Do not leave person alone",
          "Do not give up CPR"
        ],
        severity: "critical"
      },
      bleeding: {
        immediate_actions: [
          "Apply direct pressure to wound",
          "Elevate injured area",
          "Call emergency services"
        ],
        do_not: [
          "Do not remove blood-soaked cloth",
          "Do not apply tourniquet unless trained"
        ],
        severity: "high"
      },
      choking: {
        immediate_actions: [
          "Perform Heimlich maneuver if trained",
          "Call emergency services",
          "For children: 5 back blows, 5 chest thrusts"
        ],
        do_not: [
          "Do not perform if person can breathe",
          "Do not leave alone"
        ],
        severity: "high"
      }
    };

    return offlineAdvice[emergencyType] || {
      immediate_actions: [
        "Call emergency services immediately",
        "Ensure safety",
        "Stay with person"
      ],
      do_not: [
        "Do not attempt complex procedures",
        "Do not give food/drink"
      ],
      severity: "unknown"
    };
  }

  // Check if emergency is active
  isEmergencyActiveStatus(): boolean {
    return this.isEmergencyActive;
  }

  // Cancel active emergency
  cancelEmergency(): void {
    this.isEmergencyActive = false;
  }
}

export const emergencyService = new EmergencyService();