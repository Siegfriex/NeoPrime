import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Hexagon, ArrowRight, Lock, Mail } from 'lucide-react';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Mock Auth Logic
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F9FB] p-6">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
        <div className="p-8 md:p-10">
          <div className="flex justify-center mb-8">
            <div className="w-12 h-12 bg-[#FC6401] rounded-2xl flex items-center justify-center shadow-lg shadow-[#FC6401]/20">
               <Hexagon className="text-white w-7 h-7 fill-white/20" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">NeoPrime 로그인</h1>
          <p className="text-center text-gray-500 mb-8">강사 및 원장님 전용 대시보드</p>

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2 pl-1">이메일</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  required
                  className="w-full pl-11 pr-4 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] focus:border-[#FC6401] outline-none transition-all font-medium"
                  placeholder="name@neoprime.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2 pl-1">비밀번호</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="password"
                  required
                  className="w-full pl-11 pr-4 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] focus:border-[#FC6401] outline-none transition-all font-medium"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center cursor-pointer">
                <input type="checkbox" className="w-4 h-4 text-[#FC6401] rounded border-gray-300 focus:ring-[#FC6401]" />
                <span className="ml-2 text-gray-500 font-medium">로그인 유지</span>
              </label>
              <a href="#" className="text-[#FC6401] font-bold hover:underline">비밀번호 찾기</a>
            </div>

            <button
              type="submit"
              className="w-full py-4 bg-[#FC6401] text-white rounded-xl hover:bg-[#e55a00] font-bold text-lg shadow-lg shadow-[#FC6401]/30 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5"
            >
              로그인
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>
        </div>
        <div className="px-8 py-6 bg-gray-50 border-t border-gray-100 text-center">
          <p className="text-sm text-gray-600 font-medium">
            아직 계정이 없으신가요? <Link to="/auth/signup" className="text-[#FC6401] font-bold hover:underline">가입 신청</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;