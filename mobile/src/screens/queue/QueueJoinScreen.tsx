import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { RootStackParamList, Service, QueueJoinData, QueueEntry } from '../../types';

type QueueJoinScreenNavigationProp = StackNavigationProp<RootStackParamList, 'QueueJoin'>;
type QueueJoinScreenRouteProp = RouteProp<RootStackParamList, 'QueueJoin'>;

const QueueJoinScreen = () => {
  const navigation = useNavigation<QueueJoinScreenNavigationProp>();
  const route = useRoute<QueueJoinScreenRouteProp>();
  const { user } = useAuth();

  const [step, setStep] = useState<'service' | 'details' | 'confirmation'>('service');
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form data
  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(
    route.params?.serviceId || null
  );
  const [symptoms, setSymptoms] = useState('');
  const [priority, setPriority] = useState<'low' | 'normal' | 'high' | 'urgent'>('normal');
  const [patientName, setPatientName] = useState(user?.name || '');
  const [patientPhone, setPatientPhone] = useState('');
  const [patientEmail, setPatientEmail] = useState(user?.email || '');
  const [dateOfBirth, setDateOfBirth] = useState('');

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      setLoading(true);
      const response = await apiService.getServices();
      if (response.success) {
        setServices(response.data || []);
      } else {
        Alert.alert('Error', 'Failed to load services. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const validateStep = (currentStep: string) => {
    switch (currentStep) {
      case 'service':
        if (!selectedServiceId) {
          Alert.alert('Error', 'Please select a service');
          return false;
        }
        return true;
      case 'details':
        if (!symptoms.trim()) {
          Alert.alert('Error', 'Please describe your symptoms');
          return false;
        }
        if (!patientName.trim() || !patientPhone.trim() || !patientEmail.trim()) {
          Alert.alert('Error', 'Please fill in all personal information');
          return false;
        }
        return true;
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateStep(step)) {
      if (step === 'service') setStep('details');
      else if (step === 'details') setStep('confirmation');
    }
  };

  const handleBack = () => {
    if (step === 'details') setStep('service');
    else if (step === 'confirmation') setStep('details');
  };

  const handleJoinQueue = async () => {
    if (!validateStep('details')) return;

    try {
      setSubmitting(true);

      const queueData: QueueJoinData = {
        service_id: selectedServiceId!,
        symptoms: symptoms.trim(),
        priority,
        patient_details: {
          name: patientName.trim(),
          phone: patientPhone.trim(),
          email: patientEmail.trim(),
          date_of_birth: dateOfBirth.trim() || undefined,
        },
      };

      const response = await apiService.joinQueue(queueData);

      if (response.success && response.data) {
        // Navigate to queue status screen
        navigation.replace('QueueStatus', { queueId: response.data.id });
      } else {
        Alert.alert('Error', response.error || 'Failed to join queue. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const selectedService = services.find(s => s.id === selectedServiceId);

  const renderServiceStep = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Select a Service</Text>
      <Text style={styles.stepSubtitle}>Choose the healthcare service you need</Text>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563eb" />
          <Text style={styles.loadingText}>Loading services...</Text>
        </View>
      ) : (
        <View style={styles.servicesList}>
          {services.map((service) => (
            <TouchableOpacity
              key={service.id}
              style={[
                styles.serviceCard,
                selectedServiceId === service.id && styles.serviceCardSelected,
              ]}
              onPress={() => setSelectedServiceId(service.id)}
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
                {selectedServiceId === service.id && (
                  <Text style={styles.selectedText}>✓ Selected</Text>
                )}
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );

  const renderDetailsStep = () => (
    <ScrollView style={styles.stepContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.stepTitle}>Provide Details</Text>
      <Text style={styles.stepSubtitle}>Help us understand your healthcare needs</Text>

      <View style={styles.formSection}>
        <Text style={styles.sectionLabel}>Priority Level</Text>
        <View style={styles.pickerContainer}>
          <Picker
            selectedValue={priority}
            onValueChange={(value: 'low' | 'normal' | 'high' | 'urgent') => setPriority(value)}
            style={styles.picker}
          >
            <Picker.Item label="Low Priority" value="low" />
            <Picker.Item label="Normal Priority" value="normal" />
            <Picker.Item label="High Priority" value="high" />
            <Picker.Item label="Urgent (Emergency)" value="urgent" />
          </Picker>
        </View>
      </View>

      <View style={styles.formSection}>
        <Text style={styles.sectionLabel}>Describe Your Symptoms</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={symptoms}
          onChangeText={setSymptoms}
          placeholder="Please describe your symptoms, pain level, and any other relevant information..."
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />
      </View>

      <View style={styles.formSection}>
        <Text style={styles.sectionLabel}>Personal Information</Text>

        <TextInput
          style={styles.input}
          value={patientName}
          onChangeText={setPatientName}
          placeholder="Full Name"
        />

        <TextInput
          style={styles.input}
          value={patientPhone}
          onChangeText={setPatientPhone}
          placeholder="Phone Number"
          keyboardType="phone-pad"
        />

        <TextInput
          style={styles.input}
          value={patientEmail}
          onChangeText={setPatientEmail}
          placeholder="Email Address"
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <TextInput
          style={styles.input}
          value={dateOfBirth}
          onChangeText={setDateOfBirth}
          placeholder="Date of Birth (YYYY-MM-DD)"
          keyboardType="numeric"
        />
      </View>
    </ScrollView>
  );

  const renderConfirmationStep = () => (
    <ScrollView style={styles.stepContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.stepTitle}>Confirm Queue Entry</Text>
      <Text style={styles.stepSubtitle}>Please review your information before joining</Text>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Service Selected</Text>
        <Text style={styles.confirmationValue}>{selectedService?.name}</Text>
        <Text style={styles.confirmationSubtitle}>{selectedService?.department}</Text>
      </View>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Priority Level</Text>
        <Text style={[styles.confirmationValue, getPriorityStyle(priority)]}>
          {priority.charAt(0).toUpperCase() + priority.slice(1)} Priority
        </Text>
      </View>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Symptoms</Text>
        <Text style={styles.confirmationValue}>{symptoms}</Text>
      </View>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Personal Information</Text>
        <Text style={styles.confirmationValue}>{patientName}</Text>
        <Text style={styles.confirmationSubtitle}>{patientPhone}</Text>
        <Text style={styles.confirmationSubtitle}>{patientEmail}</Text>
        {dateOfBirth && <Text style={styles.confirmationSubtitle}>DOB: {dateOfBirth}</Text>}
      </View>

      <View style={styles.disclaimer}>
        <Text style={styles.disclaimerText}>
          By joining the queue, you agree to provide accurate information.
          Emergency cases will be prioritized appropriately.
        </Text>
      </View>
    </ScrollView>
  );

  const renderStepIndicator = () => (
    <View style={styles.stepIndicator}>
      {(['service', 'details', 'confirmation'] as const).map((stepName, index) => (
        <View key={stepName} style={styles.stepItem}>
          <View
            style={[
              styles.stepCircle,
              step === stepName && styles.stepCircleActive,
              (stepName === 'service' && step !== 'service') ||
              (stepName === 'details' && ['details', 'confirmation'].includes(step)) ||
              (stepName === 'confirmation' && step === 'confirmation')
                ? styles.stepCircleCompleted
                : null,
            ]}
          >
            <Text
              style={[
                styles.stepNumber,
                (step === stepName || getStepIndex(stepName) < getStepIndex(step))
                  ? styles.stepNumberActive
                  : null,
              ]}
            >
              {index + 1}
            </Text>
          </View>
          <Text
            style={[
              styles.stepLabel,
              step === stepName ? styles.stepLabelActive : null,
            ]}
          >
            {stepName.charAt(0).toUpperCase() + stepName.slice(1)}
          </Text>
        </View>
      ))}
    </View>
  );

  const getStepIndex = (stepName: string) => {
    const steps = ['service', 'details', 'confirmation'];
    return steps.indexOf(stepName);
  };

  const getPriorityStyle = (priority: string) => {
    switch (priority) {
      case 'urgent': return styles.priorityUrgent;
      case 'high': return styles.priorityHigh;
      case 'normal': return styles.priorityNormal;
      case 'low': return styles.priorityLow;
      default: return styles.priorityNormal;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Join Queue</Text>
      </View>

      {renderStepIndicator()}

      <View style={styles.content}>
        {step === 'service' && renderServiceStep()}
        {step === 'details' && renderDetailsStep()}
        {step === 'confirmation' && renderConfirmationStep()}
      </View>

      <View style={styles.footer}>
        {step !== 'service' && (
          <TouchableOpacity style={styles.backButton} onPress={handleBack}>
            <Text style={styles.backButtonText}>Back</Text>
          </TouchableOpacity>
        )}

        {step !== 'confirmation' ? (
          <TouchableOpacity
            style={[styles.nextButton, !selectedServiceId && styles.buttonDisabled]}
            onPress={handleNext}
            disabled={!selectedServiceId && step === 'service'}
          >
            <Text style={styles.nextButtonText}>Next</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={[styles.joinButton, submitting && styles.buttonDisabled]}
            onPress={handleJoinQueue}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.joinButtonText}>Join Queue</Text>
            )}
          </TouchableOpacity>
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
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
  },
  stepIndicator: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    paddingHorizontal: 24,
    backgroundColor: '#ffffff',
  },
  stepItem: {
    alignItems: 'center',
  },
  stepCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#e5e7eb',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  stepCircleActive: {
    backgroundColor: '#2563eb',
  },
  stepCircleCompleted: {
    backgroundColor: '#16a34a',
  },
  stepNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#6b7280',
  },
  stepNumberActive: {
    color: '#ffffff',
  },
  stepLabel: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '500',
  },
  stepLabelActive: {
    color: '#2563eb',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  stepContent: {
    flex: 1,
  },
  stepTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  stepSubtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 24,
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
  servicesList: {
    gap: 12,
  },
  serviceCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  serviceCardSelected: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
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
  selectedText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2563eb',
  },
  formSection: {
    marginBottom: 24,
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    backgroundColor: '#ffffff',
  },
  picker: {
    height: 50,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#ffffff',
    marginBottom: 12,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  confirmationCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  confirmationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 4,
  },
  confirmationValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  confirmationSubtitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  priorityUrgent: {
    color: '#dc2626',
  },
  priorityHigh: {
    color: '#d97706',
  },
  priorityNormal: {
    color: '#2563eb',
  },
  priorityLow: {
    color: '#6b7280',
  },
  disclaimer: {
    backgroundColor: '#fef3c7',
    padding: 16,
    borderRadius: 8,
    marginTop: 16,
  },
  disclaimerText: {
    fontSize: 14,
    color: '#92400e',
    textAlign: 'center',
    lineHeight: 20,
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  backButton: {
    flex: 1,
    backgroundColor: '#f3f4f6',
    paddingVertical: 16,
    borderRadius: 8,
    marginRight: 8,
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  nextButton: {
    flex: 2,
    backgroundColor: '#2563eb',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  nextButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  joinButton: {
    flex: 1,
    backgroundColor: '#16a34a',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  joinButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
});

export default QueueJoinScreen;