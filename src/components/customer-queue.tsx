import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Clock, Users, Phone, Mail, CheckCircle } from "lucide-react";

interface ServiceType {
  id: string;
  name: string;
  description: string;
  estimatedTime: number;
  currentWaitTime: number;
  queueLength: number;
}

export default function CustomerQueue() {
  const [step, setStep] = useState<"select" | "details" | "confirmation">("select");
  const [selectedService, setSelectedService] = useState<ServiceType | null>(null);
  const [customerDetails, setCustomerDetails] = useState({
    name: "",
    phone: "",
    email: ""
  });
  const [queueNumber, setQueueNumber] = useState<number | null>(null);

  const serviceTypes: ServiceType[] = [
    {
      id: "banking",
      name: "General Banking",
      description: "Account inquiries, deposits, withdrawals",
      estimatedTime: 8,
      currentWaitTime: 12,
      queueLength: 3
    },
    {
      id: "loans",
      name: "Loans & Mortgages",
      description: "Loan applications, mortgage consultations",
      estimatedTime: 25,
      currentWaitTime: 18,
      queueLength: 2
    },
    {
      id: "customer-service",
      name: "Customer Service",
      description: "Complaints, account issues, general support",
      estimatedTime: 15,
      currentWaitTime: 25,
      queueLength: 4
    },
    {
      id: "business",
      name: "Business Banking",
      description: "Business accounts, commercial services",
      estimatedTime: 20,
      currentWaitTime: 8,
      queueLength: 1
    }
  ];

  const handleServiceSelect = (service: ServiceType) => {
    setSelectedService(service);
    setStep("details");
  };

  const handleJoinQueue = () => {
    // Simulate queue number assignment
    const newQueueNumber = Math.floor(Math.random() * 100) + 1;
    setQueueNumber(newQueueNumber);
    setStep("confirmation");
  };

  const getWaitTimeColor = (waitTime: number) => {
    if (waitTime <= 10) return "text-green-600";
    if (waitTime <= 20) return "text-yellow-600";
    return "text-red-600";
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
              <CardTitle className="text-2xl text-green-800">Successfully Joined Queue!</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-6">
              <div className="bg-white p-6 rounded-lg border">
                <div className="text-4xl font-bold text-green-600 mb-2">#{queueNumber}</div>
                <p className="text-gray-600">Your Queue Number</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-center mb-2">
                    <Clock className="h-5 w-5 text-blue-500 mr-2" />
                    <span className="font-medium">Estimated Wait</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-600">{selectedService?.currentWaitTime}m</div>
                </div>
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-center mb-2">
                    <Users className="h-5 w-5 text-purple-500 mr-2" />
                    <span className="font-medium">People Ahead</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-600">{selectedService?.queueLength}</div>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">Smart Notifications Enabled</h3>
                <p className="text-sm text-blue-700 mb-3">
                  We'll notify you via SMS and email when your turn approaches based on AI predictions.
                </p>
                <div className="flex items-center justify-center space-x-4 text-sm">
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 mr-1" />
                    {customerDetails.phone}
                  </div>
                  <div className="flex items-center">
                    <Mail className="h-4 w-4 mr-1" />
                    {customerDetails.email}
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <Button 
                  onClick={() => window.location.reload()} 
                  className="w-full"
                >
                  Join Another Queue
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
              <CardTitle>Enter Your Details</CardTitle>
              <p className="text-gray-600">We'll use this information to notify you when your turn approaches</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-1">Selected Service</h3>
                <p className="text-blue-700">{selectedService?.name}</p>
                <p className="text-sm text-blue-600">{selectedService?.description}</p>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={customerDetails.name}
                    onChange={(e) => setCustomerDetails({...customerDetails, name: e.target.value})}
                    placeholder="Enter your full name"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="phone">Phone Number *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={customerDetails.phone}
                    onChange={(e) => setCustomerDetails({...customerDetails, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={customerDetails.email}
                    onChange={(e) => setCustomerDetails({...customerDetails, email: e.target.value})}
                    placeholder="your.email@example.com"
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">Smart Notification System</h4>
                <p className="text-sm text-yellow-700">
                  Our AI will predict when your turn is approaching and send you notifications 5-10 minutes before, 
                  so you don't have to wait in the physical queue.
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
                  disabled={!customerDetails.name || !customerDetails.phone || !customerDetails.email}
                  className="flex-1"
                >
                  Join Queue
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
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">SwiftQueue</h1>
          <p className="text-gray-600">Join a queue digitally and get notified when it's your turn</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {serviceTypes.map((service) => (
            <Card 
              key={service.id} 
              className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-200"
              onClick={() => handleServiceSelect(service)}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{service.name}</CardTitle>
                  <Badge variant="outline" className="flex items-center space-x-1">
                    <Users className="h-3 w-3" />
                    <span>{service.queueLength}</span>
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{service.description}</p>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <div className={`text-lg font-bold ${getWaitTimeColor(service.currentWaitTime)}`}>
                        {service.currentWaitTime}m
                      </div>
                      <div className="text-xs text-gray-500">Current Wait</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-700">
                        {service.estimatedTime}m
                      </div>
                      <div className="text-xs text-gray-500">Service Time</div>
                    </div>
                  </div>
                  <Button size="sm">
                    Join Queue
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
                <Clock className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">How it works</h3>
                <p className="text-sm text-gray-600">
                  Select a service, enter your details, and we'll notify you when it's almost your turn. 
                  No need to wait in physical lines!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}