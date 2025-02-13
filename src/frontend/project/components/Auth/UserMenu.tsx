import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { theme } from '../../styles/themes';
import Avatar from 'react-avatar';

const UserMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { signOut, user } = useAuth();
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-2 ${theme.colors.primary.solid} hover:${theme.colors.primary.hover} p-2 rounded-lg transition-colors duration-200`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <span className="hidden md:inline">{user?.new_email}</span>
        <Avatar
      name={user?.email}
      size="38"
      round={true}
      src={user?.user_metadata?.avatar_url || `https://api.dicebear.com/6.x/avataaars/svg?seed=${user?.email}`}
className="dark:bg-gray-800"
      />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className={`absolute right-0 mt-2 w-48 py-2 rounded-lg shadow-xl border ${theme.colors.card.border} bg-white dark:bg-gray-800`}
          >
          <div className="px-4 py-3 border-b dark:border-gray-700">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Signed in as</p>
            <p className="truncate text-sm font-semibold text-gray-900 dark:text-white">
              {user?.email}
            </p>
          </div>
            <Link
              to="/settings"
              className={`flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors`}
              onClick={() => setIsOpen(false)}
            >
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Link>
            <button
              onClick={() => {
                signOut();
                setIsOpen(false);
              }}
              className={`flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors`}
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign out
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserMenu;
