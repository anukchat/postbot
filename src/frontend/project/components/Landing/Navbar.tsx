import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import UserMenu from '../Auth/UserMenu';

export const Navbar: React.FC = () => {
  const { session } = useAuth();

  return (
    <nav className="fixed w-full bg-[#fcfaf5] z-50 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <img 
                src="/assets/riteup logo svg.svg" 
                alt="RiteUp Logo" 
                className="h-16 w-auto"
              />
            </Link>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link to="/features" className="text-gray-900 dark:text-white px-3 py-2">
                Features
              </Link>
              <Link to="/pricing" className="text-gray-900 dark:text-white px-3 py-2">
                Pricing
              </Link>
              <Link to="/about" className="text-gray-900 dark:text-white px-3 py-2">
                About
              </Link>
              <Link to="/contact" className="text-gray-900 dark:text-white px-3 py-2">
                Contact
              </Link>
            </div>
          </div>
          
          <div className="ml-auto flex items-center space-x-4">
            {session ? (
              <>
                <Link to="/dashboard" className="mr-4 text-gray-900 dark:text-white px-3 py-2">
                  Dashboard
                </Link>
                <UserMenu />
              </>
            ) : (
              <div className="flex space-x-4">
                <Link to="/login" className="text-gray-900 dark:text-white px-3 py-2">
                  Sign in
                </Link>
                <Link to="/signup" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
