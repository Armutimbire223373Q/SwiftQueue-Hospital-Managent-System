import React, { useState, useEffect } from 'react';
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform } from "framer-motion";
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
  Globe
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
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 300], [0, -50]);

  useEffect(() => {
    const loadStats = async () => {
      try {
        // Try to load real data first
        const [queueStats, aiInsights] = await Promise.all([
          queueService.getQueueStatistics(),
          aiService.getDashboardInsights()
        ]);
        
        setStats({
          totalPatients: queueStats.total_waiting + queueStats.total_being_served,
          avgWaitTime: Math.round(queueStats.avg_wait_time_today),
          efficiencyScore: Math.round(queueStats.efficiency_score * 100),
          activeDepartments: 6
        });
      } catch (error) {
        console.error('Failed to load real stats, using demo data:', error);
        // Use demo data as fallback
        setStats(demoService.getStats());
      } finally {
        setLoading(false);
      }
    };

    loadStats();

    // Set up real-time updates
    const stopUpdates = demoService.startRealTimeUpdates(() => {
      setStats(demoService.getStats());
    });

    return () => stopUpdates();
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
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
              <div className="flex items-center justify-center mb-6">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4 shadow-2xl"
                >
                  <Stethoscope className="h-10 w-10 text-white" />
                </motion.div>
                <div className="text-left">
                  <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    SwiftQueue Hospital
                  </h1>
                  <p className="text-xl text-gray-600 mt-2">AI-Powered Healthcare Management</p>
                </div>
              </div>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
            >
              Revolutionizing healthcare through intelligent queue management, real-time monitoring, 
              and AI-powered predictions that optimize patient flow and improve care delivery.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            >
              <Link to="/queue">
                <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-4 text-lg">
                  <Users className="h-5 w-5 mr-2" />
                  Join Queue Now
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button size="lg" variant="outline" className="px-8 py-4 text-lg">
                  <Monitor className="h-5 w-5 mr-2" />
                  View Dashboard
                </Button>
              </Link>
            </motion.div>

            {/* Live Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto"
            >
              {[
                { label: "Patients Waiting", value: stats.totalPatients, icon: Users, color: "text-blue-600" },
                { label: "Avg Wait Time", value: `${stats.avgWaitTime}m`, icon: Clock, color: "text-green-600" },
                { label: "Efficiency Score", value: `${stats.efficiencyScore}%`, icon: TrendingUp, color: "text-purple-600" },
                { label: "Active Departments", value: stats.activeDepartments, icon: Activity, color: "text-orange-600" }
              ].map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                    className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-white/20"
                  >
                    <div className="flex items-center justify-center mb-2">
                      <Icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
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
                  whileHover={{ y: -5 }}
                >
                  <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className={`w-12 h-12 rounded-xl ${dept.bgColor} flex items-center justify-center`}>
                          <Icon className={`h-6 w-6 ${dept.color}`} />
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {dept.patients} waiting
                        </Badge>
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {dept.name}
                      </h3>
                      <p className="text-gray-600 mb-4">
                        {dept.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4 text-gray-500" />
                          <span className="text-sm text-gray-600">Avg wait: {dept.waitTime}</span>
                        </div>
                        <Link to="/queue">
                          <Button size="sm" variant="outline">
                            Join Queue
                            <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
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
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-gray-50">
                  <CardContent className="p-6">
                    <div className="flex items-center mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <p className="text-gray-600 mb-4 italic">
                      "{testimonial.content}"
                    </p>
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                        <span className="text-white font-semibold text-sm">
                          {testimonial.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{testimonial.name}</div>
                        <div className="text-sm text-gray-500">{testimonial.role}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Experience the Future of Healthcare?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join thousands of patients who have experienced faster, more efficient healthcare 
              with SwiftQueue Hospital's AI-powered system.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/queue">
                <Button size="lg" variant="secondary" className="px-8 py-4 text-lg">
                  <Users className="h-5 w-5 mr-2" />
                  Get Started Now
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button size="lg" variant="outline" className="px-8 py-4 text-lg text-white border-white hover:bg-white hover:text-blue-600">
                  <Monitor className="h-5 w-5 mr-2" />
                  View Live Dashboard
                </Button>
              </Link>
            </div>
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
