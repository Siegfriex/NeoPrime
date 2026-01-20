import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, FileEdit, BarChart2, Settings, LogOut, Hexagon } from 'lucide-react';

const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: '대시보드' },
    { to: '/students', icon: Users, label: '학생 관리' },
    { to: '/evaluations/new', icon: FileEdit, label: '평가 입력' },
    { to: '/analytics', icon: BarChart2, label: '데이터 분석' },
  ];

  return (
    <div className="w-64 bg-white text-gray-600 flex flex-col h-screen fixed left-0 top-0 z-20 border-r border-gray-100 transition-all duration-300">
      <div className="p-6 flex items-center space-x-3">
        <div className="w-8 h-8 bg-[#FC6401] rounded-lg flex items-center justify-center shadow-lg shadow-[#FC6401]/20">
            <Hexagon className="text-white w-5 h-5 fill-white/20" />
        </div>
        <span className="text-xl font-bold tracking-tight text-gray-900">NeoPrime</span>
      </div>

      <div className="px-6 py-2">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">업무</p>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-[#FC6401] text-white shadow-md shadow-[#FC6401]/25'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-[#FC6401]'
              }`
            }
          >
            <item.icon className={`w-5 h-5 transition-colors`} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <div className="bg-gray-50 rounded-xl p-4 mb-4 border border-gray-100">
            <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-full bg-gray-200 overflow-hidden">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" />
                </div>
                <div>
                    <p className="text-sm font-bold text-gray-900">이은일</p>
                    <p className="text-xs text-gray-500">원장</p>
                </div>
            </div>
            <button className="text-xs text-[#FC6401] font-medium hover:underline">프로필 보기</button>
        </div>

        <button className="flex items-center space-x-3 px-4 py-3 w-full text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-xl transition-colors">
          <Settings className="w-5 h-5" />
          <span>설정</span>
        </button>
        <button className="flex items-center space-x-3 px-4 py-3 w-full text-gray-500 hover:bg-rose-50 hover:text-rose-500 rounded-xl transition-colors mt-1">
          <LogOut className="w-5 h-5" />
          <span>로그아웃</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;