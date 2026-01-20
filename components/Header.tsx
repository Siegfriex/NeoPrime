import React from 'react';
import { Bell, Search, Calendar, ChevronDown, MapPin } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="h-20 flex items-center justify-between px-8 fixed top-0 left-64 right-0 z-10 bg-[#F7F9FB]/80 backdrop-blur-md border-b border-white/50">
      <div className="flex items-center gap-6">
         {/* Breadcrumbs */}
         <h2 className="text-gray-800 font-semibold text-lg breadcrumbs hidden md:block">
            <span className="text-gray-400 font-normal">대시보드</span> <span className="mx-2 text-gray-300">/</span> 홈
         </h2>

         {/* Global Context Bar - Divider */}
         <div className="h-6 w-px bg-gray-200 hidden md:block"></div>

         {/* Global Context Selectors */}
         <div className="hidden md:flex items-center space-x-2">
            <button className="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs font-bold text-gray-700 hover:border-[#FC6401] hover:text-[#FC6401] transition-all shadow-sm">
                <Calendar className="w-3.5 h-3.5" />
                <span>2026 시즌</span>
                <ChevronDown className="w-3 h-3 ml-1 opacity-50" />
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 bg-transparent border border-transparent rounded-lg text-xs font-medium text-gray-500 hover:bg-gray-100 transition-colors">
                <MapPin className="w-3.5 h-3.5" />
                <span>강남 본원</span>
                <ChevronDown className="w-3 h-3 ml-1 opacity-50" />
            </button>
         </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative group hidden sm:block">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="w-4 h-4 text-gray-400 group-focus-within:text-[#FC6401] transition-colors" />
            </div>
            <input
            type="text"
            placeholder="학생 이름, 통계 검색..."
            className="bg-white border border-gray-200 text-gray-700 text-sm rounded-xl focus:ring-[#FC6401] focus:border-[#FC6401] block w-64 pl-10 p-2.5 shadow-sm transition-all focus:w-80 placeholder:text-gray-400"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className="text-gray-400 text-[10px] font-bold border border-gray-100 rounded px-1.5 py-0.5 bg-gray-50">⌘K</span>
            </div>
        </div>

        <button className="relative p-2.5 bg-white text-gray-500 border border-gray-200 hover:border-[#FC6401] hover:text-[#FC6401] rounded-xl transition-all shadow-sm active:scale-95">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2.5 w-2 h-2 bg-[#FC6401] rounded-full border-2 border-white"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;