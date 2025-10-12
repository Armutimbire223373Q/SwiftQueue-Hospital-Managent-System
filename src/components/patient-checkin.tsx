import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from './ui/use-toast';
import apiClient from '../services/apiClient';
import { format } from 'date-fns';
import { CheckCircle, Clock, MapPin, AlertTriangle } from 'lucide-react';

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

interface CheckinStatus {
  checked_in: boolean;
  checkin_time?: string;
  status?: string;
}

const PatientCheckin: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [checkinStatuses, setCheckinStatuses] = useState<Record<number, CheckinStatus>>({});
  const [loading, setLoading] = useState<Record<number, boolean>>({});
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [selectedAppointmentId, setSelectedAppointmentId] = useState<number | null>(null);
  const [addressData, setAddressData] = useState({
    street_address: '',
    city: '',
    state: '',
    zip_code: '',
    country: ''
  });
  const [addressLoading, setAddressLoading] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await apiClient.get('/appointments');
      const userAppointments = response.data.filter((apt: Appointment) =>
        apt.status === 'scheduled' || apt.status === 'confirmed'
      );
      setAppointments(userAppointments);

      // Fetch checkin status for each appointment
      const statuses: Record<number, CheckinStatus> = {};
      for (const appointment of userAppointments) {
        try {
          const statusResponse = await apiClient.get(`/checkin/appointment/${appointment.id}`);
          statuses[appointment.id] = statusResponse.data;
        } catch (error) {
          statuses[appointment.id] = { checked_in: false };
        }
      }
      setCheckinStatuses(statuses);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load appointments',
        variant: 'destructive',
      });
    }
  };

  const handleCheckin = async (appointmentId: number) => {
    // First check if user has address information
    try {
      const userResponse = await apiClient.get('/auth/me');
      const user = userResponse.data;

      // Check if address is missing
      if (!user.street_address || !user.city || !user.state || !user.zip_code || !user.country) {
        setSelectedAppointmentId(appointmentId);
        setShowAddressModal(true);
        return;
      }
    } catch (error) {
      console.error('Error checking user profile:', error);
    }

    // Proceed with check-in
    await performCheckin(appointmentId);
  };

  const performCheckin = async (appointmentId: number) => {
    setLoading(prev => ({ ...prev, [appointmentId]: true }));

    try {
      await apiClient.post('/checkin', {
        appointment_id: appointmentId,
      });

      toast({
        title: 'Success',
        description: 'Checked in successfully! Please proceed to the waiting area.',
      });

      // Update checkin status
      setCheckinStatuses(prev => ({
        ...prev,
        [appointmentId]: {
          checked_in: true,
          checkin_time: new Date().toISOString(),
          status: 'checked_in'
        }
      }));

      // Refresh appointments to update status
      fetchAppointments();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to check in',
        variant: 'destructive',
      });
    } finally {
      setLoading(prev => ({ ...prev, [appointmentId]: false }));
    }
  };

  const handleAddressSubmit = async () => {
    if (!selectedAppointmentId) return;

    setAddressLoading(true);
    try {
      // Update user profile with address
      await apiClient.put('/auth/me', addressData);

      toast({
        title: 'Success',
        description: 'Address information updated successfully.',
      });

      setShowAddressModal(false);
      setAddressData({
        street_address: '',
        city: '',
        state: '',
        zip_code: '',
        country: ''
      });

      // Now proceed with check-in
      await performCheckin(selectedAppointmentId);
      setSelectedAppointmentId(null);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update address',
        variant: 'destructive',
      });
    } finally {
      setAddressLoading(false);
    }
  };

  const handleAddressSkip = async () => {
    if (!selectedAppointmentId) return;

    setShowAddressModal(false);
    // Proceed with check-in even without address
    await performCheckin(selectedAppointmentId);
    setSelectedAppointmentId(null);
  };

  const getAppointmentStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCheckinStatusColor = (status?: string) => {
    switch (status) {
      case 'checked_in': return 'bg-green-100 text-green-800';
      case 'no_show': return 'bg-red-100 text-red-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const isAppointmentToday = (appointmentDate: string) => {
    const today = new Date();
    const appointment = new Date(appointmentDate);
    return today.toDateString() === appointment.toDateString();
  };

  const canCheckin = (appointment: Appointment, checkinStatus: CheckinStatus) => {
    return (
      !checkinStatus.checked_in &&
      isAppointmentToday(appointment.appointment_date) &&
      (appointment.status === 'scheduled' || appointment.status === 'confirmed')
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5" />
            <span>Patient Check-in</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {appointments.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No upcoming appointments found.
            </p>
          ) : (
            <div className="space-y-4">
              {appointments.map((appointment) => {
                const checkinStatus = checkinStatuses[appointment.id] || { checked_in: false };
                const canCheckinNow = canCheckin(appointment, checkinStatus);

                return (
                  <Card key={appointment.id} className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4" />
                          <span className="font-medium">
                            {format(new Date(appointment.appointment_date), 'PPP p')}
                          </span>
                          <span className="text-sm text-gray-500">
                            ({appointment.duration} min)
                          </span>
                        </div>

                        <p className="font-medium">{appointment.service_name}</p>

                        {appointment.staff_name && (
                          <p className="text-sm text-gray-600">
                            with {appointment.staff_name}
                          </p>
                        )}

                        {appointment.notes && (
                          <p className="text-sm text-gray-600">{appointment.notes}</p>
                        )}
                      </div>

                      <div className="flex flex-col items-end space-y-2">
                        <Badge className={getAppointmentStatusColor(appointment.status)}>
                          {appointment.status}
                        </Badge>

                        {checkinStatus.checked_in && (
                          <div className="flex items-center space-x-1">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <Badge className={getCheckinStatusColor(checkinStatus.status)}>
                              Checked In
                            </Badge>
                          </div>
                        )}

                        {checkinStatus.checkin_time && (
                          <p className="text-xs text-gray-500">
                            Checked in: {format(new Date(checkinStatus.checkin_time), 'p')}
                          </p>
                        )}

                        {canCheckinNow && (
                          <Button
                            onClick={() => handleCheckin(appointment.id)}
                            disabled={loading[appointment.id]}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            {loading[appointment.id] ? 'Checking in...' : 'Check In'}
                          </Button>
                        )}

                        {!canCheckinNow && !checkinStatus.checked_in && (
                          <p className="text-sm text-gray-500">
                            {isAppointmentToday(appointment.appointment_date)
                              ? 'Check-in not available yet'
                              : 'Check-in available on appointment day'
                            }
                          </p>
                        )}
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Check-in Instructions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• Check-in is available 24 hours before your appointment time</p>
            <p>• After checking in, please proceed to the waiting area</p>
            <p>• You will receive notifications when it's your turn</p>
            <p>• If you have any accessibility needs, please inform the reception</p>
          </div>
        </CardContent>
      </Card>

      {/* Address Collection Modal */}
      <Dialog open={showAddressModal} onOpenChange={setShowAddressModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              <span>Complete Your Address Information</span>
            </DialogTitle>
            <DialogDescription>
              For emergency services and better care coordination, please provide your address information.
              This helps us respond quickly in case of medical emergencies.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-sm">
                Your address information is securely stored and used only for emergency services and care coordination.
              </AlertDescription>
            </Alert>

            <div className="space-y-3">
              <div>
                <Label htmlFor="modal-street">Street Address</Label>
                <Input
                  id="modal-street"
                  value={addressData.street_address}
                  onChange={(e) => setAddressData({...addressData, street_address: e.target.value})}
                  placeholder="123 Main Street"
                  disabled={addressLoading}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="modal-city">City</Label>
                  <Input
                    id="modal-city"
                    value={addressData.city}
                    onChange={(e) => setAddressData({...addressData, city: e.target.value})}
                    placeholder="City"
                    disabled={addressLoading}
                  />
                </div>
                <div>
                  <Label htmlFor="modal-state">State</Label>
                  <Input
                    id="modal-state"
                    value={addressData.state}
                    onChange={(e) => setAddressData({...addressData, state: e.target.value})}
                    placeholder="State"
                    disabled={addressLoading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="modal-zip">ZIP Code</Label>
                  <Input
                    id="modal-zip"
                    value={addressData.zip_code}
                    onChange={(e) => setAddressData({...addressData, zip_code: e.target.value})}
                    placeholder="12345"
                    disabled={addressLoading}
                  />
                </div>
                <div>
                  <Label htmlFor="modal-country">Country</Label>
                  <Input
                    id="modal-country"
                    value={addressData.country}
                    onChange={(e) => setAddressData({...addressData, country: e.target.value})}
                    placeholder="Country"
                    disabled={addressLoading}
                  />
                </div>
              </div>
            </div>

            <div className="flex space-x-3 pt-4">
              <Button
                variant="outline"
                onClick={handleAddressSkip}
                disabled={addressLoading}
                className="flex-1"
              >
                Skip for Now
              </Button>
              <Button
                onClick={handleAddressSubmit}
                disabled={addressLoading || !addressData.street_address || !addressData.city || !addressData.state || !addressData.zip_code || !addressData.country}
                className="flex-1"
              >
                {addressLoading ? 'Saving...' : 'Save & Check In'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PatientCheckin;