import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Calendar } from './ui/calendar';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { toast } from './ui/use-toast';
import apiClient from '../services/apiClient';
import { format } from 'date-fns';

interface Service {
  id: number;
  name: string;
  description: string;
  estimated_time: number;
}

interface AvailableSlot {
  start_time: string;
  end_time: string;
  available: boolean;
}

const AppointmentBooking: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [availableSlots, setAvailableSlots] = useState<AvailableSlot[]>([]);
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchServices();
  }, []);

  useEffect(() => {
    if (selectedService && selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedService, selectedDate]);

  const fetchServices = async () => {
    try {
      const response = await apiClient.get('/services');
      setServices(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load services',
        variant: 'destructive',
      });
    }
  };

  const fetchAvailableSlots = async () => {
    if (!selectedService || !selectedDate) return;

    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      const response = await apiClient.get(`/scheduling/available/${selectedService}?date=${dateStr}`);
      setAvailableSlots(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load available slots',
        variant: 'destructive',
      });
    }
  };

  const handleBooking = async () => {
    if (!selectedService || !selectedDate || !selectedTime) {
      toast({
        title: 'Error',
        description: 'Please select service, date, and time',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const appointmentDate = new Date(selectedDate);
      const [hours, minutes] = selectedTime.split(':');
      appointmentDate.setHours(parseInt(hours), parseInt(minutes));

      const response = await apiClient.post('/appointments', {
        service_id: parseInt(selectedService),
        appointment_date: appointmentDate.toISOString(),
        duration: 30, // Default duration
        notes: notes,
      });

      toast({
        title: 'Success',
        description: 'Appointment booked successfully',
      });

      // Reset form
      setSelectedService('');
      setSelectedDate(new Date());
      setSelectedTime('');
      setNotes('');
      setAvailableSlots([]);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to book appointment',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Book Appointment</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <Label htmlFor="service">Select Service</Label>
          <Select value={selectedService} onValueChange={setSelectedService}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a service" />
            </SelectTrigger>
            <SelectContent>
              {services.map((service) => (
                <SelectItem key={service.id} value={service.id.toString()}>
                  {service.name} - {service.description}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Select Date</Label>
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={setSelectedDate}
            disabled={(date) => date < new Date()}
            className="rounded-md border"
          />
        </div>

        {availableSlots.length > 0 && (
          <div>
            <Label htmlFor="time">Select Time</Label>
            <Select value={selectedTime} onValueChange={setSelectedTime}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a time slot" />
              </SelectTrigger>
              <SelectContent>
                {availableSlots
                  .filter((slot) => slot.available)
                  .map((slot, index) => (
                    <SelectItem key={index} value={slot.start_time}>
                      {slot.start_time} - {slot.end_time}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div>
          <Label htmlFor="notes">Additional Notes (Optional)</Label>
          <Textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any special requirements or notes..."
            rows={3}
          />
        </div>

        <Button
          onClick={handleBooking}
          disabled={loading || !selectedService || !selectedDate || !selectedTime}
          className="w-full"
        >
          {loading ? 'Booking...' : 'Book Appointment'}
        </Button>
      </CardContent>
    </Card>
  );
};

export default AppointmentBooking;