import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import ErrorBoundary from './components/common/ErrorBoundary';
import AppShell from './components/layout/AppShell';
import LoginPage from './pages/LoginPage';
import AuthCallbackPage from './pages/AuthCallbackPage';
import CalendarPage from './pages/CalendarPage';
import SubscriptionPage from './pages/SubscriptionPage';
import PlansPage from './pages/PlansPage';

function AuthenticatedLayout({ children }) {
  return (
    <AppShell>
      {children}
    </AppShell>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
          <Route
            path="/calendar"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <CalendarPage />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <SubscriptionPage />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/plans"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <PlansPage />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/calendar" replace />} />
          <Route path="*" element={<Navigate to="/calendar" replace />} />
        </Routes>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
