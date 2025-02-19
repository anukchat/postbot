import React, { useState, ReactNode } from 'react';
import { FloatingNav } from '../Navigation/FloatingNav';
import { NavigationDrawer } from '../Navigation/NavigationDrawer';


export const SharedLayout = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <div className="h-full flex  dark:bg-gray-900 dark:text-white">
      <FloatingNav 
        onToggleDrawer={() => setIsDrawerOpen(!isDrawerOpen)} 
        isDrawerOpen={isDrawerOpen} 
      />

      <NavigationDrawer 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
      />

    </div>
  );
};