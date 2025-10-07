import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { toast } from './ui/use-toast';
import apiClient from '../services/apiClient';
import { format } from 'date-fns';
import { Calendar, Clock, User, FileText } from 'lucide-react';

interface Appointment {
  id: number;
  patient_id: number;
  service_id: number;
  staff_id?: number;
  appointment_date: string;
  duration: number;
  status: string;
  notes?: string;
  patient_name?: string;
  service_name?: string;
  staff_name?: string;
}

interface User {
  id: number;
  name: string;
  role: string;
}

const AppointmentManagement: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [staff, setStaff] = useState<User[]>([]);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [newStatus, setNewStatus] = useState<string>('');
  const [newNotes, setNewNotes] = useState<string>('');
  const [assignedStaff, setAssignedStaff] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAppointments();
    fetchStaff();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await apiClient.get('/appointments');
      setAppointments(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load appointments',
        variant: 'destructive',
      });
    }
  };

  const fetchStaff = async () => {
    try {
      const response = await apiClient.get('/users?role=staff');
      setStaff(response.data.filter((user: User) => user.role === 'staff' || user.role === 'admin'));
    } catch (error) {
      // Staff fetch is optional for patients
    }
  };

  const handleStatusUpdate = async (appointmentId: number) => {
    if (!newStatus) return;

    setLoading(true);
    try {
      await apiClient.put(`/appointments/${appointmentId}`, {
        status: newStatus,
        notes: newNotes,
        staff_id: assignedStaff ? parseInt(assignedStaff) : undefined,
      });

      toast({
        title: 'Success',
        description: 'Appointment updated successfully',
      });

      fetchAppointments();
      setSelectedAppointment(null);
      setNewStatus('');
      setNewNotes('');
      setAssignedStaff('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update appointment',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId: number) => {
    setLoading(true);
    try {
      await apiClient.delete(`/appointments/${appointmentId}`);

      toast({
        title: 'Success',
        description: 'Appointment cancelled successfully',
      });

      fetchAppointments();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to cancel appointment',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Appointment Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {appointments.map((appointment) => (
              <Card key={appointment.id} className="p-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4" />
                      <span className="font-medium">
                        {format(new Date(appointment.appointment_date), 'PPP')}
                      </span>
                      <Clock className="h-4 w-4" />
                      <span>
                        {format(new Date(appointment.appointment_date), 'p')} ({appointment.duration} min)
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4" />
                      <span>{appointment.service_name}</span>
                    </div>

                    {appointment.patient_name && (
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4" />
                        <span>Patient: {appointment.patient_name}</span>
                      </div>
                    )}

                    {appointment.staff_name && (
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4" />
                        <span>Staff: {appointment.staff_name}</span>
                      </div>
                    )}

                    {appointment.notes && (
                      <p className="text-sm text-gray-600">{appointment.notes}</p>
                    )}
                  </div>

                  <div className="flex flex-col items-end space-y-2">
                    <Badge className={getStatusColor(appointment.status)}>
                      {appointment.status}
                    </Badge>

                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedAppointment(appointment)}
                      >
                        Edit
                      </Button>

                      {appointment.status !== 'cancelled' && appointment.status !== 'completed' && (
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleCancelAppointment(appointment.id)}
                        >
                          Cancel
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {selectedAppointment && (
        <Card>
          <CardHeader>
            <CardTitle>Edit Appointment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={newStatus} onValueChange={setNewStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="scheduled">Scheduled</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {staff.length > 0 && (
              <div>
                <Label htmlFor="staff">Assign Staff</Label>
                <Select value={assignedStaff} onValueChange={setAssignedStaff}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select staff member" />
                  </SelectTrigger>
                  <SelectContent>
                    {staff.map((member) => (
                      <SelectItem key={member.id} value={member.id.toString()}>
                        {member.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={newNotes}
                onChange={(e) => setNewNotes(e.target.value)}
                placeholder="Update notes..."
                rows={3}
              />
            </div>

            <div className="flex space-x-2">
              <Button
                onClick={() => handleStatusUpdate(selectedAppointment.id)}
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Update'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setSelectedAppointment(null)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AppointmentManagement;