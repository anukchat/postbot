import React from 'react';
import { Link } from 'react-router-dom';
import { theme } from '../../styles/themes';

const Footer: React.FC = () => {
  return (
    <footer className={`bg-gradient-to-b ${theme.colors.background.main} py-12 border-t ${theme.colors.navbar.border}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <h3 className={`text-lg font-semibold ${theme.colors.primary.text.dark} mb-4`}>Product</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/features" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Features
                </Link>
              </li>
              <li>
                <Link to="/pricing" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Pricing
                </Link>
              </li>
              <li>
                <Link to="/about" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  About Us
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className={`text-lg font-semibold ${theme.colors.primary.text.dark} mb-4`}>Support</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/help" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Help Center
                </Link>
              </li>
              <li>
                <Link to="/contact" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Contact Us
                </Link>
              </li>
              <li>
                <Link to="/faq" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  FAQ
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className={`text-lg font-semibold ${theme.colors.primary.text.dark} mb-4`}>Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className={`text-lg font-semibold ${theme.colors.primary.text.dark} mb-4`}>Connect</h3>
            <ul className="space-y-2">
              <li>
                <a href="https://twitter.com/riteup" target="_blank" rel="noopener noreferrer" 
                   className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  Twitter
                </a>
              </li>
              <li>
                <a href="https://linkedin.com/company/riteup" target="_blank" rel="noopener noreferrer"
                   className={`${theme.colors.primary.solid} hover:${theme.colors.primary.hover} text-sm`}>
                  LinkedIn
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center">
            © {new Date().getFullYear()} RITE UP. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;