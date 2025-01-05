import { Navigate } from 'react-router-dom';
import { useAuth } from '../providers/AuthProvider';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { session, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!session) {
    return <Navigate to="/login" replace />;  // Using /login consistently
  }

  return <>{children}</>;
}
