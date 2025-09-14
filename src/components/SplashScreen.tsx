import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Stethoscope, 
  Heart, 
  Brain, 
  Activity, 
  Shield, 
  CheckCircle,
  Loader2
} from 'lucide-react';

interface SplashScreenProps {
  onComplete: () => void;
  duration?: number;
}

const SplashScreen: React.FC<SplashScreenProps> = ({ 
  onComplete, 
  duration = 3000 
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const steps = [
    { icon: Stethoscope, text: "Initializing Healthcare System", color: "text-blue-500" },
    { icon: Heart, text: "Loading Patient Care Modules", color: "text-red-500" },
    { icon: Brain, text: "Activating AI Intelligence", color: "text-purple-500" },
    { icon: Activity, text: "Connecting Real-time Services", color: "text-green-500" },
    { icon: Shield, text: "Securing Patient Data", color: "text-yellow-500" },
    { icon: CheckCircle, text: "System Ready", color: "text-emerald-500" }
  ];

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(stepInterval);
          setTimeout(() => {
            setIsComplete(true);
            setTimeout(onComplete, 500);
          }, 1000);
          return prev;
        }
      });
    }, duration / steps.length);

    return () => clearInterval(stepInterval);
  }, [duration, onComplete]);

  return (
    <AnimatePresence>
      {!isComplete && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.5 }}
          className="fixed inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center z-50"
        >
          <div className="text-center max-w-md mx-auto px-6">
            {/* Logo and Title */}
            <motion.div
              initial={{ y: -50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="mb-12"
            >
              <div className="relative">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-24 h-24 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl"
                >
                  <Stethoscope className="h-12 w-12 text-white" />
                </motion.div>
                
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                  className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center"
                >
                  <CheckCircle className="h-5 w-5 text-white" />
                </motion.div>
              </div>
              
              <motion.h1
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2"
              >
                SwiftQueue Hospital
              </motion.h1>
              
              <motion.p
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="text-lg text-gray-600 mb-8"
              >
                AI-Powered Healthcare Management
              </motion.p>
            </motion.div>

            {/* Loading Steps */}
            <div className="space-y-4 mb-8">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index === currentStep;
                const isCompleted = index < currentStep;
                
                return (
                  <motion.div
                    key={index}
                    initial={{ x: -50, opacity: 0 }}
                    animate={{ 
                      x: 0, 
                      opacity: isActive || isCompleted ? 1 : 0.3 
                    }}
                    transition={{ duration: 0.3 }}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ${
                      isActive 
                        ? 'bg-white shadow-lg border-2 border-blue-200' 
                        : isCompleted 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-gray-50'
                    }`}
                  >
                    <motion.div
                      animate={isActive ? { scale: [1, 1.2, 1] } : {}}
                      transition={{ duration: 0.5, repeat: isActive ? Infinity : 0 }}
                      className={`flex-shrink-0 ${isCompleted ? 'text-green-500' : step.color}`}
                    >
                      {isCompleted ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : isActive ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </motion.div>
                    
                    <span className={`text-sm font-medium ${
                      isActive 
                        ? 'text-blue-700' 
                        : isCompleted 
                        ? 'text-green-700' 
                        : 'text-gray-500'
                    }`}>
                      {step.text}
                    </span>
                  </motion.div>
                );
              })}
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
              <motion.div
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>

            {/* Loading Animation */}
            <motion.div
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="flex items-center justify-center space-x-2 text-gray-500"
            >
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
            </motion.div>

            {/* Footer */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1 }}
              className="mt-8 text-xs text-gray-400"
            >
              <p>© 2024 SwiftQueue Hospital. All rights reserved.</p>
              <p className="mt-1">Revolutionizing healthcare through intelligent queue management</p>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SplashScreen;
