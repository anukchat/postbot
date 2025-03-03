import { useState } from 'react';
import { FloatingNav } from '../Navigation/FloatingNav';
import { NavigationDrawer } from '../Navigation/NavigationDrawer';
import { useNavigate } from 'react-router-dom';

export const SharedLayout = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const navigate = useNavigate();
  
  return (
    <div className="h-full flex dark:bg-gray-900 dark:text-white">
      <FloatingNav 
        onToggleDrawer={() => setIsDrawerOpen(!isDrawerOpen)} 
        isDrawerOpen={isDrawerOpen} 
      />
      <NavigationDrawer 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
        onNavigateToEditor={() => navigate('/dashboard')}
      />
    </div>
  );
};