import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Alert,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { emergencyService } from '../services/emergencyService';
import { notificationService } from '../services/notificationService';
import { apiService } from '../services/apiService';

const EmergencySOSScreen: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [emergencyContacts, setEmergencyContacts] = useState<any[]>([]);
  const [firstAidRecommendations, setFirstAidRecommendations] = useState<any>(null);
  const [selectedEmergency, setSelectedEmergency] = useState<string>('');

  useEffect(() => {
    loadEmergencyContacts();
  }, []);

  const loadEmergencyContacts = async () => {
    const contacts = emergencyService.getEmergencyContacts();
    setEmergencyContacts(contacts);
  };

  const emergencyTypes = [
    { id: 'medical', label: 'Medical Emergency', icon: '🏥' },
    { id: 'accident', label: 'Car Accident', icon: '🚗' },
    { id: 'fire', label: 'Fire Emergency', icon: '🔥' },
    { id: 'crime', label: 'Crime/Safety', icon: '🚔' },
    { id: 'other', label: 'Other Emergency', icon: '⚠️' },
  ];

  const handleEmergencySelect = (emergencyType: string) => {
    setSelectedEmergency(emergencyType);
  };

  const handleTriggerSOS = async () => {
    if (!selectedEmergency) {
      Alert.alert('Select Emergency Type', 'Please select the type of emergency first.');
      return;
    }

    Alert.alert(
      'Confirm Emergency SOS',
      'This will send an emergency alert to authorities and your emergency contacts. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Send SOS',
          style: 'destructive',
          onPress: () => triggerEmergencySOS()
        }
      ]
    );
  };

  const triggerEmergencySOS = async () => {
    setIsLoading(true);

    try {
      const emergencyData = {
        type: selectedEmergency as 'medical' | 'accident' | 'fire' | 'crime' | 'other',
        description: `${selectedEmergency.charAt(0).toUpperCase() + selectedEmergency.slice(1)} emergency - Immediate assistance required`,
        severity: 'high' as 'low' | 'medium' | 'high' | 'critical',
      };

      const success = await emergencyService.triggerEmergencySOS(emergencyData);

      if (success) {
        // Get first aid recommendations
        const recommendations = await emergencyService.getFirstAidRecommendations(
          selectedEmergency,
          emergencyData.description
        );
        setFirstAidRecommendations(recommendations);
      }
    } catch (error) {
      console.error('SOS trigger error:', error);
      Alert.alert('Error', 'Failed to send emergency alert. Please call emergency services directly.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCallEmergency = () => {
    emergencyService.callEmergencyServices();
  };

  const handleGetFirstAid = async () => {
    if (!selectedEmergency) return;

    setIsLoading(true);
    try {
      const recommendations = await emergencyService.getFirstAidRecommendations(
        selectedEmergency,
        'General emergency assistance needed'
      );
      setFirstAidRecommendations(recommendations);
    } catch (error) {
      console.error('First aid error:', error);
      Alert.alert('Error', 'Could not load first aid recommendations.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Emergency SOS</Text>
        <Text style={styles.subtitle}>
          Tap the emergency button below to send an immediate alert to emergency services and your contacts.
        </Text>
      </View>

      {/* Emergency Type Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Select Emergency Type</Text>
        <View style={styles.emergencyGrid}>
          {emergencyTypes.map((emergency) => (
            <TouchableOpacity
              key={emergency.id}
              style={[
                styles.emergencyButton,
                selectedEmergency === emergency.id && styles.emergencyButtonSelected
              ]}
              onPress={() => handleEmergencySelect(emergency.id)}
            >
              <Text style={styles.emergencyIcon}>{emergency.icon}</Text>
              <Text style={styles.emergencyLabel}>{emergency.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* SOS Button */}
      <View style={styles.sosSection}>
        <TouchableOpacity
          style={[styles.sosButton, isLoading && styles.sosButtonDisabled]}
          onPress={handleTriggerSOS}
          disabled={isLoading || !selectedEmergency}
        >
          {isLoading ? (
            <ActivityIndicator color="white" size="large" />
          ) : (
            <>
              <Text style={styles.sosText}>SOS</Text>
              <Text style={styles.sosSubtext}>Send Emergency Alert</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.quickButton} onPress={handleCallEmergency}>
          <Text style={styles.quickButtonText}>📞 Call Emergency Services</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickButton}
          onPress={handleGetFirstAid}
          disabled={!selectedEmergency}
        >
          <Text style={[styles.quickButtonText, !selectedEmergency && styles.quickButtonDisabled]}>
            🩹 Get First Aid Help
          </Text>
        </TouchableOpacity>
      </View>

      {/* Emergency Contacts */}
      {emergencyContacts.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Emergency Contacts ({emergencyContacts.length})</Text>
          {emergencyContacts.map((contact) => (
            <View key={contact.id} style={styles.contactItem}>
              <Text style={styles.contactName}>{contact.name}</Text>
              <Text style={styles.contactPhone}>{contact.phone}</Text>
              <Text style={styles.contactRelation}>{contact.relationship}</Text>
            </View>
          ))}
        </View>
      )}

      {/* First Aid Recommendations */}
      {firstAidRecommendations && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>First Aid Recommendations</Text>

          {firstAidRecommendations.immediate_actions && (
            <View style={styles.firstAidSection}>
              <Text style={styles.firstAidTitle}>🚨 Immediate Actions:</Text>
              {firstAidRecommendations.immediate_actions.map((action: string, index: number) => (
                <Text key={index} style={styles.firstAidItem}>• {action}</Text>
              ))}
            </View>
          )}

          {firstAidRecommendations.do_not && (
            <View style={styles.firstAidSection}>
              <Text style={styles.firstAidTitle}>❌ Do Not:</Text>
              {firstAidRecommendations.do_not.map((item: string, index: number) => (
                <Text key={index} style={styles.firstAidItem}>• {item}</Text>
              ))}
            </View>
          )}

          {firstAidRecommendations.severity && (
            <View style={styles.severityBadge}>
              <Text style={styles.severityText}>
                Severity: {firstAidRecommendations.severity.toUpperCase()}
              </Text>
            </View>
          )}
        </View>
      )}

      {/* Emergency Information */}
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>Emergency Information</Text>
        <Text style={styles.infoText}>
          • This app will share your location with emergency services{'\n'}
          • Emergency contacts will be notified via SMS{'\n'}
          • First aid recommendations are AI-generated and should not replace professional medical advice{'\n'}
          • Always call emergency services (911/112) for serious situations
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#dc3545',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#6c757d',
    textAlign: 'center',
    lineHeight: 22,
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#343a40',
    marginBottom: 15,
  },
  emergencyGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  emergencyButton: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    borderWidth: 2,
    borderColor: '#dee2e6',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
  },
  emergencyButtonSelected: {
    backgroundColor: '#fff3cd',
    borderColor: '#ffc107',
  },
  emergencyIcon: {
    fontSize: 30,
    marginBottom: 5,
  },
  emergencyLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#495057',
    textAlign: 'center',
  },
  sosSection: {
    alignItems: 'center',
    padding: 20,
  },
  sosButton: {
    backgroundColor: '#dc3545',
    width: 150,
    height: 150,
    borderRadius: 75,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#dc3545',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  sosButtonDisabled: {
    backgroundColor: '#6c757d',
    shadowColor: '#6c757d',
  },
  sosText: {
    fontSize: 36,
    fontWeight: 'bold',
    color: 'white',
  },
  sosSubtext: {
    fontSize: 12,
    color: 'white',
    marginTop: 5,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 10,
  },
  quickButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
    minWidth: 150,
    alignItems: 'center',
  },
  quickButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  quickButtonDisabled: {
    backgroundColor: '#6c757d',
  },
  contactItem: {
    backgroundColor: '#f8f9fa',
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  contactName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#343a40',
  },
  contactPhone: {
    fontSize: 14,
    color: '#007bff',
  },
  contactRelation: {
    fontSize: 12,
    color: '#6c757d',
    fontStyle: 'italic',
  },
  firstAidSection: {
    marginBottom: 15,
  },
  firstAidTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#dc3545',
    marginBottom: 8,
  },
  firstAidItem: {
    fontSize: 14,
    color: '#495057',
    marginBottom: 4,
    lineHeight: 20,
  },
  severityBadge: {
    backgroundColor: '#dc3545',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    alignSelf: 'flex-start',
  },
  severityText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  infoSection: {
    backgroundColor: '#fff3cd',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ffeaa7',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#856404',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    color: '#856404',
    lineHeight: 20,
  },
});

export default EmergencySOSScreen;