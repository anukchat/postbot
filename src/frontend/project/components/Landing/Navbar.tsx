import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import UserMenu from '../Auth/UserMenu';
import { theme } from '../../styles/themes';

export const Navbar: React.FC = () => {
  const { session } = useAuth();

  return (
    <nav
      className={`fixed w-full bg-gradient-to-r ${theme.colors.navbar.bg} bg-blend-overlay backdrop-blur-md border-b ${theme.colors.navbar.border} z-50 font-sans`}
      style={{ backgroundBlendMode: 'overlay' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <img
                src="/assets/riteup logo svg.svg"
                alt="RiteUp Logo"
                className="h-16 w-auto transition-transform duration-300 hover:scale-105"
              />
            </Link>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/features"
                className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} px-3 py-2 transition-colors duration-200`}
              >
                Features
              </Link>
              <Link
                to="/pricing"
                className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} px-3 py-2 transition-colors duration-200`}
              >
                Pricing
              </Link>
              <Link
                to="/about"
                className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} px-3 py-2 transition-colors duration-200`}
              >
                About
              </Link>
              <Link
                to="/contact"
                className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} px-3 py-2 transition-colors duration-200`}
              >
                Contact
              </Link>
            </div>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            {session ? (
              <>
                <Link
                  to="/dashboard"
                  className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} px-3 py-2 transition-colors duration-200`}
                >
                  Dashboard
                </Link>
                <UserMenu />
              </>
            ) : (
              <div className="flex space-x-4">
                <Link
                  to="/login"
                  className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} px-3 py-2 transition-colors duration-200`}
                >
                  Sign in
                </Link>
                <Link
                  to="/signup"
                  className={`bg-gradient-to-r ${theme.colors.primary.gradient} ${theme.colors.primary.button.hover} text-white px-4 py-2 rounded-lg transition-all duration-300 shadow-sm hover:shadow-md`}
                >
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
