import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, Clock, Ticket } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface QueueJoinFormProps {
  onSubmit?: (formData: QueueFormData) => void;
}

export interface QueueFormData {
  name: string;
  phone: string;
  email: string;
  serviceType: string;
}

const QueueJoinForm = ({ onSubmit = () => {} }: QueueJoinFormProps) => {
  const [formData, setFormData] = useState<QueueFormData>({
    name: "",
    phone: "",
    email: "",
    serviceType: "",
  });

  const [submitted, setSubmitted] = useState(false);
  const [queueNumber, setQueueNumber] = useState<string>("");
  const [estimatedWaitTime, setEstimatedWaitTime] = useState<number>(0);

  const handleChange = (field: keyof QueueFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // In a real app, this would call an API to join the queue
    // and get back a queue number and estimated wait time
    const mockQueueNumber = `A${Math.floor(Math.random() * 100)}`;
    const mockWaitTime = Math.floor(Math.random() * 30) + 10; // 10-40 minutes

    setQueueNumber(mockQueueNumber);
    setEstimatedWaitTime(mockWaitTime);
    setSubmitted(true);
    onSubmit(formData);
  };

  const serviceTypes = [
    { value: "general", label: "General Inquiry" },
    { value: "account", label: "Account Services" },
    { value: "technical", label: "Technical Support" },
    { value: "payments", label: "Payments & Billing" },
  ];

  return (
    <Card className="w-full max-w-md mx-auto bg-white shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center">
          Join the Queue
        </CardTitle>
        <CardDescription className="text-center">
          Fill out the form below to get your place in line
        </CardDescription>
      </CardHeader>

      <CardContent>
        {!submitted ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="serviceType">Service Type</Label>
              <Select
                value={formData.serviceType}
                onValueChange={(value) => handleChange("serviceType", value)}
                required
              >
                <SelectTrigger id="serviceType">
                  <SelectValue placeholder="Select a service" />
                </SelectTrigger>
                <SelectContent>
                  {serviceTypes.map((service) => (
                    <SelectItem key={service.value} value={service.value}>
                      {service.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange("phone", e.target.value)}
                placeholder="+1 (555) 123-4567"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange("email", e.target.value)}
                placeholder="john.doe@example.com"
                required
              />
            </div>

            <Alert className="bg-blue-50 border-blue-200">
              <AlertCircle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-700 text-sm">
                You'll receive notifications when your turn is approaching.
              </AlertDescription>
            </Alert>

            <Button type="submit" className="w-full">
              Join Queue
            </Button>
          </form>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-col items-center justify-center space-y-4 py-6">
              <div className="h-24 w-24 rounded-full bg-green-100 flex items-center justify-center">
                <Ticket className="h-12 w-12 text-green-600" />
              </div>
              <div className="text-center">
                <h3 className="text-xl font-bold">Queue Number</h3>
                <p className="text-3xl font-bold text-green-600">
                  {queueNumber}
                </p>
              </div>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="h-5 w-5 mr-2 text-amber-500" />
                <span className="text-sm font-medium">
                  Estimated Wait Time:
                </span>
              </div>
              <span className="font-bold">{estimatedWaitTime} minutes</span>
            </div>

            <Alert className="bg-green-50 border-green-200">
              <AlertCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700 text-sm">
                We'll notify you when your turn is approaching. You can leave
                and come back when it's almost your turn.
              </AlertDescription>
            </Alert>

            <Button
              variant="outline"
              className="w-full"
              onClick={() => {
                setSubmitted(false);
                setFormData({
                  name: "",
                  phone: "",
                  email: "",
                  serviceType: "",
                });
              }}
            >
              Join Another Queue
            </Button>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex justify-center border-t pt-4">
        <p className="text-xs text-gray-500">
          Powered by SwiftQueue AI - Smart Queue Management
        </p>
      </CardFooter>
    </Card>
  );
};

export default QueueJoinForm;
