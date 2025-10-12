import * as LocalAuthentication from 'expo-local-authentication';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert, Platform } from 'react-native';
import { apiService } from './apiService';

export interface BiometricAuthResult {
  success: boolean;
  error?: string;
  method?: 'fingerprint' | 'facial' | 'iris' | 'unknown';
}

export interface BiometricSettings {
  enabled: boolean;
  method: 'fingerprint' | 'facial' | 'iris' | 'unknown';
  enrolled: boolean;
  hasHardware: boolean;
  isDeviceSecure: boolean;
}

class BiometricAuthService {
  private static readonly SETTINGS_KEY = 'biometricSettings';
  private static readonly LAST_AUTH_KEY = 'lastBiometricAuth';

  // Check if biometric authentication is available
  async checkBiometricAvailability(): Promise<BiometricSettings> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();

      // Determine the primary biometric method
      let method: 'fingerprint' | 'facial' | 'iris' | 'unknown' = 'unknown';

      if (Platform.OS === 'ios') {
        if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
          method = 'facial';
        } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
          method = 'fingerprint';
        }
      } else if (Platform.OS === 'android') {
        if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
          method = 'fingerprint';
        } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
          method = 'facial';
        } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.IRIS)) {
          method = 'iris';
        }
      }

      const settings: BiometricSettings = {
        enabled: false, // Will be loaded from storage
        method,
        enrolled: isEnrolled,
        hasHardware: hasHardware,
        isDeviceSecure: await this.checkDeviceSecurity(),
      };

      // Load saved settings
      const savedSettings = await this.loadBiometricSettings();
      if (savedSettings && savedSettings.enabled !== undefined) {
        settings.enabled = savedSettings.enabled;
      }

      return settings;
    } catch (error) {
      console.error('Error checking biometric availability:', error);
      return {
        enabled: false,
        method: 'unknown',
        enrolled: false,
        hasHardware: false,
        isDeviceSecure: false,
      };
    }
  }

  // Check if device has security features
  private async checkDeviceSecurity(): Promise<boolean> {
    try {
      // Check if device has passcode/PIN/pattern
      const securityLevel = await LocalAuthentication.getEnrolledLevelAsync();
      return securityLevel !== LocalAuthentication.SecurityLevel.NONE;
    } catch (error) {
      console.error('Error checking device security:', error);
      return false;
    }
  }

  // Authenticate using biometrics
  async authenticateBiometric(
    reason: string = 'Authenticate to access your account',
    fallbackToPIN: boolean = true
  ): Promise<BiometricAuthResult> {
    try {
      const settings = await this.checkBiometricAvailability();

      if (!settings.hasHardware) {
        return {
          success: false,
          error: 'Biometric authentication is not available on this device',
        };
      }

      if (!settings.enrolled) {
        return {
          success: false,
          error: 'No biometric data enrolled on this device',
        };
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: reason,
        fallbackLabel: fallbackToPIN ? 'Use PIN' : undefined,
        cancelLabel: 'Cancel',
        disableDeviceFallback: !fallbackToPIN,
      });

      if (result.success) {
        // Save last authentication time
        await this.saveLastAuthTime();

        return {
          success: true,
          method: settings.method,
        };
      } else {
        let errorMessage = 'Authentication failed';

        switch (result.error) {
          case 'user_cancel':
            errorMessage = 'Authentication was cancelled';
            break;
          case 'user_fallback':
            errorMessage = 'Authentication fell back to PIN/passcode';
            break;
          case 'system_cancel':
            errorMessage = 'Authentication was cancelled by system';
            break;
          case 'lockout':
            errorMessage = 'Too many failed attempts. Try again later.';
            break;
          case 'not_enrolled':
            errorMessage = 'No biometric data enrolled';
            break;
          default:
            errorMessage = result.error || 'Authentication failed';
        }

        return {
          success: false,
          error: errorMessage,
        };
      }
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return {
        success: false,
        error: 'Biometric authentication failed',
      };
    }
  }

  // Enable biometric authentication
  async enableBiometric(): Promise<boolean> {
    try {
      const settings = await this.checkBiometricAvailability();

      if (!settings.hasHardware) {
        Alert.alert(
          'Not Available',
          'Biometric authentication is not available on this device.'
        );
        return false;
      }

      if (!settings.enrolled) {
        Alert.alert(
          'Not Enrolled',
          'Please enroll biometric data in your device settings first.',
          [
            { text: 'Cancel', style: 'cancel' },
            {
              text: 'Open Settings',
              onPress: () => {
                // Note: In a real app, you'd use Linking.openSettings()
                Alert.alert('Settings', 'Please go to Settings > Security to enroll biometrics.');
              }
            }
          ]
        );
        return false;
      }

      // Test authentication before enabling
      const testResult = await this.authenticateBiometric(
        'Test biometric authentication before enabling'
      );

      if (testResult.success) {
        const newSettings: Partial<BiometricSettings> = {
          enabled: true,
          method: settings.method,
        };

        await this.saveBiometricSettings(newSettings);

        Alert.alert(
          'Success',
          'Biometric authentication has been enabled for this app.'
        );

        return true;
      } else {
        Alert.alert(
          'Test Failed',
          'Biometric authentication test failed. Please try again.'
        );
        return false;
      }
    } catch (error) {
      console.error('Error enabling biometric:', error);
      Alert.alert('Error', 'Failed to enable biometric authentication.');
      return false;
    }
  }

  // Disable biometric authentication
  async disableBiometric(): Promise<void> {
    try {
      await this.saveBiometricSettings({ enabled: false });
      Alert.alert('Success', 'Biometric authentication has been disabled.');
    } catch (error) {
      console.error('Error disabling biometric:', error);
      Alert.alert('Error', 'Failed to disable biometric authentication.');
    }
  }

  // Check if biometric is enabled
  async isBiometricEnabled(): Promise<boolean> {
    try {
      const settings = await this.loadBiometricSettings();
      return settings?.enabled || false;
    } catch (error) {
      console.error('Error checking biometric status:', error);
      return false;
    }
  }

  // Get biometric settings
  async getBiometricSettings(): Promise<BiometricSettings | null> {
    try {
      const settings = await this.loadBiometricSettings();
      if (settings) {
        const availability = await this.checkBiometricAvailability();
        return {
          ...availability,
          enabled: settings.enabled ?? false,
        };
      }
      return null;
    } catch (error) {
      console.error('Error getting biometric settings:', error);
      return null;
    }
  }

  // Authenticate user with biometrics (if enabled)
  async authenticateUserIfEnabled(
    reason: string = 'Authenticate to continue'
  ): Promise<BiometricAuthResult> {
    try {
      const isEnabled = await this.isBiometricEnabled();

      if (!isEnabled) {
        return { success: true }; // Skip if not enabled
      }

      // Check if recently authenticated (within 5 minutes)
      const lastAuth = await this.getLastAuthTime();
      const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);

      if (lastAuth && lastAuth > fiveMinutesAgo) {
        return { success: true }; // Recently authenticated
      }

      return await this.authenticateBiometric(reason);
    } catch (error) {
      console.error('Error in user authentication:', error);
      return {
        success: false,
        error: 'Authentication failed',
      };
    }
  }

  // Private methods for storage
  private async loadBiometricSettings(): Promise<Partial<BiometricSettings> | null> {
    try {
      const data = await AsyncStorage.getItem(BiometricAuthService.SETTINGS_KEY);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error loading biometric settings:', error);
      return null;
    }
  }

  private async saveBiometricSettings(settings: Partial<BiometricSettings>): Promise<void> {
    try {
      const currentSettings = await this.loadBiometricSettings();
      const updatedSettings = { ...currentSettings, ...settings };
      await AsyncStorage.setItem(BiometricAuthService.SETTINGS_KEY, JSON.stringify(updatedSettings));
    } catch (error) {
      console.error('Error saving biometric settings:', error);
      throw error;
    }
  }

  private async saveLastAuthTime(): Promise<void> {
    try {
      await AsyncStorage.setItem(BiometricAuthService.LAST_AUTH_KEY, Date.now().toString());
    } catch (error) {
      console.error('Error saving last auth time:', error);
    }
  }

  private async getLastAuthTime(): Promise<number | null> {
    try {
      const time = await AsyncStorage.getItem(BiometricAuthService.LAST_AUTH_KEY);
      return time ? parseInt(time) : null;
    } catch (error) {
      console.error('Error getting last auth time:', error);
      return null;
    }
  }

  // Clear all biometric data
  async clearBiometricData(): Promise<void> {
    try {
      await AsyncStorage.removeItem(BiometricAuthService.SETTINGS_KEY);
      await AsyncStorage.removeItem(BiometricAuthService.LAST_AUTH_KEY);
    } catch (error) {
      console.error('Error clearing biometric data:', error);
    }
  }

  // Get biometric method display name
  getBiometricMethodName(method: string): string {
    switch (method) {
      case 'fingerprint':
        return Platform.OS === 'ios' ? 'Touch ID' : 'Fingerprint';
      case 'facial':
        return Platform.OS === 'ios' ? 'Face ID' : 'Face Recognition';
      case 'iris':
        return 'Iris Recognition';
      default:
        return 'Biometric Authentication';
    }
  }

  // Show biometric setup prompt
  async showBiometricSetupPrompt(): Promise<void> {
    const settings = await this.checkBiometricAvailability();

    if (!settings.hasHardware) {
      Alert.alert(
        'Not Supported',
        'Your device does not support biometric authentication.'
      );
      return;
    }

    if (!settings.enrolled) {
      Alert.alert(
        'Setup Required',
        `Please set up ${this.getBiometricMethodName(settings.method)} in your device settings first.`,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Open Settings',
            onPress: () => {
              // In production: Linking.openSettings()
              Alert.alert('Settings', 'Please go to Settings > Security to set up biometrics.');
            }
          }
        ]
      );
      return;
    }

    Alert.alert(
      'Enable Biometric Login',
      `Use ${this.getBiometricMethodName(settings.method)} to quickly access your account?`,
      [
        { text: 'Not Now', style: 'cancel' },
        {
          text: 'Enable',
          onPress: () => this.enableBiometric()
        }
      ]
    );
  }
}

export const biometricAuthService = new BiometricAuthService();