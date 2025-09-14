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
  RefreshCw
} from 'lucide-react';
import { queueService, PatientDetails } from '@/services/queueService';
import { servicesService } from '@/services/servicesService';
import { notificationService } from '@/services/notificationService';
import { demoService } from '@/services/demoService';

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

const QueuePage: React.FC = () => {
  const [step, setStep] = useState<'select' | 'details' | 'confirmation' | 'waiting'>('select');
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

  useEffect(() => {
    loadServices();
    // Set up real-time updates
    const interval = setInterval(loadServices, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadServices = async () => {
    try {
      const servicesData = await servicesService.getAllServices();
      setServices(servicesData);
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

  const handleDetailsSubmit = async () => {
    if (!selectedService) return;

    setLoading(true);
    setError(null);

    try {
      const result = await queueService.joinQueue({
        service_id: selectedService.id,
        patient_details: patientDetails
      });

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
      notificationService.showSuccess(
        'Queue Joined Successfully!',
        `You are now in queue for ${selectedService.name}. Queue #${result.queue_number}`
      );

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
    { id: 'select', title: 'Select Service', icon: Stethoscope },
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
                Join Hospital Queue
              </h1>
              <p className="text-lg text-gray-600">AI-Powered Patient Registration</p>
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
          {step === 'select' && (
            <motion.div
              key="select"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl text-center mb-2">
                    Choose Your Medical Service
                  </CardTitle>
                  <p className="text-center text-gray-600">
                    Select the department that best matches your needs. Our AI will optimize your queue position.
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {services.map((service) => {
                      const Icon = getServiceIcon(service.department);
                      return (
                        <motion.div
                          key={service.id}
                          whileHover={{ y: -5, scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleServiceSelect(service)}
                          className="cursor-pointer"
                        >
                          <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-gray-50 group">
                            <CardContent className="p-6">
                              <div className="flex items-start justify-between mb-4">
                                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
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
                              
                              <Button className="w-full mt-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                                Select Service
                                <ArrowRight className="h-4 w-4 ml-2" />
                              </Button>
                            </CardContent>
                          </Card>
                        </motion.div>
                      );
                    })}
                  </div>
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
                      onClick={() => setStep('select')}
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
                      onClick={() => setStep('select')}
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
                      onClick={() => setStep('select')}
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
