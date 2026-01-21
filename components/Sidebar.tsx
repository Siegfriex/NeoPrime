import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { LayoutDashboard, Users, FileEdit, BarChart2, Settings, LogOut, Hexagon, Calculator } from 'lucide-react';

const Sidebar: React.FC = () => {
  // Reordered navigation items for better flow
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: '대시보드' },
    { to: '/students', icon: Users, label: '학생 관리' },
    { to: '/simulation', icon: Calculator, label: '합격 시뮬레이터' }, // Moved up
    { to: '/evaluations/new', icon: FileEdit, label: '평가 입력' },
    { to: '/analytics', icon: BarChart2, label: '데이터 분석' },
  ];

  return (
    <div className="w-[280px] bg-white text-gray-600 flex flex-col h-screen fixed left-0 top-0 z-20 border-r border-gray-200 transition-all duration-300">
      <div className="h-[60px] flex items-center px-6 border-b border-gray-100">
        <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-[#FC6401] rounded-lg flex items-center justify-center shadow-lg shadow-[#FC6401]/20">
                <Hexagon className="text-white w-5 h-5 fill-white/20" />
            </div>
            <span className="text-xl font-bold tracking-tight text-gray-900">NeoPrime</span>
        </div>
      </div>

      <div className="px-6 py-4">
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Workspace</p>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-[#FC6401] text-white shadow-md shadow-[#FC6401]/25 font-bold'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-[#FC6401] font-medium'
              }`
            }
          >
            <item.icon className={`w-5 h-5 transition-colors`} />
            <span className="text-sm">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto border-t border-gray-100">
        <div className="flex items-center gap-3 mb-4 px-2">
            <div className="w-9 h-9 rounded-full bg-gray-200 overflow-hidden border border-gray-200">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" />
            </div>
            <div>
                <p className="text-sm font-bold text-gray-900">이은일</p>
                <p className="text-[10px] text-gray-500 font-medium">Elite Director</p>
            </div>
        </div>

        <Link to="/settings" className="flex items-center space-x-3 px-4 py-2.5 w-full text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-lg transition-colors text-sm font-medium">
          <Settings className="w-4 h-4" />
          <span>설정</span>
        </Link>
        <Link to="/auth/login" className="flex items-center space-x-3 px-4 py-2.5 w-full text-gray-500 hover:bg-rose-50 hover:text-rose-500 rounded-lg transition-colors mt-1 text-sm font-medium">
          <LogOut className="w-4 h-4" />
          <span>로그아웃</span>
        </Link>
      </div>
    </div>
  );
};

export default Sidebar;