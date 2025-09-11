import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Clock, Users, Phone, Mail, CheckCircle, Heart, Brain, Stethoscope, Activity, AlertCircle } from "lucide-react";

interface ServiceType {
  id: string;
  name: string;
  description: string;
  estimatedTime: number;
  currentWaitTime: number;
  queueLength: number;
  department: string;
  aiPredictedWait: number;
}

export default function CustomerQueue() {
  const [step, setStep] = useState<"select" | "details" | "confirmation">("select");
  const [selectedService, setSelectedService] = useState<ServiceType | null>(null);
  const [patientDetails, setPatientDetails] = useState({
    name: "",
    phone: "",
    email: "",
    dateOfBirth: "",
    symptoms: "",
    priority: "medium"
  });
  const [queueNumber, setQueueNumber] = useState<number | null>(null);

  const serviceTypes: ServiceType[] = [
    {
      id: "general",
      name: "General Consultation",
      description: "Routine check-ups, general health concerns",
      department: "Internal Medicine",
      estimatedTime: 20,
      currentWaitTime: 15,
      queueLength: 4,
      aiPredictedWait: 12
    },
    {
      id: "cardiology",
      name: "Cardiology",
      description: "Heart-related conditions and consultations",
      department: "Cardiology",
      estimatedTime: 30,
      currentWaitTime: 25,
      queueLength: 3,
      aiPredictedWait: 18
    },
    {
      id: "laboratory",
      name: "Laboratory Services",
      description: "Blood tests, urine tests, diagnostic procedures",
      department: "Laboratory",
      estimatedTime: 10,
      currentWaitTime: 8,
      queueLength: 2,
      aiPredictedWait: 6
    },
    {
      id: "emergency",
      name: "Emergency Care",
      description: "Urgent medical attention required",
      department: "Emergency",
      estimatedTime: 15,
      currentWaitTime: 5,
      queueLength: 1,
      aiPredictedWait: 3
    },
    {
      id: "radiology",
      name: "Radiology",
      description: "X-rays, MRI, CT scans, ultrasounds",
      department: "Radiology",
      estimatedTime: 25,
      currentWaitTime: 20,
      queueLength: 3,
      aiPredictedWait: 15
    },
    {
      id: "pediatrics",
      name: "Pediatrics",
      description: "Medical care for children and adolescents",
      department: "Pediatrics",
      estimatedTime: 25,
      currentWaitTime: 18,
      queueLength: 2,
      aiPredictedWait: 14
    }
  ];

  const handleServiceSelect = (service: ServiceType) => {
    setSelectedService(service);
    setStep("details");
  };

  const handleJoinQueue = () => {
    // Simulate AI-powered queue number assignment
    const newQueueNumber = Math.floor(Math.random() * 100) + 1;
    setQueueNumber(newQueueNumber);
    setStep("confirmation");
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
                </div>

                <div>
                  <Label htmlFor="priority">Priority Level</Label>
                  <Select value={patientDetails.priority} onValueChange={(value) => setPatientDetails({...patientDetails, priority: value})}>
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
                >
                  Back
                </Button>
                <Button 
                  onClick={handleJoinQueue}
                  disabled={!patientDetails.name || !patientDetails.phone || !patientDetails.email || !patientDetails.dateOfBirth}
                  className="flex-1"
                >
                  Register & Join Queue
                </Button>
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
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hospital Patient Registration</h1>
          <p className="text-gray-600">Select your service and join the queue digitally with AI-powered optimization</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {serviceTypes.map((service) => (
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