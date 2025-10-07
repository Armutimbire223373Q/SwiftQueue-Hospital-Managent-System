import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { toast } from './ui/use-toast';
import apiClient from '../services/apiClient';
import { MapPin, Navigation, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

interface NavigationRoute {
  steps: string[];
  estimated_time: number;
  distance: number;
  accessibility_notes: string[];
}

const HospitalNavigation: React.FC = () => {
  const [currentLocation, setCurrentLocation] = useState<string>('');
  const [destination, setDestination] = useState<string>('');
  const [accessibilityNeeds, setAccessibilityNeeds] = useState<string>('');
  const [route, setRoute] = useState<NavigationRoute | null>(null);
  const [availableLocations, setAvailableLocations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [emergencyLoading, setEmergencyLoading] = useState(false);

  React.useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await apiClient.get('/navigation/locations');
      setAvailableLocations(response.data);
    } catch (error) {
      // Use default locations if API fails
      setAvailableLocations([
        "entrance", "registration", "waiting_area", "consultation_room_1",
        "consultation_room_2", "consultation_room_3", "pharmacy", "laboratory",
        "radiology", "emergency", "cafeteria", "exit"
      ]);
    }
  };

  const getDirections = async () => {
    if (!currentLocation || !destination) {
      toast({
        title: 'Error',
        description: 'Please select both current location and destination',
        variant: 'destructive',
      });
      return;
    }

    if (currentLocation === destination) {
      toast({
        title: 'Error',
        description: 'Current location and destination cannot be the same',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/navigation/route', {
        current_location: currentLocation,
        destination: destination,
        accessibility_needs: accessibilityNeeds,
      });

      setRoute(response.data);
      toast({
        title: 'Success',
        description: 'Navigation route calculated',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to get directions',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const requestEmergencyAssistance = async () => {
    if (!currentLocation) {
      toast({
        title: 'Error',
        description: 'Please select your current location',
        variant: 'destructive',
      });
      return;
    }

    setEmergencyLoading(true);
    try {
      await apiClient.post('/navigation/emergency', {
        location: currentLocation,
        description: 'Emergency assistance requested via navigation app',
      });

      toast({
        title: 'Emergency Assistance Requested',
        description: 'Help is on the way. Please stay where you are.',
        variant: 'destructive',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to request emergency assistance',
        variant: 'destructive',
      });
    } finally {
      setEmergencyLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Navigation className="h-5 w-5" />
            <span>Hospital Navigation</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="current">Current Location</Label>
              <Select value={currentLocation} onValueChange={setCurrentLocation}>
                <SelectTrigger>
                  <SelectValue placeholder="Where are you now?" />
                </SelectTrigger>
                <SelectContent>
                  {availableLocations.map((location) => (
                    <SelectItem key={location} value={location}>
                      {location.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="destination">Destination</Label>
              <Select value={destination} onValueChange={setDestination}>
                <SelectTrigger>
                  <SelectValue placeholder="Where do you want to go?" />
                </SelectTrigger>
                <SelectContent>
                  {availableLocations.map((location) => (
                    <SelectItem key={location} value={location}>
                      {location.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="accessibility">Accessibility Needs (Optional)</Label>
            <Textarea
              id="accessibility"
              value={accessibilityNeeds}
              onChange={(e) => setAccessibilityNeeds(e.target.value)}
              placeholder="e.g., wheelchair, assistance needed, visual impairment..."
              rows={2}
            />
          </div>

          <div className="flex space-x-2">
            <Button
              onClick={getDirections}
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Getting Directions...' : 'Get Directions'}
            </Button>

            <Button
              variant="destructive"
              onClick={requestEmergencyAssistance}
              disabled={emergencyLoading}
            >
              <AlertTriangle className="h-4 w-4 mr-1" />
              {emergencyLoading ? 'Requesting...' : 'Emergency'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {route && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5" />
              <span>Navigation Route</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span>{route.estimated_time} min</span>
              </div>
              <div className="flex items-center space-x-1">
                <MapPin className="h-4 w-4" />
                <span>{route.distance}m</span>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Directions:</h4>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                {route.steps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>

            {route.accessibility_notes.length > 0 && (
              <div>
                <h4 className="font-medium mb-2 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Accessibility Notes:
                </h4>
                <ul className="space-y-1">
                  {route.accessibility_notes.map((note, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Badge variant="secondary" className="text-xs mt-0.5">
                        ✓
                      </Badge>
                      <span className="text-sm">{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Navigation Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• Use the emergency button only for urgent situations</p>
            <p>• If you have accessibility needs, please specify them for better directions</p>
            <p>• Follow hospital signage and ask staff if you get lost</p>
            <p>• Keep this device with you at all times during your visit</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default HospitalNavigation;