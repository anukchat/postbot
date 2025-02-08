export const authDebugService = {
  authFlow: (step: string, data?: any) => {
    console.group(`Auth Flow - ${step}`);
    console.log('Timestamp:', new Date().toISOString());
    if (data) {
      console.log('Data:', data);
    }
    console.groupEnd();
  },

  error: (step: string, error: any) => {
    console.group(`Auth Error - ${step}`);
    console.error('Timestamp:', new Date().toISOString());
    console.error('Error:', error);
    if (error instanceof Error) {
      console.error('Stack:', error.stack);
    }
    console.groupEnd();
  }
};