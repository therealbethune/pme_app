import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CssBaseline from "@mui/material/CssBaseline";
import { ColorModeProvider } from "./contexts/ColorModeContext";
import Navbar from "./components/Navbar";
import Analysis from "./pages/Analysis";
import DataUpload from "./pages/DataUpload";
import ChartsTest from "./pages/ChartsTest";
import { ApiConnectionError, DemoModeBanner, GlassfundsLoader } from "./components/ProfessionalErrorStates";
import { healthCheckService } from "./services/healthCheck";
import { NotificationProvider } from "./components/NotificationSystem";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { TestingPanel } from "./components/TestingPanel";
import { GradientBackground } from "./components/ui/GradientBackground";
import DashboardShell from "./components/DashboardShell";
import NeonDashboard from "./components/NeonDashboard";
import EnhancedNeonDashboard from "./components/EnhancedNeonDashboard";
import SimpleEnhancedDashboard from "./components/SimpleEnhancedDashboard";
import CommandPalette from "./components/ui/CommandPalette";

function App() {
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showTestingPanel, setShowTestingPanel] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  const checkApiConnection = async () => {
    try {
      const status = await healthCheckService.checkNow();
      setApiConnected(status);
    } catch (error) {
      console.warn('API connection check failed:', error);
      setApiConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Subscribe to health check updates
    const unsubscribe = healthCheckService.subscribe((status) => {
      setApiConnected(status);
      setIsLoading(false);
    });

    // Start periodic checks
    healthCheckService.startPeriodicChecks();

    return unsubscribe;
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Testing panel shortcut
      if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        setShowTestingPanel(!showTestingPanel);
      }
      
      // Command palette shortcut
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen(!isCommandPaletteOpen);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showTestingPanel, isCommandPaletteOpen]);

  if (isLoading) {
    return <GlassfundsLoader />;
  }

  if (apiConnected === false && !isDemoMode) {
    return <ApiConnectionError onRetry={checkApiConnection} onSwitchToDemo={() => setIsDemoMode(true)} />;
  }

  return (
    <ErrorBoundary>
      <ColorModeProvider>
        <CssBaseline />
        <NotificationProvider>
          <Router>
            <GradientBackground variant="financial">
              {isDemoMode && <DemoModeBanner onConnectBackend={() => {
                setIsDemoMode(false);
                checkApiConnection();
              }} />}
              <Navbar />
              <Routes>
                <Route path="/" element={<DashboardShell />} />
                <Route path="/neon" element={<NeonDashboard />} />
                <Route path="/enhanced" element={<EnhancedNeonDashboard />} />
                <Route path="/simple" element={<SimpleEnhancedDashboard />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/upload" element={<DataUpload />} />
                <Route path="/charts-test" element={<ChartsTest />} />
                <Route path="/legacy" element={<DataUpload />} />
              </Routes>
            </GradientBackground>
          </Router>
        </NotificationProvider>
        
        {/* Testing Panel - Ctrl+Shift+T to toggle */}
        <TestingPanel 
          visible={showTestingPanel} 
          onClose={() => setShowTestingPanel(false)} 
        />
        
        {/* Command Palette - Cmd/Ctrl+K to toggle */}
        <CommandPalette 
          isOpen={isCommandPaletteOpen}
          onClose={() => setIsCommandPaletteOpen(false)}
        />
      </ColorModeProvider>
    </ErrorBoundary>
  );
}

export default App; 