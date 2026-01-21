import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, GraduationCap, Target, Palette, Users, Link as LinkIcon, 
  Save, ChevronLeft, Check 
} from 'lucide-react';
import { addStudent } from '../services/storageService';
import { Student } from '../types';

const StudentAdd: React.FC = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('basic');

  // --- Form State ---
  const [formData, setFormData] = useState({
    // 2.1 Basic Info
    name: '',
    englishName: '',
    birthDate: '',
    grade: '3학년',
    school: '',
    majorTrack: '시각디자인',
    contact: '',
    email: '',

    // 2.2 Admission Strategy
    targetGa: { univ: '', major: '' },
    targetNa: { univ: '', major: '' },
    targetDa: { univ: '', major: '' },
    strategyTags: ['나군 메인'], // Default
    strategyNote: '',

    // 2.3 Academic Profile
    gpa: '',
    scores: {
      korean: { score: '', grade: '' },
      math: { score: '', grade: '' },
      english: { grade: '' },
      social1: { subject: '', score: '' },
      social2: { subject: '', score: '' },
    },
    mockSummary: '',
    academicNote: '',

    // 2.4 Practical Profile
    practicalLevel: 'B+',
    mainInstructor: '',
    initialEval: {
      composition: 5,
      tone: 5,
      idea: 5,
      completeness: 5
    },
    portfolioStatus: '진행 중',
    strengthNote: '',
    weaknessNote: '',

    // 2.5 Guardian Info
    guardianName: '',
    guardianRelation: '모',
    guardianContact: '',
    contactChannel: { call: true, sms: true, kakao: false, email: false },
    consultationNote: '',

    // 2.6 Account
    accountType: 'invite' // 'link' or 'invite'
  });

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNestedChange = (parent: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...(prev as any)[parent],
        [field]: value
      }
    }));
  };

  const handleScoreChange = (subject: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      scores: {
        ...prev.scores,
        [subject]: {
          ...(prev.scores as any)[subject],
          [field]: value
        }
      }
    }));
  };

  const toggleStrategyTag = (tag: string) => {
    setFormData(prev => {
      const tags = prev.strategyTags.includes(tag)
        ? prev.strategyTags.filter(t => t !== tag)
        : [...prev.strategyTags, tag];
      return { ...prev, strategyTags: tags };
    });
  };

  const handleSubmit = () => {
    // Validation Logic
    if (!formData.name || !formData.school) {
      alert("필수 정보(이름, 학교)를 입력해주세요.");
      return;
    }
    
    // Construct Student Object from FormData
    // Note: In a real app, we would map all fields properly.
    // For this prototype, we'll map essential fields and use defaults/randoms for others to match the Type.
    const newStudent: Student = {
        id: '', // will be generated in service
        name: formData.name,
        grade: formData.grade as any,
        school: formData.school,
        targetUniversity: formData.targetNa.univ || '미정',
        major: formData.majorTrack,
        currentLevel: formData.practicalLevel as any,
        instructorId: 'i1', // Default
        avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${formData.name}`,
        artworks: [],
        academicScores: {
            korean: { standardScore: Number(formData.scores.korean.score), grade: Number(formData.scores.korean.grade) },
            english: { grade: Number(formData.scores.english.grade) },
            math: { standardScore: Number(formData.scores.math.score), grade: Number(formData.scores.math.grade) },
            social1: { subjectName: formData.scores.social1.subject, standardScore: Number(formData.scores.social1.score) },
            social2: { subjectName: formData.scores.social2.subject, standardScore: Number(formData.scores.social2.score) }
        },
        targetUnivAvgScores: {
             korean: { standardScore: 130 },
             english: { grade: 1 },
             math: { standardScore: 120 },
             social1: { standardScore: 60 },
             social2: { standardScore: 60 }
        },
        admissionHistory: [],
        similarCases: []
    };

    addStudent(newStudent);
    
    alert(`학생 "${formData.name}" 등록이 완료되었습니다.\n대시보드에 반영됩니다.`);
    navigate('/students');
  };

  // --- UI Components ---
  const SectionHeader = ({ icon: Icon, title, id }: any) => (
    <div className="flex items-center gap-2 mb-6 pb-2 border-b border-gray-100">
      <div className="p-2 bg-[#FFF0E6] rounded-lg text-[#FC6401]">
        <Icon className="w-5 h-5" />
      </div>
      <h3 className="text-lg font-bold text-gray-900">{title}</h3>
    </div>
  );

  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    setActiveSection(id);
    const element = document.getElementById(id);
    if (element) {
      const yOffset = -120; // Adjust for sticky header
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({top: y, behavior: 'smooth'});
    }
  };

  return (
    <div className="max-w-5xl mx-auto pb-20 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="sticky top-20 z-10 bg-[#F7F9FB]/95 backdrop-blur py-4 mb-6 flex justify-between items-center border-b border-gray-200/50">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-500">
            <ChevronLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">학생 등록</h1>
            <p className="text-sm text-gray-500">새로운 학생의 입시 전략 및 프로필을 설정합니다.</p>
          </div>
        </div>
        <div className="flex gap-3">
          <button onClick={() => navigate(-1)} className="px-5 py-2.5 text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 font-bold text-sm transition-colors">
            취소
          </button>
          <button onClick={handleSubmit} className="px-6 py-2.5 bg-[#FC6401] text-white rounded-xl hover:bg-[#e55a00] font-bold text-sm shadow-lg shadow-[#FC6401]/20 flex items-center gap-2 transition-all">
            <Save className="w-4 h-4" />
            등록 완료
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8">
        
        {/* Navigation Rail (Optional for long forms) */}
        <div className="hidden lg:block col-span-3">
          <div className="sticky top-40 space-y-1">
            {[
              { id: 'basic', label: '기본 정보', icon: User },
              { id: 'strategy', label: '입시 전략', icon: Target },
              { id: 'academic', label: '학업 프로파일', icon: GraduationCap },
              { id: 'practical', label: '실기 프로파일', icon: Palette },
              { id: 'guardian', label: '보호자 정보', icon: Users },
              { id: 'account', label: '계정 연동', icon: LinkIcon },
            ].map((item) => (
              <a 
                key={item.id}
                href={`#${item.id}`}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                  activeSection === item.id 
                    ? 'bg-white text-[#FC6401] shadow-sm border border-gray-100' 
                    : 'text-gray-500 hover:bg-gray-100/50 hover:text-gray-900'
                }`}
                onClick={(e) => scrollToSection(e, item.id)}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </a>
            ))}
          </div>
        </div>

        {/* Main Form Area */}
        <div className="col-span-12 lg:col-span-9 space-y-8">
          
          {/* 2.1 Basic Info */}
          <div id="basic" className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm scroll-mt-32">
            <SectionHeader icon={User} title="기본 정보" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">이름 *</label>
                <input type="text" placeholder="예) 김지민" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-bold text-gray-900" 
                  value={formData.name} onChange={(e) => handleInputChange('name', e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">영문 이름 (선택)</label>
                <input type="text" placeholder="예) Jimin Kim" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none" 
                   value={formData.englishName} onChange={(e) => handleInputChange('englishName', e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">생년월일 *</label>
                <input type="date" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none text-gray-700" 
                   value={formData.birthDate} onChange={(e) => handleInputChange('birthDate', e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">학년 *</label>
                <select className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-bold text-gray-900"
                   value={formData.grade} onChange={(e) => handleInputChange('grade', e.target.value)}>
                  <option value="고1">고1</option>
                  <option value="고2">고2</option>
                  <option value="고3">고3</option>
                  <option value="재수">재수/N수</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">현재 학교 *</label>
                <input type="text" placeholder="예) 세화고 / 검정고시" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none" 
                   value={formData.school} onChange={(e) => handleInputChange('school', e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">전공 트랙 *</label>
                <select className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none"
                   value={formData.majorTrack} onChange={(e) => handleInputChange('majorTrack', e.target.value)}>
                  <option value="시각디자인">시각디자인</option>
                  <option value="산업디자인">산업디자인</option>
                  <option value="공예">공예</option>
                  <option value="서양화">서양화</option>
                  <option value="동양화">동양화</option>
                  <option value="조소">조소</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">연락처 (학생)</label>
                <input type="tel" placeholder="010-0000-0000" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none" 
                   value={formData.contact} onChange={(e) => handleInputChange('contact', e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">이메일 (학생)</label>
                <input type="email" placeholder="student@example.com" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none" 
                   value={formData.email} onChange={(e) => handleInputChange('email', e.target.value)} />
              </div>
            </div>
          </div>

          {/* 2.2 Admission Strategy */}
          <div id="strategy" className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm scroll-mt-32">
            <SectionHeader icon={Target} title="입시 전략 (가/나/다군)" />
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {[
                { label: '가군 목표', state: formData.targetGa, key: 'targetGa', placeholder: '예) 서울대' },
                { label: '나군 목표', state: formData.targetNa, key: 'targetNa', placeholder: '예) 홍익대' },
                { label: '다군 목표', state: formData.targetDa, key: 'targetDa', placeholder: '예) 이화여대' },
              ].map((group) => (
                <div key={group.key} className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-3">{group.label}</label>
                  <input type="text" placeholder="대학명" className="w-full p-2 mb-2 bg-white border border-gray-200 rounded-lg text-sm font-bold focus:border-[#FC6401] outline-none"
                    value={group.state.univ} onChange={(e) => handleNestedChange(group.key, 'univ', e.target.value)} />
                  <input type="text" placeholder="전공" className="w-full p-2 bg-white border border-gray-200 rounded-lg text-sm focus:border-[#FC6401] outline-none"
                    value={group.state.major} onChange={(e) => handleNestedChange(group.key, 'major', e.target.value)} />
                </div>
              ))}
            </div>

            <div className="mb-6">
              <label className="block text-xs font-bold text-gray-500 uppercase mb-3">전략 라인 태그</label>
              <div className="flex flex-wrap gap-2">
                {['가군 도전', '나군 메인', '다군 안정', '수시 집중', '정시 올인', '실기 우수'].map(tag => (
                  <button 
                    key={tag}
                    onClick={() => toggleStrategyTag(tag)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-bold border transition-all ${
                      formData.strategyTags.includes(tag) 
                        ? 'bg-[#FFF0E6] text-[#FC6401] border-[#FC6401]' 
                        : 'bg-white text-gray-500 border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2">전략 비고</label>
              <textarea placeholder="예) 가군은 실기 상향 지원, 나군은 안정적으로 가져가는 전략..." 
                className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none resize-none h-24"
                value={formData.strategyNote} onChange={(e) => handleInputChange('strategyNote', e.target.value)} />
            </div>
          </div>

          {/* 2.3 Academic Profile */}
          <div id="academic" className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm scroll-mt-32">
            <SectionHeader icon={GraduationCap} title="학업 프로파일" />
            
            <div className="mb-6">
               <label className="block text-xs font-bold text-gray-500 uppercase mb-2">내신 등급 (전체 평균)</label>
               <input type="text" placeholder="예) 2.4 등급" className="w-full md:w-1/3 p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none" 
                  value={formData.gpa} onChange={(e) => handleInputChange('gpa', e.target.value)} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
               <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-500">국어</label>
                  <input type="text" placeholder="표점" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.korean.score} onChange={(e) => handleScoreChange('korean', 'score', e.target.value)} />
                  <input type="text" placeholder="등급" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.korean.grade} onChange={(e) => handleScoreChange('korean', 'grade', e.target.value)} />
               </div>
               <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-500">수학</label>
                  <input type="text" placeholder="표점" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.math.score} onChange={(e) => handleScoreChange('math', 'score', e.target.value)} />
                  <input type="text" placeholder="등급" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.math.grade} onChange={(e) => handleScoreChange('math', 'grade', e.target.value)} />
               </div>
               <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-500">영어</label>
                  <input type="text" disabled className="w-full p-2 bg-gray-100 border border-transparent rounded-lg text-sm" placeholder="-" />
                  <input type="text" placeholder="등급" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.english.grade} onChange={(e) => handleScoreChange('english', 'grade', e.target.value)} />
               </div>
               <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-500">탐구 1</label>
                  <input type="text" placeholder="과목명" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.social1.subject} onChange={(e) => handleScoreChange('social1', 'subject', e.target.value)} />
                  <input type="text" placeholder="점수" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.social1.score} onChange={(e) => handleScoreChange('social1', 'score', e.target.value)} />
               </div>
               <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-500">탐구 2</label>
                  <input type="text" placeholder="과목명" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.social2.subject} onChange={(e) => handleScoreChange('social2', 'subject', e.target.value)} />
                  <input type="text" placeholder="점수" className="w-full p-2 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    value={formData.scores.social2.score} onChange={(e) => handleScoreChange('social2', 'score', e.target.value)} />
               </div>
            </div>
            
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2">최근 모의고사 총평</label>
              <input type="text" placeholder="예) 6월 모평 국영수탐 평균 2.1등급, 상승세" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none"
                value={formData.mockSummary} onChange={(e) => handleInputChange('mockSummary', e.target.value)} />
            </div>
          </div>

          {/* 2.4 Practical Profile */}
          <div id="practical" className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm scroll-mt-32">
            <SectionHeader icon={Palette} title="실기 프로파일" />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">현재 실기 레벨</label>
                <select className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none font-bold text-gray-900"
                  value={formData.practicalLevel} onChange={(e) => handleInputChange('practicalLevel', e.target.value)}>
                  <option value="A+">A+ (탁월)</option>
                  <option value="A">A (우수)</option>
                  <option value="B+">B+ (양호)</option>
                  <option value="B">B (보통)</option>
                  <option value="C">C (노력 요함)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">주 평가 강사</label>
                <select className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none"
                  value={formData.mainInstructor} onChange={(e) => handleInputChange('mainInstructor', e.target.value)}>
                  <option value="">강사 선택...</option>
                  <option value="i1">이은일 원장</option>
                  <option value="i2">김철수 수석</option>
                  <option value="i3">박지영 강사</option>
                </select>
              </div>
            </div>

            <div className="mb-8">
               <label className="block text-xs font-bold text-gray-500 uppercase mb-4">4축 초기 평가 (Initial Assessment)</label>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                 {Object.entries(formData.initialEval).map(([key, val]) => (
                   <div key={key}>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-bold text-gray-700 capitalize">
                           {key === 'composition' ? '구도' : key === 'tone' ? '톤/명암' : key === 'idea' ? '발상' : '완성도'}
                        </span>
                        <span className="text-sm font-bold text-[#FC6401]">{val} / 10</span>
                      </div>
                      <input 
                        type="range" min="0" max="10" step="1"
                        value={val}
                        onChange={(e) => handleNestedChange('initialEval', key, parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#FC6401]"
                      />
                   </div>
                 ))}
               </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-2">강점 메모</label>
                  <textarea placeholder="예) 형태력이 우수하고 묘사 속도가 빠름" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none h-20 resize-none"
                    value={formData.strengthNote} onChange={(e) => handleInputChange('strengthNote', e.target.value)} />
               </div>
               <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-2">약점 메모</label>
                  <textarea placeholder="예) 아이디어 발상이 소극적임" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none h-20 resize-none"
                    value={formData.weaknessNote} onChange={(e) => handleInputChange('weaknessNote', e.target.value)} />
               </div>
            </div>
          </div>

          <div className="flex justify-end pt-8">
            <button onClick={handleSubmit} className="px-10 py-4 bg-[#FC6401] text-white rounded-2xl hover:bg-[#e55a00] font-bold text-lg shadow-xl shadow-[#FC6401]/30 flex items-center gap-3 transition-all transform hover:-translate-y-1">
              <Check className="w-6 h-6" />
              학생 등록 및 평가 시작
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};

export default StudentAdd;
