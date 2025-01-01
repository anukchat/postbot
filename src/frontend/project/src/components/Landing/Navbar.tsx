import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import UserMenu from '../Auth/UserMenu';

export const Navbar: React.FC = () => {
  const { session } = useAuth();

  return (
    <nav className="fixed w-full bg-white dark:bg-gray-900 shadow-lg z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900 dark:text-white">
              PostBot
            </Link>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link to="/features" className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2">
                Features
              </Link>
              <Link to="/pricing" className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2">
                Pricing
              </Link>
              <Link to="/about" className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2">
                About
              </Link>
              <Link to="/contact" className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2">
                Contact
              </Link>
            </div>
          </div>
          
          <div className="ml-auto flex items-center space-x-4">
            {session ? (
              <>
                <Link to="/app" className="mr-4 text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2">
                  Dashboard
                </Link>
                <UserMenu />
              </>
            ) : (
              <div className="flex space-x-4">
                <Link to="/login" className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2">
                  Sign in
                </Link>
                <Link to="/signup" className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
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
