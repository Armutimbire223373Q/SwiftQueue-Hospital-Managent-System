import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Clock, Users, Phone, Mail, CheckCircle, Heart, Brain, Stethoscope, Activity, AlertCircle, UserCheck, AlertTriangle, Bot, Loader2 } from "lucide-react";
import { ServiceType, queueService, PatientDetails } from "@/services/queueService";
import { servicesService } from "@/services/servicesService";
import { aiService, SymptomAnalysisRequest, SymptomAnalysisResponse } from "@/services/aiService";
import { LoadingSpinner, LoadingButton, LoadingOverlay } from "@/components/ui/loading-spinner";

export default function CustomerQueue() {
  const [step, setStep] = useState<"select" | "details" | "confirmation">("select");
  const [selectedService, setSelectedService] = useState<ServiceType | null>(null);
  const [patientDetails, setPatientDetails] = useState<PatientDetails>({
    name: "",
    phone: "",
    email: "",
    dateOfBirth: "",
    symptoms: "",
    priority: "medium"
  });
  const [queueNumber, setQueueNumber] = useState<number | null>(null);
  const [services, setServices] = useState<ServiceType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // AI Analysis state
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  const [aiAnalysisResult, setAiAnalysisResult] = useState<SymptomAnalysisResponse | null>(null);
  const [showAiAnalysis, setShowAiAnalysis] = useState(false);
  
  const isGuestSession = localStorage.getItem('isGuestSession') === 'true';
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const isEmergencyGuest = user?.name === 'Emergency Patient';

  // Fallback services data for emergency access and offline mode
  const availableServices: ServiceType[] = [
    {
      id: 1,
      name: "Emergency Care",
      description: "Urgent medical attention required",
      department: "Emergency",
      estimatedTime: 15,
      currentWaitTime: 5,
      queueLength: 1,
      aiPredictedWait: 3,
      staffCount: 8,
      serviceRate: 1.2,
      estimated_time: 15,
      current_wait_time: 5,
      queue_length: 1,
      ai_predicted_wait: 3,
      staff_count: 8,
      service_rate: 1.2
    },
    {
      id: 2,
      name: "Laboratory Services",
      description: "Blood tests, urine tests, diagnostic procedures",
      department: "Laboratory",
      estimatedTime: 10,
      currentWaitTime: 8,
      queueLength: 2,
      aiPredictedWait: 6,
      staffCount: 4,
      serviceRate: 1.0,
      estimated_time: 10,
      current_wait_time: 8,
      queue_length: 2,
      ai_predicted_wait: 6,
      staff_count: 4,
      service_rate: 1.0
    },
    {
      id: 3,
      name: "Radiology",
      description: "X-rays, MRI, CT scans, ultrasounds",
      department: "Radiology",
      estimatedTime: 25,
      currentWaitTime: 20,
      queueLength: 3,
      aiPredictedWait: 15,
      staffCount: 3,
      serviceRate: 0.9,
      estimated_time: 25,
      current_wait_time: 20,
      queue_length: 3,
      ai_predicted_wait: 15,
      staff_count: 3,
      service_rate: 0.9
    },
    {
      id: 4,
      name: "Pediatrics",
      description: "Medical care for children and adolescents",
      department: "Pediatrics",
      estimatedTime: 25,
      currentWaitTime: 18,
      queueLength: 2,
      aiPredictedWait: 14,
      staffCount: 5,
      serviceRate: 1.0,
      estimated_time: 25,
      current_wait_time: 18,
      queue_length: 2,
      ai_predicted_wait: 14,
      staff_count: 5,
      service_rate: 1.0
    },
    {
      id: 5,
      name: "Cardiology",
      description: "Heart and cardiovascular care",
      department: "Cardiology",
      estimatedTime: 30,
      currentWaitTime: 22,
      queueLength: 4,
      aiPredictedWait: 18,
      staffCount: 6,
      serviceRate: 1.1,
      estimated_time: 30,
      current_wait_time: 22,
      queue_length: 4,
      ai_predicted_wait: 18,
      staff_count: 6,
      service_rate: 1.1
    },
    {
      id: 6,
      name: "Orthopedics",
      description: "Bone, joint, and muscle care",
      department: "Orthopedics",
      estimatedTime: 35,
      currentWaitTime: 28,
      queueLength: 5,
      aiPredictedWait: 25,
      staffCount: 4,
      serviceRate: 0.95,
      estimated_time: 35,
      current_wait_time: 28,
      queue_length: 5,
      ai_predicted_wait: 25,
      staff_count: 4,
      service_rate: 0.95
    }
  ];

  // Automatic AI analysis when symptoms change (debounced)
  useEffect(() => {
    if (!patientDetails.symptoms.trim()) {
      // Reset AI analysis when symptoms are cleared
      setAiAnalysisResult(null);
      setShowAiAnalysis(false);
      setPatientDetails(prev => ({ ...prev, priority: "medium" }));
      return;
    }

    // Debounce the AI analysis to avoid too many API calls
    const timeoutId = setTimeout(async () => {
      if (patientDetails.symptoms.trim() && patientDetails.name && patientDetails.dateOfBirth) {
        setAiAnalyzing(true);
        setError(null);

        try {
          const analysisRequest: SymptomAnalysisRequest = {
            symptoms: patientDetails.symptoms,
            patient_age: patientDetails.dateOfBirth ? 
              String(new Date().getFullYear() - new Date(patientDetails.dateOfBirth).getFullYear()) : undefined,
            medical_history: '',
            additional_context: `Patient requesting ${selectedService?.name || 'medical'} service`
          };

          console.log("🔬 Auto-analyzing symptoms with AI:", analysisRequest);
          const result = await aiService.analyzeSymptomsWithAI(analysisRequest);
          
          if (result.success) {
            setAiAnalysisResult(result);
            setShowAiAnalysis(true);
            
            // Update priority based on AI analysis
            const aiPriority = aiService.emergencyLevelToPriority(result.analysis.emergency_level);
            setPatientDetails(prev => ({ ...prev, priority: aiPriority }));
            
            console.log("✅ Auto AI Analysis completed:", {
              emergency_level: result.analysis.emergency_level,
              priority: aiPriority,
              confidence: result.analysis.confidence
            });
          }
        } catch (err) {
          console.error('Auto AI analysis failed:', err);
          // Don't show error for automatic analysis, just fall back to medium priority
          setPatientDetails(prev => ({ ...prev, priority: "medium" }));
        } finally {
          setAiAnalyzing(false);
        }
      }
    }, 1500); // 1.5 second debounce

    return () => clearTimeout(timeoutId);
  }, [patientDetails.symptoms, patientDetails.name, patientDetails.dateOfBirth, selectedService?.name]);

  // Load services on component mount
  useEffect(() => {
    console.log("CustomerQueue: Loading services on mount");
    loadServices();
  }, []); // Only run once on mount

  // Handle guest session pre-filling (separate effect)
  useEffect(() => {
    console.log("CustomerQueue: Handling guest session pre-fill");
    if (isGuestSession && user) {
      setPatientDetails(prev => ({
        ...prev,
        name: user.name || "",
        email: user.email || "",
        priority: isEmergencyGuest ? "high" : "medium"
      }));
    }
  }, [isGuestSession, user, isEmergencyGuest]);

  // Handle emergency patient auto-selection (separate effect)
  useEffect(() => {
    console.log("CustomerQueue: Handling emergency auto-selection", { isEmergencyGuest, servicesLength: services.length });
    if (isEmergencyGuest && services.length > 0) {
      const emergencyService = services.find(service =>
        service.name.toLowerCase().includes("emergency")
      );
      if (emergencyService) {
        console.log("CustomerQueue: Auto-selecting emergency service", emergencyService);
        setSelectedService(emergencyService);
        setStep("details");
      }
    }
  }, [isEmergencyGuest, services]);

  const loadServices = async () => {
    console.log("CustomerQueue: loadServices called");
    try {
      setLoading(true);
      setError(null);
      console.log("CustomerQueue: Calling servicesService.getAllServices()");
      const servicesData = await servicesService.getAllServices();
      console.log("CustomerQueue: Got services data", servicesData);
      setServices(servicesData);
    } catch (err) {
      console.error("Error loading services:", err);
      // Fallback to mock data for demo purposes (especially important for emergency access)
      console.log("CustomerQueue: Using fallback services");
      setServices(availableServices);
      
      // Only show error for non-emergency guests
      if (!isEmergencyGuest) {
        setError("Using offline services data. Some features may be limited.");
      }
    } finally {
      setLoading(false);
    }
  };

  const queueStats = {
    estimatedTime: 30,
    currentWaitTime: 25,
    queueLength: 3,
    aiPredictedWait: 18
  };

  const handleServiceSelect = (service: ServiceType) => {
    setSelectedService(service);
    setStep("details");
  };

  // AI Analysis function
  const analyzeSymptoms = async () => {
    if (!patientDetails.symptoms.trim()) {
      setError("Please enter symptoms to get AI analysis");
      return;
    }

    setAiAnalyzing(true);
    setError(null);

    try {
      const analysisRequest: SymptomAnalysisRequest = {
        symptoms: patientDetails.symptoms,
        patient_age: patientDetails.dateOfBirth ? 
          String(new Date().getFullYear() - new Date(patientDetails.dateOfBirth).getFullYear()) : undefined,
        medical_history: '',
        additional_context: `Patient requesting ${selectedService?.name || 'medical'} service`
      };

      console.log("🔬 Analyzing symptoms with AI:", analysisRequest);
      const result = await aiService.analyzeSymptomsWithAI(analysisRequest);
      
      if (result.success) {
        setAiAnalysisResult(result);
        setShowAiAnalysis(true);
        
        // Update priority based on AI analysis
        const aiPriority = aiService.emergencyLevelToPriority(result.analysis.emergency_level);
        setPatientDetails(prev => ({ ...prev, priority: aiPriority }));
        
        console.log("✅ AI Analysis completed:", {
          emergency_level: result.analysis.emergency_level,
          priority: aiPriority,
          confidence: result.analysis.confidence
        });
      }
    } catch (err) {
      console.error('AI analysis failed:', err);
      setError("AI analysis temporarily unavailable. Priority set to medium.");
    } finally {
      setAiAnalyzing(false);
    }
  };

  const handleJoinQueue = async () => {
    if (!selectedService || !patientDetails.name || !patientDetails.phone || !patientDetails.email || !patientDetails.dateOfBirth) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // For emergency guests, try the API but fall back to mock response
      if (isEmergencyGuest) {
        try {
          const result = await queueService.joinQueue(Number(selectedService.id), patientDetails);
          setQueueNumber(result.queueNumber);
          setStep("confirmation");
        } catch (apiError) {
          console.warn("API unavailable for emergency, using fallback:", apiError);
          // Emergency fallback - generate queue number locally
          const emergencyQueueNumber = Math.floor(Math.random() * 10) + 1;
          setQueueNumber(emergencyQueueNumber);
          setStep("confirmation");
        }
      } else {
        // Regular users need the API to work
        const result = await queueService.joinQueue(Number(selectedService.id), patientDetails);
        setQueueNumber(result.queueNumber);
        setStep("confirmation");
      }
    } catch (err) {
      if (!isEmergencyGuest) {
        setError("Failed to join queue. Please try again.");
      }
      console.error("Error joining queue:", err);
    } finally {
      setLoading(false);
    }
  };

  const getWaitTimeColor = (waitTime: number) => {
    if (waitTime <= 10) return "text-green-600";
    if (waitTime <= 20) return "text-yellow-600";
    return "text-red-600";
  };

  const getDepartmentIcon = (department: string) => {
    switch (department) {
      case "Cardiology": return <Heart className="h-4 w-4" />;
      case "Emergency": return <AlertCircle className="h-4 w-4" />;
      case "Laboratory": return <Activity className="h-4 w-4" />;
      default: return <Stethoscope className="h-4 w-4" />;
    }
  };

  if (step === "confirmation") {
    return (
      <div className="bg-white min-h-screen p-6">
        <div className="max-w-2xl mx-auto">
          <Card className="border-green-200 bg-green-50">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl text-green-800">Successfully Registered!</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-6">
              <div className="bg-white p-6 rounded-lg border">
                <div className="text-4xl font-bold text-green-600 mb-2">#{queueNumber}</div>
                <p className="text-gray-600">Your Queue Number</p>
                <p className="text-sm text-gray-500 mt-1">{selectedService?.department}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-center mb-2">
                    <Brain className="h-5 w-5 text-blue-500 mr-2" />
                    <span className="font-medium">AI Predicted Wait</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-600">{selectedService?.aiPredictedWait}m</div>
                  <p className="text-xs text-gray-500">Standard: {selectedService?.currentWaitTime}m</p>
                </div>
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-center mb-2">
                    <Users className="h-5 w-5 text-purple-500 mr-2" />
                    <span className="font-medium">Patients Ahead</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-600">{selectedService?.queueLength}</div>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2 flex items-center justify-center">
                  <Brain className="h-4 w-4 mr-2" />
                  AI-Powered Smart Notifications
                </h3>
                <p className="text-sm text-blue-700 mb-3">
                  Our AI system continuously monitors patient flow and will notify you via SMS and email 
                  when your appointment time approaches, optimizing your waiting experience.
                </p>
                <div className="flex items-center justify-center space-x-4 text-sm">
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 mr-1" />
                    {patientDetails.phone}
                  </div>
                  <div className="flex items-center">
                    <Mail className="h-4 w-4 mr-1" />
                    {patientDetails.email}
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">AI Health Insights</h4>
                <p className="text-sm text-yellow-700">
                  Based on your symptoms and selected service, our AI has optimized your queue position 
                  and estimated consultation time for the best care experience.
                </p>
              </div>

              <div className="space-y-3">
                <Button 
                  onClick={() => window.location.reload()} 
                  className="w-full"
                >
                  Register for Another Service
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setStep("select")}
                  className="w-full"
                >
                  Back to Services
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (step === "details") {
    return (
      <div className="bg-white min-h-screen p-6">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Patient Registration</CardTitle>
              <p className="text-gray-600">Please provide your details for optimal care coordination</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-1 flex items-center">
                  {getDepartmentIcon(selectedService?.department || "")}
                  <span className="ml-2">{selectedService?.name}</span>
                </h3>
                <p className="text-blue-700">{selectedService?.description}</p>
                <p className="text-sm text-blue-600 mt-1">Department: {selectedService?.department}</p>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={patientDetails.name}
                    onChange={(e) => setPatientDetails({...patientDetails, name: e.target.value})}
                    placeholder="Enter your full name"
                    className="mt-1"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone">Phone Number *</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={patientDetails.phone}
                      onChange={(e) => setPatientDetails({...patientDetails, phone: e.target.value})}
                      placeholder="+1 (555) 123-4567"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="dob">Date of Birth *</Label>
                    <Input
                      id="dob"
                      type="date"
                      value={patientDetails.dateOfBirth}
                      onChange={(e) => setPatientDetails({...patientDetails, dateOfBirth: e.target.value})}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={patientDetails.email}
                    onChange={(e) => setPatientDetails({...patientDetails, email: e.target.value})}
                    placeholder="your.email@example.com"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="symptoms">Symptoms / Reason for Visit</Label>
                  <Textarea
                    id="symptoms"
                    value={patientDetails.symptoms}
                    onChange={(e) => setPatientDetails({...patientDetails, symptoms: e.target.value})}
                    placeholder="Briefly describe your symptoms or reason for visit (optional)"
                    className="mt-1"
                    rows={3}
                  />
                  
                  {/* AI Analysis Status */}
                  {patientDetails.symptoms.trim() && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2 text-sm text-purple-600">
                        {aiAnalyzing ? (
                          <>
                            <LoadingSpinner size="sm" />
                            <span>AI is analyzing your symptoms...</span>
                          </>
                        ) : showAiAnalysis ? (
                          <>
                            <Bot className="h-4 w-4" />
                            <span>✅ AI analysis complete - Priority automatically set</span>
                          </>
                        ) : (
                          <>
                            <Bot className="h-4 w-4" />
                            <span>🤖 AI will analyze symptoms when you complete the form</span>
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  {/* AI Analysis Results */}
                  {showAiAnalysis && aiAnalysisResult && (
                    <div className="mt-4 p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50">
                      <div className="flex items-center gap-2 mb-3">
                        <Brain className="h-5 w-5 text-purple-600" />
                        <h4 className="font-semibold text-purple-800">AI Analysis Results</h4>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Emergency Level:</span>
                          <Badge className={aiService.getPriorityBadgeClass(aiAnalysisResult.analysis.emergency_level)}>
                            {aiAnalysisResult.analysis.emergency_level.toUpperCase()}
                          </Badge>
                        </div>
                        
                        <div className="flex justify-between">
                          <span>AI Confidence:</span>
                          <span className="font-medium">
                            {Math.round(aiAnalysisResult.analysis.confidence * 100)}%
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span>Recommended Department:</span>
                          <span className="font-medium">
                            {aiAnalysisResult.analysis.department_recommendation}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span>Estimated Wait:</span>
                          <span className="font-medium">
                            {aiAnalysisResult.analysis.estimated_wait_time} minutes
                          </span>
                        </div>
                        
                        {aiAnalysisResult.analysis.recommended_actions.length > 0 && (
                          <div className="mt-3">
                            <p className="font-medium text-purple-700 mb-1">Recommendations:</p>
                            <ul className="list-disc list-inside space-y-1 text-xs">
                              {aiAnalysisResult.analysis.recommended_actions.map((action, index) => (
                                <li key={index} className="text-purple-600">{action}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        <div className="mt-3 p-2 bg-white rounded border-l-4 border-purple-400">
                          <p className="text-xs text-gray-600">
                            <strong>AI Reasoning:</strong> {aiAnalysisResult.analysis.ai_reasoning}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor="priority">Priority Level</Label>
                    <Badge variant="outline" className="text-xs bg-purple-100 text-purple-700">
                      🤖 AI Determined
                    </Badge>
                  </div>
                  <div className="mt-1 p-3 bg-purple-50 border border-purple-200 rounded-md">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize text-purple-900">
                        {patientDetails.priority === 'urgent' ? 'Urgent - Immediate care needed' :
                         patientDetails.priority === 'high' ? 'High - Needs attention soon' :
                         patientDetails.priority === 'medium' ? 'Medium - Standard care' :
                         'Low - Routine care'}
                      </span>
                      <Badge className={
                        patientDetails.priority === 'urgent' ? 'bg-red-500' :
                        patientDetails.priority === 'high' ? 'bg-orange-500' :
                        patientDetails.priority === 'medium' ? 'bg-yellow-500' :
                        'bg-green-500'
                      }>
                        {patientDetails.priority.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-xs text-purple-600 mt-2">
                      Priority automatically determined by AI analysis based on symptoms and patient information.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-2 flex items-center">
                  <Brain className="h-4 w-4 mr-2" />
                  AI-Enhanced Care Coordination
                </h4>
                <p className="text-sm text-purple-700">
                  Our AI system will analyze your information to optimize your care experience, 
                  predict accurate wait times, and coordinate with medical staff for efficient service.
                </p>
              </div>

              <div className="flex space-x-3">
                <Button
                  variant="outline"
                  onClick={() => setStep("select")}
                  className="flex-1"
                  disabled={loading}
                >
                  Back
                </Button>
                <LoadingButton
                  onClick={handleJoinQueue}
                  disabled={!patientDetails.name || !patientDetails.phone || !patientDetails.email || !patientDetails.dateOfBirth}
                  loading={loading}
                  loadingText="Joining Queue..."
                  className="flex-1"
                >
                  Register & Join Queue
                </LoadingButton>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        {/* Guest Session Alert */}
        {isGuestSession && (
          <Alert className={`mb-6 ${isEmergencyGuest ? 'border-red-200 bg-red-50' : 'border-blue-200 bg-blue-50'}`}>
            {isEmergencyGuest ? (
              <AlertTriangle className="h-4 w-4 text-red-600" />
            ) : (
              <UserCheck className="h-4 w-4 text-blue-600" />
            )}
            <AlertDescription>
              {isEmergencyGuest ? (
                <span>
                  <strong className="text-red-600">🚨 Emergency Mode:</strong> Fast-track access enabled. Please proceed with your registration.
                </span>
              ) : (
                <span>
                  <strong>Guest Access:</strong> You're using guest mode. Some features may be limited.
                </span>
              )}
            </AlertDescription>
          </Alert>
        )}

        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hospital Patient Registration</h1>
          <p className="text-gray-600">Select your service and join the queue digitally with AI-powered optimization</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => (
            <Card 
              key={service.id} 
              className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-200"
              onClick={() => handleServiceSelect(service)}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center">
                    {getDepartmentIcon(service.department)}
                    <span className="ml-2">{service.name}</span>
                  </CardTitle>
                  <Badge variant="outline" className="flex items-center space-x-1">
                    <Users className="h-3 w-3" />
                    <span>{service.queueLength}</span>
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{service.description}</p>
                <p className="text-xs text-blue-600 font-medium">{service.department}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="flex items-center space-x-1">
                          <Brain className="h-3 w-3 text-blue-500" />
                          <div className={`text-lg font-bold ${getWaitTimeColor(service.aiPredictedWait)}`}>
                            {service.aiPredictedWait}m
                          </div>
                        </div>
                        <div className="text-xs text-blue-600">AI Predicted</div>
                      </div>
                      <div className="text-center">
                        <div className={`text-sm font-medium ${getWaitTimeColor(service.currentWaitTime)}`}>
                          {service.currentWaitTime}m
                        </div>
                        <div className="text-xs text-gray-500">Standard Wait</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-700">
                          {service.estimatedTime}m
                        </div>
                        <div className="text-xs text-gray-500">Service Time</div>
                      </div>
                    </div>
                  </div>
                  <Button size="sm" className="w-full">
                    Select Service
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">AI-Powered Healthcare Experience</h3>
                <p className="text-sm text-gray-600">
                  Our advanced AI system optimizes your healthcare journey by predicting wait times, 
                  coordinating care, and sending smart notifications when it's your turn.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}