import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStudentById, getEvaluationsByStudentId } from '../services/storageService';
import { 
  ArrowLeft, ChevronLeft, ChevronRight, Activity, 
  TrendingUp, AlertCircle, GraduationCap, 
  CheckCircle2, Calendar, Scale, ClipboardList, 
  MessageSquare, CheckSquare, Clock, AlertTriangle, FileText, Pencil, Calculator
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Student, Evaluation } from '../types';

const StudentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [student, setStudent] = useState<Student | undefined>(undefined);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Load Data
  useEffect(() => {
    if (id) {
      setStudent(getStudentById(id));
      setEvaluations(getEvaluationsByStudentId(id));
    }
  }, [id]);

  // Worksheet State
  const [todoList, setTodoList] = useState([
    { id: 1, text: '가/나/다군 지원 전략 상담 일정 잡기', done: false, due: '2일 남음' },
    { id: 2, text: '"아이디어 발상" 보충 워크샵 배정', done: true, due: '완료' },
    { id: 3, text: '6월 모의고사 이후 성적 추이 검토', done: false, due: '1주 남음' },
  ]);

  if (!student) {
    return <div className="p-8 text-center text-gray-500">학생을 찾을 수 없습니다.</div>;
  }

  const hasImages = student.artworks && student.artworks.length > 0;
  
  const nextImage = () => {
    if (hasImages) {
      setCurrentImageIndex((prev) => (prev + 1) % student.artworks.length);
    }
  };

  const prevImage = () => {
    if (hasImages) {
      setCurrentImageIndex((prev) => (prev - 1 + student.artworks.length) % student.artworks.length);
    }
  };

  const latestEval = evaluations.length > 0 ? evaluations[0] : null;

  const toggleTodo = (id: number) => {
    setTodoList(prev => prev.map(todo => todo.id === id ? { ...todo, done: !todo.done } : todo));
  };

  // --- Mock Analysis Data ---
  
  const strategyStatus = {
    badge: '잠재력 높음'
  };

  // Recruitment Group Strategy (Ga/Na/Da)
  const recruitmentStrategy = [
    { group: '가군', univ: '서울대', line: '상향(Reach)', prob: 35, color: 'bg-rose-500', text: 'text-rose-600' },
    { group: '나군', univ: '홍익대', line: '적정(Safe)', prob: 78, color: 'bg-[#FC6401]', text: 'text-[#FC6401]' },
    { group: '다군', univ: '이화여대', line: '소신(Top)', prob: 92, color: 'bg-emerald-500', text: 'text-emerald-600' }
  ];

  // Academic Score Data Structure for Table
  const academicTableData = [
    { subject: '국어', student: student.academicScores.korean.standardScore, avg: 138, type: 'score' },
    { subject: '영어', student: student.academicScores.english.grade, avg: 1, type: 'grade' },
    { subject: '수학', student: student.academicScores.math.standardScore, avg: 135, type: 'score' },
    { subject: '탐구1', student: student.academicScores.social1.standardScore, avg: 66, type: 'score' },
    { subject: '탐구2', student: student.academicScores.social2.standardScore, avg: 65, type: 'score' },
  ];

  const instructorBias = {
    name: '한 강사',
    biasScore: -2.5,
    note: '한 강사는 "톤(Tone)"을 엄격하게 평가하는 경향이 있음; 보정된 점수는 약 86.5점 예상.'
  };
  
  // Format Data for Chart (Reverse order to show timeline left to right)
  const chartData = [...evaluations].reverse().map(e => ({
      date: e.date.substring(5), // MM-DD
      score: e.totalScore,
      fullDate: e.date
  }));

  return (
    <div className="min-h-screen font-sans pb-12 animate-in fade-in duration-500 bg-[#F7F9FB]">
      
      {/* --- 1. Top: Executive Summary Header --- */}
      <div className="bg-white border-b border-gray-200 sticky top-20 z-20 px-8 py-4 shadow-sm">
          <div className="max-w-[1600px] mx-auto flex justify-between items-center">
            <div className="flex items-center gap-5">
                <Link to="/students" className="p-2.5 bg-gray-50 hover:bg-[#FFF0E6] text-gray-500 hover:text-[#FC6401] rounded-xl transition-colors">
                    <ArrowLeft className="w-5 h-5" />
                </Link>
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold text-gray-900">{student.name}</h1>
                        <span className="px-2.5 py-0.5 bg-gray-100 text-gray-600 text-xs font-bold rounded border border-gray-200 uppercase tracking-wide">
                            {student.grade}
                        </span>
                        <span className="px-2.5 py-0.5 bg-[#FFF0E6] text-[#FC6401] text-xs font-bold rounded border border-[#FC6401]/20 uppercase tracking-wide">
                            {strategyStatus.badge}
                        </span>
                    </div>
                    {/* Recruitment Group Targets Header Line */}
                    <div className="flex items-center gap-6 text-sm mt-2">
                        <span className="flex items-center gap-1.5 font-medium text-gray-700 bg-gray-50 px-2 py-0.5 rounded-lg border border-gray-100">
                            <span className="text-gray-400 font-bold text-xs uppercase">목표 대학</span>
                        </span>
                        {recruitmentStrategy.map((strat, idx) => (
                            <div key={strat.group} className="flex items-center gap-2">
                                <span className="text-gray-500 font-bold text-xs">{strat.group}:</span>
                                <span className="font-bold text-gray-800">{strat.univ}</span>
                                <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold border uppercase ${
                                    strat.line.includes('Safe') || strat.line.includes('Top') 
                                    ? 'bg-emerald-50 text-emerald-600 border-emerald-100' 
                                    : strat.line.includes('Reach') 
                                    ? 'bg-rose-50 text-rose-600 border-rose-100'
                                    : 'bg-amber-50 text-amber-600 border-amber-100'
                                }`}>
                                    {strat.line}
                                </span>
                                {idx < recruitmentStrategy.length - 1 && <span className="text-gray-300">|</span>}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            
            <div className="flex items-center gap-6">
                 <div className="text-right hidden sm:block">
                     <div className="text-[10px] text-gray-400 uppercase font-bold tracking-wider mb-1">현재 레벨</div>
                     <div className={`text-2xl font-bold ${student.currentLevel.includes('A') ? 'text-[#FC6401]' : 'text-emerald-600'}`}>
                         {student.currentLevel}
                     </div>
                 </div>
                 <div className="h-10 w-px bg-gray-200 mx-2"></div>
                 <Link 
                    to={`/evaluations/new?studentId=${student.id}`}
                    className="flex items-center gap-2 bg-gray-900 text-white px-4 py-2.5 rounded-xl hover:bg-gray-800 transition-colors shadow-lg shadow-gray-900/10"
                 >
                    <MessageSquare className="w-4 h-4" />
                    <span className="text-sm font-bold">상담 시작</span>
                 </Link>
            </div>
          </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-8 space-y-8">
        
        {/* --- 2. Main Worksheet Grid (4/4/4 Columns) --- */}
        <div className="grid grid-cols-12 gap-8">
            
            {/* --- LEFT COL: Strategy & Positioning (4 cols) --- */}
            <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
                
                {/* Section A: Admission & Academic Position */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                    <div className="flex justify-between items-center mb-5">
                        <h3 className="text-xs font-bold text-gray-400 uppercase flex items-center gap-2 tracking-wider">
                             <Activity className="w-4 h-4" /> 입시 및 학업 위치
                        </h3>
                        <Link 
                            to={`/simulation?studentId=${student.id}`}
                            className="text-xs font-bold text-[#FC6401] hover:bg-[#FFF0E6] px-2 py-1 rounded transition-colors flex items-center gap-1"
                        >
                            <Calculator className="w-3 h-3" />
                            시뮬레이터 실행
                        </Link>
                    </div>
                    
                    {/* 1. Group Summary Bars */}
                    <div className="space-y-4 mb-8">
                        {recruitmentStrategy.map((strat) => (
                            <div key={strat.group} className="relative">
                                <div className="flex justify-between items-end mb-1.5">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-bold text-gray-500 w-8">{strat.group}</span>
                                        <span className="text-sm font-bold text-gray-800 truncate max-w-[140px]">{strat.univ}</span>
                                    </div>
                                    <span className={`text-sm font-bold ${strat.text}`}>{strat.prob}%</span>
                                </div>
                                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                    <div 
                                        className={`h-full rounded-full ${strat.color}`} 
                                        style={{ width: `${strat.prob}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* 2. Detailed Score Table */}
                    <div className="mb-6">
                        <table className="w-full text-xs text-left">
                            <thead>
                                <tr className="text-gray-400 border-b border-gray-100">
                                    <th className="pb-2 font-medium pl-1">과목</th>
                                    <th className="pb-2 font-medium text-right">학생 점수</th>
                                    <th className="pb-2 font-medium text-right text-gray-400">합격 평균</th>
                                    <th className="pb-2 font-medium text-right">차이</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {academicTableData.map((row) => {
                                    // Gap Calculation logic
                                    let gap = 0;
                                    let displayGap = '';
                                    let isPositive = false;

                                    if (row.type === 'grade') {
                                        // Lower grade is better
                                        gap = (row.avg || 0) - (row.student || 0); 
                                        isPositive = gap >= 0; 
                                        displayGap = gap === 0 ? '-' : `${gap > 0 ? '-' : '+'}${Math.abs(gap)}`; 
                                    } else {
                                        // Higher score is better
                                        gap = (row.student || 0) - (row.avg || 0);
                                        isPositive = gap >= 0;
                                        displayGap = gap === 0 ? '-' : `${gap > 0 ? '+' : ''}${gap}`;
                                    }

                                    return (
                                        <tr key={row.subject}>
                                            <td className="py-2.5 font-medium text-gray-700 pl-1">{row.subject}</td>
                                            <td className="py-2.5 text-right font-bold text-gray-900">
                                                {row.student || '-'}
                                                {row.type === 'grade' && <span className="text-[9px] font-normal ml-0.5 text-gray-400">등급</span>}
                                            </td>
                                            <td className="py-2.5 text-right text-gray-400">{row.avg}</td>
                                            <td className={`py-2.5 text-right font-bold ${isPositive ? 'text-emerald-600' : 'text-rose-500'}`}>
                                                {displayGap}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>

                    {/* 3. Insight Summary */}
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                        <p className="text-xs text-gray-600 leading-relaxed mb-3">
                            전반적인 학업 지수는 홍익대(나군) 합격 평균보다 <strong className="text-emerald-600">+4.5점 높으며</strong>, 서울대(가군) 수학 커트라인보다는 약간 낮습니다.
                        </p>
                        <p className="text-xs text-gray-600 leading-relaxed flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                            <span>주요 학업 리스크는 <strong>서울대 수학 점수</strong>이며, 나머지는 목표 범위 내에 있습니다.</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* --- CENTER COL: Artwork & Evidence (4 cols) --- */}
            <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
                
                {/* Main Artwork Viewer */}
                <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden relative group flex-1 min-h-[500px] flex flex-col">
                    <div className="absolute top-6 left-6 z-10 bg-white/90 backdrop-blur px-4 py-1.5 rounded-full text-xs font-bold text-gray-800 shadow-sm border border-gray-200 flex items-center gap-2">
                        <Calendar className="w-3 h-3 text-[#FC6401]" />
                        {latestEval ? new Date(latestEval.date).toLocaleDateString() : '날짜 없음'}
                    </div>
                    
                    <div className="flex-1 bg-[#F7F9FB] relative flex items-center justify-center p-8">
                        {hasImages ? (
                            <>
                                <img 
                                    src={student.artworks[currentImageIndex]} 
                                    alt="Artwork" 
                                    className="w-full h-full object-contain max-h-[550px] shadow-lg rounded-lg"
                                />
                                <button onClick={prevImage} className="absolute left-6 top-1/2 -translate-y-1/2 p-3 bg-white hover:text-[#FC6401] text-gray-400 rounded-full shadow-xl opacity-0 group-hover:opacity-100 transition-all transform hover:scale-110">
                                    <ChevronLeft className="w-6 h-6" />
                                </button>
                                <button onClick={nextImage} className="absolute right-6 top-1/2 -translate-y-1/2 p-3 bg-white hover:text-[#FC6401] text-gray-400 rounded-full shadow-xl opacity-0 group-hover:opacity-100 transition-all transform hover:scale-110">
                                    <ChevronRight className="w-6 h-6" />
                                </button>
                                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex gap-2">
                                    {student.artworks.map((_, idx) => (
                                        <div key={idx} className={`w-2.5 h-2.5 rounded-full shadow-sm transition-all ${idx === currentImageIndex ? 'bg-[#FC6401] w-6' : 'bg-gray-300'}`} />
                                    ))}
                                </div>
                                {/* Edit Action Overlay */}
                                <Link 
                                    to={`/evaluations/new?studentId=${student.id}`}
                                    className="absolute top-6 right-6 p-2 bg-white/90 backdrop-blur rounded-full text-gray-400 hover:text-[#FC6401] border border-gray-200 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <Pencil className="w-4 h-4" />
                                </Link>
                            </>
                        ) : (
                            <div className="text-gray-400 flex flex-col items-center">
                                <AlertCircle className="w-16 h-16 mb-4 opacity-20" />
                                <p>업로드된 작품이 없습니다.</p>
                            </div>
                        )}
                    </div>

                    {/* Evaluation Summary Footer */}
                    <div className="p-6 border-t border-gray-100 bg-white">
                        <div className="flex gap-6">
                            <div className="flex-1">
                                <h4 className="font-bold text-gray-900 text-sm mb-2">원장 리뷰 노트</h4>
                                <p className="text-sm text-gray-500 leading-relaxed line-clamp-3">
                                    {latestEval?.notes || "이 작품에 대한 노트가 없습니다."}
                                </p>
                            </div>
                            <div className="flex gap-4 border-l border-gray-100 pl-6">
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">구도</div>
                                    <div className="font-bold text-gray-900 text-lg">{latestEval?.scores.composition}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">소묘/톤</div>
                                    <div className="font-bold text-gray-900 text-lg">{latestEval?.scores.tone}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">발상</div>
                                    <div className="font-bold text-gray-900 text-lg">{latestEval?.scores.idea}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">총점</div>
                                    <div className="font-bold text-[#FC6401] text-xl">{latestEval?.totalScore}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* --- RIGHT COL: Coaching & Consult (4 cols) --- */}
            <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
                
                {/* Section D: Instructor Bias (Upgraded Visuals) */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-5 flex items-center gap-2 tracking-wider">
                         <Scale className="w-4 h-4" /> 강사 편차 분석
                    </h3>
                    
                    {/* Visual Dot Plot */}
                    <div className="relative h-14 w-full mb-4 flex items-center">
                        {/* Base Line */}
                        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200"></div>
                        
                        {/* Avg Line */}
                        <div className="absolute top-1/2 left-[50%] -translate-y-1/2 -translate-x-1/2 w-0.5 h-4 bg-gray-400"></div>
                        
                        {/* Raw Score */}
                        <div className="absolute top-1/2 left-[40%] -translate-y-1/2 -translate-x-1/2 flex flex-col items-center group">
                            <div className="w-3 h-3 rounded-full bg-gray-500 border-2 border-white shadow-sm z-10"></div>
                            <span className="text-[10px] text-gray-500 font-bold mt-1">원점수</span>
                        </div>

                        {/* Adjusted Score */}
                        <div className="absolute top-1/2 left-[55%] -translate-y-1/2 -translate-x-1/2 flex flex-col items-center group">
                            <div className="w-3.5 h-3.5 rounded-full bg-[#FC6401] border-2 border-white shadow-sm z-10"></div>
                            <span className="text-[10px] text-[#FC6401] font-bold mt-1">보정값</span>
                        </div>
                        
                        {/* Connection Arc (Stylized) */}
                        <svg className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-visible">
                            <path d="M 120 28 Q 140 10 160 28" fill="none" stroke="#FC6401" strokeWidth="1.5" strokeDasharray="3 3" />
                        </svg>
                    </div>

                    <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-bold text-gray-800">{instructorBias.name}</span>
                            <span className="text-xs font-bold text-rose-500 bg-rose-100 px-1.5 py-0.5 rounded">
                                {instructorBias.biasScore} 편차
                            </span>
                        </div>
                        <p className="text-xs text-gray-600 leading-snug">
                            {instructorBias.note}
                        </p>
                    </div>
                </div>

                {/* Section E: Resource Plan */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                         <Clock className="w-4 h-4" /> 리소스 플랜 (4주)
                    </h3>
                    <ul className="space-y-4">
                        <li className="flex gap-3 text-sm text-gray-700">
                            <div className="w-2 h-2 rounded-full bg-[#FC6401] mt-1.5 shrink-0"></div>
                            <span>
                                구도 집중 실기 세션 <strong>+1.5시간</strong> 추가/주.
                            </span>
                        </li>
                        <li className="flex gap-3 text-sm text-gray-700">
                            <div className="w-2 h-2 rounded-full bg-gray-300 mt-1.5 shrink-0"></div>
                            <span>
                                '아이디어 발상' 소그룹 워크샵 배정 (학생 S.Y와 함께).
                            </span>
                        </li>
                    </ul>
                </div>

                {/* Section F: Consultation Agenda */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex-1 bg-gradient-to-b from-white to-[#FFF9F5]">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                         <ClipboardList className="w-4 h-4" /> 상담 아젠다
                    </h3>
                    <div className="space-y-5">
                        <div className="flex gap-3">
                            <div className="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] font-bold text-xs flex items-center justify-center shrink-0 border border-[#FC6401]/20">1</div>
                            <p className="text-sm text-gray-800 font-medium">
                                학업 성적은 안정적입니다. <span className="text-[#FC6401]">실기 "아이디어" 점수</span> 향상에 집중하세요.
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <div className="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] font-bold text-xs flex items-center justify-center shrink-0 border border-[#FC6401]/20">2</div>
                            <p className="text-sm text-gray-800 font-medium">
                                홍익대(상위) vs 이화여대(최상위) 전략적 선택 논의.
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <div className="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] font-bold text-xs flex items-center justify-center shrink-0 border border-[#FC6401]/20">3</div>
                            <p className="text-sm text-gray-800 font-medium">
                                최근 지각 패턴(2회) 점검.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* --- 3. Bottom: Workspace & Timeline (6/6 Split) --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* Evaluation Timeline (Updated with Academic Events) */}
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-gray-400" />
                    성적 변화 추이
                </h3>

                {/* --- Trend Chart --- */}
                {chartData.length > 1 ? (
                   <div className="h-48 w-full mb-8">
                      <ResponsiveContainer width="100%" height="100%">
                         <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                            <XAxis dataKey="date" tick={{fontSize: 10, fill: '#9ca3af'}} axisLine={false} tickLine={false} />
                            <YAxis domain={[50, 100]} hide />
                            <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 2px 5px rgba(0,0,0,0.1)'}} />
                            <Line type="monotone" dataKey="score" stroke="#FC6401" strokeWidth={3} dot={{r: 4, fill: '#FC6401', strokeWidth: 2, stroke: '#fff'}} />
                         </LineChart>
                      </ResponsiveContainer>
                   </div>
                ) : (
                   <div className="h-24 w-full mb-8 bg-gray-50 rounded-xl flex items-center justify-center text-gray-400 text-sm">
                      데이터가 충분하지 않습니다. (최소 2개 이상의 평가 필요)
                   </div>
                )}

                <div className="relative pl-5 border-l-2 border-gray-100 space-y-8">
                    
                    {/* Mock Academic Event (Inserted) */}
                    <div className="relative">
                        <div className="absolute -left-[27px] top-1 w-8 h-8 rounded-full bg-blue-50 border-4 border-white shadow-sm flex items-center justify-center">
                            <FileText className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex justify-between items-start mb-1">
                            <span className="text-sm font-bold text-blue-600">6월 모의고사</span>
                            <span className="text-xs text-gray-400">2026-06-04</span>
                        </div>
                        <div className="text-xs text-gray-500 mb-2 font-medium">학업 체크포인트</div>
                        <p className="text-sm text-gray-600 bg-blue-50 p-3 rounded-xl border border-blue-100">
                            성적 확인 완료. 수학 백분위가 소폭 하락(-2)했으나, 국어는 최상위권(99%) 유지.
                        </p>
                    </div>

                    {evaluations.map((ev, idx) => (
                        <div key={ev.id} className="relative">
                            <div className="absolute -left-[27px] top-1 w-8 h-8 rounded-full bg-[#FFF0E6] border-4 border-white shadow-sm flex items-center justify-center">
                                <Activity className="w-4 h-4 text-[#FC6401]" />
                            </div>
                            <div className="flex justify-between items-start mb-1">
                                <span className="text-sm font-bold text-gray-900">주간 평가 #{evaluations.length - idx}</span>
                                <span className="text-xs text-gray-400">{new Date(ev.date).toLocaleDateString()}</span>
                            </div>
                            <div className="text-xs text-gray-500 mb-2 font-medium">
                                점수: <span className="font-bold text-gray-700">{ev.totalScore}</span> ({ev.instructorId === 'i1' ? '한 강사' : '김 강사'})
                            </div>
                            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-xl border border-gray-100">
                                "{ev.notes}"
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* To-Do Checklist */}
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                        <CheckSquare className="w-5 h-5 text-gray-400" />
                        다음 할 일 (Next Actions)
                    </h3>
                    <button className="text-xs font-bold text-[#FC6401] hover:underline">+ 할 일 추가</button>
                </div>
                
                <div className="space-y-3 flex-1">
                    {todoList.map((todo) => (
                        <div 
                            key={todo.id} 
                            onClick={() => toggleTodo(todo.id)}
                            className={`p-4 rounded-xl border transition-all cursor-pointer flex items-center gap-4 group
                                ${todo.done ? 'bg-gray-50 border-gray-100' : 'bg-white border-gray-200 hover:border-[#FC6401]'}`}
                        >
                            <div className={`w-5 h-5 rounded-md border flex items-center justify-center transition-colors shrink-0
                                ${todo.done ? 'bg-emerald-500 border-emerald-500' : 'bg-white border-gray-300 group-hover:border-[#FC6401]'}`}>
                                {todo.done && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                            </div>
                            <div className="flex-1">
                                <span className={`text-sm font-medium block ${todo.done ? 'text-gray-400 line-through' : 'text-gray-800'}`}>
                                    {todo.text}
                                </span>
                            </div>
                            {todo.due && (
                                <span className="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-1 rounded">
                                    {todo.due}
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>

      </div>
    </div>
  );
};

export default StudentDetail;