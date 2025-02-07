import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabaseClient } from '../../utils/supaclient';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const handleCallback = async () => {
      try {
        const { data: { session }, error: sessionError } = await supabaseClient.auth.getSession();
        
        if (sessionError || !session) {
          console.error('Session error:', sessionError);
          throw new Error('No session found');
        }

        const { user } = session;
        if (!user) throw new Error('No user found');


        // Check if profile exists
        //TODO: call python api endpoint to check if user exists in the database
        const { data: existingProfile, error: profileCheckError } = await supabaseClient
          .from('profiles')
          .select('id')
          .eq('user_id', user.id)
          .single();

        if (profileCheckError || !existingProfile) {
          
          // Create new profile
          const { error: profileError } = await supabaseClient
            .from('profiles')
            .insert({
                id: crypto.randomUUID(),
                user_id: user.id,
                full_name: user.user_metadata.full_name,
                avatar_url: user.user_metadata.avatar_url,
                role: 'free',
                subscription_status: 'none',
                created_at: new Date().toISOString()
            });

          if (profileError) {
            throw profileError;
          }
        }

        if (mounted) {
          navigate('/dashboard');
        }
      } catch (err) {
        if (mounted) {
          setError('Authentication failed');
          setTimeout(() => navigate('/login'), 2000);
        }
      }
    };

    handleCallback();

    return () => {
      mounted = false;
    };
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Authenticating...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return null;
};

export default AuthCallback;
