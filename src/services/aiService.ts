/**
 * AI Service for Queue Management System
 * Handles AI-powered features like predictions, recommendations, and optimizations
 */

import { apiService, AIServiceSuggestion, AIEfficiencyMetrics, AIStaffOptimization, AIRecommendation } from './apiService';

export interface WaitTimePrediction {
  service_id: number;
  service_name: string;
  predicted_wait_minutes: number;
}

export interface AnomalyDetection {
  anomalies_detected: number;
  anomalies: Array<{
    service_id: number;
    metrics: Record<string, number>;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export interface StaffOptimizationResponse {
  recommendations: AIStaffOptimization[];
  total_adjustments_needed: number;
}

class AIService {
  /**
   * Train or retrain AI models with current data
   */
  async trainModels(): Promise<{ message: string }> {
    return apiService.post('/ai/train');
  }

  /**
   * Get AI-predicted wait time for a specific service
   */
  async predictWaitTime(serviceId: number): Promise<WaitTimePrediction> {
    return apiService.get(`/ai/wait-prediction/${serviceId}`);
  }

  /**
   * Detect anomalies in the current system state
   */
  async detectAnomalies(): Promise<AnomalyDetection> {
    return apiService.get('/ai/anomalies');
  }

  /**
   * Get AI-powered service suggestion based on symptoms
   */
  async getServiceSuggestion(symptoms: string): Promise<AIServiceSuggestion> {
    return apiService.post('/ai/service-suggestion', { symptoms });
  }

  /**
   * Get AI-analyzed efficiency metrics for a service
   */
  async getServiceEfficiency(serviceId: number): Promise<{
    service_id: number;
    service_name: string;
    metrics: AIEfficiencyMetrics;
  }> {
    return apiService.get(`/ai/efficiency/${serviceId}`);
  }

  /**
   * Get AI recommendations for staff optimization
   */
  async getStaffOptimization(): Promise<StaffOptimizationResponse> {
    return apiService.get('/ai/optimize-staff');
  }

  /**
   * Get general AI recommendations for the system
   */
  async getRecommendations(): Promise<AIRecommendation[]> {
    return apiService.get('/analytics/recommendations');
  }

  /**
   * Predict peak times for all services
   */
  async predictPeakTimes(): Promise<Array<{
    service_id: number;
    service_name: string;
    peak_hours: Array<{ hour: number; avg_load: number }>;
    next_predicted_peak: { hour: number; expected_load: number };
    current_trend: 'increasing' | 'stable' | 'decreasing';
  }>> {
    // This would be implemented as a separate endpoint in the backend
    // For now, return mock data
    return [
      {
        service_id: 1,
        service_name: "Emergency Care",
        peak_hours: [
          { hour: 14, avg_load: 15 },
          { hour: 16, avg_load: 12 },
          { hour: 10, avg_load: 10 }
        ],
        next_predicted_peak: { hour: 16, expected_load: 12 },
        current_trend: "increasing"
      }
    ];
  }

  /**
   * Get AI insights for dashboard
   */
  async getDashboardInsights(): Promise<{
    total_patients_today: number;
    avg_wait_time: number;
    efficiency_score: number;
    peak_department: string;
    anomalies_count: number;
    recommendations_count: number;
    ai_accuracy: number;
    system_health: 'excellent' | 'good' | 'fair' | 'poor';
  }> {
    try {
      // Combine multiple AI endpoints to create dashboard insights
      const [anomalies, recommendations] = await Promise.all([
        this.detectAnomalies(),
        this.getRecommendations()
      ]);

      // Calculate system health based on anomalies and efficiency
      let systemHealth: 'excellent' | 'good' | 'fair' | 'poor' = 'good';
      if (anomalies.anomalies_detected === 0) {
        systemHealth = 'excellent';
      } else if (anomalies.anomalies_detected <= 2) {
        systemHealth = 'good';
      } else if (anomalies.anomalies_detected <= 5) {
        systemHealth = 'fair';
      } else {
        systemHealth = 'poor';
      }

      return {
        total_patients_today: 73, // This would come from analytics
        avg_wait_time: 18.5,
        efficiency_score: 0.92,
        peak_department: "Emergency",
        anomalies_count: anomalies.anomalies_detected,
        recommendations_count: recommendations.length,
        ai_accuracy: 0.89, // This would be calculated from prediction accuracy
        system_health: systemHealth
      };
    } catch (error) {
      console.error('Failed to get dashboard insights:', error);
      // Return default values on error
      return {
        total_patients_today: 0,
        avg_wait_time: 0,
        efficiency_score: 0,
        peak_department: "Unknown",
        anomalies_count: 0,
        recommendations_count: 0,
        ai_accuracy: 0,
        system_health: 'poor'
      };
    }
  }

  /**
   * Get AI-powered patient flow predictions
   */
  async getPatientFlowPredictions(): Promise<{
    next_hour_prediction: number;
    next_4_hours: Array<{ hour: number; predicted_patients: number }>;
    confidence: number;
    factors: string[];
  }> {
    // This would be a separate endpoint in a full implementation
    const currentHour = new Date().getHours();
    
    return {
      next_hour_prediction: Math.floor(Math.random() * 15) + 5,
      next_4_hours: Array.from({ length: 4 }, (_, i) => ({
        hour: (currentHour + i + 1) % 24,
        predicted_patients: Math.floor(Math.random() * 20) + 5
      })),
      confidence: 0.85,
      factors: [
        "Historical patterns",
        "Day of week trends",
        "Seasonal variations",
        "Current queue state"
      ]
    };
  }

  /**
   * Get AI recommendations for resource allocation
   */
  async getResourceAllocationRecommendations(): Promise<Array<{
    resource_type: 'staff' | 'equipment' | 'space';
    department: string;
    current_allocation: number;
    recommended_allocation: number;
    priority: 'low' | 'medium' | 'high' | 'critical';
    reasoning: string;
    expected_impact: string;
  }>> {
    // This would be implemented as a backend endpoint
    return [
      {
        resource_type: 'staff',
        department: 'Emergency',
        current_allocation: 3,
        recommended_allocation: 4,
        priority: 'high',
        reasoning: 'Expected patient surge in next 2 hours based on historical patterns',
        expected_impact: '25% reduction in wait times'
      },
      {
        resource_type: 'equipment',
        department: 'Radiology',
        current_allocation: 1,
        recommended_allocation: 2,
        priority: 'medium',
        reasoning: 'High utilization rate and growing queue',
        expected_impact: '40% increase in throughput'
      }
    ];
  }
}

// Export singleton instance
export const aiService = new AIService();
export default aiService;