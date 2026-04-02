import { motion } from 'framer-motion';
import Sidebar from './Sidebar';

export default function MainLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/30">
      <Sidebar />

      {/* Main Content Area */}
      <main className="flex-1 lg:ml-[280px] transition-all duration-300">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
          className="p-4 lg:p-8 min-h-screen"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
