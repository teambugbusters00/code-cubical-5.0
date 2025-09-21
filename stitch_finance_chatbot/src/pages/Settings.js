import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { User, Moon, Sun, LogOut, Save, Shield, Bell, Palette } from 'lucide-react';

const Settings = () => {
  const { user, logout } = useAuth();
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem('notifications');
    return saved ? JSON.parse(saved) : true;
  });
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Apply dark mode to document
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // Here you would typically make an API call to update the profile
      // For now, we'll just simulate it
      await new Promise(resolve => setTimeout(resolve, 1000));

      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Failed to update profile. Please try again.');
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="flex h-screen flex-col">
      <Header title="Settings" />

      <main className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Profile Section */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <div className="flex items-center mb-6">
            <User className="w-6 h-6 text-primary mr-3" />
            <h2 className="text-xl font-bold text-black dark:text-white">Profile Settings</h2>
          </div>

          <form onSubmit={handleProfileUpdate} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-black dark:text-white mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={profileData.username}
                onChange={(e) => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                className="w-full px-4 py-3 rounded-lg bg-white/20 dark:bg-white/5 border border-white/20 dark:border-white/10 text-black dark:text-white placeholder-black/50 dark:placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter your username"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-black dark:text-white mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={profileData.email}
                onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-4 py-3 rounded-lg bg-white/20 dark:bg-white/5 border border-white/20 dark:border-white/10 text-black dark:text-white placeholder-black/50 dark:placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter your email"
              />
            </div>

            {message && (
              <div className={`p-3 rounded-lg ${
                message.includes('successfully')
                  ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                  : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
              }`}>
                <p className="text-sm">{message}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex items-center justify-center w-full bg-primary text-black font-semibold py-3 px-4 rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black mr-2"></div>
                  Updating...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5 mr-2" />
                  Update Profile
                </>
              )}
            </button>
          </form>
        </div>

        {/* Appearance Section */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <div className="flex items-center mb-6">
            <Palette className="w-6 h-6 text-primary mr-3" />
            <h2 className="text-xl font-bold text-black dark:text-white">Appearance</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 dark:bg-white/5">
              <div className="flex items-center">
                {darkMode ? (
                  <Moon className="w-5 h-5 text-primary mr-3" />
                ) : (
                  <Sun className="w-5 h-5 text-primary mr-3" />
                )}
                <div>
                  <p className="font-medium text-black dark:text-white">Dark Mode</p>
                  <p className="text-sm text-black/60 dark:text-white/60">
                    Toggle between light and dark themes
                  </p>
                </div>
              </div>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  darkMode ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    darkMode ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Notifications Section */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <div className="flex items-center mb-6">
            <Bell className="w-6 h-6 text-primary mr-3" />
            <h2 className="text-xl font-bold text-black dark:text-white">Notifications</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 dark:bg-white/5">
              <div className="flex items-center">
                <Bell className="w-5 h-5 text-primary mr-3" />
                <div>
                  <p className="font-medium text-black dark:text-white">Push Notifications</p>
                  <p className="text-sm text-black/60 dark:text-white/60">
                    Receive notifications for market updates
                  </p>
                </div>
              </div>
              <button
                onClick={() => setNotifications(!notifications)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Security Section */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <div className="flex items-center mb-6">
            <Shield className="w-6 h-6 text-primary mr-3" />
            <h2 className="text-xl font-bold text-black dark:text-white">Security</h2>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-white/5 dark:bg-white/5">
              <p className="font-medium text-black dark:text-white mb-2">Account Security</p>
              <p className="text-sm text-black/60 dark:text-white/60 mb-3">
                Your account is secured with JWT authentication and encrypted data transmission.
              </p>
              <button className="text-primary hover:text-primary/80 text-sm font-medium">
                Change Password
              </button>
            </div>
          </div>
        </div>

        {/* Logout Section */}
        <div className="bg-red-100/10 dark:bg-red-900/10 rounded-xl p-6 border border-red-400/20 dark:border-red-800/20">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-red-700 dark:text-red-400">Account Actions</h2>
              <p className="text-sm text-red-600 dark:text-red-500 mt-1">
                Sign out of your account
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </main>

      <Navigation />
    </div>
  );
};

export default Settings;