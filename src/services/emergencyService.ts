/**
 * Emergency Service for handling ambulance dispatch operations
 */

import { apiService, EmergencyDispatch, DispatchRequest, DispatchStatusResponse } from './apiService';

export class EmergencyService {
  /**
   * Dispatch an ambulance for a patient emergency
   */
  async dispatchAmbulance(request: DispatchRequest): Promise<EmergencyDispatch> {
    return apiService.post<EmergencyDispatch>('/emergency/dispatch-ambulance', request);
  }

  /**
   * Get the status of a specific emergency dispatch
   */
  async getDispatchStatus(dispatchId: number): Promise<DispatchStatusResponse> {
    return apiService.get<DispatchStatusResponse>(`/emergency/dispatch/${dispatchId}`);
  }

  /**
   * Get all emergency dispatches for a specific patient
   */
  async getPatientDispatches(patientId: number): Promise<EmergencyDispatch[]> {
    return apiService.get<EmergencyDispatch[]>(`/emergency/dispatches/patient/${patientId}`);
  }

  /**
   * Get all active emergency dispatches (for staff dashboard)
   * This would need a new backend endpoint, but for now we'll simulate
   */
  async getActiveDispatches(): Promise<EmergencyDispatch[]> {
    // This endpoint doesn't exist yet, but we can implement it later
    // For now, return empty array
    try {
      return await apiService.get<EmergencyDispatch[]>('/emergency/active-dispatches');
    } catch (error) {
      console.warn('Active dispatches endpoint not available, returning empty array');
      return [];
    }
  }

  /**
   * Update dispatch status (for staff to manually update status)
   */
  async updateDispatchStatus(dispatchId: number, status: string, notes?: string): Promise<void> {
    return apiService.put(`/emergency/dispatch/${dispatchId}/status`, { status, notes });
  }
}

// Export singleton instance
export const emergencyService = new EmergencyService();

export default emergencyService;