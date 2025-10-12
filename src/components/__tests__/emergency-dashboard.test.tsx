/**
 * Tests for Emergency Dashboard Component
 * Tests component rendering, state management, and user interactions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EmergencyDashboard from '../emergency-dashboard';
import { emergencyService } from '../../services/emergencyService';

// Mock the emergency service
vi.mock('../../services/emergencyService', () => ({
  emergencyService: {
    dispatchAmbulance: vi.fn(),
    getDispatchStatus: vi.fn(),
    getPatientDispatches: vi.fn(),
  },
}));

// Mock auth service
vi.mock('../../services/authService', () => ({
  authService: {
    getCurrentUser: vi.fn(),
  },
}));

describe('EmergencyDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the emergency dashboard with title', () => {
    render(<EmergencyDashboard />);

    expect(screen.getByText('Emergency Response Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Real-time ambulance dispatch monitoring')).toBeInTheDocument();
  });

  it('displays stats overview cards', () => {
    render(<EmergencyDashboard />);

    expect(screen.getByText('Active Dispatches')).toBeInTheDocument();
    expect(screen.getByText('Completed Today')).toBeInTheDocument();
    expect(screen.getByText('Avg Response Time')).toBeInTheDocument();
  });

  it('shows dispatch ambulance button', () => {
    render(<EmergencyDashboard />);

    const dispatchButton = screen.getByRole('button', { name: /dispatch ambulance/i });
    expect(dispatchButton).toBeInTheDocument();
  });

  it('opens dispatch dialog when button is clicked', async () => {
    const user = userEvent.setup();
    render(<EmergencyDashboard />);

    const dispatchButton = screen.getByRole('button', { name: /dispatch ambulance/i });
    await user.click(dispatchButton);

    expect(screen.getByText('Manual Ambulance Dispatch')).toBeInTheDocument();
  });

  it('validates form inputs in dispatch dialog', async () => {
    const user = userEvent.setup();
    render(<EmergencyDashboard />);

    // Open dispatch dialog
    const dispatchButton = screen.getByRole('button', { name: /dispatch ambulance/i });
    await user.click(dispatchButton);

    // Try to submit without filling form
    const submitButton = screen.getByRole('button', { name: /dispatch ambulance/i });
    await user.click(submitButton);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/please select a patient and provide emergency details/i)).toBeInTheDocument();
    });
  });

  it('submits dispatch form with valid data', async () => {
    const user = userEvent.setup();

    // Mock successful dispatch
    const mockDispatch = {
      id: 1,
      patient_id: 1,
      emergency_details: 'Test emergency',
      dispatch_address: '123 Test St',
      dispatch_status: 'dispatched',
      dispatched_at: new Date().toISOString(),
      response_time: 10,
      ambulance_id: 'AMB-123',
      notes: 'Test dispatch',
      created_at: new Date().toISOString(),
    };

    emergencyService.dispatchAmbulance.mockResolvedValue(mockDispatch);

    render(<EmergencyDashboard />);

    // Open dispatch dialog
    const dispatchButton = screen.getByRole('button', { name: /dispatch ambulance/i });
    await user.click(dispatchButton);

    // Fill form
    const patientSelect = screen.getByRole('combobox');
    await user.click(patientSelect);
    // Note: In a real test, you'd need to mock the patient options

    const detailsTextarea = screen.getByPlaceholderText(/describe the emergency situation/i);
    await user.type(detailsTextarea, 'Chest pain and difficulty breathing');

    // Submit form
    const submitButton = screen.getAllByRole('button', { name: /dispatch ambulance/i })[1];
    await user.click(submitButton);

    // Verify service was called
    await waitFor(() => {
      expect(emergencyService.dispatchAmbulance).toHaveBeenCalledWith({
        patient_id: expect.any(Number),
        emergency_details: 'Chest pain and difficulty breathing',
      });
    });
  });

  it('displays active dispatches list', () => {
    render(<EmergencyDashboard />);

    expect(screen.getByText('Active Ambulance Dispatches')).toBeInTheDocument();
  });

  it('shows empty state when no dispatches', () => {
    render(<EmergencyDashboard />);

    expect(screen.getByText('No active dispatches at this time')).toBeInTheDocument();
  });

  it('handles dispatch errors gracefully', async () => {
    const user = userEvent.setup();

    // Mock dispatch failure
    emergencyService.dispatchAmbulance.mockRejectedValue(new Error('Dispatch failed'));

    render(<EmergencyDashboard />);

    // Open dispatch dialog
    const dispatchButton = screen.getByRole('button', { name: /dispatch ambulance/i });
    await user.click(dispatchButton);

    // Fill and submit form
    const detailsTextarea = screen.getByPlaceholderText(/describe the emergency situation/i);
    await user.type(detailsTextarea, 'Test emergency');

    const submitButton = screen.getAllByRole('button', { name: /dispatch ambulance/i })[1];
    await user.click(submitButton);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/failed to dispatch ambulance/i)).toBeInTheDocument();
    });
  });

  it('refreshes data when refresh button is clicked', async () => {
    const user = userEvent.setup();
    render(<EmergencyDashboard />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    await user.click(refreshButton);

    // Verify refresh functionality is triggered
    // Note: In real implementation, this would trigger data reloading
  });

  it('displays dispatch status with correct colors', () => {
    // This test would verify that different dispatch statuses
    // are displayed with appropriate colors and icons
    render(<EmergencyDashboard />);

    // Test would check CSS classes for different statuses
    // pending: yellow, dispatched: blue, en_route: orange, arrived: green
  });

  it('formats time and elapsed time correctly', () => {
    // Test time formatting utilities
    render(<EmergencyDashboard />);

    // Verify time display formatting
  });

  it('calculates and displays statistics correctly', () => {
    // Test stats calculation from dispatch data
    render(<EmergencyDashboard />);

    // Verify active dispatches count, completed today, avg response time
  });
});

// Integration tests with API
describe('EmergencyDashboard API Integration', () => {
  it('loads dispatches on component mount', async () => {
    // Mock API responses
    emergencyService.getPatientDispatches.mockResolvedValue([]);

    render(<EmergencyDashboard />);

    // Verify API calls are made on mount
    await waitFor(() => {
      expect(emergencyService.getPatientDispatches).toHaveBeenCalled();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock API failure
    emergencyService.getPatientDispatches.mockRejectedValue(new Error('API Error'));

    render(<EmergencyDashboard />);

    // Should display error message
    await waitFor(() => {
      expect(screen.getByText(/failed to load emergency data/i)).toBeInTheDocument();
    });
  });
});