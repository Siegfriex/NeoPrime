
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ChatBot from './ChatBot';

const Layout: React.FC = () => {
  return (
    <div className="h-screen w-screen bg-[#F9FAFB] flex font-sans selection:bg-[#FC6401] selection:text-white overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 pl-[280px] transition-all duration-300 h-full">
        <Header />
        {/* Main Content Area: Fixed height, allowing children to decide scrolling behavior */}
        <main className="flex-1 pt-[60px] h-full relative overflow-hidden flex flex-col">
          <Outlet />
        </main>
      </div>
      <ChatBot />
    </div>
  );
};

export default Layout;
