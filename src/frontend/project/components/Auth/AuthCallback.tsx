import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { supabaseClient } from '../../utils/supaclient';
import { profileService } from '../../services/profiles';
import { authDebugService } from '../../services/authDebug';
import Cookies from 'js-cookie';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      authDebugService.authFlow('Starting Auth Callback', { params: Object.fromEntries(searchParams) });
      
      try {
        if (searchParams.get('noAutoSignIn')) {
          authDebugService.authFlow('NoAutoSignIn detected, redirecting to login');
          await supabaseClient.auth.signOut(); // Ensure clean state
          navigate('/login');
          return;
        }

        const { data: { session }, error: sessionError } = await supabaseClient.auth.getSession();
        
        if (sessionError) {
          authDebugService.error('Session Error', sessionError);
          navigate('/login');
          return;
        }

        if (!session?.user) {
          authDebugService.error('No User in Session', { session });
          navigate('/login');
          return;
        }

        // Set refresh token in cookies
        if (session.refresh_token) {
          authDebugService.authFlow('Setting refresh token cookie');
          Cookies.set('refresh_token', session.refresh_token, { 
            path: '/',
            secure: window.location.protocol === 'https:',
            sameSite: 'Lax'
          });
        } else {
          authDebugService.error('No refresh token in session');
        }

        const provider = session.user.app_metadata?.provider;
        authDebugService.authFlow('Auth Provider Check', { 
          provider,
          userId: session.user.id,
          metadata: session.user.user_metadata 
        });

        if (provider === 'google') {
          try {
            const exists = await profileService.checkProfileExists(session.user.id);
            authDebugService.authFlow('Profile Check', { exists });
            
            if (!exists) {
              authDebugService.authFlow('Creating Google User Profile', {
                userId: session.user.id,
                metadata: session.user.user_metadata
              });
              
              await profileService.createProfile(session.user.id, {
                email: session.user.email || '',
                full_name: session.user.user_metadata?.full_name || null,
                avatar_url: session.user.user_metadata?.avatar_url || null,
                role: 'free',
                subscription_status: 'none',
                generations_used_per_thread: 0,
                preferences: {},
                is_deleted: false
              });
            }
            
            authDebugService.authFlow('Google Auth Complete - Navigating to Dashboard');
            navigate('/dashboard');
          } catch (profileError) {
            authDebugService.error('Profile Creation Error', profileError);
            await supabaseClient.auth.signOut();
            navigate('/login');
          }
        } else {
          authDebugService.authFlow('Non-Google Auth - Redirecting to Login');
          navigate('/login');
        }
      } catch (err) {
        authDebugService.error('Auth Callback Error', err);
        await supabaseClient.auth.signOut(); // Clean up if anything goes wrong
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
