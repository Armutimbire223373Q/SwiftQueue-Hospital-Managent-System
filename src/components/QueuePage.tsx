import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Clock, 
  Users, 
  Phone, 
  Mail, 
  CheckCircle, 
  Heart, 
  Brain, 
  Stethoscope, 
  Activity, 
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  User,
  Calendar,
  FileText,
  Star,
  Zap,
  Shield,
  Sparkles,
  TrendingUp,
  Timer,
  MapPin,
  Bell,
  RefreshCw,
  Bot,
  Cpu,
  Target,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Eye,
  BarChart3
} from 'lucide-react';
import { queueService, PatientDetails } from '@/services/queueService';
import { servicesService } from '@/services/servicesService';
import { notificationService } from '@/services/notificationService';
import { demoService } from '@/services/demoService';
import { aiService, AITriageRequest, SymptomAnalysisRequest } from '@/services/aiService';

interface ServiceType {
  id: number;
  name: string;
  description: string;
  estimatedTime: number;
  currentWaitTime: number;
  queueLength: number;
  department: string;
  aiPredictedWait: number;
  staffCount: number;
  serviceRate: number;
}

interface QueueStatus {
  queueNumber: number;
  estimatedWait: number;
  aiPredictedWait: number;
  position: number;
  status: 'waiting' | 'called' | 'serving' | 'completed';
}

interface AITriageResult {
  triage_score: number;
  category: string;
  priority_level: number;
  estimated_wait_time: number;
  recommended_department: string;
  ai_analysis: {
    emergency_level: string;
    confidence: number;
    reasoning: string;
    recommended_actions: string[];
    risk_factors: string[];
  };
}

interface SymptomAnalysisResult {
  emergency_level: string;
  confidence: number;
  triage_category: string;
  estimated_wait_time: number;
  department_recommendation: string;
  recommended_actions: string[];
  risk_factors: string[];
  ai_reasoning: string;
}

const QueuePage: React.FC = () => {
  const [step, setStep] = useState<'symptoms' | 'service' | 'details' | 'confirmation' | 'waiting'>('symptoms');
  const [selectedService, setSelectedService] = useState<ServiceType | null>(null);
  const [patientDetails, setPatientDetails] = useState<PatientDetails>({
    name: '',
    phone: '',
    email: '',
    dateOfBirth: '',
    symptoms: '',
    priority: 'medium'
  });
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [services, setServices] = useState<ServiceType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // AI-related state
  const [aiTriageResult, setAiTriageResult] = useState<AITriageResult | null>(null);
  const [symptomAnalysisResult, setSymptomAnalysisResult] = useState<SymptomAnalysisResult | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiRecommendations, setAiRecommendations] = useState<string[]>([]);
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const [aiConfidence, setAiConfidence] = useState<number>(0);
  const [emergencyLevel, setEmergencyLevel] = useState<string>('moderate');
  const [aiRecommendedServices, setAiRecommendedServices] = useState<ServiceType[]>([]);
  const [showServiceRecommendations, setShowServiceRecommendations] = useState(false);

  useEffect(() => {
    loadServices();
    // Set up real-time updates
    const interval = setInterval(loadServices, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadServices = async () => {
    try {
      const servicesData = await servicesService.getAllServices();
      // Transform the data to match our ServiceType interface
      const transformedServices = servicesData.map(service => ({
        ...service,
        aiPredictedWait: service.aiPredictedWait || Math.round(service.currentWaitTime * 0.8),
        staffCount: Math.floor(Math.random() * 3) + 1,
        serviceRate: Math.random() * 2 + 0.5
      }));
      setServices(transformedServices);
    } catch (err) {
      console.error('Failed to load services:', err);
      // Use demo data as fallback
      const demoServices = demoService.generateQueueData().services.map((service, index) => ({
        id: index + 1,
        name: service.name,
        description: `Professional ${service.name.toLowerCase()} services`,
        estimatedTime: service.waitTime,
        currentWaitTime: service.waitTime,
        queueLength: service.patients,
        department: service.name.split(' ')[0],
        aiPredictedWait: Math.round(service.waitTime * 0.8),
        staffCount: Math.floor(Math.random() * 3) + 1,
        serviceRate: Math.random() * 2 + 0.5
      }));
      setServices(demoServices);
    }
  };

  const handleServiceSelect = (service: ServiceType) => {
    setSelectedService(service);
    setStep('details');
    setError(null);
  };

  const analyzeSymptomsWithAI = async () => {
    if (!patientDetails.symptoms.trim()) {
      setError('Please describe your symptoms to get AI analysis');
      return;
    }

    setAiLoading(true);
    setError(null);

    try {
      const analysisRequest: SymptomAnalysisRequest = {
        symptoms: patientDetails.symptoms,
        patient_age: patientDetails.dateOfBirth ? 
          new Date().getFullYear() - new Date(patientDetails.dateOfBirth).getFullYear() + '' : undefined,
        medical_history: '', // Could be added to patient details
        additional_context: ''
      };

      const result = await aiService.analyzeSymptomsWithAI(analysisRequest);
      
      if (result.success) {
        setSymptomAnalysisResult(result.analysis);
        setAiRecommendations(result.recommendations);
        setAiConfidence(result.analysis.confidence);
        setEmergencyLevel(result.analysis.emergency_level);
        setShowAIAnalysis(true);
        
        // Update patient priority based on AI analysis
        if (result.analysis.emergency_level === 'critical') {
          setPatientDetails(prev => ({ ...prev, priority: 'urgent' }));
        } else if (result.analysis.emergency_level === 'high') {
          setPatientDetails(prev => ({ ...prev, priority: 'high' }));
        }
      }
    } catch (err) {
      console.error('AI analysis failed:', err);
      
      // Fallback: Use local analysis
      const symptomsLower = patientDetails.symptoms.toLowerCase();
      let emergencyLevel = 'moderate';
      let confidence = 0.6;
      let recommendations = ['📋 Basic symptom analysis completed'];
      
      if (symptomsLower.includes('emergency') || symptomsLower.includes('urgent') || 
          symptomsLower.includes('chest pain') || symptomsLower.includes('severe')) {
        emergencyLevel = 'critical';
        confidence = 0.8;
        recommendations = ['🚨 CRITICAL - Seek immediate medical attention'];
        setPatientDetails(prev => ({ ...prev, priority: 'urgent' }));
      } else if (symptomsLower.includes('pain') || symptomsLower.includes('fever')) {
        emergencyLevel = 'high';
        confidence = 0.7;
        recommendations = ['⚠️ HIGH PRIORITY - Seek medical attention soon'];
        setPatientDetails(prev => ({ ...prev, priority: 'high' }));
      }
      
      const mockAnalysis = {
        emergency_level: emergencyLevel,
        confidence: confidence,
        triage_category: emergencyLevel === 'critical' ? 'Emergency' : 
                        emergencyLevel === 'high' ? 'Urgent' : 'Semi-urgent',
        estimated_wait_time: emergencyLevel === 'critical' ? 0 : 
                           emergencyLevel === 'high' ? 15 : 45,
        department_recommendation: emergencyLevel === 'critical' ? 'Emergency Care' :
                                 emergencyLevel === 'high' ? 'Urgent Care' : 'General Medicine',
        recommended_actions: recommendations,
        risk_factors: emergencyLevel === 'critical' ? ['Potential emergency'] : [],
        ai_reasoning: `Local analysis indicates ${emergencyLevel} priority based on symptom keywords.`
      };
      
      setSymptomAnalysisResult(mockAnalysis);
      setAiRecommendations(recommendations);
      setAiConfidence(confidence);
      setEmergencyLevel(emergencyLevel);
      setShowAIAnalysis(true);
      
      // Toast notification removed temporarily
      
      setError('AI analysis completed using local analysis. Results may be less accurate.');
    } finally {
      setAiLoading(false);
    }
  };

  const getAITriageAnalysis = async () => {
    if (!patientDetails.symptoms.trim()) {
      setError('Please describe your symptoms to get AI triage analysis');
      return;
    }

    setAiLoading(true);
    setError(null);

    try {
      const triageRequest: AITriageRequest = {
        symptoms: patientDetails.symptoms,
        age_group: patientDetails.dateOfBirth ? 
          new Date().getFullYear() - new Date(patientDetails.dateOfBirth).getFullYear() < 18 ? 'pediatric' : 'adult' : 'adult',
        insurance_type: 'private', // Default, could be made configurable
        department: selectedService?.department,
        medical_history: '', // Could be added to patient details
        additional_context: ''
      };

      const result = await aiService.getAITriageAnalysis(triageRequest);
      
      if (result.success) {
        setAiTriageResult(result.triage_result);
        setAiRecommendations(result.recommendations);
        setAiConfidence(result.triage_result.ai_analysis.confidence);
        setEmergencyLevel(result.triage_result.ai_analysis.emergency_level);
        setShowAIAnalysis(true);
        
        // Update patient priority based on AI triage
        if (result.triage_result.category === 'Emergency') {
          setPatientDetails(prev => ({ ...prev, priority: 'urgent' }));
        } else if (result.triage_result.category === 'Urgent') {
          setPatientDetails(prev => ({ ...prev, priority: 'high' }));
        }
      }
    } catch (err) {
      console.error('AI triage analysis failed:', err);
      
      // Fallback: Use local triage analysis
      const symptomsLower = patientDetails.symptoms.toLowerCase();
      let category = 'Semi-urgent';
      let triageScore = 5;
      let emergencyLevel = 'moderate';
      let confidence = 0.6;
      let recommendations = ['📋 Basic triage analysis completed'];
      
      if (symptomsLower.includes('emergency') || symptomsLower.includes('urgent') || 
          symptomsLower.includes('chest pain') || symptomsLower.includes('severe') ||
          symptomsLower.includes('bleeding') || symptomsLower.includes('unconscious')) {
        category = 'Emergency';
        triageScore = 9;
        emergencyLevel = 'critical';
        confidence = 0.8;
        recommendations = ['🚨 EMERGENCY - Immediate attention required'];
        setPatientDetails(prev => ({ ...prev, priority: 'urgent' }));
      } else if (symptomsLower.includes('pain') || symptomsLower.includes('fever') ||
                 symptomsLower.includes('serious') || symptomsLower.includes('high')) {
        category = 'Urgent';
        triageScore = 7;
        emergencyLevel = 'high';
        confidence = 0.7;
        recommendations = ['⚠️ URGENT - Prompt attention needed'];
        setPatientDetails(prev => ({ ...prev, priority: 'high' }));
      }
      
      const mockTriageResult = {
        triage_score: triageScore,
        category: category,
        priority_level: emergencyLevel === 'critical' ? 5 : emergencyLevel === 'high' ? 4 : 3,
        estimated_wait_time: emergencyLevel === 'critical' ? 0 : 
                           emergencyLevel === 'high' ? 15 : 45,
        recommended_department: emergencyLevel === 'critical' ? 'Emergency Care' :
                              emergencyLevel === 'high' ? 'Urgent Care' : 'General Medicine',
        ai_analysis: {
          emergency_level: emergencyLevel,
          confidence: confidence,
          reasoning: `Local triage analysis indicates ${category} priority based on symptom keywords.`,
          recommended_actions: recommendations,
          risk_factors: emergencyLevel === 'critical' ? ['Potential emergency'] : []
        }
      };
      
      setAiTriageResult(mockTriageResult);
      setAiRecommendations(recommendations);
      setAiConfidence(confidence);
      setEmergencyLevel(emergencyLevel);
      setShowAIAnalysis(true);
      
      setError('AI triage analysis completed using local analysis. Results may be less accurate.');
    } finally {
      setAiLoading(false);
    }
  };

  const getComprehensiveAIAnalysis = async () => {
    if (!patientDetails.symptoms.trim()) {
      setError('Please describe your symptoms to get comprehensive AI analysis');
      return;
    }

    setAiLoading(true);
    setError(null);

    try {
      const result = await aiService.getComprehensiveSymptomAnalysis(
        patientDetails.symptoms,
        patientDetails.dateOfBirth ? 
          new Date().getFullYear() - new Date(patientDetails.dateOfBirth).getFullYear() + '' : undefined,
        '', // medical history
        '' // additional context
      );

      setSymptomAnalysisResult(result.analysis.analysis);
      setAiTriageResult(result.triage.triage_result);
      setAiRecommendations(result.combinedRecommendations);
      setAiConfidence(Math.max(result.analysis.analysis.confidence, result.triage.triage_result.ai_analysis.confidence));
      setEmergencyLevel(result.analysis.analysis.emergency_level);
      setShowAIAnalysis(true);
      
      // Update patient priority based on comprehensive analysis
      if (result.analysis.analysis.emergency_level === 'critical') {
        setPatientDetails(prev => ({ ...prev, priority: 'urgent' }));
      } else if (result.analysis.analysis.emergency_level === 'high') {
        setPatientDetails(prev => ({ ...prev, priority: 'high' }));
      }
    } catch (err) {
      console.error('Comprehensive AI analysis failed:', err);
      
      // Fallback: Create mock analysis based on symptoms
      const symptomsLower = patientDetails.symptoms.toLowerCase();
      let emergencyLevel = 'moderate';
      let confidence = 0.7;
      let recommendations = [];
      
      // Determine emergency level based on keywords
      if (symptomsLower.includes('emergency') || symptomsLower.includes('urgent') || 
          symptomsLower.includes('chest pain') || symptomsLower.includes('severe') ||
          symptomsLower.includes('bleeding') || symptomsLower.includes('unconscious') ||
          symptomsLower.includes('difficulty breathing') || symptomsLower.includes('critical')) {
        emergencyLevel = 'critical';
        confidence = 0.9;
        recommendations = [
          '🚨 CRITICAL EMERGENCY - Immediate medical attention required',
          '📞 Call emergency services immediately',
          '⚡ Seek emergency room immediately'
        ];
        setPatientDetails(prev => ({ ...prev, priority: 'urgent' }));
      } else if (symptomsLower.includes('high') || symptomsLower.includes('serious') ||
                 symptomsLower.includes('pain') || symptomsLower.includes('fever')) {
        emergencyLevel = 'high';
        confidence = 0.8;
        recommendations = [
          '⚠️ HIGH PRIORITY - Seek medical attention within 30 minutes',
          '👥 Ensure adequate staff coverage for urgent cases',
          '📋 Monitor symptoms closely'
        ];
        setPatientDetails(prev => ({ ...prev, priority: 'high' }));
      } else {
        emergencyLevel = 'moderate';
        confidence = 0.6;
        recommendations = [
          '📋 MODERATE PRIORITY - Schedule appointment within 1-2 hours',
          '📅 Routine care appropriate',
          '⏰ Monitor symptoms and seek care if they worsen'
        ];
      }
      
      // Create mock analysis results
      const mockSymptomAnalysis = {
        emergency_level: emergencyLevel,
        confidence: confidence,
        triage_category: emergencyLevel === 'critical' ? 'Emergency' : 
                        emergencyLevel === 'high' ? 'Urgent' : 'Semi-urgent',
        estimated_wait_time: emergencyLevel === 'critical' ? 0 : 
                           emergencyLevel === 'high' ? 15 : 45,
        department_recommendation: emergencyLevel === 'critical' ? 'Emergency Care' :
                                 emergencyLevel === 'high' ? 'Urgent Care' : 'General Medicine',
        recommended_actions: recommendations,
        risk_factors: emergencyLevel === 'critical' ? ['Life-threatening condition'] : [],
        ai_reasoning: `Based on symptom analysis, this appears to be a ${emergencyLevel} priority case requiring ${emergencyLevel === 'critical' ? 'immediate' : emergencyLevel === 'high' ? 'prompt' : 'routine'} medical attention.`
      };
      
      const mockTriageResult = {
        triage_score: emergencyLevel === 'critical' ? 9 : emergencyLevel === 'high' ? 7 : 5,
        category: mockSymptomAnalysis.triage_category,
        priority_level: emergencyLevel === 'critical' ? 5 : emergencyLevel === 'high' ? 4 : 3,
        estimated_wait_time: mockSymptomAnalysis.estimated_wait_time,
        recommended_department: mockSymptomAnalysis.department_recommendation,
        ai_analysis: {
          emergency_level: emergencyLevel,
          confidence: confidence,
          reasoning: mockSymptomAnalysis.ai_reasoning,
          recommended_actions: recommendations,
          risk_factors: mockSymptomAnalysis.risk_factors
        }
      };
      
      setSymptomAnalysisResult(mockSymptomAnalysis);
      setAiTriageResult(mockTriageResult);
      setAiRecommendations(recommendations);
      setAiConfidence(confidence);
      setEmergencyLevel(emergencyLevel);
      setShowAIAnalysis(true);
      
      setError('AI analysis completed using fallback analysis. Results may be less accurate.');
    } finally {
      setAiLoading(false);
    }
  };

  const getAIServiceRecommendations = async () => {
    if (!patientDetails.symptoms.trim()) {
      setError('Please describe your symptoms to get AI service recommendations');
      return;
    }

    setAiLoading(true);
    setError(null);

    try {
      // First try to get AI service suggestion from backend
      let suggestion = null;
      try {
        suggestion = await aiService.getServiceSuggestion(patientDetails.symptoms);
        console.log('AI suggestion received:', suggestion);
      } catch (aiError) {
        console.log('AI service suggestion failed, using local analysis:', aiError);
      }
      
      // Local symptom analysis as fallback
      const symptomsLower = patientDetails.symptoms.toLowerCase();
      let recommendedServices = [];
      
      // Emergency keywords
      if (symptomsLower.includes('emergency') || symptomsLower.includes('urgent') || 
          symptomsLower.includes('chest pain') || symptomsLower.includes('severe') ||
          symptomsLower.includes('bleeding') || symptomsLower.includes('unconscious') ||
          symptomsLower.includes('difficulty breathing') || symptomsLower.includes('critical')) {
        recommendedServices = services.filter(s => 
          s.department.toLowerCase().includes('emergency') || 
          s.name.toLowerCase().includes('emergency')
        );
      }
      // Heart/Cardiac keywords
      else if (symptomsLower.includes('heart') || symptomsLower.includes('cardiac') ||
               symptomsLower.includes('palpitations') || symptomsLower.includes('blood pressure')) {
        recommendedServices = services.filter(s => 
          s.department.toLowerCase().includes('cardiology') || 
          s.name.toLowerCase().includes('cardiology')
        );
      }
      // Pediatric keywords
      else if (symptomsLower.includes('child') || symptomsLower.includes('baby') ||
               symptomsLower.includes('infant') || symptomsLower.includes('pediatric')) {
        recommendedServices = services.filter(s => 
          s.department.toLowerCase().includes('pediatric') || 
          s.name.toLowerCase().includes('pediatric')
        );
      }
      // Lab/Test keywords
      else if (symptomsLower.includes('blood test') || symptomsLower.includes('lab') ||
               symptomsLower.includes('test') || symptomsLower.includes('screening')) {
        recommendedServices = services.filter(s => 
          s.department.toLowerCase().includes('laboratory') || 
          s.name.toLowerCase().includes('laboratory')
        );
      }
      // Radiology keywords
      else if (symptomsLower.includes('x-ray') || symptomsLower.includes('scan') ||
               symptomsLower.includes('imaging') || symptomsLower.includes('fracture')) {
        recommendedServices = services.filter(s => 
          s.department.toLowerCase().includes('radiology') || 
          s.name.toLowerCase().includes('radiology')
        );
      }
      // General medicine keywords
      else if (symptomsLower.includes('fever') || symptomsLower.includes('cold') ||
               symptomsLower.includes('flu') || symptomsLower.includes('headache') ||
               symptomsLower.includes('general') || symptomsLower.includes('checkup')) {
        recommendedServices = services.filter(s => 
          s.department.toLowerCase().includes('general') || 
          s.name.toLowerCase().includes('general')
        );
      }

      // If we have AI suggestion, try to use it
      if (suggestion && suggestion.service) {
        const aiMatchedServices = services.filter(service => 
          service.name.toLowerCase().includes(suggestion.service.toLowerCase()) ||
          service.department.toLowerCase().includes(suggestion.service.toLowerCase()) ||
          suggestion.service.toLowerCase().includes(service.name.toLowerCase()) ||
          suggestion.service.toLowerCase().includes(service.department.toLowerCase())
        );
        
        if (aiMatchedServices.length > 0) {
          recommendedServices = aiMatchedServices;
        }
      }

      // If still no matches, use all services
      if (recommendedServices.length === 0) {
        recommendedServices = services;
      }

      // Sort by AI predicted wait time and take top 3
      const finalRecommendations = recommendedServices
        .sort((a, b) => a.aiPredictedWait - b.aiPredictedWait)
        .slice(0, 3);

      console.log('Final recommendations:', finalRecommendations);

      setAiRecommendedServices(finalRecommendations);
      setShowServiceRecommendations(true);
      
      // Auto-select the best recommendation
      if (finalRecommendations.length > 0) {
        setSelectedService(finalRecommendations[0]);
      }
      
      // Toast notification removed temporarily
      
    } catch (err) {
      console.error('Service recommendation failed:', err);
      
      // Ultimate fallback: show first 3 services
      const fallbackServices = services.slice(0, 3);
      setAiRecommendedServices(fallbackServices);
      setShowServiceRecommendations(true);
      if (fallbackServices.length > 0) {
        setSelectedService(fallbackServices[0]);
      }
      
      setError('Service recommendation completed with fallback options.');
    } finally {
      setAiLoading(false);
    }
  };

  const proceedWithAIAnalysis = async () => {
    if (!patientDetails.symptoms.trim()) {
      setError('Please describe your symptoms to proceed');
      return;
    }

    setAiLoading(true);
    setError(null);

    try {
      // Get comprehensive analysis and service recommendations
      await Promise.all([
        getComprehensiveAIAnalysis(),
        getAIServiceRecommendations()
      ]);
      
      // Move to service selection step
      setStep('service');
    } catch (err) {
      console.error('AI analysis failed:', err);
      setError('AI analysis failed. Please try again or proceed manually.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleDetailsSubmit = async () => {
    if (!selectedService) return;

    setLoading(true);
    setError(null);

    try {
      const result = await queueService.joinQueue(selectedService.id, patientDetails);

      setQueueStatus({
        queueNumber: result.queue_number,
        estimatedWait: result.estimated_wait,
        aiPredictedWait: result.ai_predicted_wait,
        position: Math.floor(Math.random() * 5) + 1,
        status: 'waiting'
      });

      setStep('confirmation');
      setSuccess(`Successfully joined queue! Your queue number is ${result.queue_number}`);
      
      // Add notification
      notificationService.addNotification({
        type: 'success',
        title: 'Queue Joined Successfully!',
        message: `You are now in queue for ${selectedService.name}. Queue #${result.queue_number}`
      });
      
      // Toast notification removed temporarily

    } catch (err: any) {
      setError(err.message || 'Failed to join queue. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    setStep('waiting');
    setSuccess(null);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-blue-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent': return AlertCircle;
      case 'high': return TrendingUp;
      case 'medium': return Clock;
      case 'low': return CheckCircle;
      default: return Clock;
    }
  };

  const getServiceIcon = (department: string) => {
    switch (department.toLowerCase()) {
      case 'emergency': return AlertCircle;
      case 'cardiology': return Heart;
      case 'general': return Stethoscope;
      case 'laboratory': return Activity;
      case 'radiology': return Brain;
      case 'pediatrics': return Users;
      default: return Stethoscope;
    }
  };

  const steps = [
    { id: 'symptoms', title: 'Describe Symptoms', icon: FileText },
    { id: 'service', title: 'AI Service Recommendation', icon: Bot },
    { id: 'details', title: 'Patient Details', icon: User },
    { id: 'confirmation', title: 'Confirmation', icon: CheckCircle },
    { id: 'waiting', title: 'Queue Status', icon: Clock }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8">
      <div className="max-w-6xl mx-auto px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4">
              <Stethoscope className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI-Powered Hospital Queue
              </h1>
              <p className="text-lg text-gray-600">Describe your symptoms and let AI find the best service for you</p>
            </div>
          </div>
        </motion.div>

        {/* Progress Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-center space-x-4">
            {steps.map((stepItem, index) => {
              const Icon = stepItem.icon;
              const isActive = step === stepItem.id;
              const isCompleted = steps.findIndex(s => s.id === step) > index;
              
              return (
                <div key={stepItem.id} className="flex items-center">
                  <div className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
                    isActive 
                      ? 'bg-blue-500 text-white shadow-lg' 
                      : isCompleted 
                      ? 'bg-green-500 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    <Icon className="h-5 w-5" />
                    <span className="font-medium">{stepItem.title}</span>
                  </div>
                  {index < steps.length - 1 && (
                    <ArrowRight className="h-5 w-5 text-gray-400 mx-2" />
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Main Content */}
        <AnimatePresence mode="wait">
          {step === 'symptoms' && (
            <motion.div
              key="symptoms"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl text-center mb-2 flex items-center justify-center">
                    <Bot className="h-6 w-6 mr-2 text-blue-600" />
                    Describe Your Symptoms
                  </CardTitle>
                  <p className="text-center text-gray-600">
                    Tell us what's bothering you and our AI will recommend the best medical service for your needs.
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="max-w-2xl mx-auto space-y-6">
                    {/* Symptoms Input */}
                    <div>
                      <Label htmlFor="symptoms" className="text-lg font-medium flex items-center mb-3">
                        <FileText className="h-5 w-5 mr-2 text-blue-600" />
                        What symptoms are you experiencing?
                      </Label>
                      <Textarea
                        id="symptoms"
                        value={patientDetails.symptoms}
                        onChange={(e) => setPatientDetails({ ...patientDetails, symptoms: e.target.value })}
                        placeholder="Please describe your symptoms in detail. For example: 'I have chest pain that started this morning, accompanied by shortness of breath and dizziness...'"
                        className="min-h-[120px] text-base"
                        rows={5}
                      />
                      <p className="text-sm text-gray-500 mt-2">
                        💡 The more details you provide, the better our AI can recommend the right service for you.
                      </p>
                    </div>

                    {/* Age Group Selection */}
                    <div>
                      <Label htmlFor="ageGroup" className="text-lg font-medium flex items-center mb-3">
                        <User className="h-5 w-5 mr-2 text-blue-600" />
                        Age Group (Optional)
                      </Label>
                      <Select
                        value={patientDetails.dateOfBirth ? 
                          new Date().getFullYear() - new Date(patientDetails.dateOfBirth).getFullYear() < 18 ? 'pediatric' : 'adult' : 'adult'}
                        onValueChange={(value) => {
                          // Set a default date of birth based on age group
                          const currentYear = new Date().getFullYear();
                          const birthYear = value === 'pediatric' ? currentYear - 10 : currentYear - 30;
                          setPatientDetails({ 
                            ...patientDetails, 
                            dateOfBirth: `${birthYear}-01-01` 
                          });
                        }}
                      >
                        <SelectTrigger className="text-base">
                          <SelectValue placeholder="Select your age group" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pediatric">Pediatric (Under 18)</SelectItem>
                          <SelectItem value="adult">Adult (18+)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* AI Analysis Button */}
                    <div className="text-center">
                      <Button
                        onClick={proceedWithAIAnalysis}
                        disabled={aiLoading || !patientDetails.symptoms.trim()}
                        size="lg"
                        className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 px-8 py-3 text-lg"
                      >
                        {aiLoading ? (
                          <>
                            <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                            AI is analyzing your symptoms...
                          </>
                        ) : (
                          <>
                            <Bot className="h-5 w-5 mr-2" />
                            Get AI Service Recommendation
                          </>
                        )}
                      </Button>
                      <p className="text-sm text-gray-500 mt-3">
                        Our AI will analyze your symptoms and recommend the most appropriate medical service
                      </p>
                    </div>

                    {/* Emergency Notice */}
                    <Alert className="border-red-200 bg-red-50">
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                      <AlertDescription className="text-red-800">
                        <strong>Emergency Notice:</strong> If you're experiencing a life-threatening emergency (chest pain, severe bleeding, difficulty breathing), please call emergency services immediately or go to the nearest emergency room.
                      </AlertDescription>
                    </Alert>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {step === 'service' && (
            <motion.div
              key="service"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-2xl mb-2 flex items-center">
                        <Bot className="h-6 w-6 mr-2 text-green-600" />
                        AI Service Recommendation
                      </CardTitle>
                      <p className="text-gray-600">Based on your symptoms, our AI recommends these services:</p>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => setStep('symptoms')}
                      className="flex items-center"
                    >
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* AI Analysis Results */}
                  {showAIAnalysis && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mb-6 space-y-4"
                    >
                      {/* Emergency Level Alert */}
                      {emergencyLevel === 'critical' && (
                        <Alert className="border-red-500 bg-red-50">
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                          <AlertDescription className="text-red-800">
                            <strong>CRITICAL EMERGENCY DETECTED</strong> - AI analysis indicates this may be a life-threatening condition requiring immediate medical attention.
                          </AlertDescription>
                        </Alert>
                      )}

                      {emergencyLevel === 'high' && (
                        <Alert className="border-orange-500 bg-orange-50">
                          <AlertTriangle className="h-4 w-4 text-orange-600" />
                          <AlertDescription className="text-orange-800">
                            <strong>HIGH PRIORITY</strong> - AI analysis suggests this condition requires prompt medical attention.
                          </AlertDescription>
                        </Alert>
                      )}

                      {/* AI Analysis Summary */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {symptomAnalysisResult && (
                          <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-lg flex items-center">
                                <Brain className="h-5 w-5 mr-2 text-purple-600" />
                                AI Analysis Summary
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Confidence:</span>
                                <div className="flex items-center">
                                  <Progress value={symptomAnalysisResult.confidence * 100} className="w-20 mr-2" />
                                  <span className="text-sm font-semibold">
                                    {Math.round(symptomAnalysisResult.confidence * 100)}%
                                  </span>
                                </div>
                              </div>
                              
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Emergency Level:</span>
                                <Badge variant={
                                  symptomAnalysisResult.emergency_level === 'critical' ? 'destructive' :
                                  symptomAnalysisResult.emergency_level === 'high' ? 'default' :
                                  symptomAnalysisResult.emergency_level === 'moderate' ? 'secondary' : 'outline'
                                }>
                                  {symptomAnalysisResult.emergency_level.toUpperCase()}
                                </Badge>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Recommended Department:</span>
                                <span className="text-sm font-semibold text-purple-600">
                                  {symptomAnalysisResult.department_recommendation}
                                </span>
                              </div>
                            </CardContent>
                          </Card>
                        )}

                        {aiTriageResult && (
                          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-lg flex items-center">
                                <Target className="h-5 w-5 mr-2 text-green-600" />
                                Triage Analysis
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Triage Score:</span>
                                <span className="text-sm font-semibold text-green-600">
                                  {aiTriageResult.triage_score}/10
                                </span>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Category:</span>
                                <Badge variant={
                                  aiTriageResult.category === 'Emergency' ? 'destructive' :
                                  aiTriageResult.category === 'Urgent' ? 'default' :
                                  aiTriageResult.category === 'Semi-urgent' ? 'secondary' : 'outline'
                                }>
                                  {aiTriageResult.category}
                                </Badge>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">AI Confidence:</span>
                                <div className="flex items-center">
                                  <Progress value={aiTriageResult.ai_analysis.confidence * 100} className="w-20 mr-2" />
                                  <span className="text-sm font-semibold">
                                    {Math.round(aiTriageResult.ai_analysis.confidence * 100)}%
                                  </span>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {/* Recommended Services */}
                  {showServiceRecommendations && aiRecommendedServices.length > 0 && (
                    <div className="space-y-4">
                      <h3 className="text-xl font-semibold text-center mb-4">
                        🎯 Recommended Services for You
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {aiRecommendedServices.map((service, index) => {
                          const Icon = getServiceIcon(service.department);
                          const isRecommended = index === 0;
                          return (
                            <motion.div
                              key={service.id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.1 }}
                              whileHover={{ y: -5, scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                              onClick={() => {
                                setSelectedService(service);
                                setStep('details');
                              }}
                              className="cursor-pointer"
                            >
                              <Card className={`h-full hover:shadow-xl transition-all duration-300 border-0 bg-gradient-to-br ${
                                isRecommended 
                                  ? 'from-green-50 to-emerald-50 border-green-200' 
                                  : 'from-white to-gray-50'
                              } group relative`}>
                                {isRecommended && (
                                  <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
                                    AI TOP PICK
                                  </div>
                                )}
                                <CardContent className="p-6">
                                  <div className="flex items-start justify-between mb-4">
                                    <div className={`w-12 h-12 bg-gradient-to-r ${
                                      isRecommended 
                                        ? 'from-green-500 to-emerald-600' 
                                        : 'from-blue-500 to-purple-600'
                                    } rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                                      <Icon className="h-6 w-6 text-white" />
                                    </div>
                                    <Badge variant="outline" className="text-xs">
                                      {service.queueLength} waiting
                                    </Badge>
                                  </div>
                                  
                                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                    {service.name}
                                  </h3>
                                  
                                  <p className="text-gray-600 mb-4 text-sm">
                                    {service.description}
                                  </p>
                                  
                                  <div className="space-y-2">
                                    <div className="flex items-center justify-between text-sm">
                                      <div className="flex items-center text-gray-500">
                                        <Clock className="h-4 w-4 mr-1" />
                                        <span>Avg Wait</span>
                                      </div>
                                      <span className="font-medium">{service.currentWaitTime} min</span>
                                    </div>
                                    
                                    <div className="flex items-center justify-between text-sm">
                                      <div className="flex items-center text-gray-500">
                                        <Brain className="h-4 w-4 mr-1" />
                                        <span>AI Prediction</span>
                                      </div>
                                      <span className="font-medium text-green-600">{service.aiPredictedWait} min</span>
                                    </div>
                                    
                                    <div className="flex items-center justify-between text-sm">
                                      <div className="flex items-center text-gray-500">
                                        <Users className="h-4 w-4 mr-1" />
                                        <span>Staff</span>
                                      </div>
                                      <span className="font-medium">{service.staffCount} available</span>
                                    </div>
                                  </div>
                                  
                                  <Button className={`w-full mt-4 ${
                                    isRecommended 
                                      ? 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700' 
                                      : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
                                  }`}>
                                    {isRecommended ? 'Select Recommended' : 'Select Service'}
                                    <ArrowRight className="h-4 w-4 ml-2" />
                                  </Button>
                                </CardContent>
                              </Card>
                            </motion.div>
                          );
                        })}
                      </div>

                      {/* Manual Selection Option */}
                      <div className="text-center mt-6">
                        <Button
                          variant="outline"
                          onClick={() => {
                            setShowServiceRecommendations(false);
                            setStep('details');
                          }}
                          className="text-gray-600"
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          View All Services Instead
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {step === 'details' && (
            <motion.div
              key="details"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-2xl mb-2">Patient Information</CardTitle>
                      <p className="text-gray-600">Please provide your details for queue registration</p>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => setStep('symptoms')}
                      className="flex items-center"
                    >
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="name" className="text-sm font-medium flex items-center">
                          <User className="h-4 w-4 mr-2" />
                          Full Name *
                        </Label>
                        <Input
                          id="name"
                          value={patientDetails.name}
                          onChange={(e) => setPatientDetails({ ...patientDetails, name: e.target.value })}
                          placeholder="Enter your full name"
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="phone" className="text-sm font-medium flex items-center">
                          <Phone className="h-4 w-4 mr-2" />
                          Phone Number *
                        </Label>
                        <Input
                          id="phone"
                          value={patientDetails.phone}
                          onChange={(e) => setPatientDetails({ ...patientDetails, phone: e.target.value })}
                          placeholder="Enter your phone number"
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="email" className="text-sm font-medium flex items-center">
                          <Mail className="h-4 w-4 mr-2" />
                          Email Address *
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          value={patientDetails.email}
                          onChange={(e) => setPatientDetails({ ...patientDetails, email: e.target.value })}
                          placeholder="Enter your email address"
                          className="mt-1"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="dateOfBirth" className="text-sm font-medium flex items-center">
                          <Calendar className="h-4 w-4 mr-2" />
                          Date of Birth *
                        </Label>
                        <Input
                          id="dateOfBirth"
                          type="date"
                          value={patientDetails.dateOfBirth}
                          onChange={(e) => setPatientDetails({ ...patientDetails, dateOfBirth: e.target.value })}
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="priority" className="text-sm font-medium flex items-center">
                          <Star className="h-4 w-4 mr-2" />
                          Priority Level
                        </Label>
                        <Select
                          value={patientDetails.priority}
                          onValueChange={(value) => setPatientDetails({ ...patientDetails, priority: value as any })}
                        >
                          <SelectTrigger className="mt-1">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="low">Low - Routine care</SelectItem>
                            <SelectItem value="medium">Medium - Standard care</SelectItem>
                            <SelectItem value="high">High - Needs attention soon</SelectItem>
                            <SelectItem value="urgent">Urgent - Immediate care needed</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="symptoms" className="text-sm font-medium flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          Symptoms (Optional)
                        </Label>
                        <Textarea
                          id="symptoms"
                          value={patientDetails.symptoms}
                          onChange={(e) => setPatientDetails({ ...patientDetails, symptoms: e.target.value })}
                          placeholder="Describe your symptoms or reason for visit"
                          className="mt-1"
                          rows={3}
                        />
                        
                      </div>
                    </div>
                  </div>
                  
                  {selectedService && (
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <h4 className="font-semibold text-blue-900 mb-2">Selected Service</h4>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          {React.createElement(getServiceIcon(selectedService.department), { className: "h-5 w-5 text-blue-600 mr-2" })}
                          <span className="font-medium">{selectedService.name}</span>
                        </div>
                        <div className="text-sm text-blue-600">
                          Est. Wait: {selectedService.currentWaitTime} min
                        </div>
                      </div>
                    </div>
                  )}

                  {/* AI Analysis Results */}
                  {showAIAnalysis && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-6 space-y-4"
                    >
                      {/* Emergency Level Alert */}
                      {emergencyLevel === 'critical' && (
                        <Alert className="border-red-500 bg-red-50">
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                          <AlertDescription className="text-red-800">
                            <strong>CRITICAL EMERGENCY DETECTED</strong> - AI analysis indicates this may be a life-threatening condition requiring immediate medical attention.
                          </AlertDescription>
                        </Alert>
                      )}

                      {emergencyLevel === 'high' && (
                        <Alert className="border-orange-500 bg-orange-50">
                          <AlertTriangle className="h-4 w-4 text-orange-600" />
                          <AlertDescription className="text-orange-800">
                            <strong>HIGH PRIORITY</strong> - AI analysis suggests this condition requires prompt medical attention.
                          </AlertDescription>
                        </Alert>
                      )}

                      {/* AI Analysis Cards */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Symptom Analysis */}
                        {symptomAnalysisResult && (
                          <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-lg flex items-center">
                                <Brain className="h-5 w-5 mr-2 text-purple-600" />
                                AI Symptom Analysis
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Confidence:</span>
                                <div className="flex items-center">
                                  <Progress value={symptomAnalysisResult.confidence * 100} className="w-20 mr-2" />
                                  <span className="text-sm font-semibold">
                                    {Math.round(symptomAnalysisResult.confidence * 100)}%
                                  </span>
                                </div>
                              </div>
                              
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Emergency Level:</span>
                                <Badge variant={
                                  symptomAnalysisResult.emergency_level === 'critical' ? 'destructive' :
                                  symptomAnalysisResult.emergency_level === 'high' ? 'default' :
                                  symptomAnalysisResult.emergency_level === 'moderate' ? 'secondary' : 'outline'
                                }>
                                  {symptomAnalysisResult.emergency_level.toUpperCase()}
                                </Badge>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Recommended Department:</span>
                                <span className="text-sm font-semibold text-purple-600">
                                  {symptomAnalysisResult.department_recommendation}
                                </span>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Estimated Wait:</span>
                                <span className="text-sm font-semibold">
                                  {symptomAnalysisResult.estimated_wait_time} min
                                </span>
                              </div>

                              {symptomAnalysisResult.ai_reasoning && (
                                <div className="mt-3 p-3 bg-white/50 rounded-lg">
                                  <p className="text-sm text-gray-700">
                                    <strong>AI Reasoning:</strong> {symptomAnalysisResult.ai_reasoning}
                                  </p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}

                        {/* Triage Analysis */}
                        {aiTriageResult && (
                          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-lg flex items-center">
                                <Target className="h-5 w-5 mr-2 text-green-600" />
                                AI Triage Analysis
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Triage Score:</span>
                                <span className="text-sm font-semibold text-green-600">
                                  {aiTriageResult.triage_score}/10
                                </span>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Category:</span>
                                <Badge variant={
                                  aiTriageResult.category === 'Emergency' ? 'destructive' :
                                  aiTriageResult.category === 'Urgent' ? 'default' :
                                  aiTriageResult.category === 'Semi-urgent' ? 'secondary' : 'outline'
                                }>
                                  {aiTriageResult.category}
                                </Badge>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Priority Level:</span>
                                <span className="text-sm font-semibold">
                                  {aiTriageResult.priority_level}/5
                                </span>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">AI Confidence:</span>
                                <div className="flex items-center">
                                  <Progress value={aiTriageResult.ai_analysis.confidence * 100} className="w-20 mr-2" />
                                  <span className="text-sm font-semibold">
                                    {Math.round(aiTriageResult.ai_analysis.confidence * 100)}%
                                  </span>
                                </div>
                              </div>

                              {aiTriageResult.ai_analysis.reasoning && (
                                <div className="mt-3 p-3 bg-white/50 rounded-lg">
                                  <p className="text-sm text-gray-700">
                                    <strong>AI Reasoning:</strong> {aiTriageResult.ai_analysis.reasoning}
                                  </p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}
                      </div>

                      {/* AI Recommendations */}
                      {aiRecommendations.length > 0 && (
                        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-lg flex items-center">
                              <Sparkles className="h-5 w-5 mr-2 text-blue-600" />
                              AI Recommendations
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <ul className="space-y-2">
                              {aiRecommendations.map((recommendation, index) => (
                                <li key={index} className="flex items-start">
                                  <CheckCircle2 className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                                  <span className="text-sm text-gray-700">{recommendation}</span>
                                </li>
                              ))}
                            </ul>
                          </CardContent>
                        </Card>
                      )}

                      {/* Risk Factors */}
                      {(symptomAnalysisResult?.risk_factors?.length > 0 || aiTriageResult?.ai_analysis?.risk_factors?.length > 0) && (
                        <Card className="bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-lg flex items-center">
                              <AlertTriangle className="h-5 w-5 mr-2 text-yellow-600" />
                              Identified Risk Factors
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <ul className="space-y-2">
                              {[
                                ...(symptomAnalysisResult?.risk_factors || []),
                                ...(aiTriageResult?.ai_analysis?.risk_factors || [])
                              ].filter((factor, index, arr) => arr.indexOf(factor) === index).map((factor, index) => (
                                <li key={index} className="flex items-start">
                                  <AlertTriangle className="h-4 w-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                                  <span className="text-sm text-gray-700">{factor}</span>
                                </li>
                              ))}
                            </ul>
                          </CardContent>
                        </Card>
                      )}
                    </motion.div>
                  )}
                  
                  <div className="flex justify-end mt-6">
                    <Button
                      onClick={handleDetailsSubmit}
                      disabled={loading || !patientDetails.name || !patientDetails.phone || !patientDetails.email || !patientDetails.dateOfBirth}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 px-8"
                    >
                      {loading ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          Join Queue
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {step === 'confirmation' && queueStatus && (
            <motion.div
              key="confirmation"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl text-center text-green-600 mb-2">
                    <CheckCircle className="h-8 w-8 inline mr-2" />
                    Queue Registration Successful!
                  </CardTitle>
                  <p className="text-center text-gray-600">
                    You have been successfully added to the queue
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-6">
                    <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-3xl font-bold text-white">
                        {queueStatus.queueNumber}
                      </span>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      Queue Number #{queueStatus.queueNumber}
                    </h3>
                    <p className="text-gray-600">
                      {selectedService?.name} • {selectedService?.department}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <Clock className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-blue-600">{queueStatus.estimatedWait}</div>
                      <div className="text-sm text-gray-600">Estimated Wait</div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <Brain className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-purple-600">{queueStatus.aiPredictedWait}</div>
                      <div className="text-sm text-gray-600">AI Prediction</div>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <Users className="h-6 w-6 text-green-600 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-green-600">{queueStatus.position}</div>
                      <div className="text-sm text-gray-600">Position in Queue</div>
                    </div>
                  </div>
                  
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                    <div className="flex items-start">
                      <Bell className="h-5 w-5 text-yellow-600 mr-2 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-yellow-800 mb-1">Important Information</h4>
                        <ul className="text-sm text-yellow-700 space-y-1">
                          <li>• Please arrive 10 minutes before your estimated time</li>
                          <li>• You will receive SMS notifications for updates</li>
                          <li>• Check the dashboard for real-time queue status</li>
                          <li>• Contact us if you need to reschedule</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-center space-x-4">
                    <Button
                      onClick={handleConfirm}
                      className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 px-8"
                    >
                      <Timer className="h-4 w-4 mr-2" />
                      View Queue Status
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setStep('symptoms')}
                    >
                      Join Another Queue
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {step === 'waiting' && queueStatus && (
            <motion.div
              key="waiting"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl text-center mb-2">
                    <Clock className="h-8 w-8 inline mr-2 text-blue-600" />
                    Queue Status
                  </CardTitle>
                  <p className="text-center text-gray-600">
                    Monitor your position and estimated wait time
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-6">
                    <div className="w-32 h-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-4xl font-bold text-white">
                        {queueStatus.queueNumber}
                      </span>
                    </div>
                    <h3 className="text-3xl font-bold text-gray-900 mb-2">
                      Queue #{queueStatus.queueNumber}
                    </h3>
                    <p className="text-lg text-gray-600">
                      {selectedService?.name}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-3xl font-bold text-blue-600 mb-1">{queueStatus.position}</div>
                      <div className="text-sm text-gray-600">Position</div>
                    </div>
                    
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-3xl font-bold text-orange-600 mb-1">{queueStatus.estimatedWait}</div>
                      <div className="text-sm text-gray-600">Est. Wait (min)</div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-3xl font-bold text-purple-600 mb-1">{queueStatus.aiPredictedWait}</div>
                      <div className="text-sm text-gray-600">AI Prediction</div>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <Badge className={`${getPriorityColor(patientDetails.priority)} text-sm px-3 py-1`}>
                        {patientDetails.priority.toUpperCase()}
                      </Badge>
                      <div className="text-sm text-gray-600 mt-1">Priority</div>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
                    <h4 className="font-semibold text-gray-900 mb-4 text-center">Real-time Updates</h4>
                    <div className="flex items-center justify-center space-x-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <Bell className="h-4 w-4 mr-1" />
                        <span>SMS notifications enabled</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                        <span>Auto-refreshing every 30s</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-center space-x-4">
                    <Button
                      onClick={() => setStep('symptoms')}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Join Another Queue
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => window.location.href = '/dashboard'}
                    >
                      <TrendingUp className="h-4 w-4 mr-2" />
                      View Dashboard
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error/Success Messages */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}

        {success && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default QueuePage;
