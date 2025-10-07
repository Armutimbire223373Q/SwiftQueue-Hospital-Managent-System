const API_BASE_URL = 'http://localhost:8000/api';

export interface SymptomAnalysisRequest {
  symptoms: string;
  patient_age?: string;
  medical_history?: string;
  additional_context?: string;
}

export interface SymptomAnalysisResponse {
  success: boolean;
  analysis: {
    emergency_level: string;
    confidence: number;
    triage_category: string;
    estimated_wait_time: number;
    department_recommendation: string;
    recommended_actions: string[];
    risk_factors: string[];
    ai_reasoning: string;
    timestamp: string;
  };
  recommendations: string[];
}

export interface TriageAnalysisRequest {
  symptoms: string;
  age_group?: string;
  insurance_type?: string;
  department?: string;
  medical_history?: string;
  additional_context?: string;
}

export interface TriageAnalysisResponse {
  success: boolean;
  triage_result: {
    triage_score: number;
    category: string;
    priority_level: number;
    estimated_wait_time: number;
    resource_requirements: any;
    recommended_department: string;
    ai_analysis: {
      emergency_level: string;
      confidence: number;
      reasoning: string;
      recommended_actions: string[];
      risk_factors: string[];
    };
  };
  recommendations: string[];
}

export interface AIHealthStatus {
  status: string;
  models_available: boolean;
  model_in_use?: string;
  error?: string;
}

class AIService {
  /**
   * Analyze patient symptoms using AI to determine priority and emergency level
   */
  async analyzeSymptomsWithAI(request: SymptomAnalysisRequest): Promise<SymptomAnalysisResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/analyze-symptoms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI symptom analysis failed:', error);
      
      // Fallback analysis based on keyword detection
      const fallbackAnalysis = this.fallbackSymptomAnalysis(request.symptoms);
      
      return {
        success: true,
        analysis: fallbackAnalysis,
        recommendations: fallbackAnalysis.recommended_actions
      };
    }
  }

  /**
   * Perform comprehensive AI triage analysis
   */
  async performTriageAnalysis(request: TriageAnalysisRequest): Promise<TriageAnalysisResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/triage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI triage analysis failed:', error);
      throw error;
    }
  }

  /**
   * Check AI service health and availability
   */
  async checkAIHealth(): Promise<AIHealthStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI health check failed:', error);
      return {
        status: 'unhealthy',
        models_available: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Get available AI models
   */
  async getAvailableModels(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/models`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get AI models:', error);
      throw error;
    }
  }

  /**
   * Fallback symptom analysis using keyword matching
   */
  private fallbackSymptomAnalysis(symptoms: string): any {
    const symptomsLower = symptoms.toLowerCase();
    
    // Critical symptoms
    const criticalKeywords = [
      'chest pain', 'difficulty breathing', 'unconscious', 'severe bleeding',
      'stroke', 'heart attack', 'anaphylaxis', 'cardiac arrest', 'emergency'
    ];
    
    // High priority symptoms  
    const highKeywords = [
      'severe pain', 'high fever', 'broken bone', 'mental crisis',
      'dehydration', 'urgent', 'severe'
    ];
    
    // Moderate symptoms
    const moderateKeywords = [
      'pain', 'fever', 'nausea', 'headache', 'infection'
    ];

    let emergency_level = 'low';
    let confidence = 0.6;
    let triage_category = 'Non-urgent';
    let estimated_wait_time = 120;
    let department_recommendation = 'General Medicine';
    let recommended_actions = ['Schedule regular appointment'];

    if (criticalKeywords.some(keyword => symptomsLower.includes(keyword))) {
      emergency_level = 'critical';
      confidence = 0.85;
      triage_category = 'Emergency';
      estimated_wait_time = 0;
      department_recommendation = 'Emergency';
      recommended_actions = ['Seek immediate emergency care', 'Call 911 if severe'];
    } else if (highKeywords.some(keyword => symptomsLower.includes(keyword))) {
      emergency_level = 'high';
      confidence = 0.75;
      triage_category = 'Urgent';
      estimated_wait_time = 30;
      department_recommendation = 'Urgent Care';
      recommended_actions = ['Seek prompt medical attention', 'Consider urgent care'];
    } else if (moderateKeywords.some(keyword => symptomsLower.includes(keyword))) {
      emergency_level = 'moderate';
      confidence = 0.65;
      triage_category = 'Semi-urgent';
      estimated_wait_time = 90;
      department_recommendation = 'General Medicine';
      recommended_actions = ['Schedule appointment within 24 hours'];
    }

    return {
      emergency_level,
      confidence,
      triage_category,
      estimated_wait_time,
      department_recommendation,
      recommended_actions,
      risk_factors: emergency_level === 'critical' ? ['High risk condition detected'] : [],
      ai_reasoning: `Fallback analysis based on symptom keywords. Emergency level: ${emergency_level}`,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Convert emergency level to priority for queue management
   */
  emergencyLevelToPriority(emergencyLevel: string): 'low' | 'medium' | 'high' | 'urgent' {
    switch (emergencyLevel) {
      case 'critical':
        return 'urgent';
      case 'high':
        return 'high';
      case 'moderate':
        return 'medium';
      case 'low':
      default:
        return 'low';
    }
  }

  /**
   * Get priority badge styling based on emergency level
   */
  getPriorityBadgeClass(emergencyLevel: string): string {
    switch (emergencyLevel) {
      case 'critical':
        return 'bg-red-500 text-white';
      case 'high':
        return 'bg-orange-500 text-white';
      case 'moderate':
        return 'bg-yellow-500 text-black';
      case 'low':
      default:
        return 'bg-green-500 text-white';
    }
  }
}

// Export singleton instance
export const aiService = new AIService();
export default aiService;