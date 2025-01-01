import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../services/auth';
import { useAuth } from '../../providers/AuthProvider';

const AuthCallback = () => {
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const { session } = useAuth();

    useEffect(() => {
        const handleCallback = async () => {
            try {
                // Get the auth code from URL
                const hashParams = new URLSearchParams(window.location.hash.substring(1));
                const accessToken = hashParams.get('access_token');

                if (!accessToken) {
                    throw new Error('No access token found in URL');
                }

                // Exchange the token if needed
                const { data, error } = await supabase.auth.setSession({
                    access_token: accessToken,
                    refresh_token: hashParams.get('refresh_token') || '',
                });

                if (error) throw error;

                // If successful, redirect to app
                if (data.session) {
                    navigate('/app');
                }
            } catch (err) {
                console.error('Error in auth callback:', err);
                setError(err instanceof Error ? err.message : 'Authentication failed');
                // Redirect to login after a delay if there's an error
                setTimeout(() => navigate('/login'), 3000);
            }
        };

        // If we already have a session, go straight to the app
        if (session) {
            navigate('/app');
            return;
        }

        handleCallback();
    }, [navigate, session]);

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                    <h1 className="text-red-600 text-xl mb-4">Authentication Error</h1>
                    <p className="text-gray-600 dark:text-gray-400">{error}</p>
                    <p className="text-gray-500 dark:text-gray-500 mt-2">Redirecting to login...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
            <div className="text-center">
                <h1 className="text-2xl mb-4 text-gray-700 dark:text-gray-300">Completing Sign In</h1>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            </div>
        </div>
    );
};

export default AuthCallback;
