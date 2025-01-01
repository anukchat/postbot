import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Menu } from '@headlessui/react';
import { User, Settings, LogOut } from 'lucide-react';
import Avatar from 'react-avatar';
import { AvatarGenerator } from 'random-avatar-generator';


const UserMenu: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const generator = new AvatarGenerator();
  
  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <Menu as="div" className="relative">

    <Menu.Button className="flex items-center space-x-2 rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
    {/* <Avatar name={user?.email} size="32" round={true} /> */}
        {user?.user_metadata?.avatar_url ? (
            <img
            src={user.user_metadata.avatar_url}
            alt="User avatar"
            className="h-8 w-8 rounded-full"
            />
        ) : (
            <img
            src={generator.generateRandomAvatar()}
            alt="Random avatar"
            className="h-8 w-8 rounded-full"
            />
        )}
    </Menu.Button>

      <Menu.Items className="absolute right-0 mt-2 w-56 origin-top-right rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
        <div className="px-4 py-3">
          <p className="text-sm text-gray-700 dark:text-gray-200">Signed in as</p>
          <p className="truncate text-sm font-medium text-gray-900 dark:text-white">
            {user?.email}
          </p>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700">
          <Menu.Item>
            {({ active }) => (
              <button
                onClick={() => navigate('/settings')}
                className={`${
                  active ? 'bg-gray-100 dark:bg-gray-700' : ''
                } group flex w-full items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200`}
              >
                <Settings className="mr-3 h-5 w-5" />
                Settings
              </button>
            )}
          </Menu.Item>
          <Menu.Item>
            {({ active }) => (
              <button
                onClick={handleSignOut}
                className={`${
                  active ? 'bg-gray-100 dark:bg-gray-700' : ''
                } group flex w-full items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200`}
              >
                <LogOut className="mr-3 h-5 w-5" />
                Sign out
              </button>
            )}
          </Menu.Item>
        </div>
      </Menu.Items>
    </Menu>
  );
};

export default UserMenu;
