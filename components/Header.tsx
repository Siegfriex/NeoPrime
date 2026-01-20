import React from 'react';
import { Bell, Search } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="h-20 flex items-center justify-between px-8 fixed top-0 left-64 right-0 z-10 bg-[#F7F9FB]/80 backdrop-blur-md">
      <div className="flex items-center">
         <h2 className="text-gray-800 font-semibold text-lg breadcrumbs">
            <span className="text-gray-400 font-normal">Dashboard</span> <span className="mx-2 text-gray-300">/</span> Home
         </h2>
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="w-4 h-4 text-gray-400 group-focus-within:text-[#FC6401] transition-colors" />
            </div>
            <input
            type="text"
            placeholder="Search..."
            className="bg-white border border-gray-200 text-gray-700 text-sm rounded-xl focus:ring-[#FC6401] focus:border-[#FC6401] block w-64 pl-10 p-2.5 shadow-sm transition-all focus:w-80"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className="text-gray-400 text-xs border border-gray-200 rounded px-1.5 py-0.5">⌘K</span>
            </div>
        </div>

        <button className="relative p-2.5 bg-white text-gray-500 border border-gray-200 hover:border-[#FC6401] hover:text-[#FC6401] rounded-xl transition-all shadow-sm">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2.5 w-2 h-2 bg-[#FC6401] rounded-full border-2 border-white"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;