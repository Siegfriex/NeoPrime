import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Hexagon, ArrowRight, User, Mail, Lock, Building } from 'lucide-react';

const Signup: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: '', email: '', password: '', academy: '' });

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    alert("가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다.");
    navigate('/auth/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F9FB] p-6">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden animate-in fade-in duration-500">
        <div className="p-8 md:p-10">
          <div className="flex justify-center mb-6">
             <div className="w-10 h-10 bg-gray-900 rounded-xl flex items-center justify-center">
               <Hexagon className="text-white w-6 h-6 fill-white/20" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">파트너 가입 신청</h1>
          <p className="text-center text-gray-500 mb-8">NeoPrime의 Elite 파트너가 되어보세요.</p>

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="relative">
              <User className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input type="text" placeholder="이름 (실명)" required className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-medium" 
                value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
            </div>
            
            <div className="relative">
              <Building className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input type="text" placeholder="학원명" required className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-medium" 
                value={formData.academy} onChange={e => setFormData({...formData, academy: e.target.value})} />
            </div>

            <div className="relative">
              <Mail className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input type="email" placeholder="이메일" required className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-medium" 
                value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
            </div>

            <div className="relative">
              <Lock className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input type="password" placeholder="비밀번호" required className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-medium" 
                value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} />
            </div>

            <button type="submit" className="w-full mt-4 py-4 bg-gray-900 text-white rounded-xl hover:bg-gray-800 font-bold text-lg shadow-lg shadow-gray-900/20 flex items-center justify-center gap-2 transition-all">
              가입 신청하기
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>
        </div>
        <div className="px-8 py-6 bg-gray-50 border-t border-gray-100 text-center">
          <p className="text-sm text-gray-600 font-medium">
            이미 계정이 있으신가요? <Link to="/auth/login" className="text-[#FC6401] font-bold hover:underline">로그인</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;