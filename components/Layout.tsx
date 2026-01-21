import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ChatBot from './ChatBot';

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F7F9FB]">
      <Sidebar />
      <Header />
      <main className="ml-64 pt-20 min-h-screen">
        {/* Changed max-w-7xl to max-w-[1600px] and px-8 for wider layout */}
        <div className="p-8 max-w-[1600px] mx-auto w-full">
          <Outlet />
        </div>
      </main>
      <ChatBot />
    </div>
  );
};

export default Layout;