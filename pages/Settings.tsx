import React, { useState } from 'react';
import { User, Building, Users, Database, Save, Bell, Shield } from 'lucide-react';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('account');

  const tabs = [
    { id: 'account', label: '내 계정', icon: User },
    { id: 'academy', label: '학원 정보', icon: Building },
    { id: 'instructors', label: '강사 관리', icon: Users },
    { id: 'data', label: '데이터 관리', icon: Database },
  ];

  return (
    <div className="max-w-5xl mx-auto pb-12 animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">설정</h1>
        <p className="text-gray-500 mt-2">플랫폼 환경설정 및 계정 관리</p>
      </div>

      <div className="grid grid-cols-12 gap-8">
        {/* Sidebar Tabs */}
        <div className="col-span-12 md:col-span-3">
          <nav className="space-y-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl font-bold text-sm transition-all text-left ${
                  activeTab === tab.id 
                    ? 'bg-white text-[#FC6401] shadow-sm border border-gray-100' 
                    : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content Area */}
        <div className="col-span-12 md:col-span-9 bg-white rounded-2xl border border-gray-200 shadow-sm p-8 min-h-[500px]">
          
          {activeTab === 'account' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h2 className="text-xl font-bold text-gray-900 pb-4 border-b border-gray-100">내 계정 설정</h2>
              
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 rounded-full bg-gray-200 overflow-hidden border-4 border-gray-50">
                   <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Profile" />
                </div>
                <div>
                  <button className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-50">사진 변경</button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                   <label className="block text-xs font-bold text-gray-500 uppercase mb-2">이름</label>
                   <input type="text" defaultValue="이은일" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl font-medium outline-none focus:border-[#FC6401]" />
                </div>
                <div>
                   <label className="block text-xs font-bold text-gray-500 uppercase mb-2">직책</label>
                   <input type="text" defaultValue="원장" disabled className="w-full p-3 bg-gray-100 border border-gray-200 rounded-xl font-medium text-gray-500" />
                </div>
                <div>
                   <label className="block text-xs font-bold text-gray-500 uppercase mb-2">이메일</label>
                   <input type="email" defaultValue="director@neoprime.com" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl font-medium outline-none focus:border-[#FC6401]" />
                </div>
              </div>

              <div className="pt-6 border-t border-gray-100">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2"><Bell className="w-4 h-4"/> 알림 설정</h3>
                <div className="space-y-3">
                   <label className="flex items-center justify-between p-3 border border-gray-200 rounded-xl">
                      <span className="text-sm font-medium text-gray-700">학생 평가 완료 알림</span>
                      <input type="checkbox" defaultChecked className="w-5 h-5 text-[#FC6401] rounded focus:ring-[#FC6401]" />
                   </label>
                   <label className="flex items-center justify-between p-3 border border-gray-200 rounded-xl">
                      <span className="text-sm font-medium text-gray-700">주간 리포트 생성 알림</span>
                      <input type="checkbox" defaultChecked className="w-5 h-5 text-[#FC6401] rounded focus:ring-[#FC6401]" />
                   </label>
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <button className="px-6 py-3 bg-[#FC6401] text-white rounded-xl font-bold shadow-lg shadow-[#FC6401]/20 flex items-center gap-2 hover:bg-[#e55a00] transition-colors">
                   <Save className="w-4 h-4" /> 저장하기
                </button>
              </div>
            </div>
          )}

          {activeTab === 'academy' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h2 className="text-xl font-bold text-gray-900 pb-4 border-b border-gray-100">학원 정보 관리</h2>
                <div className="p-6 bg-gray-50 rounded-xl text-center text-gray-500">
                   <Building className="w-10 h-10 mx-auto mb-3 opacity-20" />
                   <p>학원 정보 수정 기능은 준비 중입니다.</p>
                </div>
             </div>
          )}
          
          {activeTab === 'instructors' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h2 className="text-xl font-bold text-gray-900 pb-4 border-b border-gray-100">강사 계정 관리</h2>
                <div className="p-6 bg-gray-50 rounded-xl text-center text-gray-500">
                   <Users className="w-10 h-10 mx-auto mb-3 opacity-20" />
                   <p>강사 초대 및 권한 관리 기능은 준비 중입니다.</p>
                </div>
             </div>
          )}

          {activeTab === 'data' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h2 className="text-xl font-bold text-gray-900 pb-4 border-b border-gray-100">데이터 관리</h2>
                <div className="space-y-4">
                  <div className="p-4 border border-gray-200 rounded-xl flex justify-between items-center">
                    <div>
                      <h4 className="font-bold text-gray-900">데이터 백업</h4>
                      <p className="text-sm text-gray-500">전체 학생 및 평가 데이터를 CSV로 내보냅니다.</p>
                    </div>
                    <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-bold hover:bg-gray-50">CSV 다운로드</button>
                  </div>
                  <div className="p-4 border border-rose-100 bg-rose-50/50 rounded-xl flex justify-between items-center">
                    <div>
                      <h4 className="font-bold text-rose-600 flex items-center gap-2"><Shield className="w-4 h-4"/> 데이터 초기화</h4>
                      <p className="text-sm text-rose-400">이번 시즌 데이터를 모두 삭제합니다. (복구 불가)</p>
                    </div>
                    <button className="px-4 py-2 bg-white border border-rose-200 text-rose-600 rounded-lg text-sm font-bold hover:bg-rose-50">초기화</button>
                  </div>
                </div>
             </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Settings;