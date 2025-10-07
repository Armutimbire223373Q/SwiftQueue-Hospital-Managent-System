import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Eye, EyeOff, AlertTriangle, UserCheck } from 'lucide-react';
import { authService } from '@/services/authService';

export default function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  // Check if this is a staff/admin trying to access - hide emergency options
  const urlParams = new URLSearchParams(window.location.search);
  const isStaffLogin = urlParams.get('role') === 'staff' || urlParams.get('role') === 'admin';
  const currentPath = window.location.pathname;
  const isAdminPath = currentPath.includes('/admin') || currentPath.includes('/staff');

  // Check if redirected from a protected route (staff trying to access dashboard)
  const location = useLocation();
  const redirectedFromProtected = location.state?.from?.pathname && (
    location.state.from.pathname.includes('/dashboard') ||
    location.state.from.pathname.includes('/admin') ||
    location.state.from.pathname.includes('/analytics')
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await authService.login(formData.email, formData.password);

      if (response.access_token) {
        // Store token in localStorage
        localStorage.setItem('token', response.access_token);

        // Get user profile
        const userProfile = await authService.getCurrentUser();
        localStorage.setItem('user', JSON.stringify(userProfile));

        // Redirect based on role
        switch (userProfile.role) {
          case 'admin':
            navigate('/admin');
            break;
          case 'staff':
            navigate('/dashboard');
            break;
          default:
            navigate('/');
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmergencyAccess = () => {
    // Create a temporary guest session for emergency situations
    const guestUser = {
      id: 'guest-' + Date.now(),
      name: 'Emergency Patient',
      email: 'emergency@guest.temp',
      role: 'patient',
      isGuest: true
    };
    
    localStorage.setItem('user', JSON.stringify(guestUser));
    localStorage.setItem('isGuestSession', 'true');
    
    // Redirect directly to queue join
    navigate('/join-queue');
  };

  const handleQuickAccess = () => {
    // Quick guest access for non-emergency situations
    const guestUser = {
      id: 'guest-' + Date.now(),
      name: 'Guest Patient',
      email: 'guest@temp.temp',
      role: 'patient',
      isGuest: true
    };
    
    localStorage.setItem('user', JSON.stringify(guestUser));
    localStorage.setItem('isGuestSession', 'true');
    
    // Redirect to home page
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            Welcome Back
          </CardTitle>
          <p className="text-gray-600">Sign in to your account</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          {/* Emergency and Guest Access Options - Only for patients */}
           {!isStaffLogin && !isAdminPath && !redirectedFromProtected && (
            <div className="mt-6 space-y-3">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-muted-foreground">
                    Emergency or Guest Access
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Button
                  onClick={handleEmergencyAccess}
                  variant="destructive"
                  className="w-full bg-red-600 hover:bg-red-700"
                  disabled={isLoading}
                >
                  <AlertTriangle className="mr-2 h-4 w-4" />
                  🚨 Emergency Access - Skip Registration
                </Button>
                
                <Button
                  onClick={handleQuickAccess}
                  variant="outline"
                  className="w-full"
                  disabled={isLoading}
                >
                  <UserCheck className="mr-2 h-4 w-4" />
                  Continue as Guest
                </Button>
              </div>

              <Alert className="mt-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  <strong>Emergency Access:</strong> Immediately join the queue for urgent medical situations.
                  <br />
                  <strong>Guest Access:</strong> Browse and join the queue without creating an account.
                </AlertDescription>
              </Alert>
            </div>
          )}

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign up
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}