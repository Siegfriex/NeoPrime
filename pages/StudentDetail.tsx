import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStudentById, getEvaluationsByStudentId } from '../services/mockData';
import { 
  ArrowLeft, ChevronLeft, ChevronRight, Target, Activity, 
  TrendingUp, Layers, AlertCircle, GraduationCap, 
  ArrowUpRight, ArrowDownRight, Minus, Users, 
  CheckCircle2, Calendar, Scale, ClipboardList, 
  MessageSquare, CheckSquare, Clock, BookOpen, AlertTriangle, FileText
} from 'lucide-react';

const StudentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const student = getStudentById(id || '');
  const evaluations = getEvaluationsByStudentId(id || '');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Worksheet State
  const [todoList, setTodoList] = useState([
    { id: 1, text: 'Schedule counseling on Ga/Na/Da selection strategy', done: false, due: '2d' },
    { id: 2, text: 'Assign "Idea Generation" supplementary workshop', done: true, due: 'Done' },
    { id: 3, text: 'Review academic score trend after June Mock Exam', done: false, due: '1w' },
  ]);

  if (!student) {
    return <div className="p-8 text-center text-gray-500">Student not found</div>;
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

  const latestEval = evaluations[evaluations.length - 1];

  const toggleTodo = (id: number) => {
    setTodoList(prev => prev.map(todo => todo.id === id ? { ...todo, done: !todo.done } : todo));
  };

  // --- Mock Analysis Data ---
  
  const strategyStatus = {
    badge: 'High Potential'
  };

  // Recruitment Group Strategy (Ga/Na/Da)
  const recruitmentStrategy = [
    { group: 'Ga', univ: 'SNU', line: 'Reach', prob: 35, color: 'bg-rose-500', text: 'text-rose-600' },
    { group: 'Na', univ: 'Hongik Univ.', line: 'Safe', prob: 78, color: 'bg-[#FC6401]', text: 'text-[#FC6401]' },
    { group: 'Da', univ: 'Ewha Womans', line: 'Top', prob: 92, color: 'bg-emerald-500', text: 'text-emerald-600' }
  ];

  // Academic Score Data Structure for Table
  const academicTableData = [
    { subject: 'Korean', student: student.academicScores.korean.standardScore, avg: 138, type: 'score' },
    { subject: 'English', student: student.academicScores.english.grade, avg: 1, type: 'grade' },
    { subject: 'Math', student: student.academicScores.math.standardScore, avg: 135, type: 'score' },
    { subject: 'Soc 1', student: student.academicScores.social1.standardScore, avg: 66, type: 'score' },
    { subject: 'Soc 2', student: student.academicScores.social2.standardScore, avg: 65, type: 'score' },
  ];

  const instructorBias = {
    name: 'Instructor Han',
    biasScore: -2.5,
    note: 'Han tends to grade "Tone" heavily; adjusted score likely ~86.5.'
  };

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
                            <span className="text-gray-400 font-bold text-xs uppercase">Target</span>
                        </span>
                        {recruitmentStrategy.map((strat, idx) => (
                            <div key={strat.group} className="flex items-center gap-2">
                                <span className="text-gray-500 font-bold text-xs">{strat.group}:</span>
                                <span className="font-bold text-gray-800">{strat.univ}</span>
                                <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold border uppercase ${
                                    strat.line === 'Safe' || strat.line === 'Top' 
                                    ? 'bg-emerald-50 text-emerald-600 border-emerald-100' 
                                    : strat.line === 'Reach' 
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
                     <div className="text-[10px] text-gray-400 uppercase font-bold tracking-wider mb-1">Current Level</div>
                     <div className={`text-2xl font-bold ${student.currentLevel.includes('A') ? 'text-[#FC6401]' : 'text-emerald-600'}`}>
                         {student.currentLevel}
                     </div>
                 </div>
                 <div className="h-10 w-px bg-gray-200 mx-2"></div>
                 <button className="flex items-center gap-2 bg-gray-900 text-white px-4 py-2.5 rounded-xl hover:bg-gray-800 transition-colors shadow-lg shadow-gray-900/10">
                    <MessageSquare className="w-4 h-4" />
                    <span className="text-sm font-bold">Start Consult</span>
                 </button>
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
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-5 flex items-center gap-2 tracking-wider">
                         <Activity className="w-4 h-4" /> Admission & Academic Position
                    </h3>
                    
                    {/* 1. Group Summary Bars */}
                    <div className="space-y-4 mb-8">
                        {recruitmentStrategy.map((strat) => (
                            <div key={strat.group} className="relative">
                                <div className="flex justify-between items-end mb-1.5">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-bold text-gray-500 w-5">{strat.group}</span>
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
                                    <th className="pb-2 font-medium pl-1">Subject</th>
                                    <th className="pb-2 font-medium text-right">Student</th>
                                    <th className="pb-2 font-medium text-right text-gray-400">Avg Admit</th>
                                    <th className="pb-2 font-medium text-right">Gap</th>
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
                                                {row.type === 'grade' && <span className="text-[9px] font-normal ml-0.5 text-gray-400">Gr</span>}
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
                            Overall academic index is <strong className="text-emerald-600">+4.5pts above</strong> the average admitted profile for Hongik (Na), and slightly below SNU (Ga) cutline in Math.
                        </p>
                        <p className="text-xs text-gray-600 leading-relaxed flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                            <span>Main academic risk is <strong>SNU Math score</strong>; others are within target ranges.</span>
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
                        {latestEval ? new Date(latestEval.date).toLocaleDateString() : 'No Date'}
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
                            </>
                        ) : (
                            <div className="text-gray-400 flex flex-col items-center">
                                <AlertCircle className="w-16 h-16 mb-4 opacity-20" />
                                <p>No artworks uploaded</p>
                            </div>
                        )}
                    </div>

                    {/* Evaluation Summary Footer */}
                    <div className="p-6 border-t border-gray-100 bg-white">
                        <div className="flex gap-6">
                            <div className="flex-1">
                                <h4 className="font-bold text-gray-900 text-sm mb-2">Director's Review Note</h4>
                                <p className="text-sm text-gray-500 leading-relaxed line-clamp-3">
                                    {latestEval?.notes || "No specific notes available for this artwork."}
                                </p>
                            </div>
                            <div className="flex gap-4 border-l border-gray-100 pl-6">
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">Comp</div>
                                    <div className="font-bold text-gray-900 text-lg">{latestEval?.scores.composition}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">Tone</div>
                                    <div className="font-bold text-gray-900 text-lg">{latestEval?.scores.tone}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">Idea</div>
                                    <div className="font-bold text-gray-900 text-lg">{latestEval?.scores.idea}</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-[10px] text-gray-400 uppercase font-bold">Total</div>
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
                         <Scale className="w-4 h-4" /> Instructor Bias Analysis
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
                            <span className="text-[10px] text-gray-500 font-bold mt-1">Raw</span>
                        </div>

                        {/* Adjusted Score */}
                        <div className="absolute top-1/2 left-[55%] -translate-y-1/2 -translate-x-1/2 flex flex-col items-center group">
                            <div className="w-3.5 h-3.5 rounded-full bg-[#FC6401] border-2 border-white shadow-sm z-10"></div>
                            <span className="text-[10px] text-[#FC6401] font-bold mt-1">Adj</span>
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
                                {instructorBias.biasScore} bias
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
                         <Clock className="w-4 h-4" /> Resource Plan (4 Weeks)
                    </h3>
                    <ul className="space-y-4">
                        <li className="flex gap-3 text-sm text-gray-700">
                            <div className="w-2 h-2 rounded-full bg-[#FC6401] mt-1.5 shrink-0"></div>
                            <span>
                                Add <strong>+1.5h</strong> practical session/week focusing on composition.
                            </span>
                        </li>
                        <li className="flex gap-3 text-sm text-gray-700">
                            <div className="w-2 h-2 rounded-full bg-gray-300 mt-1.5 shrink-0"></div>
                            <span>
                                Assign to 'Idea Generation' small group workshop (with student S.Y).
                            </span>
                        </li>
                    </ul>
                </div>

                {/* Section F: Consultation Agenda */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex-1 bg-gradient-to-b from-white to-[#FFF9F5]">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                         <ClipboardList className="w-4 h-4" /> Consult Agenda
                    </h3>
                    <div className="space-y-5">
                        <div className="flex gap-3">
                            <div className="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] font-bold text-xs flex items-center justify-center shrink-0 border border-[#FC6401]/20">1</div>
                            <p className="text-sm text-gray-800 font-medium">
                                Academic scores are stable above cut-off. Focus discussion on <span className="text-[#FC6401]">Practical "Idea" scores</span>.
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <div className="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] font-bold text-xs flex items-center justify-center shrink-0 border border-[#FC6401]/20">2</div>
                            <p className="text-sm text-gray-800 font-medium">
                                Discuss Hongik HIGH vs Ewha TOP strategic choice.
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <div className="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] font-bold text-xs flex items-center justify-center shrink-0 border border-[#FC6401]/20">3</div>
                            <p className="text-sm text-gray-800 font-medium">
                                Review recent attendance pattern (2 late arrivals).
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
                    Evaluation & Event Log
                </h3>
                <div className="relative pl-5 border-l-2 border-gray-100 space-y-8">
                    
                    {/* Mock Academic Event (Inserted) */}
                    <div className="relative">
                        <div className="absolute -left-[27px] top-1 w-8 h-8 rounded-full bg-blue-50 border-4 border-white shadow-sm flex items-center justify-center">
                            <FileText className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex justify-between items-start mb-1">
                            <span className="text-sm font-bold text-blue-600">June Mock Exam</span>
                            <span className="text-xs text-gray-400">2026-06-04</span>
                        </div>
                        <div className="text-xs text-gray-500 mb-2 font-medium">Academic Checkpoint</div>
                        <p className="text-sm text-gray-600 bg-blue-50 p-3 rounded-xl border border-blue-100">
                            Scores confirmed. Math percentile dropped slightly (-2), but Korean remains top tier (99%).
                        </p>
                    </div>

                    {evaluations.slice(0, 3).map((ev, idx) => (
                        <div key={ev.id} className="relative">
                            <div className="absolute -left-[27px] top-1 w-8 h-8 rounded-full bg-[#FFF0E6] border-4 border-white shadow-sm flex items-center justify-center">
                                <Target className="w-4 h-4 text-[#FC6401]" />
                            </div>
                            <div className="flex justify-between items-start mb-1">
                                <span className="text-sm font-bold text-gray-900">Weekly Eval #{evaluations.length - idx}</span>
                                <span className="text-xs text-gray-400">{new Date(ev.date).toLocaleDateString()}</span>
                            </div>
                            <div className="text-xs text-gray-500 mb-2 font-medium">
                                Score: <span className="font-bold text-gray-700">{ev.totalScore}</span> ({ev.instructorId === 'i1' ? 'Instr. Han' : 'Instr. Kim'})
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
                        Next Actions
                    </h3>
                    <button className="text-xs font-bold text-[#FC6401] hover:underline">+ Add Task</button>
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