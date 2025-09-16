import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Clock, Users, ArrowRight, CheckCircle, AlertCircle, 
  Activity, Timer, MapPin, Stethoscope, TestTube
} from 'lucide-react';

interface WorkflowStage {
  id: string;
  name: string;
  status: 'completed' | 'current' | 'pending' | 'delayed';
  startTime?: Date;
  endTime?: Date;
  duration?: number;
  patientCount: number;
  avgWaitTime: number;
  icon: React.ReactNode;
  color: string;
}

interface PatientWorkflow {
  id: string;
  patientName: string;
  patientId: string;
  department: string;
  triageCategory: 'Emergency' | 'Urgent' | 'Semi-urgent' | 'Non-urgent';
  currentStage: string;
  stages: WorkflowStage[];
  totalTime: number;
  estimatedCompletion: Date;
  priority: number;
}

interface MultiStageWorkflowTrackerProps {
  selectedDepartment?: string;
}

const STAGE_ICONS = {
  'Registration': <Users className="h-4 w-4" />,
  'Check-in': <CheckCircle className="h-4 w-4" />,
  'Triage': <Stethoscope className="h-4 w-4" />,
  'Provider': <Activity className="h-4 w-4" />,
  'Tests': <TestTube className="h-4 w-4" />,
  'Discharge': <ArrowRight className="h-4 w-4" />
};

const STAGE_COLORS = {
  'Registration': 'bg-blue-100 text-blue-800',
  'Check-in': 'bg-green-100 text-green-800',
  'Triage': 'bg-yellow-100 text-yellow-800',
  'Provider': 'bg-purple-100 text-purple-800',
  'Tests': 'bg-orange-100 text-orange-800',
  'Discharge': 'bg-gray-100 text-gray-800'
};

export default function MultiStageWorkflowTracker({ selectedDepartment }: MultiStageWorkflowTrackerProps) {
  const [patients, setPatients] = useState<PatientWorkflow[]>([]);
  const [workflowStages, setWorkflowStages] = useState<WorkflowStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState<PatientWorkflow | null>(null);

  useEffect(() => {
    loadWorkflowData();
    loadPatientData();
  }, [selectedDepartment]);

  const loadWorkflowData = async () => {
    try {
      // Simulate API call - replace with actual API
      const mockStages: WorkflowStage[] = [
        {
          id: 'registration',
          name: 'Registration',
          status: 'completed',
          patientCount: 45,
          avgWaitTime: 6.0,
          icon: STAGE_ICONS['Registration'],
          color: STAGE_COLORS['Registration']
        },
        {
          id: 'checkin',
          name: 'Check-in',
          status: 'completed',
          patientCount: 42,
          avgWaitTime: 3.2,
          icon: STAGE_ICONS['Check-in'],
          color: STAGE_COLORS['Check-in']
        },
        {
          id: 'triage',
          name: 'Triage',
          status: 'current',
          patientCount: 38,
          avgWaitTime: 4.0,
          icon: STAGE_ICONS['Triage'],
          color: STAGE_COLORS['Triage']
        },
        {
          id: 'provider',
          name: 'Provider',
          status: 'pending',
          patientCount: 35,
          avgWaitTime: 51.7,
          icon: STAGE_ICONS['Provider'],
          color: STAGE_COLORS['Provider']
        },
        {
          id: 'tests',
          name: 'Tests',
          status: 'pending',
          patientCount: 28,
          avgWaitTime: 18.7,
          icon: STAGE_ICONS['Tests'],
          color: STAGE_COLORS['Tests']
        },
        {
          id: 'discharge',
          name: 'Discharge',
          status: 'pending',
          patientCount: 25,
          avgWaitTime: 8.5,
          icon: STAGE_ICONS['Discharge'],
          color: STAGE_COLORS['Discharge']
        }
      ];

      setWorkflowStages(mockStages);
    } catch (error) {
      console.error('Error loading workflow data:', error);
    }
  };

  const loadPatientData = async () => {
    try {
      // Simulate API call - replace with actual API
      const mockPatients: PatientWorkflow[] = [
        {
          id: '1',
          patientName: 'John Smith',
          patientId: 'P100001',
          department: 'Cardiology',
          triageCategory: 'Urgent',
          currentStage: 'Triage',
          totalTime: 45,
          estimatedCompletion: new Date(Date.now() + 2 * 60 * 60 * 1000), // 2 hours from now
          priority: 3,
          stages: [
            { id: 'reg', name: 'Registration', status: 'completed', patientCount: 0, avgWaitTime: 6, icon: STAGE_ICONS['Registration'], color: STAGE_COLORS['Registration'] },
            { id: 'checkin', name: 'Check-in', status: 'completed', patientCount: 0, avgWaitTime: 3, icon: STAGE_ICONS['Check-in'], color: STAGE_COLORS['Check-in'] },
            { id: 'triage', name: 'Triage', status: 'current', patientCount: 0, avgWaitTime: 4, icon: STAGE_ICONS['Triage'], color: STAGE_COLORS['Triage'] },
            { id: 'provider', name: 'Provider', status: 'pending', patientCount: 0, avgWaitTime: 52, icon: STAGE_ICONS['Provider'], color: STAGE_COLORS['Provider'] },
            { id: 'tests', name: 'Tests', status: 'pending', patientCount: 0, avgWaitTime: 19, icon: STAGE_ICONS['Tests'], color: STAGE_COLORS['Tests'] },
            { id: 'discharge', name: 'Discharge', status: 'pending', patientCount: 0, avgWaitTime: 9, icon: STAGE_ICONS['Discharge'], color: STAGE_COLORS['Discharge'] }
          ]
        },
        {
          id: '2',
          patientName: 'Sarah Johnson',
          patientId: 'P100002',
          department: 'Emergency',
          triageCategory: 'Emergency',
          currentStage: 'Provider',
          totalTime: 25,
          estimatedCompletion: new Date(Date.now() + 45 * 60 * 1000), // 45 minutes from now
          priority: 4,
          stages: [
            { id: 'reg', name: 'Registration', status: 'completed', patientCount: 0, avgWaitTime: 2, icon: STAGE_ICONS['Registration'], color: STAGE_COLORS['Registration'] },
            { id: 'checkin', name: 'Check-in', status: 'completed', patientCount: 0, avgWaitTime: 1, icon: STAGE_ICONS['Check-in'], color: STAGE_COLORS['Check-in'] },
            { id: 'triage', name: 'Triage', status: 'completed', patientCount: 0, avgWaitTime: 3, icon: STAGE_ICONS['Triage'], color: STAGE_COLORS['Triage'] },
            { id: 'provider', name: 'Provider', status: 'current', patientCount: 0, avgWaitTime: 15, icon: STAGE_ICONS['Provider'], color: STAGE_COLORS['Provider'] },
            { id: 'tests', name: 'Tests', status: 'pending', patientCount: 0, avgWaitTime: 10, icon: STAGE_ICONS['Tests'], color: STAGE_COLORS['Tests'] },
            { id: 'discharge', name: 'Discharge', status: 'pending', patientCount: 0, avgWaitTime: 5, icon: STAGE_ICONS['Discharge'], color: STAGE_COLORS['Discharge'] }
          ]
        },
        {
          id: '3',
          patientName: 'Mike Davis',
          patientId: 'P100003',
          department: 'Orthopedics',
          triageCategory: 'Non-urgent',
          currentStage: 'Tests',
          totalTime: 120,
          estimatedCompletion: new Date(Date.now() + 30 * 60 * 1000), // 30 minutes from now
          priority: 1,
          stages: [
            { id: 'reg', name: 'Registration', status: 'completed', patientCount: 0, avgWaitTime: 8, icon: STAGE_ICONS['Registration'], color: STAGE_COLORS['Registration'] },
            { id: 'checkin', name: 'Check-in', status: 'completed', patientCount: 0, avgWaitTime: 4, icon: STAGE_ICONS['Check-in'], color: STAGE_COLORS['Check-in'] },
            { id: 'triage', name: 'Triage', status: 'completed', patientCount: 0, avgWaitTime: 5, icon: STAGE_ICONS['Triage'], color: STAGE_COLORS['Triage'] },
            { id: 'provider', name: 'Provider', status: 'completed', patientCount: 0, avgWaitTime: 60, icon: STAGE_ICONS['Provider'], color: STAGE_COLORS['Provider'] },
            { id: 'tests', name: 'Tests', status: 'current', patientCount: 0, avgWaitTime: 20, icon: STAGE_ICONS['Tests'], color: STAGE_COLORS['Tests'] },
            { id: 'discharge', name: 'Discharge', status: 'pending', patientCount: 0, avgWaitTime: 10, icon: STAGE_ICONS['Discharge'], color: STAGE_COLORS['Discharge'] }
          ]
        }
      ];

      setPatients(mockPatients);
      setLoading(false);
    } catch (error) {
      console.error('Error loading patient data:', error);
    }
  };

  const getTriageColor = (category: string) => {
    switch (category) {
      case 'Emergency': return 'bg-red-100 text-red-800';
      case 'Urgent': return 'bg-orange-100 text-orange-800';
      case 'Semi-urgent': return 'bg-yellow-100 text-yellow-800';
      case 'Non-urgent': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'current': return <Clock className="h-4 w-4 text-blue-600" />;
      case 'delayed': return <AlertCircle className="h-4 w-4 text-red-600" />;
      default: return <Timer className="h-4 w-4 text-gray-400" />;
    }
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Multi-Stage Workflow Tracker</h2>
          <p className="text-gray-600">Track patients through complete hospital workflow</p>
        </div>
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-600" />
          <span className="text-sm font-medium text-gray-700">
            {patients.length} Active Patients
          </span>
        </div>
      </div>

      {/* Workflow Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5" />
            <span>Workflow Overview</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between space-x-4 overflow-x-auto">
            {workflowStages.map((stage, index) => (
              <div key={stage.id} className="flex items-center space-x-2 min-w-0">
                <div className="flex flex-col items-center space-y-2">
                  <div className={`p-3 rounded-full ${stage.color} ${
                    stage.status === 'current' ? 'ring-2 ring-blue-500' : ''
                  }`}>
                    {stage.icon}
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium">{stage.name}</p>
                    <p className="text-xs text-gray-600">{stage.patientCount} patients</p>
                    <p className="text-xs text-gray-500">{stage.avgWaitTime}min avg</p>
                  </div>
                </div>
                {index < workflowStages.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-gray-400 mx-2" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Patient List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {patients.map((patient) => (
          <Card 
            key={patient.id} 
            className={`hover:shadow-lg transition-shadow cursor-pointer ${
              selectedPatient?.id === patient.id ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => setSelectedPatient(patient)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{patient.patientName}</CardTitle>
                  <p className="text-sm text-gray-600">ID: {patient.patientId}</p>
                </div>
                <Badge className={getTriageColor(patient.triageCategory)}>
                  {patient.triageCategory}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Department</span>
                <span className="font-medium">{patient.department}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Current Stage</span>
                <Badge className={STAGE_COLORS[patient.currentStage as keyof typeof STAGE_COLORS]}>
                  {patient.currentStage}
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Time in Hospital</span>
                <span className="font-medium">{formatTime(patient.totalTime)}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Est. Completion</span>
                <span className="font-medium">
                  {patient.estimatedCompletion.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{Math.round((patient.stages.filter(s => s.status === 'completed').length / patient.stages.length) * 100)}%</span>
                </div>
                <Progress 
                  value={(patient.stages.filter(s => s.status === 'completed').length / patient.stages.length) * 100} 
                  className="h-2"
                />
              </div>

              {/* Stage Indicators */}
              <div className="flex items-center space-x-1">
                {patient.stages.map((stage, index) => (
                  <div key={stage.id} className="flex items-center">
                    <div className={`p-1 rounded-full ${stage.color} ${
                      stage.status === 'current' ? 'ring-2 ring-blue-500' : ''
                    }`}>
                      {getStatusIcon(stage.status)}
                    </div>
                    {index < patient.stages.length - 1 && (
                      <div className="w-2 h-0.5 bg-gray-300 mx-1"></div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Selected Patient Details */}
      {selectedPatient && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Patient Journey: {selectedPatient.patientName}</span>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setSelectedPatient(null)}
              >
                Close
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Priority</p>
                  <p className="text-lg font-semibold">{selectedPatient.priority}/4</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Total Time</p>
                  <p className="text-lg font-semibold">{formatTime(selectedPatient.totalTime)}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Department</p>
                  <p className="text-lg font-semibold">{selectedPatient.department}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Est. Completion</p>
                  <p className="text-lg font-semibold">
                    {selectedPatient.estimatedCompletion.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold">Stage Details</h4>
                {selectedPatient.stages.map((stage) => (
                  <div key={stage.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${stage.color}`}>
                        {stage.icon}
                      </div>
                      <div>
                        <p className="font-medium">{stage.name}</p>
                        <p className="text-sm text-gray-600">Avg: {stage.avgWaitTime} min</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(stage.status)}
                      <Badge className={stage.color}>
                        {stage.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
