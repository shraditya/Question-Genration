import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Upload,
  Sparkles,
  Tags,
  Copy,
  Download,
  Menu,
  X,
  ChevronLeft,
  Settings,
  HelpCircle
} from 'lucide-react';

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/', color: 'from-blue-500 to-cyan-500' },
    { icon: Upload, label: 'Upload Documents', path: '/upload', color: 'from-indigo-500 to-purple-500' },
    { icon: Sparkles, label: 'Generate MCQs', path: '/generate', color: 'from-purple-500 to-pink-500' },
    { icon: Tags, label: 'Smart Tagging', path: '/tag', color: 'from-emerald-500 to-green-500' },
    { icon: Copy, label: 'Duplicate Detection', path: '/similarity', color: 'from-orange-500 to-red-500' },
    { icon: Download, label: 'Export Data', path: '/export', color: 'from-pink-500 to-rose-500' },
  ];

  const bottomItems = [
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: HelpCircle, label: 'Help', path: '/help' },
  ];

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-xl bg-white shadow-lg hover:shadow-xl transition-all"
      >
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setMobileOpen(false)}
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          width: collapsed ? '80px' : '280px',
          x: mobileOpen ? 0 : (window.innerWidth < 1024 ? -280 : 0)
        }}
        className={`
          fixed left-0 top-0 h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900
          border-r border-slate-700/50 z-40 flex flex-col
          lg:translate-x-0
        `}
      >
        {/* Logo */}
        <div className="p-6 border-b border-slate-700/50">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl shadow-lg group-hover:shadow-blue-500/50 transition-all">
              <Sparkles className="text-white" size={24} />
            </div>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-1"
              >
                <h1 className="text-white font-bold text-lg">RAG MCQ</h1>
                <p className="text-slate-400 text-xs">AI Generator</p>
              </motion.div>
            )}
          </Link>
        </div>

        {/* Collapse Button (Desktop only) */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:block absolute -right-3 top-24 bg-white rounded-full p-1 shadow-lg hover:shadow-xl transition-all z-50"
        >
          <motion.div
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronLeft size={16} className="text-slate-600" />
          </motion.div>
        </button>

        {/* Main Navigation */}
        <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className="block group"
              >
                <motion.div
                  whileHover={{ x: 4 }}
                  className={`
                    relative flex items-center space-x-3 px-4 py-3 rounded-xl
                    transition-all duration-200
                    ${isActive
                      ? 'bg-gradient-to-r ' + item.color + ' text-white shadow-lg'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                    }
                  `}
                >
                  <Icon size={20} className={isActive ? 'animate-pulse' : ''} />
                  {!collapsed && (
                    <span className="font-medium text-sm">{item.label}</span>
                  )}
                  {isActive && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="absolute left-0 w-1 h-8 bg-white rounded-r-full"
                    />
                  )}
                </motion.div>
              </Link>
            );
          })}
        </nav>

        {/* Bottom Items */}
        <div className="border-t border-slate-700/50 p-3 space-y-1">
          {bottomItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className="block group"
              >
                <motion.div
                  whileHover={{ x: 4 }}
                  className="flex items-center space-x-3 px-4 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
                >
                  <Icon size={20} />
                  {!collapsed && <span className="text-sm">{item.label}</span>}
                </motion.div>
              </Link>
            );
          })}
        </div>

        {/* User Profile (collapsed) */}
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-4 border-t border-slate-700/50"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                U
              </div>
              <div className="flex-1">
                <p className="text-white text-sm font-medium">User</p>
                <p className="text-slate-400 text-xs">Admin</p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.aside>
    </>
  );
}
