import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  Ambulance,
  Clock,
  MapPin,
  User,
  AlertTriangle,
  CheckCircle,
  Truck,
  Phone,
  RefreshCw,
  Plus
} from "lucide-react";
import { emergencyService } from "@/services/emergencyService";
import { EmergencyDispatch, DispatchRequest } from "@/services/apiService";
import { authService } from "@/services/authService";

interface Patient {
  id: number;
  name: string;
  email: string;
}

export default function EmergencyDashboard() {
  const [dispatches, setDispatches] = useState<EmergencyDispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dispatching, setDispatching] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Manual dispatch form state
  const [showDispatchDialog, setShowDispatchDialog] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>("");
  const [emergencyDetails, setEmergencyDetails] = useState("");

  // Stats
  const [activeDispatches, setActiveDispatches] = useState(0);
  const [completedToday, setCompletedToday] = useState(0);
  const [averageResponseTime, setAverageResponseTime] = useState(0);

  useEffect(() => {
    loadInitialData();
    // Set up polling for real-time updates every 30 seconds
    const interval = setInterval(loadDispatches, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      await Promise.all([
        loadDispatches(),
        loadPatients()
      ]);
      updateStats();
    } catch (err) {
      setError("Failed to load emergency data");
      console.error("Error loading emergency data:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadDispatches = async () => {
    try {
      // For now, we'll get dispatches for all patients since we don't have an "active dispatches" endpoint
      // In a real implementation, we'd have a dedicated endpoint for staff to see all active dispatches
      const allDispatches: EmergencyDispatch[] = [];

      // Get some sample dispatches - in real implementation, this would be from a staff endpoint
      // For demo purposes, we'll create some mock data if no real data exists
      if (allDispatches.length === 0) {
        // Mock data for demonstration
        const mockDispatches: EmergencyDispatch[] = [
          {
            id: 1,
            patient_id: 1,
            emergency_details: "Chest pain and difficulty breathing",
            dispatch_address: "123 Main St, City, State 12345, Country",
            dispatch_status: "en_route",
            dispatched_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
            response_time: 12,
            ambulance_id: "AMB-123",
            notes: "Patient reports severe chest pain",
            created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            patient_name: "John Doe"
          },
          {
            id: 2,
            patient_id: 2,
            emergency_details: "Severe allergic reaction",
            dispatch_address: "456 Oak Ave, City, State 67890, Country",
            dispatch_status: "arrived",
            dispatched_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
            response_time: 8,
            ambulance_id: "AMB-456",
            notes: "Patient has epinephrine auto-injector",
            created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
            patient_name: "Jane Smith"
          }
        ];
        setDispatches(mockDispatches);
      } else {
        setDispatches(allDispatches);
      }
    } catch (err) {
      console.error("Error loading dispatches:", err);
      // Don't set error here as it's called periodically
    }
  };

  const loadPatients = async () => {
    try {
      // In a real implementation, we'd have an endpoint to get all patients for staff
      // For now, we'll use mock data
      const mockPatients: Patient[] = [
        { id: 1, name: "John Doe", email: "john@example.com" },
        { id: 2, name: "Jane Smith", email: "jane@example.com" },
        { id: 3, name: "Bob Johnson", email: "bob@example.com" }
      ];
      setPatients(mockPatients);
    } catch (err) {
      console.error("Error loading patients:", err);
    }
  };

  const updateStats = () => {
    const active = dispatches.filter(d => ['pending', 'dispatched', 'en_route'].includes(d.dispatch_status)).length;
    const completed = dispatches.filter(d => d.dispatch_status === 'completed').length;
    const avgResponse = dispatches
      .filter(d => d.response_time)
      .reduce((sum, d) => sum + (d.response_time || 0), 0) / dispatches.filter(d => d.response_time).length || 0;

    setActiveDispatches(active);
    setCompletedToday(completed);
    setAverageResponseTime(Math.round(avgResponse));
  };

  const handleManualDispatch = async () => {
    if (!selectedPatientId || !emergencyDetails.trim()) {
      setError("Please select a patient and provide emergency details");
      return;
    }

    try {
      setDispatching(true);
      setError(null);

      const request: DispatchRequest = {
        patient_id: parseInt(selectedPatientId),
        emergency_details: emergencyDetails.trim()
      };

      const newDispatch = await emergencyService.dispatchAmbulance(request);

      // Add the new dispatch to the list
      setDispatches(prev => [newDispatch, ...prev]);
      updateStats();

      // Reset form
      setSelectedPatientId("");
      setEmergencyDetails("");
      setShowDispatchDialog(false);

    } catch (err) {
      setError("Failed to dispatch ambulance. Please try again.");
      console.error("Error dispatching ambulance:", err);
    } finally {
      setDispatching(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDispatches();
    updateStats();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "bg-yellow-500";
      case "dispatched": return "bg-blue-500";
      case "en_route": return "bg-orange-500";
      case "arrived": return "bg-green-500";
      case "completed": return "bg-gray-500";
      case "cancelled": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending": return <Clock className="h-4 w-4" />;
      case "dispatched": return <Truck className="h-4 w-4" />;
      case "en_route": return <Ambulance className="h-4 w-4" />;
      case "arrived": return <MapPin className="h-4 w-4" />;
      case "completed": return <CheckCircle className="h-4 w-4" />;
      case "cancelled": return <AlertTriangle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const formatTime = (dateString?: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleTimeString();
  };

  const getElapsedTime = (dispatchedAt?: string) => {
    if (!dispatchedAt) return "N/A";
    const elapsed = Math.floor((Date.now() - new Date(dispatchedAt).getTime()) / (1000 * 60));
    return `${elapsed}m ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Emergency Response Dashboard</h1>
            <p className="text-gray-600">Real-time ambulance dispatch monitoring</p>
          </div>
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" text="Loading emergency data..." />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Emergency Response Dashboard</h1>
            <p className="text-gray-600">Real-time ambulance dispatch monitoring and management</p>
          </div>
          <div className="flex space-x-2">
            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Dialog open={showDispatchDialog} onOpenChange={setShowDispatchDialog}>
              <DialogTrigger asChild>
                <Button className="bg-red-600 hover:bg-red-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Dispatch Ambulance
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Manual Ambulance Dispatch</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="patient">Select Patient</Label>
                    <Select value={selectedPatientId} onValueChange={setSelectedPatientId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a patient" />
                      </SelectTrigger>
                      <SelectContent>
                        {patients.map((patient) => (
                          <SelectItem key={patient.id} value={patient.id.toString()}>
                            {patient.name} ({patient.email})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="emergency-details">Emergency Details</Label>
                    <Textarea
                      id="emergency-details"
                      placeholder="Describe the emergency situation..."
                      value={emergencyDetails}
                      onChange={(e) => setEmergencyDetails(e.target.value)}
                      rows={3}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setShowDispatchDialog(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleManualDispatch}
                      disabled={dispatching}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      {dispatching ? (
                        <>
                          <LoadingSpinner size="sm" className="mr-2" />
                          Dispatching...
                        </>
                      ) : (
                        <>
                          <Ambulance className="h-4 w-4 mr-2" />
                          Dispatch Ambulance
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Dispatches</CardTitle>
              <Ambulance className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{activeDispatches}</div>
              <p className="text-xs text-muted-foreground">ambulances in transit</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{completedToday}</div>
              <p className="text-xs text-muted-foreground">successful responses</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Clock className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{averageResponseTime}m</div>
              <p className="text-xs text-muted-foreground">average dispatch time</p>
            </CardContent>
          </Card>
        </div>

        {/* Active Dispatches */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Ambulance className="h-5 w-5 text-red-500" />
              <span>Active Ambulance Dispatches</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dispatches.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Ambulance className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No active dispatches at this time</p>
                </div>
              ) : (
                dispatches.map((dispatch) => (
                  <div key={dispatch.id} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-full ${getStatusColor(dispatch.dispatch_status)} flex items-center justify-center text-white`}>
                          {getStatusIcon(dispatch.dispatch_status)}
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">
                            Dispatch #{dispatch.id}
                          </h3>
                          <p className="text-sm text-gray-600">
                            Ambulance: {dispatch.ambulance_id || "Unassigned"}
                          </p>
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className={`flex items-center space-x-1 ${
                          dispatch.dispatch_status === 'arrived' ? 'border-green-500 text-green-700' :
                          dispatch.dispatch_status === 'en_route' ? 'border-orange-500 text-orange-700' :
                          dispatch.dispatch_status === 'dispatched' ? 'border-blue-500 text-blue-700' :
                          'border-gray-500 text-gray-700'
                        }`}
                      >
                        {getStatusIcon(dispatch.dispatch_status)}
                        <span className="capitalize">{dispatch.dispatch_status.replace('_', ' ')}</span>
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <User className="h-4 w-4 text-gray-500" />
                          <span className="text-sm font-medium">Patient: {dispatch.patient_name || `Patient #${dispatch.patient_id}`}</span>
                        </div>
                        <div className="flex items-center space-x-2 mb-2">
                          <MapPin className="h-4 w-4 text-gray-500" />
                          <span className="text-sm text-gray-600">{dispatch.dispatch_address}</span>
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <Clock className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">
                            Dispatched: {formatTime(dispatch.dispatched_at)} ({getElapsedTime(dispatch.dispatched_at)})
                          </span>
                        </div>
                        {dispatch.response_time && (
                          <div className="flex items-center space-x-2">
                            <Truck className="h-4 w-4 text-gray-500" />
                            <span className="text-sm">
                              Response Time: {dispatch.response_time} minutes
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="bg-white p-3 rounded border">
                      <p className="text-sm text-gray-700">
                        <strong>Emergency:</strong> {dispatch.emergency_details}
                      </p>
                      {dispatch.notes && (
                        <p className="text-sm text-gray-600 mt-1">
                          <strong>Notes:</strong> {dispatch.notes}
                        </p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}