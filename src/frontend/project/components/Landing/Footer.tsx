import React from 'react';
import { Linkedin, Twitter, Instagram } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="w-full bg-[#fcfaf5]">
      {/* Top Navigation Bar */}
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col md:flex-row justify-between items-center">
      {/* Left Side - Links */}
      <div className="flex items-center space-x-8 md:w-1/4">
        <a href="/terms" className="text-gray-600 hover:text-gray-900">Terms of Use</a>
        <a href="/privacy" className="text-gray-600 hover:text-gray-900">Privacy Policy</a>
      </div>

      {/* Center - Copyright */}
      <div className="text-center text-gray-600 my-4 md:my-0 md:w-2/4 flex justify-center">
        <p>
        2025 © RiteUp. All rights reserved - Designed by{' '}
        <a href="#" className="text-blue-600 hover:text-blue-700">Anukool Chaturvedi</a>
        </p>
      </div>

      {/* Right Side - Social Icons */}
      <div className="flex items-center space-x-6 md:w-1/4 justify-end">
        <a href="#" className="text-gray-600 hover:text-gray-900">
        <Linkedin className="w-6 h-6" />
        </a>
        <a href="#" className="text-gray-600 hover:text-gray-900">
        <Twitter className="w-6 h-6" />
        </a>
        <a href="#" className="text-gray-600 hover:text-gray-900">
        <Instagram className="w-6 h-6" />
        </a>
      </div>
    </div>

      {/* Bottom Illustration */}
    </footer>
  );
};

export default Footer;