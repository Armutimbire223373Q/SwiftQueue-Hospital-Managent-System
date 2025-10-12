import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';

const AppointmentDetailsScreen = () => {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Appointment Details</Text>
        <Text style={styles.subtitle}>View appointment information and status</Text>
        <Text style={styles.placeholder}>Appointment details coming soon...</Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 32,
  },
  placeholder: {
    fontSize: 16,
    color: '#9ca3af',
    textAlign: 'center',
  },
});

export default AppointmentDetailsScreen;