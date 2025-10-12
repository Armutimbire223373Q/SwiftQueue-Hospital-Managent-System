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
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { Picker } from '@react-native-picker/picker';
import Modal from 'react-native-modal';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { RootStackParamList, Service, AppointmentBookingData } from '../../types';

type AppointmentBookingScreenNavigationProp = StackNavigationProp<RootStackParamList, 'AppointmentBooking'>;

const AppointmentBookingScreen = () => {
  const navigation = useNavigation<AppointmentBookingScreenNavigationProp>();
  const { user } = useAuth();

  const [step, setStep] = useState<'service' | 'datetime' | 'details' | 'confirmation'>('service');
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form data
  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [patientName, setPatientName] = useState(user?.name || '');
  const [patientPhone, setPatientPhone] = useState('');
  const [patientEmail, setPatientEmail] = useState(user?.email || '');

  // UI state
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [availableTimeSlots, setAvailableTimeSlots] = useState<string[]>([]);

  useEffect(() => {
    loadServices();
  }, []);

  useEffect(() => {
    if (selectedDate && selectedServiceId) {
      loadAvailableTimeSlots();
    }
  }, [selectedDate, selectedServiceId]);

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

  const loadAvailableTimeSlots = async () => {
    // Generate time slots for the selected date
    const slots: string[] = [];
    const startHour = 9; // 9 AM
    const endHour = 17; // 5 PM

    for (let hour = startHour; hour < endHour; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        slots.push(timeString);
      }
    }

    setAvailableTimeSlots(slots);
  };

  const validateStep = (currentStep: string) => {
    switch (currentStep) {
      case 'service':
        if (!selectedServiceId) {
          Alert.alert('Error', 'Please select a service');
          return false;
        }
        return true;
      case 'datetime':
        if (!selectedDate) {
          Alert.alert('Error', 'Please select a date');
          return false;
        }
        if (!selectedTime) {
          Alert.alert('Error', 'Please select a time');
          return false;
        }
        return true;
      case 'details':
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
      if (step === 'service') setStep('datetime');
      else if (step === 'datetime') setStep('details');
      else if (step === 'details') setStep('confirmation');
    }
  };

  const handleBack = () => {
    if (step === 'datetime') setStep('service');
    else if (step === 'details') setStep('datetime');
    else if (step === 'confirmation') setStep('details');
  };

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setShowDatePicker(false);
  };

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time);
  };

  const handleBookAppointment = async () => {
    if (!validateStep('details')) return;

    try {
      setSubmitting(true);

      const appointmentData: AppointmentBookingData = {
        service_id: selectedServiceId!,
        appointment_date: selectedDate!.toISOString().split('T')[0],
        appointment_time: selectedTime,
        notes: notes.trim() || undefined,
      };

      const response = await apiService.bookAppointment(appointmentData);

      if (response.success && response.data) {
        Alert.alert(
          'Success',
          'Appointment booked successfully!',
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack()
            }
          ]
        );
      } else {
        Alert.alert('Error', response.error || 'Failed to book appointment. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (date: Date | null) => {
    if (!date) return 'Select Date';
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const generateDateOptions = () => {
    const dates = [];
    const today = new Date();

    // Generate next 30 days
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      dates.push(date);
    }

    return dates;
  };

  const selectedService = services.find(s => s.id === selectedServiceId);

  const renderServiceStep = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Select a Service</Text>
      <Text style={styles.stepSubtitle}>Choose the healthcare service for your appointment</Text>

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
                  Est. duration: 30min
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

  const renderDateTimeStep = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Select Date & Time</Text>
      <Text style={styles.stepSubtitle}>Choose your preferred appointment date and time</Text>

      <View style={styles.dateTimeSection}>
        <Text style={styles.sectionLabel}>Appointment Date</Text>
        <TouchableOpacity
          style={styles.dateButton}
          onPress={() => setShowDatePicker(true)}
        >
          <Text style={styles.dateButtonText}>
            {selectedDate ? formatDate(selectedDate) : 'Select Date'}
          </Text>
          <Text style={styles.dateButtonIcon}>📅</Text>
        </TouchableOpacity>
      </View>

      {selectedDate && (
        <View style={styles.dateTimeSection}>
          <Text style={styles.sectionLabel}>Available Time Slots</Text>
          <View style={styles.timeSlotsGrid}>
            {availableTimeSlots.map((time, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.timeSlot,
                  selectedTime === time && styles.timeSlotSelected,
                ]}
                onPress={() => handleTimeSelect(time)}
              >
                <Text
                  style={[
                    styles.timeSlotText,
                    selectedTime === time && styles.timeSlotTextSelected,
                  ]}
                >
                  {time}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}
    </View>
  );

  const renderDetailsStep = () => (
    <ScrollView style={styles.stepContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.stepTitle}>Appointment Details</Text>
      <Text style={styles.stepSubtitle}>Provide additional information for your appointment</Text>

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
      </View>

      <View style={styles.formSection}>
        <Text style={styles.sectionLabel}>Additional Notes (Optional)</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={notes}
          onChangeText={setNotes}
          placeholder="Any specific symptoms, concerns, or information you'd like to share..."
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />
      </View>
    </ScrollView>
  );

  const renderConfirmationStep = () => (
    <ScrollView style={styles.stepContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.stepTitle}>Confirm Appointment</Text>
      <Text style={styles.stepSubtitle}>Please review your appointment details</Text>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Service</Text>
        <Text style={styles.confirmationValue}>{selectedService?.name}</Text>
        <Text style={styles.confirmationSubtitle}>{selectedService?.department}</Text>
      </View>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Date & Time</Text>
        <Text style={styles.confirmationValue}>
          {selectedDate ? formatDate(selectedDate) : 'N/A'}
        </Text>
        <Text style={styles.confirmationSubtitle}>
          {selectedTime ? selectedTime : 'N/A'}
        </Text>
      </View>

      <View style={styles.confirmationCard}>
        <Text style={styles.confirmationTitle}>Patient Information</Text>
        <Text style={styles.confirmationValue}>{patientName}</Text>
        <Text style={styles.confirmationSubtitle}>{patientPhone}</Text>
        <Text style={styles.confirmationSubtitle}>{patientEmail}</Text>
      </View>

      {notes.trim() && (
        <View style={styles.confirmationCard}>
          <Text style={styles.confirmationTitle}>Notes</Text>
          <Text style={styles.confirmationValue}>{notes}</Text>
        </View>
      )}

      <View style={styles.disclaimer}>
        <Text style={styles.disclaimerText}>
          By booking this appointment, you agree to arrive on time and provide accurate information.
          You can cancel or reschedule up to 24 hours before the appointment.
        </Text>
      </View>
    </ScrollView>
  );

  const renderStepIndicator = () => (
    <View style={styles.stepIndicator}>
      {(['service', 'datetime', 'details', 'confirmation'] as const).map((stepName, index) => (
        <View key={stepName} style={styles.stepItem}>
          <View
            style={[
              styles.stepCircle,
              step === stepName && styles.stepCircleActive,
              (stepName === 'service' && step !== 'service') ||
              (stepName === 'datetime' && ['datetime', 'details', 'confirmation'].includes(step)) ||
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
    const steps = ['service', 'datetime', 'details', 'confirmation'];
    return steps.indexOf(stepName);
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Book Appointment</Text>
      </View>

      {renderStepIndicator()}

      <View style={styles.content}>
        {step === 'service' && renderServiceStep()}
        {step === 'datetime' && renderDateTimeStep()}
        {step === 'details' && renderDetailsStep()}
        {step === 'confirmation' && renderConfirmationStep()}
      </View>

      {/* Date Picker Modal */}
      <Modal
        isVisible={showDatePicker}
        onBackdropPress={() => setShowDatePicker(false)}
        style={styles.modal}
      >
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Select Date</Text>
          <ScrollView style={styles.dateList}>
            {generateDateOptions().map((date, index) => (
              <TouchableOpacity
                key={index}
                style={styles.dateOption}
                onPress={() => handleDateSelect(date)}
              >
                <Text style={styles.dateOptionText}>
                  {date.toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </Text>
                {date.toDateString() === new Date().toDateString() && (
                  <Text style={styles.todayText}>Today</Text>
                )}
              </TouchableOpacity>
            ))}
          </ScrollView>
          <TouchableOpacity
            style={styles.modalCloseButton}
            onPress={() => setShowDatePicker(false)}
          >
            <Text style={styles.modalCloseButtonText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </Modal>

      <View style={styles.footer}>
        {step !== 'service' && (
          <TouchableOpacity style={styles.backButton} onPress={handleBack}>
            <Text style={styles.backButtonText}>Back</Text>
          </TouchableOpacity>
        )}

        {step !== 'confirmation' ? (
          <TouchableOpacity
            style={[styles.nextButton, !selectedServiceId && step === 'service' && styles.buttonDisabled]}
            onPress={handleNext}
            disabled={!selectedServiceId && step === 'service'}
          >
            <Text style={styles.nextButtonText}>Next</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={[styles.bookButton, submitting && styles.buttonDisabled]}
            onPress={handleBookAppointment}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.bookButtonText}>Book Appointment</Text>
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
    paddingHorizontal: 16,
    backgroundColor: '#ffffff',
  },
  stepItem: {
    alignItems: 'center',
    flex: 1,
  },
  stepCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
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
    fontSize: 14,
    fontWeight: 'bold',
    color: '#6b7280',
  },
  stepNumberActive: {
    color: '#ffffff',
  },
  stepLabel: {
    fontSize: 10,
    color: '#6b7280',
    fontWeight: '500',
    textAlign: 'center',
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
  dateTimeSection: {
    marginBottom: 24,
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  dateButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
  },
  dateButtonText: {
    fontSize: 16,
    color: '#374151',
  },
  dateButtonIcon: {
    fontSize: 18,
  },
  timeSlotsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  timeSlot: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: '#ffffff',
    minWidth: 80,
    alignItems: 'center',
  },
  timeSlotSelected: {
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  timeSlotText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  timeSlotTextSelected: {
    color: '#ffffff',
  },
  formSection: {
    marginBottom: 24,
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
  modal: {
    margin: 0,
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '70%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
    textAlign: 'center',
  },
  dateList: {
    maxHeight: 300,
  },
  dateOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  dateOptionText: {
    fontSize: 16,
    color: '#374151',
  },
  todayText: {
    fontSize: 12,
    color: '#2563eb',
    fontWeight: '600',
  },
  modalCloseButton: {
    marginTop: 16,
    paddingVertical: 12,
    alignItems: 'center',
  },
  modalCloseButtonText: {
    fontSize: 16,
    color: '#6b7280',
    fontWeight: '600',
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
  bookButton: {
    flex: 1,
    backgroundColor: '#16a34a',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  bookButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
});

export default AppointmentBookingScreen;