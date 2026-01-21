
import React from 'react';
import { Mail, Phone, MapPin, Calendar, Award, Briefcase } from 'lucide-react';

const Profile: React.FC = () => {
  return (
    <div className="h-full overflow-y-auto custom-scrollbar">
      <div className="max-w-4xl mx-auto p-8 pb-12 animate-in fade-in duration-500">
        
        <div className="bg-white rounded-3xl border border-gray-200 shadow-sm overflow-hidden mb-8">
            <div className="h-48 bg-gradient-to-r from-gray-900 to-gray-800 relative">
              <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-black/50 to-transparent"></div>
            </div>
            <div className="px-8 pb-8 relative">
              <div className="flex justify-between items-end -mt-12 mb-6">
                  <div className="w-32 h-32 rounded-3xl bg-white p-1.5 shadow-xl">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Profile" className="w-full h-full rounded-2xl bg-gray-100" />
                  </div>
                  <button className="mb-2 px-6 py-2.5 bg-[#FC6401] text-white font-bold rounded-xl shadow-lg shadow-[#FC6401]/20 hover:bg-[#e55a00] transition-colors">
                    프로필 편집
                  </button>
              </div>
              
              <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-1">이은일 원장</h1>
                  <p className="text-gray-500 font-medium mb-6">NeoPrime 강남 본원 • 총괄 디렉터</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-gray-100">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-gray-600">
                          <Mail className="w-5 h-5 text-gray-400" />
                          <span>director@neoprime.com</span>
                        </div>
                        <div className="flex items-center gap-3 text-gray-600">
                          <Phone className="w-5 h-5 text-gray-400" />
                          <span>010-1234-5678</span>
                        </div>
                        <div className="flex items-center gap-3 text-gray-600">
                          <MapPin className="w-5 h-5 text-gray-400" />
                          <span>서울시 강남구 테헤란로 123</span>
                        </div>
                    </div>
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-gray-600">
                          <Briefcase className="w-5 h-5 text-gray-400" />
                          <span>Elite Academy Partner (Tier 1)</span>
                        </div>
                        <div className="flex items-center gap-3 text-gray-600">
                          <Calendar className="w-5 h-5 text-gray-400" />
                          <span>가입일: 2024.01.15</span>
                        </div>
                        <div className="flex items-center gap-3 text-gray-600">
                          <Award className="w-5 h-5 text-gray-400" />
                          <span>서울대 합격 배출: 15명</span>
                        </div>
                    </div>
                  </div>
              </div>
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
              <h3 className="font-bold text-gray-900 mb-4">최근 활동 로그</h3>
              <ul className="space-y-4">
                  <li className="flex gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5"></div>
                    <div>
                        <p className="text-gray-900 font-medium">김지민 학생 평가 입력</p>
                        <p className="text-gray-400 text-xs">2시간 전</p>
                    </div>
                  </li>
                  <li className="flex gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-[#FC6401] mt-1.5"></div>
                    <div>
                        <p className="text-gray-900 font-medium">주간 리포트 생성 (홍익대 코호트)</p>
                        <p className="text-gray-400 text-xs">어제</p>
                    </div>
                  </li>
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
              <h3 className="font-bold text-gray-900 mb-4">구독 정보</h3>
              <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 mb-4">
                  <p className="text-xs font-bold text-gray-500 uppercase mb-1">현재 플랜</p>
                  <div className="flex justify-between items-center">
                    <p className="text-lg font-bold text-gray-900">Elite Partner Pro</p>
                    <span className="px-2 py-1 bg-[#FC6401] text-white text-xs font-bold rounded">Active</span>
                  </div>
              </div>
              <p className="text-xs text-gray-500">다음 결제일: 2026. 03. 01</p>
            </div>
        </div>

      </div>
    </div>
  );
};

export default Profile;
