import React, { useState } from 'react';
import { Sparkles, ListChecks, Brain } from 'lucide-react';
import GeneratePage from './components/GeneratePage';
import ReviewPage from './components/ReviewPage';

function App() {
  const [activeTab, setActiveTab] = useState('generate');

  const navItems = [
    { id: 'generate', label: 'Generate', icon: Sparkles },
    { id: 'review', label: 'Tag & Review', icon: ListChecks },
  ];

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <Brain size={24} />
          <span>Question Gen</span>
        </div>
        <div className="nav-menu">
          {navItems.map((item) => (
            <div
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {activeTab === 'generate' && <GeneratePage onComplete={() => setActiveTab('review')} />}
        {activeTab === 'review' && <ReviewPage />}
      </main>
    </div>
  );
}

export default App;
