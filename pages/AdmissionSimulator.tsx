
import React, { useState, useEffect, useMemo } from 'react';
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell, LineChart, Line, ReferenceLine
} from 'recharts';
import { 
  Calculator, TrendingUp, AlertCircle, School, ArrowRight, RotateCcw, 
  ChevronLeft, User, Sliders, Sparkles, Target, Save, CheckCircle2,
  Zap, Brain, Plus, X, Search
} from 'lucide-react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getStudentById, getStudents } from '../services/storageService';
import { Student } from '../types';

// --- Mock Data & Types ---
interface SimulationState {
  korean: number;
  math: number;
  english: number; // Grade
  social1: number;
  social2: number;
  history: number; // Grade
  practical: number; // 0-100 score
}

interface TargetUniv {
  id: string;
  name: string;
  major: string;
  group: '가군' | '나군' | '다군';
  weights: { kor: number; math: number; eng: number; social: number; prac: number };
  cutline: number;
}

const DEFAULT_UNIVS: TargetUniv[] = [
  { id: 'hongik', name: '홍익대', major: '시각디자인', group: '나군', weights: { kor: 1.0, math: 0.8, eng: 0.5, social: 1.0, prac: 0 }, cutline: 135 }, // Non-practical for simplicity in demo
  { id: 'snu', name: '서울대', major: '공예', group: '가군', weights: { kor: 1.0, math: 1.0, eng: 0.5, social: 1.0, prac: 1.5 }, cutline: 420 },
  { id: 'ewha', name: '이화여대', major: '디자인', group: '다군', weights: { kor: 1.0, math: 0.5, eng: 0.5, social: 1.0, prac: 1.2 }, cutline: 380 },
  { id: 'kookmin', name: '국민대', major: '시각디자인', group: '가군', weights: { kor: 1.0, math: 0.3, eng: 0.5, social: 1.0, prac: 1.0 }, cutline: 350 },
];

const AdmissionSimulator: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const studentId = searchParams.get('studentId');
  const [student, setStudent] = useState<Student | null>(null);
  const [allStudents, setAllStudents] = useState<Student[]>([]);

  // --- State ---
  // 1. Selected Targets (Multi-select)
  const [selectedTargets, setSelectedTargets] = useState<TargetUniv[]>([DEFAULT_UNIVS[0]]);
  
  // 2. Base Scores (Fixed)
  const [baseScores, setBaseScores] = useState<SimulationState>({
    korean: 120, math: 110, english: 2, social1: 60, social2: 60, history: 1, practical: 88
  });

  // 3. Simulated Scores (Mutable via sliders)
  const [simScores, setSimScores] = useState<SimulationState>({
    korean: 120, math: 110, english: 2, social1: 60, social2: 60, history: 1, practical: 88
  });

  // 4. Scenario Mode
  const [activeScenario, setActiveScenario] = useState<'current' | 'realistic' | 'aggressive'>('current');

  // --- Load Data ---
  useEffect(() => {
    // Load student list for dropdown
    setAllStudents(getStudents());
  }, []);

  useEffect(() => {
    if (studentId) {
      const s = getStudentById(studentId);
      if (s) {
        setStudent(s);
        const initialScores = {
          korean: s.academicScores.korean.standardScore || 120,
          math: s.academicScores.math.standardScore || 110,
          english: s.academicScores.english.grade || 2,
          social1: s.academicScores.social1.standardScore || 60,
          social2: s.academicScores.social2.standardScore || 60,
          history: 1,
          practical: s.currentLevel === 'A+' ? 96 : s.currentLevel === 'A' ? 92 : s.currentLevel === 'B+' ? 88 : 80
        };
        setBaseScores(initialScores);
        setSimScores(initialScores);
        setActiveScenario('current');

        // Auto-select target based on student data
        const matched = DEFAULT_UNIVS.find(u => s.targetUniversity.includes(u.name));
        if (matched) setSelectedTargets([matched]);
      }
    } else {
        setStudent(null);
    }
  }, [studentId]);

  // --- Calculation Engine ---
  const calculateScore = (scores: SimulationState, univ: TargetUniv) => {
    // Simple weighted sum mock
    const engScore = 100 - (scores.english * 5);
    const total = 
      (scores.korean * univ.weights.kor) + 
      (scores.math * univ.weights.math) + 
      (engScore * univ.weights.eng) + 
      ((scores.social1 + scores.social2) * 0.5 * univ.weights.social) +
      (scores.practical * univ.weights.prac);
    
    // Normalize roughly to 100% based on cutline (Mock)
    const maxScore = univ.cutline * 1.1; 
    const probability = Math.min(Math.round((total / maxScore) * 100), 99);
    
    return { total: Math.round(total), probability };
  };

  const getRiskLevel = (prob: number) => {
    if (prob >= 90) return { label: '안정 (Safe)', color: 'text-emerald-600', bg: 'bg-emerald-50', bar: '#10b981' };
    if (prob >= 75) return { label: '적정 (Stable)', color: 'text-blue-600', bg: 'bg-blue-50', bar: '#3b82f6' };
    if (prob >= 50) return { label: '소신 (Reach)', color: 'text-[#FC6401]', bg: 'bg-[#FFF0E6]', bar: '#FC6401' };
    return { label: '위험 (Risk)', color: 'text-rose-600', bg: 'bg-rose-50', bar: '#f43f5e' };
  };

  // --- Handlers ---
  const handleStudentChange = (id: string) => {
    if (id) {
        navigate(`/simulation?studentId=${id}`);
    } else {
        navigate(`/simulation`);
    }
  };

  const handleSliderChange = (field: keyof SimulationState, val: number) => {
    setSimScores(prev => ({ ...prev, [field]: val }));
    setActiveScenario('realistic'); // Custom changes default to realistic bucket visually
  };

  const applyPreset = (type: 'current' | 'realistic' | 'aggressive') => {
    setActiveScenario(type);
    if (type === 'current') {
      setSimScores(baseScores);
    } else if (type === 'realistic') {
      setSimScores({
        ...baseScores,
        korean: baseScores.korean + 4,
        math: baseScores.math + 3,
        practical: Math.min(baseScores.practical + 3, 98)
      });
    } else if (type === 'aggressive') {
      setSimScores({
        ...baseScores,
        korean: baseScores.korean + 8,
        math: baseScores.math + 8,
        social1: baseScores.social1 + 5,
        practical: Math.min(baseScores.practical + 6, 99)
      });
    }
  };

  const toggleTarget = (univId: string) => {
    const univ = DEFAULT_UNIVS.find(u => u.id === univId);
    if (!univ) return;
    
    if (selectedTargets.find(t => t.id === univId)) {
      if (selectedTargets.length > 1) {
        setSelectedTargets(prev => prev.filter(t => t.id !== univId));
      }
    } else {
      if (selectedTargets.length < 3) {
        setSelectedTargets(prev => [...prev, univ]);
      }
    }
  };

  // --- Derived Data for Charts ---
  const radarData = [
    { subject: '국어', A: baseScores.korean, B: simScores.korean, full: 140 },
    { subject: '수학', A: baseScores.math, B: simScores.math, full: 140 },
    { subject: '탐구', A: (baseScores.social1 + baseScores.social2)/2, B: (simScores.social1 + simScores.social2)/2, full: 70 },
    { subject: '실기', A: baseScores.practical, B: simScores.practical, full: 100 },
  ];

  const chartData = selectedTargets.map(univ => {
    const current = calculateScore(baseScores, univ);
    const sim = calculateScore(simScores, univ);
    return {
      name: univ.name,
      currentProb: current.probability,
      simProb: sim.probability,
      gap: sim.probability - current.probability
    };
  });

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-[#F9FAFB]">
      <div className="max-w-[1600px] mx-auto p-8 pb-20 animate-in fade-in duration-500">
        
        {/* 1. Header & Navigation */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <button 
              onClick={() => navigate(-1)} 
              className="text-xs font-bold text-gray-400 hover:text-gray-600 flex items-center gap-1 transition-colors mb-2"
            >
              <ChevronLeft className="w-3 h-3" /> 돌아가기
            </button>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Calculator className="w-8 h-8 text-[#FC6401]" />
              입시 전략 시뮬레이터
              <span className="text-xs font-bold bg-gray-900 text-white px-2 py-0.5 rounded border border-gray-700">Meta-AI Beta</span>
            </h1>
            <p className="text-gray-500 mt-2 flex items-center gap-2">
              <Brain className="w-4 h-4 text-gray-400" />
              NeoPrime의 과거 20만 건 합격 데이터를 기반으로 시나리오별 합격 확률을 예측합니다.
            </p>
          </div>
          
          {/* Scenario Presets */}
          <div className="flex bg-white p-1 rounded-xl border border-gray-200 shadow-sm">
            {[
              { id: 'current', label: '현재 상태 (Current)' },
              { id: 'realistic', label: '현실적 개선 (+Alpha)' },
              { id: 'aggressive', label: '공격적 목표 (Dream)' }
            ].map(mode => (
              <button
                  key={mode.id}
                  onClick={() => applyPreset(mode.id as any)}
                  className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                    activeScenario === mode.id 
                      ? 'bg-gray-900 text-white shadow-md' 
                      : 'text-gray-500 hover:bg-gray-50'
                  }`}
              >
                  {mode.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-12 gap-8">
          
          {/* --- 2. LEFT PANEL: Input & Controls (3 cols) --- */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
              
              {/* Student Selection */}
              <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-gray-900 text-sm flex items-center gap-2">
                      <User className="w-4 h-4 text-[#FC6401]" /> 학생 선택
                    </h3>
                </div>
                <div className="relative">
                  <select 
                      className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-[#FC6401] outline-none appearance-none font-medium"
                      value={student?.id || ''}
                      onChange={(e) => handleStudentChange(e.target.value)}
                  >
                      <option value="">학생을 선택하세요...</option>
                      {allStudents.map(s => (
                        <option key={s.id} value={s.id}>{s.name} ({s.grade})</option>
                      ))}
                  </select>
                  <div className="absolute right-3 top-3.5 pointer-events-none text-gray-400">
                      <Search className="w-4 h-4" />
                  </div>
                </div>
                
                {student && (
                    <div className="mt-4 flex items-center gap-3 p-3 bg-gray-50 rounded-xl border border-gray-100 animate-in fade-in">
                        <img src={student.avatarUrl} alt="" className="w-10 h-10 rounded-full bg-white border border-gray-200" />
                        <div>
                            <div className="font-bold text-gray-900 text-sm">{student.name}</div>
                            <div className="text-xs text-gray-500">{student.school} • {student.targetUniversity}</div>
                        </div>
                    </div>
                )}
              </div>

              {/* Target Selection */}
              <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-gray-900 text-sm flex items-center gap-2">
                      <Target className="w-4 h-4 text-[#FC6401]" /> 목표 대학 (최대 3)
                    </h3>
                </div>
                <div className="space-y-2">
                    {DEFAULT_UNIVS.map(univ => {
                      const isSelected = selectedTargets.find(t => t.id === univ.id);
                      return (
                          <button 
                            key={univ.id}
                            onClick={() => toggleTarget(univ.id)}
                            className={`w-full flex items-center justify-between p-3 rounded-xl border text-sm font-medium transition-all ${
                                isSelected 
                                ? 'bg-[#FFF0E6] border-[#FC6401] text-[#FC6401]' 
                                : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'
                            }`}
                          >
                            <span>{univ.name} <span className="text-xs opacity-70">({univ.major})</span></span>
                            {isSelected && <CheckCircle2 className="w-4 h-4" />}
                          </button>
                      );
                    })}
                </div>
              </div>

              {/* Score Sliders */}
              <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-gray-900 text-sm flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-gray-500" /> 가상 점수 조정
                    </h3>
                    <button onClick={() => applyPreset('current')} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                      <RotateCcw className="w-3 h-3" /> 초기화
                    </button>
                </div>
                
                <div className="space-y-6">
                    {/* Academic Sliders */}
                    {[
                        { label: '국어 (표점)', key: 'korean', max: 150 },
                        { label: '수학 (표점)', key: 'math', max: 150 },
                        { label: '탐구1 (표점)', key: 'social1', max: 80 },
                        { label: '탐구2 (표점)', key: 'social2', max: 80 },
                    ].map((field) => (
                        <div key={field.key}>
                            <div className="flex justify-between mb-2 text-xs">
                                <span className="font-bold text-gray-600">{field.label}</span>
                                <span className="font-bold text-[#FC6401]">
                                    {simScores[field.key as keyof SimulationState]}
                                    <span className="text-gray-300 ml-1">
                                        ({simScores[field.key as keyof SimulationState] - baseScores[field.key as keyof SimulationState] > 0 ? '+' : ''}
                                        {simScores[field.key as keyof SimulationState] - baseScores[field.key as keyof SimulationState]})
                                    </span>
                                </span>
                            </div>
                            <input 
                                type="range" min={0} max={field.max} step={1}
                                value={simScores[field.key as keyof SimulationState]}
                                onChange={(e) => handleSliderChange(field.key as keyof SimulationState, parseInt(e.target.value))}
                                className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#FC6401]"
                            />
                        </div>
                    ))}

                    <div className="w-full h-px bg-gray-100 my-4"></div>

                    {/* Practical Slider */}
                    <div>
                        <div className="flex justify-between mb-2 text-xs">
                            <span className="font-bold text-gray-600 flex items-center gap-1"><Zap className="w-3 h-3 text-[#FC6401]" /> 실기 점수</span>
                            <span className="font-bold text-[#FC6401]">{simScores.practical}점</span>
                        </div>
                        <input 
                            type="range" min={50} max={100} step={1}
                            value={simScores.practical}
                            onChange={(e) => handleSliderChange('practical', parseInt(e.target.value))}
                            className="w-full h-2 bg-gradient-to-r from-gray-200 to-[#FFF0E6] rounded-lg appearance-none cursor-pointer accent-[#FC6401]"
                        />
                        <div className="flex justify-between mt-1 text-[10px] text-gray-400">
                            <span>C</span><span>B</span><span>A</span><span>A+</span>
                        </div>
                    </div>
                </div>
              </div>
          </div>

          {/* --- 3. CENTER & RIGHT: Analysis Dashboard (9 cols) --- */}
          <div className="col-span-12 lg:col-span-9 space-y-6">
              
              {/* Top Cards: Multi-Univ Results */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {selectedTargets.map(univ => {
                      const result = calculateScore(simScores, univ);
                      const risk = getRiskLevel(result.probability);
                      const baseResult = calculateScore(baseScores, univ);
                      const delta = result.probability - baseResult.probability;

                      return (
                          <div key={univ.id} className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm relative overflow-hidden group">
                              <div className={`absolute top-0 left-0 w-1.5 h-full ${risk.bg.replace('bg-', 'bg-').replace('-50', '-500')}`}></div>
                              <div className="flex justify-between items-start mb-4 pl-3">
                                  <div>
                                      <h3 className="text-lg font-bold text-gray-900">{univ.name}</h3>
                                      <p className="text-xs text-gray-500">{univ.major} • {univ.group}</p>
                                  </div>
                                  <span className={`px-2 py-1 rounded-lg text-xs font-bold ${risk.bg} ${risk.color}`}>
                                      {risk.label.split(' ')[0]}
                                  </span>
                              </div>
                              
                              <div className="flex items-end gap-2 pl-3 mb-2">
                                  <span className="text-4xl font-bold text-gray-900">{result.probability}%</span>
                                  {delta !== 0 && (
                                      <span className={`text-sm font-bold mb-1.5 ${delta > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                          {delta > 0 ? '+' : ''}{delta}%
                                      </span>
                                  )}
                              </div>
                              <div className="pl-3 text-xs text-gray-400 font-medium">환산점수: {result.total}점 (예상 컷: {univ.cutline})</div>
                          </div>
                      );
                  })}
                  
                  {/* Add Placeholder if less than 3 */}
                  {selectedTargets.length < 3 && (
                      <div 
                          className="border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center text-gray-400 p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                          onClick={() => document.querySelector('.lg\\:col-span-3')?.scrollIntoView({ behavior: 'smooth' })}
                      >
                          <Plus className="w-8 h-8 mb-2 opacity-50" />
                          <span className="text-sm font-bold">대학 추가 비교</span>
                      </div>
                  )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Chart 1: Radar Comparison */}
                  <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                      <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                          <RotateCcw className="w-4 h-4 text-gray-400" /> 변화 전/후 밸런스 비교
                      </h3>
                      <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                  <PolarGrid stroke="#e5e7eb" />
                                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 'bold' }} />
                                  <PolarRadiusAxis angle={30} domain={[0, 160]} tick={false} axisLine={false} />
                                  <Radar name="현재 점수" dataKey="A" stroke="#9ca3af" strokeWidth={2} fill="#9ca3af" fillOpacity={0.1} />
                                  <Radar name="시뮬레이션" dataKey="B" stroke="#FC6401" strokeWidth={2} fill="#FC6401" fillOpacity={0.4} />
                                  <Legend />
                                  <Tooltip />
                              </RadarChart>
                          </ResponsiveContainer>
                      </div>
                  </div>

                  {/* Chart 2: Probability Bar Comparison */}
                  <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                      <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-gray-400" /> 대학별 합격 확률 변화
                      </h3>
                      <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={chartData} layout="vertical" barGap={2} barSize={20}>
                                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f3f4f6" />
                                  <XAxis type="number" domain={[0, 100]} hide />
                                  <YAxis dataKey="name" type="category" width={80} tick={{fontSize: 12, fontWeight: 'bold'}} axisLine={false} tickLine={false} />
                                  <Tooltip cursor={{fill: 'transparent'}} />
                                  <Legend />
                                  <Bar dataKey="currentProb" name="현재" fill="#e5e7eb" radius={[0, 4, 4, 0]} />
                                  <Bar dataKey="simProb" name="시뮬레이션" fill="#FC6401" radius={[0, 4, 4, 0]} />
                              </BarChart>
                          </ResponsiveContainer>
                      </div>
                  </div>
              </div>

              {/* AI Insight Box */}
              <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-32 bg-[#FC6401] rounded-full blur-[100px] opacity-20"></div>
                  
                  <div className="relative z-10">
                      <div className="flex items-center gap-3 mb-4">
                          <div className="p-2 bg-[#FC6401] rounded-lg">
                              <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <h3 className="text-lg font-bold">NeoPrime Meta-Insight</h3>
                      </div>

                      <div className="space-y-4">
                          <p className="text-gray-200 leading-relaxed font-medium">
                              "{selectedTargets[0]?.name}" 기준, 현재 시나리오에서는 국어 점수가 합격자 평균 대비 <strong className="text-rose-400">-8점</strong> 부족하여 소신 지원(Reach)권입니다.
                              <br/>
                              하지만 <strong className="text-emerald-400">국어 +4점, 실기 A(92점)</strong> 달성 시 합격 확률이 <strong>78% (안정권)</strong>까지 급상승하는 구간이 확인됩니다.
                          </p>
                          
                          <div className="bg-white/10 rounded-xl p-4 border border-white/10 mt-4">
                              <h4 className="text-xs font-bold text-gray-400 uppercase mb-3 flex items-center gap-2">
                                  <Zap className="w-3 h-3 text-[#FC6401]" /> 추천 액션 플랜 (4주)
                              </h4>
                              <ul className="space-y-2 text-sm">
                                  <li className="flex gap-2">
                                      <span className="text-[#FC6401] font-bold">•</span>
                                      <span>국어 비문학 추론 유형 집중 공략 (일 3지문)</span>
                                  </li>
                                  <li className="flex gap-2">
                                      <span className="text-[#FC6401] font-bold">•</span>
                                      <span>실기 구도 안정감 확보를 위한 '패턴 A' 반복 훈련</span>
                                  </li>
                              </ul>
                          </div>
                      </div>

                      <div className="mt-6 flex gap-3">
                          <button className="px-5 py-2.5 bg-white text-gray-900 rounded-xl font-bold text-sm hover:bg-gray-100 transition-colors flex items-center gap-2">
                              <Save className="w-4 h-4" /> 시나리오 저장
                          </button>
                          <button className="px-5 py-2.5 border border-white/30 text-white rounded-xl font-bold text-sm hover:bg-white/10 transition-colors">
                              리포트 공유
                          </button>
                      </div>
                  </div>
              </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default AdmissionSimulator;
