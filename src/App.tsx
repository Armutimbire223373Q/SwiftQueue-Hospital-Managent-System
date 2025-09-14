import { Suspense, useState, useEffect } from "react";
import { useRoutes } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import ErrorBoundary from "./components/ErrorBoundary";
import LoadingSpinner from "./components/LoadingSpinner";
import SplashScreen from "./components/SplashScreen";
import Navigation from "./components/Navigation";
import { routes } from "./routes";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const routeElement = useRoutes(routes);

  useEffect(() => {
    // Show splash screen for 3 seconds
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  if (showSplash) {
    return (
      <SplashScreen 
        onComplete={() => setShowSplash(false)}
        duration={3000}
      />
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Suspense fallback={<LoadingSpinner size="xl" text="Loading application..." fullScreen />}>
          <>
            {routeElement}
            <Toaster />
          </>
        </Suspense>
      </div>
    </ErrorBoundary>
  );
}

export default App;