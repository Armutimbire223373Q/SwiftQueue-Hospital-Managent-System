import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Clock, Users, Brain, AlertCircle, Heart, Stethoscope, Activity } from "lucide-react";
import { queueService, PatientDetails } from "@/services/queueService";
import { servicesService } from "@/services/servicesService";

interface ServiceType {
  id: number;
  name: string;
  description: string;
  department: string;
  estimated_time: number;
  current_wait_time: number;
  queue_length: number;
}

interface QueueJoinFormProps {
  onSuccess?: (queueNumber: number) => void;
  onCancel?: () => void;
}

export default function QueueJoinForm({ onSuccess, onCancel }: QueueJoinFormProps) {
  const [selectedService, setSelectedService] = useState<ServiceType | null>(null);
  const [patientDetails, setPatientDetails] = useState<PatientDetails>({
    name: "",
    phone: "",
    email: "",
    dateOfBirth: "",
    symptoms: "",
    priority: "medium"
  });
  const [services, setServices] = useState<ServiceType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      setLoading(true);
      const servicesData = await servicesService.getAllServices();
      setServices(servicesData);
    } catch (err) {
      setError("Failed to load services. Please try again later.");
      console.error("Error loading services:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinQueue = async () => {
    if (!selectedService || !patientDetails.name || !patientDetails.phone || !patientDetails.email || !patientDetails.dateOfBirth) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      setLoading(true);
      const result = await queueService.joinQueue(selectedService.id, patientDetails);
      onSuccess?.(result.queue_number);
    } catch (err) {
      setError("Failed to join queue. Please try again.");
      console.error("Error joining queue:", err);
    } finally {
      setLoading(false);
    }
  };

  const getDepartmentIcon = (department: string) => {
    switch (department) {
      case "Cardiology": return <Heart className="h-4 w-4" />;
      case "Emergency": return <AlertCircle className="h-4 w-4" />;
      case "Laboratory": return <Activity className="h-4 w-4" />;
      default: return <Stethoscope className="h-4 w-4" />;
    }
  };

  if (loading && services.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Join Hospital Queue</CardTitle>
          <p className="text-gray-600">Select a service and provide your details</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Service Selection */}
          <div>
            <Label htmlFor="service">Select Service *</Label>
            <Select onValueChange={(value) => {
              const service = services.find(s => s.id.toString() === value);
              setSelectedService(service || null);
            }}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Choose a medical service" />
              </SelectTrigger>
              <SelectContent>
                {services.map((service) => (
                  <SelectItem key={service.id} value={service.id.toString()}>
                    <div className="flex items-center space-x-2">
                      {getDepartmentIcon(service.department)}
                      <span>{service.name}</span>
                      <Badge variant="outline" className="ml-2">
                        {service.queue_length} in queue
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {selectedService && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-1 flex items-center">
                {getDepartmentIcon(selectedService.department)}
                <span className="ml-2">{selectedService.name}</span>
              </h3>
              <p className="text-blue-700">{selectedService.description}</p>
              <div className="flex items-center space-x-4 mt-2 text-sm">
                <div className="flex items-center space-x-1">
                  <Brain className="h-3 w-3 text-blue-500" />
                  <span className="text-blue-600">AI Predicted: {selectedService.current_wait_time}m</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="h-3 w-3 text-purple-500" />
                  <span className="text-purple-600">{selectedService.queue_length} ahead</span>
                </div>
              </div>
            </div>
          )}

          {/* Patient Details */}
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
              <Select value={patientDetails.priority} onValueChange={(value) => setPatientDetails({...patientDetails, priority: value as any})}>
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

          {error && (
            <div className="bg-red-50 p-3 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="flex space-x-3">
            {onCancel && (
              <Button variant="outline" onClick={onCancel} className="flex-1">
                Cancel
              </Button>
            )}
            <Button 
              onClick={handleJoinQueue}
              disabled={!selectedService || !patientDetails.name || !patientDetails.phone || !patientDetails.email || !patientDetails.dateOfBirth || loading}
              className="flex-1"
            >
              {loading ? "Joining Queue..." : "Join Queue"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}