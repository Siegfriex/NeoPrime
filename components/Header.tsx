import React from 'react';
import { Bell, Search, Calendar, ChevronDown, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="h-[60px] flex items-center justify-between px-6 fixed top-0 left-[280px] right-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="flex items-center gap-6">
         {/* Breadcrumbs */}
         <h2 className="text-gray-800 font-bold text-sm breadcrumbs hidden md:flex items-center gap-2">
            <span className="text-gray-400 font-medium">Console</span> 
            <span className="text-gray-300">/</span> 
            <span>Dashboard</span>
         </h2>

         {/* Global Context Bar - Divider */}
         <div className="h-4 w-px bg-gray-200 hidden md:block"></div>

         {/* Global Context Selectors */}
         <div className="hidden md:flex items-center space-x-2">
            <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-[11px] font-bold text-gray-700 hover:border-[#FC6401] hover:text-[#FC6401] transition-all">
                <Calendar className="w-3 h-3" />
                <span>2026 시즌</span>
                <ChevronDown className="w-3 h-3 ml-1 opacity-50" />
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 bg-transparent border border-transparent rounded-lg text-[11px] font-bold text-gray-500 hover:bg-gray-100 transition-colors">
                <MapPin className="w-3 h-3" />
                <span>강남 본원</span>
                <ChevronDown className="w-3 h-3 ml-1 opacity-50" />
            </button>
         </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative group hidden sm:block">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="w-3.5 h-3.5 text-gray-400 group-focus-within:text-[#FC6401] transition-colors" />
            </div>
            <input
            type="text"
            placeholder="Search..."
            className="bg-gray-50 border border-gray-200 text-gray-700 text-xs rounded-lg focus:ring-[#FC6401] focus:border-[#FC6401] block w-56 pl-9 p-2 transition-all focus:w-64 placeholder:text-gray-400 font-medium"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className="text-gray-400 text-[9px] font-bold border border-gray-200 rounded px-1.5 bg-white">/</span>
            </div>
        </div>

        <Link to="/profile" className="relative p-2 text-gray-400 hover:text-[#FC6401] transition-all active:scale-95">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 bg-[#FC6401] rounded-full ring-2 ring-white"></span>
        </Link>
      </div>
    </header>
  );
};

export default Header;