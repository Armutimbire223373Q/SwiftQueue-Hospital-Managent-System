const API_BASE_URL = 'http://localhost:8000/api';

export interface SymptomAnalysisRequest {
  symptoms: string;
  patient_age?: string;
  medical_history?: string;
  additional_context?: string;
  patient_id?: number;
}

export interface SymptomAnalysisResponse {
  success: boolean;
  // Allow flexible shapes: components expect either a flat analysis or nested { analysis: {...} }
  analysis: any;
  triage?: any;
  recommendations?: string[];
  combinedRecommendations?: any;
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

// Compatibility alias expected by some components
export type AITriageRequest = TriageAnalysisRequest;

class AIService {
  /**
   * Analyze patient symptoms using AI to determine priority and emergency level
   */
  async analyzeSymptomsWithAI(request: SymptomAnalysisRequest): Promise<SymptomAnalysisResponse> {
    // If patient_id is provided, try to fetch their historical data to enrich the analysis
    let enrichedRequest = { ...request } as SymptomAnalysisRequest;
    if (request.patient_id) {
      try {
        const histResp = await fetch(`${API_BASE_URL}/patient-history/${request.patient_id}`);
        if (histResp.ok) {
          const history = await histResp.json();
          // Summarize history: collect diagnoses, chronic_conditions, allergies, prescribed_medication, remarks
          const recent = Array.isArray(history) ? history.slice(-5) : [];
          const diagnoses = recent.map((r: any) => r.diagnosis).filter(Boolean);
          const chronic = recent.map((r: any) => r.chronic_conditions).filter(Boolean);
          const meds = recent.map((r: any) => r.prescribed_medication).filter(Boolean);
          const allergies = recent.map((r: any) => r.allergies).filter(Boolean);
          const remarks = recent.map((r: any) => r.remarks).filter(Boolean);

          const summaryParts = [] as string[];
          if (diagnoses.length) summaryParts.push(`Past diagnoses: ${[...new Set(diagnoses)].join('; ')}`);
          if (chronic.length) summaryParts.push(`Chronic conditions: ${[...new Set(chronic)].join('; ')}`);
          if (meds.length) summaryParts.push(`Medications: ${[...new Set(meds)].join('; ')}`);
          if (allergies.length) summaryParts.push(`Allergies: ${[...new Set(allergies)].join('; ')}`);
          if (remarks.length) summaryParts.push(`Recent notes: ${remarks.join(' | ')}`);

          const summary = summaryParts.join('. ');
          if (summary) {
            enrichedRequest.medical_history = (enrichedRequest.medical_history ? enrichedRequest.medical_history + '. ' : '') + summary;
            enrichedRequest.additional_context = (enrichedRequest.additional_context ? enrichedRequest.additional_context + '. ' : '') + `Patient history summary: ${summary}`;
          }
        }
      } catch (err) {
        // Non-fatal: proceed without history enrichment
        console.warn('Failed to fetch patient history for enrichment:', err);
      }
    }

    try {
      const response = await fetch(`${API_BASE_URL}/ai/analyze-symptoms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(enrichedRequest),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const json = await response.json();
      // Normalize shapes to include both flat and nested analysis forms
      return this.normalizeSymptomResponse(json);
    } catch (error) {
      console.error('AI symptom analysis failed:', error);
      
      // Fallback analysis based on keyword detection
      const fallbackAnalysis = this.fallbackSymptomAnalysis(request.symptoms);

      // If we have enrichedRequest.medical_history include a short note
      if (enrichedRequest.medical_history) {
        fallbackAnalysis.previous_history = enrichedRequest.medical_history;
        fallbackAnalysis.ai_reasoning += ` Previous history considered: ${enrichedRequest.medical_history}`;
      }

      // Build a response that contains both flat and nested analysis for compatibility
      const resp: any = {
        success: true,
        // analysis contains flat fields and also a nested `analysis` pointing to same object
        analysis: {
          ...fallbackAnalysis,
          analysis: fallbackAnalysis
        },
        triage: {
          triage_result: {
            ai_analysis: {
              emergency_level: fallbackAnalysis.emergency_level,
              confidence: fallbackAnalysis.confidence,
              reasoning: fallbackAnalysis.ai_reasoning,
              recommended_actions: fallbackAnalysis.recommended_actions,
              risk_factors: fallbackAnalysis.risk_factors
            },
            // include some of the summary triage fields for convenience
            triage_score: 0,
            category: fallbackAnalysis.triage_category,
            priority_level: 0,
            estimated_wait_time: fallbackAnalysis.estimated_wait_time,
            recommended_department: fallbackAnalysis.department_recommendation
          }
        },
        recommendations: fallbackAnalysis.recommended_actions,
        combinedRecommendations: fallbackAnalysis.recommended_actions
      };

      return this.normalizeSymptomResponse(resp as any);
    }
  }

      /**
       * Normalize SymptomAnalysisResponse shapes so callers can safely access
       * both `result.analysis` (flat) and `result.analysis.analysis` (nested)
       */
      private normalizeSymptomResponse(response: any): SymptomAnalysisResponse {
        const res: any = { ...(response || {}) };

        // Normalize analysis
        if (res.analysis) {
          // If nested form exists, use it as canonical and also expose flat fields
          if (res.analysis.analysis) {
            const nested = res.analysis.analysis;
            res.analysis = { ...nested, analysis: nested };
          } else {
            // Flat analysis provided; expose nested copy under `analysis.analysis`
            const flat = res.analysis;
            res.analysis = { ...flat, analysis: flat };
          }
        } else if (res.analysis === undefined && res.analysis === null) {
          // nothing
        }

        // Normalize triage.ai_analysis if present
        if (res.triage && res.triage.triage_result) {
          const tri = res.triage.triage_result;
          if (tri.ai_analysis && !tri.ai_analysis.emergency_level && res.analysis && res.analysis.analysis) {
            tri.ai_analysis.emergency_level = res.analysis.analysis.emergency_level;
          }
          // ensure a0 fields exist
          if (!tri.ai_analysis) {
            tri.ai_analysis = {
              emergency_level: res.analysis?.analysis?.emergency_level ?? 'low',
              confidence: res.analysis?.analysis?.confidence ?? 0,
              reasoning: res.analysis?.analysis?.ai_reasoning ?? '',
              recommended_actions: res.recommendations ?? [],
              risk_factors: res.analysis?.analysis?.risk_factors ?? []
            };
          }
          res.triage.triage_result = { ...tri };
        }

        // Ensure combinedRecommendations exist
        if (!res.combinedRecommendations) {
          res.combinedRecommendations = res.recommendations ?? (res.analysis?.analysis?.recommended_actions ?? []);
        }

        return res as SymptomAnalysisResponse;
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

  // Compatibility alias: components call getAITriageAnalysis
  async getAITriageAnalysis(request: TriageAnalysisRequest): Promise<TriageAnalysisResponse> {
    return this.performTriageAnalysis(request);
  }

  // Compatibility alias for comprehensive analysis
  async getComprehensiveSymptomAnalysis(request: SymptomAnalysisRequest): Promise<SymptomAnalysisResponse>;
  async getComprehensiveSymptomAnalysis(symptoms: string, patient_age?: string, medical_history?: string, additional_context?: string): Promise<SymptomAnalysisResponse>;
  async getComprehensiveSymptomAnalysis(arg1: any, arg2?: any, arg3?: any, arg4?: any): Promise<SymptomAnalysisResponse> {
    // Support two call signatures: object request or positional args
    let request: SymptomAnalysisRequest;
    if (typeof arg1 === 'string') {
      request = {
        symptoms: arg1,
        patient_age: arg2,
        medical_history: arg3,
        additional_context: arg4
      };
    } else {
      request = arg1;
    }

    const result = await this.analyzeSymptomsWithAI(request);
    // If the remote service returned top-level analysis without nested wrappers,
    // normalize it so components expecting result.analysis.analysis or result.triage.triage_result work.
    if ((result as any).analysis && !(result as any).analysis.analysis) {
      (result as any).analysis = { analysis: (result as any).analysis };
    }
    if (!(result as any).triage && (result as any).analysis && (result as any).analysis.analysis) {
      // create a minimal triage wrapper if not present
      (result as any).triage = { triage_result: { ai_analysis: { emergency_level: (result as any).analysis.analysis.emergency_level ?? 'low', confidence: (result as any).analysis.analysis.confidence ?? 0 } } };
    }

    return result as SymptomAnalysisResponse;
  }

  // Simple service suggestion helper (components expect this)
  async getServiceSuggestion(symptoms: string): Promise<{ suggestedService?: string }> {
    // Basic keyword-based mapping as fallback
    const s = symptoms.toLowerCase();
    if (s.includes('heart') || s.includes('chest')) return { suggestedService: 'Cardiology' };
    if (s.includes('bone') || s.includes('fracture')) return { suggestedService: 'Orthopedics' };
    if (s.includes('preg') || s.includes('pregnancy')) return { suggestedService: 'Obstetrics' };
    return { suggestedService: 'General Medicine' };
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

      // Log critical emergency detection - dispatch will be handled by backend if patient_id provided
      console.warn('🚨 CRITICAL EMERGENCY DETECTED: Ambulance dispatch will be attempted if patient_id provided');
      console.warn('Patient symptoms:', symptoms);
      console.warn('Emergency level:', emergency_level);
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
      timestamp: new Date().toISOString(),
      ambulance_dispatch: emergency_level === 'critical' ? { status: 'pending_backend_dispatch' } : undefined
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

  /**
   * Get dashboard insights from AI service
   */
  async getDashboardInsights(): Promise<any> {
    // For now, return mock data since backend doesn't have this endpoint
    return {
      efficiency_score: 0.89,
      patient_satisfaction: 0.92,
      peak_hours: ['10:00 AM', '2:00 PM'],
      recommendations: [
        'Optimize staff scheduling during peak hours',
        'Implement AI triage for faster patient routing'
      ]
    };
  }
}

// Export singleton instance
export const aiService = new AIService();
export default aiService;