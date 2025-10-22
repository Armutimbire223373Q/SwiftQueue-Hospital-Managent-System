import React, { useState, useEffect } from 'react';
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Monitor,
  Users,
  Settings,
  Clock,
  Brain,
  Smartphone,
  BarChart3,
  CheckCircle,
  Heart,
  Stethoscope,
  Activity,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Shield,
  Zap,
  TrendingUp,
  Star,
  Play,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Award,
  Target,
  Globe,
  Crown,
  UserCheck,
  Menu,
  X,
  ChevronRight
} from "lucide-react";
import { queueService } from '@/services/queueService';
import { aiService } from '@/services/aiService';
import { demoService } from '@/services/demoService';

const HomePage: React.FC = () => {
  const [stats, setStats] = useState({
    totalPatients: 0,
    avgWaitTime: 0,
    efficiencyScore: 0,
    activeDepartments: 0
  });
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 300], [0, -50]);

  useEffect(() => {
    const loadStats = async () => {
      console.log('HomePage: Starting to load stats...');
      try {
        // Try to load real data first
        console.log('HomePage: Attempting to load real queue stats...');
        const [queueStats, aiInsights] = await Promise.all([
          queueService.getQueueStatistics(),
          aiService.getDashboardInsights()
        ]);

        console.log('HomePage: Real stats loaded successfully:', { queueStats, aiInsights });

        setStats({
          totalPatients: queueStats.total_waiting + queueStats.total_being_served,
          avgWaitTime: Math.round(queueStats.avg_wait_time_today),
          efficiencyScore: Math.round(queueStats.efficiency_score * 100),
          activeDepartments: 6
        });
        console.log('HomePage: Real stats set successfully');
      } catch (error) {
        console.error('HomePage: Failed to load real stats, using demo data:', error);
        console.log('HomePage: Falling back to demo stats');
        // Use demo data as fallback
        setStats(demoService.getStats());
        console.log('HomePage: Demo stats set');
      } finally {
        setLoading(false);
        console.log('HomePage: Loading state set to false');
      }
    };

    loadStats();

    // Set up real-time updates
    console.log('HomePage: Setting up real-time updates');
    const stopUpdates = demoService.startRealTimeUpdates(() => {
      console.log('HomePage: Real-time update triggered');
      setStats(demoService.getStats());
    });

    return () => {
      console.log('HomePage: Cleaning up real-time updates');
      stopUpdates();
    };
  }, []);

  const features = [
    {
      icon: Brain,
      title: "AI Patient Flow",
      description: "Smart patient routing and treatment time predictions",
      color: "from-blue-500 to-cyan-500",
      bgColor: "bg-blue-50",
      iconColor: "text-blue-600"
    },
    {
      icon: Smartphone,
      title: "Smart Notifications",
      description: "Automated patient alerts and appointment reminders",
      color: "from-green-500 to-emerald-500",
      bgColor: "bg-green-50",
      iconColor: "text-green-600"
    },
    {
      icon: Monitor,
      title: "Real-time Monitoring",
      description: "Live patient queue and department status tracking",
      color: "from-purple-500 to-pink-500",
      bgColor: "bg-purple-50",
      iconColor: "text-purple-600"
    },
    {
      icon: BarChart3,
      title: "Healthcare Analytics",
      description: "Patient flow insights and resource optimization",
      color: "from-orange-500 to-red-500",
      bgColor: "bg-orange-50",
      iconColor: "text-orange-600"
    }
  ];

  const [departments, setDepartments] = useState([
    {
      name: "Emergency Care",
      icon: AlertTriangle,
      color: "text-red-500",
      bgColor: "bg-red-50",
      description: "24/7 emergency medical services",
      waitTime: "5 min",
      patients: 3
    },
    {
      name: "Cardiology",
      icon: Heart,
      color: "text-red-500",
      bgColor: "bg-red-50",
      description: "Heart and cardiovascular care",
      waitTime: "15 min",
      patients: 2
    },
    {
      name: "General Medicine",
      icon: Stethoscope,
      color: "text-blue-500",
      bgColor: "bg-blue-50",
      description: "Primary care and consultations",
      waitTime: "12 min",
      patients: 4
    },
    {
      name: "Laboratory",
      icon: Activity,
      color: "text-green-500",
      bgColor: "bg-green-50",
      description: "Blood tests and diagnostics",
      waitTime: "8 min",
      patients: 1
    },
    {
      name: "Radiology",
      icon: Monitor,
      color: "text-purple-500",
      bgColor: "bg-purple-50",
      description: "Medical imaging and scans",
      waitTime: "20 min",
      patients: 2
    },
    {
      name: "Pediatrics",
      icon: Users,
      color: "text-pink-500",
      bgColor: "bg-pink-50",
      description: "Child and infant care",
      waitTime: "10 min",
      patients: 1
    }
  ]);

  // Update departments with demo data
  useEffect(() => {
    const updateDepartments = () => {
      const demoDepts = demoService.getDepartments();
      setDepartments(prev => prev.map((dept, index) => ({
        ...dept,
        waitTime: demoDepts[index]?.waitTime || dept.waitTime,
        patients: demoDepts[index]?.patients || dept.patients
      })));
    };

    updateDepartments();
    const interval = setInterval(updateDepartments, 15000); // Update every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const testimonials = [
    {
      name: "Dr. Sarah Johnson",
      role: "Chief Medical Officer",
      content: "SwiftQueue has revolutionized our patient flow management. The AI predictions are incredibly accurate.",
      rating: 5
    },
    {
      name: "Nurse Michael Chen",
      role: "Emergency Department",
      content: "The real-time monitoring helps us stay organized and provide better care to our patients.",
      rating: 5
    },
    {
      name: "Admin Lisa Rodriguez",
      role: "Hospital Administrator",
      content: "The analytics dashboard gives us insights we never had before. Highly recommended!",
      rating: 5
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl"
          >
            <Stethoscope className="h-10 w-10 text-white" />
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 px-4"
          >
            Loading SwiftQueue Hospital
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-gray-600 px-4 text-center"
          >
            Connecting to our AI-powered healthcare system...
          </motion.p>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-6 flex justify-center space-x-2"
          >
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.2 }}
                className="w-3 h-3 bg-blue-500 rounded-full"
              />
            ))}
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
              onClick={() => setSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
              className="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-50 overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-xl font-bold text-gray-900">Staff & Admin Access</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSidebarOpen(false)}
                    className="hover:bg-gray-100"
                  >
                    <X className="h-5 w-5" />
                  </Button>
                </div>

                <div className="space-y-4">
                  {/* Receptionist Portal */}
                  <Link to="/receptionist-portal" onClick={() => setSidebarOpen(false)}>
                    <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-green-50 to-green-100 cursor-pointer group">
                      <CardContent className="p-6 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                          <Monitor className="h-8 w-8 text-white" />
                        </div>
                        <h4 className="text-xl font-semibold text-gray-900 mb-2">Receptionist Portal</h4>
                        <p className="text-gray-600 mb-4 text-sm">Monitor client requests, manage queues, and coordinate patient flow</p>
                        <Button className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 shadow-lg">
                          Enter Receptionist Portal
                          <ChevronRight className="h-4 w-4 ml-2" />
                        </Button>
                      </CardContent>
                    </Card>
                  </Link>

                  {/* Department Portals */}
                  <div className="space-y-3">
                    <h5 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Department Portals</h5>

                    <Link to="/department/emergency" onClick={() => setSidebarOpen(false)}>
                      <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-red-50 to-red-100 cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-r from-red-500 to-red-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <AlertTriangle className="h-6 w-6 text-white" />
                          </div>
                          <h6 className="text-lg font-semibold text-gray-900 mb-1">Emergency Care</h6>
                          <p className="text-gray-600 text-xs">24/7 emergency medical services</p>
                        </CardContent>
                      </Card>
                    </Link>

                    <Link to="/department/cardiology" onClick={() => setSidebarOpen(false)}>
                      <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-pink-50 to-pink-100 cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-r from-pink-500 to-pink-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <Heart className="h-6 w-6 text-white" />
                          </div>
                          <h6 className="text-lg font-semibold text-gray-900 mb-1">Cardiology</h6>
                          <p className="text-gray-600 text-xs">Heart and cardiovascular care</p>
                        </CardContent>
                      </Card>
                    </Link>

                    <Link to="/department/general-medicine" onClick={() => setSidebarOpen(false)}>
                      <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-blue-50 to-blue-100 cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <Stethoscope className="h-6 w-6 text-white" />
                          </div>
                          <h6 className="text-lg font-semibold text-gray-900 mb-1">General Medicine</h6>
                          <p className="text-gray-600 text-xs">Primary care and consultations</p>
                        </CardContent>
                      </Card>
                    </Link>

                    <Link to="/department/laboratory" onClick={() => setSidebarOpen(false)}>
                      <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-teal-50 to-teal-100 cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-r from-teal-500 to-teal-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <Activity className="h-6 w-6 text-white" />
                          </div>
                          <h6 className="text-lg font-semibold text-gray-900 mb-1">Laboratory</h6>
                          <p className="text-gray-600 text-xs">Blood tests and diagnostics</p>
                        </CardContent>
                      </Card>
                    </Link>

                    <Link to="/department/radiology" onClick={() => setSidebarOpen(false)}>
                      <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-purple-50 to-purple-100 cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <Monitor className="h-6 w-6 text-white" />
                          </div>
                          <h6 className="text-lg font-semibold text-gray-900 mb-1">Radiology</h6>
                          <p className="text-gray-600 text-xs">Medical imaging and scans</p>
                        </CardContent>
                      </Card>
                    </Link>

                    <Link to="/department/pediatrics" onClick={() => setSidebarOpen(false)}>
                      <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-yellow-50 to-yellow-100 cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-r from-yellow-500 to-yellow-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <Users className="h-6 w-6 text-white" />
                          </div>
                          <h6 className="text-lg font-semibold text-gray-900 mb-1">Pediatrics</h6>
                          <p className="text-gray-600 text-xs">Child and infant care</p>
                        </CardContent>
                      </Card>
                    </Link>
                  </div>

                  {/* Admin Dashboard */}
                  <Link to="/admin-dashboard" onClick={() => setSidebarOpen(false)}>
                    <Card className="hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-gray-50 to-gray-100 cursor-pointer group">
                      <CardContent className="p-6 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-r from-gray-500 to-gray-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                          <Crown className="h-8 w-8 text-white" />
                        </div>
                        <h4 className="text-xl font-semibold text-gray-900 mb-2">Admin Dashboard</h4>
                        <p className="text-gray-600 mb-4 text-sm">Complete system administration and user management</p>
                        <Button className="w-full bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 shadow-lg">
                          Enter Admin Dashboard
                          <ChevronRight className="h-4 w-4 ml-2" />
                        </Button>
                      </CardContent>
                    </Card>
                  </Link>
                </div>

                {/* Login Credentials */}
                <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-3">Demo Credentials</h4>
                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="font-medium text-gray-700">Admin Access:</p>
                      <p className="text-gray-600">Email: admin@hospital.com</p>
                      <p className="text-gray-600">Password: AdminPass123!</p>
                    </div>
                    <div>
                      <p className="font-medium text-gray-700">Staff Access:</p>
                      <p className="text-gray-600">Email: sarah.johnson@hospital.com</p>
                      <p className="text-gray-600">Password: StaffPass123!</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Hero Section */}
      <motion.section
        style={{ y }}
        className="relative overflow-hidden pt-20 pb-16"
      >
        {/* Background Elements */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/4 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
          <div className="absolute top-0 right-1/4 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" style={{ animationDelay: '2s' }}></div>
          <div className="absolute -bottom-8 left-1/3 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" style={{ animationDelay: '4s' }}></div>
        </div>

        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="mb-8"
            >
              <div className="flex flex-col sm:flex-row items-center justify-center mb-6">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 sm:mb-0 sm:mr-4 shadow-2xl"
                >
                  <Stethoscope className="h-8 w-8 sm:h-10 sm:w-10 text-white" />
                </motion.div>
                <div className="text-center sm:text-left">
                  <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    SwiftQueue Hospital
                  </h1>
                  <p className="text-lg sm:text-xl text-gray-600 mt-2">AI-Powered Healthcare Management</p>
                </div>
              </div>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-lg sm:text-xl text-gray-600 mb-8 max-w-3xl mx-auto px-4 sm:px-0"
            >
              Revolutionizing healthcare through intelligent queue management, real-time monitoring,
              and AI-powered predictions that optimize patient flow and improve care delivery.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-12 px-4 sm:px-0"
            >
              <Link to="/queue" className="w-full sm:w-auto">
                <Button size="lg" className="w-full sm:w-auto bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 sm:px-8 py-4 text-base sm:text-lg">
                  <Users className="h-5 w-5 mr-2" />
                  Join Queue Now
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </Link>
              <Link to="/dashboard" className="w-full sm:w-auto">
                <Button size="lg" variant="outline" className="w-full sm:w-auto px-6 sm:px-8 py-4 text-base sm:text-lg">
                  <Monitor className="h-5 w-5 mr-2" />
                  View Dashboard
                </Button>
              </Link>
              <Button
                size="lg"
                variant="outline"
                onClick={() => setSidebarOpen(true)}
                className="w-full sm:w-auto px-6 sm:px-8 py-4 text-base sm:text-lg border-gray-300 hover:border-blue-400 hover:bg-blue-50"
              >
                <Settings className="h-5 w-5 mr-2" />
                Staff Access
              </Button>
            </motion.div>

            {/* Live Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 max-w-4xl mx-auto px-4 sm:px-0"
            >
              {[
                { label: "Patients Waiting", value: stats.totalPatients, icon: Users, color: "text-blue-600", bgColor: "bg-blue-50", glowColor: "shadow-blue-500/25" },
                { label: "Avg Wait Time", value: `${stats.avgWaitTime}m`, icon: Clock, color: "text-green-600", bgColor: "bg-green-50", glowColor: "shadow-green-500/25" },
                { label: "Efficiency Score", value: `${stats.efficiencyScore}%`, icon: TrendingUp, color: "text-purple-600", bgColor: "bg-purple-50", glowColor: "shadow-purple-500/25" },
                { label: "Active Departments", value: stats.activeDepartments, icon: Activity, color: "text-orange-600", bgColor: "bg-orange-50", glowColor: "shadow-orange-500/25" }
              ].map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, scale: 0.8, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                    whileHover={{
                      scale: 1.05,
                      boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
                    }}
                    className={`bg-white/90 backdrop-blur-sm rounded-xl p-4 sm:p-6 shadow-lg border border-white/20 cursor-pointer group transition-all duration-300 hover:shadow-2xl ${stat.glowColor}`}
                  >
                    <div className={`flex items-center justify-center mb-4 w-12 h-12 mx-auto rounded-full ${stat.bgColor} group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                    <motion.div
                      className="text-3xl font-bold text-gray-900 mb-1"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 1 + index * 0.1, type: "spring", stiffness: 200 }}
                    >
                      {stat.value}
                    </motion.div>
                    <div className="text-sm text-gray-600 font-medium">{stat.label}</div>
                    <motion.div
                      className="w-full bg-gray-200 rounded-full h-1 mt-3 overflow-hidden"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 1.2 + index * 0.1, duration: 0.8 }}
                    >
                      <motion.div
                        className={`h-full ${stat.bgColor.replace('bg-', 'bg-')} rounded-full`}
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 0.7 }}
                        transition={{ delay: 1.5 + index * 0.1, duration: 1 }}
                      />
                    </motion.div>
                  </motion.div>
                );
              })}
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Advanced Healthcare Technology
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI-powered platform combines cutting-edge technology with compassionate care
              to deliver the best possible healthcare experience.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -5 }}
                  className="group"
                >
                  <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-gray-50">
                    <CardContent className="p-6 text-center">
                      <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl ${feature.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                        <Icon className={`h-8 w-8 ${feature.iconColor}`} />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Departments Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Hospital Departments
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive medical services across all major specialties,
              each optimized with AI-powered queue management.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {departments.map((dept, index) => {
              const Icon = dept.icon;
              return (
                <motion.div
                  key={dept.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="group"
                >
                  <Card className="h-full hover:shadow-2xl transition-all duration-500 border-0 bg-white/90 backdrop-blur-sm overflow-hidden relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-white/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <CardContent className="p-6 relative z-10">
                      <div className="flex items-start justify-between mb-4">
                        <motion.div
                          className={`w-12 h-12 rounded-xl ${dept.bgColor} flex items-center justify-center shadow-lg`}
                          whileHover={{ rotate: [0, -5, 5, 0] }}
                          transition={{ duration: 0.5 }}
                        >
                          <Icon className={`h-6 w-6 ${dept.color}`} />
                        </motion.div>
                        <motion.div
                          whileHover={{ scale: 1.1 }}
                          transition={{ type: "spring", stiffness: 400 }}
                        >
                          <Badge variant="outline" className="text-xs bg-white/80 backdrop-blur-sm border-gray-300">
                            <motion.span
                              key={dept.patients}
                              initial={{ scale: 0.8 }}
                              animate={{ scale: 1 }}
                              className="inline-block"
                            >
                              {dept.patients}
                            </motion.span>
                            {' '}waiting
                          </Badge>
                        </motion.div>
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-gray-800 transition-colors">
                        {dept.name}
                      </h3>
                      <p className="text-gray-600 mb-4 group-hover:text-gray-700 transition-colors">
                        {dept.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <motion.div
                            animate={{ rotate: [0, 360] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                          >
                            <Clock className="h-4 w-4 text-gray-500" />
                          </motion.div>
                          <span className="text-sm text-gray-600 font-medium">Avg wait: {dept.waitTime}</span>
                        </div>
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Link to="/queue">
                            <Button size="sm" variant="outline" className="border-gray-300 hover:border-blue-400 hover:bg-blue-50 transition-all duration-300">
                              Join Queue
                              <motion.div
                                animate={{ x: [0, 2, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                              >
                                <ArrowRight className="h-3 w-3 ml-1" />
                              </motion.div>
                            </Button>
                          </Link>
                        </motion.div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Healthcare Professionals
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See what our medical staff and administrators say about SwiftQueue Hospital.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -5, scale: 1.02 }}
                className="group"
              >
                <Card className="h-full hover:shadow-2xl transition-all duration-500 border-0 bg-gradient-to-br from-white via-gray-50 to-white overflow-hidden relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-purple-50/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <CardContent className="p-6 relative z-10">
                    <motion.div
                      className="flex items-center mb-4"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                    >
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <motion.div
                          key={i}
                          initial={{ scale: 0, rotate: -180 }}
                          whileInView={{ scale: 1, rotate: 0 }}
                          transition={{ delay: 0.5 + index * 0.1 + i * 0.1, type: "spring", stiffness: 200 }}
                        >
                          <Star className="h-5 w-5 text-yellow-400 fill-current" />
                        </motion.div>
                      ))}
                    </motion.div>
                    <motion.p
                      className="text-gray-600 mb-4 italic text-lg leading-relaxed"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                    >
                      "{testimonial.content}"
                    </motion.p>
                    <motion.div
                      className="flex items-center"
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.9 + index * 0.1 }}
                    >
                      <motion.div
                        className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4 shadow-lg"
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <span className="text-white font-bold text-sm">
                          {testimonial.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </motion.div>
                      <div>
                        <div className="font-semibold text-gray-900 group-hover:text-blue-900 transition-colors">{testimonial.name}</div>
                        <div className="text-sm text-gray-500 group-hover:text-purple-600 transition-colors">{testimonial.role}</div>
                      </div>
                    </motion.div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10" />
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-300/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
        </div>
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
              className="inline-block mb-6"
            >
              <Sparkles className="h-12 w-12 text-yellow-300 mx-auto" />
            </motion.div>
            <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight px-4">
              Ready to Experience the Future of Healthcare?
            </h2>
            <p className="text-lg sm:text-xl text-blue-100 mb-8 max-w-2xl mx-auto leading-relaxed px-4">
              Join thousands of patients who have experienced faster, more efficient healthcare
              with SwiftQueue Hospital's AI-powered system.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center px-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto"
              >
                <Link to="/queue">
                  <Button size="lg" variant="secondary" className="w-full sm:w-auto px-8 sm:px-10 py-4 sm:py-5 text-base sm:text-lg font-semibold bg-white text-blue-600 hover:bg-gray-100 shadow-2xl hover:shadow-white/25 transition-all duration-300">
                    <Users className="h-5 w-5 sm:h-6 sm:w-6 mr-3" />
                    Get Started Now
                    <motion.div
                      className="ml-3"
                      animate={{ x: [0, 5, 0] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <ArrowRight className="h-4 w-4 sm:h-5 sm:w-5" />
                    </motion.div>
                  </Button>
                </Link>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto"
              >
                <Link to="/dashboard">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto px-8 sm:px-10 py-4 sm:py-5 text-base sm:text-lg font-semibold text-white border-2 border-white hover:bg-white hover:text-blue-600 shadow-xl hover:shadow-white/25 transition-all duration-300">
                    <Monitor className="h-5 w-5 sm:h-6 sm:w-6 mr-3" />
                    View Live Dashboard
                  </Button>
                </Link>
              </motion.div>
            </div>
            <motion.div
              className="mt-12 flex flex-wrap justify-center gap-4 sm:gap-8 text-blue-200 px-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="text-xs sm:text-sm">AI-Powered</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="text-xs sm:text-sm">Real-time Updates</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="text-xs sm:text-sm">24/7 Support</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Stethoscope className="h-6 w-6 text-white" />
                </div>
                <span className="text-xl font-bold">SwiftQueue Hospital</span>
              </div>
              <p className="text-gray-400">
                Revolutionizing healthcare through intelligent queue management and AI-powered predictions.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/queue" className="hover:text-white transition-colors">Join Queue</Link></li>
                <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
                <li><Link to="/analytics" className="hover:text-white transition-colors">Analytics</Link></li>
                <li><Link to="/admin" className="hover:text-white transition-colors">Admin</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Departments</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Emergency Care</li>
                <li>Cardiology</li>
                <li>General Medicine</li>
                <li>Laboratory</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li className="flex items-center">
                  <Phone className="h-4 w-4 mr-2" />
                  +1 (555) 123-4567
                </li>
                <li className="flex items-center">
                  <Mail className="h-4 w-4 mr-2" />
                  info@swiftqueue.hospital
                </li>
                <li className="flex items-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  123 Healthcare Ave, Medical City
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 SwiftQueue Hospital. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
