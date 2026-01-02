import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../../services/auth';
import { authDebugService } from '../../services/authDebug';
import Cookies from 'js-cookie';
import axios from 'axios';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      authDebugService.authFlow('Starting Auth Callback', { params: Object.fromEntries(searchParams) });
      
      try {
        if (searchParams.get('noAutoSignIn')) {
          authDebugService.authFlow('NoAutoSignIn detected, redirecting to login');
          await authService.signOut(); // Ensure clean state
          navigate('/login');
          return;
        }

        // Wait for Supabase to process OAuth callback (it needs to exchange code for tokens)
        // Try multiple times with delays to allow Supabase client to finish processing
        let session = null;
        let attempts = 0;
        const maxAttempts = 5;
        
        while (!session && attempts < maxAttempts) {
          if (attempts > 0) {
            authDebugService.authFlow(`Retry ${attempts}: Waiting for session...`);
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms between attempts
          }
          session = await authService.getSession();
          attempts++;
        }

        if (!session || !session.user) {
          authDebugService.error('No User in Session after retries', { session, attempts });
          navigate('/login');
          return;
        }
        
        authDebugService.authFlow('Session retrieved successfully', { 
          userId: session.user.id, 
          hasAccessToken: !!session.access_token,
          accessTokenPreview: session.access_token ? session.access_token.substring(0, 20) : 'UNDEFINED',
          attempts 
        });

        // Set refresh token in cookies
        if (session.refresh_token) {
          authDebugService.authFlow('Setting refresh token cookie');
          Cookies.set('refresh_token', session.refresh_token, { 
            path: '/',
            secure: window.location.protocol === 'https:',
            sameSite: 'Lax',
            expires: 30 // Add 30 day expiration
          });
        } else {
          authDebugService.error('No refresh token in session', { session });
        }

        const provider = (session.user.app_metadata?.provider || session.user.user_metadata?.provider) || 'google';
        authDebugService.authFlow('Auth Provider Check', { 
          provider,
          userId: session.user.id,
          metadata: session.user.user_metadata 
        });

        if (provider === 'google') {
          try {
            authDebugService.authFlow('Syncing user profile with backend', {
              userId: session.user.id,
              email: session.user.email,
              metadata: session.user.user_metadata
            });
            
            // Sync profile with backend API (which can connect to ANY PostgreSQL database)
            // Backend will create or update the profile in the configured database
            const apiUrl = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000/api`;
            await axios.post(`${apiUrl}/profiles/sync`, {
              user_id: session.user.id,
              email: session.user.email || '',
              full_name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || null,
              avatar_url: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture || null,
              provider: provider
            }, {
              headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json'
              }
            });
            
            authDebugService.authFlow('Profile synced successfully - Navigating to App');
            navigate('/app');
          } catch (profileError: any) {
            authDebugService.error('Profile Sync Error', profileError);
            
            // Check if it's a network error or backend is down
            if (profileError.code === 'ERR_NETWORK' || profileError.code === 'ECONNREFUSED') {
              console.error('Backend API is not reachable. Please ensure backend is running.');
              alert('Cannot connect to backend server. Please ensure the backend is running on ' + 
                    (import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`));
            }
            
            await authService.signOut();
            navigate('/login');
          }
        } else {
          authDebugService.authFlow('Non-Google Auth - Redirecting to Login');
          navigate('/login');
        }
      } catch (err) {
        authDebugService.error('Auth Callback Error', err);
        await authService.signOut(); // Clean up if anything goes wrong
        navigate('/login');
      }
    };

    handleCallback();
  }, [navigate, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-600">Completing authentication...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
