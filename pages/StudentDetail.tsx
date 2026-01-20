import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStudentById, getEvaluationsByStudentId } from '../services/mockData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { ArrowLeft, ChevronLeft, ChevronRight, Target, Activity, TrendingUp, Layers, AlertCircle, Maximize2, GraduationCap, ArrowUpRight, ArrowDownRight, Minus, ScrollText, Users, CheckCircle2, XCircle } from 'lucide-react';

const StudentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const student = getStudentById(id || '');
  const evaluations = getEvaluationsByStudentId(id || '');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

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

  const progressData = evaluations.map(e => ({
    date: new Date(e.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    score: e.totalScore
  }));

  const latestEval = evaluations[evaluations.length - 1];
  const radarData = latestEval ? [
    { subject: 'Composition', A: latestEval.scores.composition, fullMark: 10 },
    { subject: 'Tone', A: latestEval.scores.tone, fullMark: 10 },
    { subject: 'Idea', A: latestEval.scores.idea, fullMark: 10 },
    { subject: 'Attitude', A: latestEval.scores.completeness, fullMark: 10 },
  ] : [];

  const getDiff = (current: number | undefined, target: number | undefined) => {
    if (current === undefined || target === undefined) return null;
    return (current - target).toFixed(1);
  };

  const ScoreCard = ({ title, score, type, prevAvg, subtitle }: { title: string, score: any, type: 'std' | 'grade' | 'raw', prevAvg: any, subtitle?: string }) => {
    let mainValue = 0;
    let avgValue = 0;
    
    if (type === 'std') {
        mainValue = score.standardScore;
        avgValue = prevAvg.standardScore;
    } else if (type === 'grade') {
        mainValue = score.grade;
        avgValue = prevAvg.grade;
    } else {
        mainValue = score.rawScore;
        avgValue = prevAvg.rawScore; // Assuming raw for history
    }

    const diff = getDiff(mainValue, avgValue);
    const isPositive = type === 'grade' ? Number(diff) < 0 : Number(diff) > 0; 

    return (
        <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm flex flex-col items-center text-center relative overflow-hidden group hover:border-[#FC6401] hover:shadow-md transition-all">
            <div className={`absolute top-0 left-0 w-full h-1.5 ${isPositive ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">{title}</div>
            {subtitle && <div className="text-[10px] text-gray-400 mb-2 truncate max-w-[120px]">{subtitle}</div>}
            
            <div className="flex items-baseline justify-center gap-1 my-1">
                <span className="text-3xl font-bold text-gray-900">{mainValue}</span>
                <span className="text-xs text-gray-500 font-medium bg-gray-100 px-1.5 py-0.5 rounded">{type === 'std' ? 'Std' : type === 'grade' ? 'Grade' : 'Raw'}</span>
            </div>

            {score.percentile && (
                <div className="text-xs font-mono text-[#FC6401] font-bold mb-3">
                    Top {100 - score.percentile}%
                </div>
            )}

            <div className="w-full border-t border-gray-100 pt-3 mt-auto">
                <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-gray-400">Target Avg</span>
                    <span className="font-semibold text-gray-600">{avgValue}</span>
                </div>
                <div className={`flex justify-center items-center gap-1 text-xs font-bold ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {Number(diff) === 0 ? <Minus className="w-3 h-3" /> : isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {Math.abs(Number(diff))} {type === 'grade' ? '' : 'pts'}
                </div>
            </div>
        </div>
    );
  };
  
  return (
    <div className="min-h-screen font-sans pb-12 animate-in fade-in duration-500">
      {/* --- Top Navigation & Profile --- */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-20 z-10 px-8 py-4 shadow-sm mb-8 rounded-b-2xl">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-5">
                <Link to="/students" className="p-2.5 bg-gray-50 hover:bg-[#FFF0E6] text-gray-500 hover:text-[#FC6401] rounded-xl transition-colors">
                    <ArrowLeft className="w-5 h-5" />
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                        {student.name}
                        <span className="px-2.5 py-1 bg-[#FFF0E6] text-[#FC6401] text-xs font-bold rounded-lg border border-[#FC6401]/20 uppercase tracking-wide">
                            {student.grade}
                        </span>
                    </h1>
                    <p className="text-sm text-gray-500 flex items-center gap-2 mt-0.5">
                        <GraduationCap className="w-4 h-4 text-gray-400" />
                        Target: <span className="font-semibold text-gray-800">{student.targetUniversity}</span> 
                        <span className="text-gray-300">•</span> 
                        {student.major}
                    </p>
                </div>
            </div>
            
            <div className="flex items-center gap-8">
                 <div className="text-right hidden sm:block">
                     <div className="text-xs text-gray-400 uppercase font-bold tracking-wider mb-1">Current Level</div>
                     <div className={`text-3xl font-bold ${student.currentLevel.includes('A') ? 'text-[#FC6401]' : 'text-emerald-600'}`}>
                         {student.currentLevel}
                     </div>
                 </div>
                 <img src={student.avatarUrl} className="w-14 h-14 rounded-full border-4 border-white shadow-md" alt="profile" />
            </div>
          </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* --- SECTION 1: ACADEMIC SCORECARD --- */}
        <div>
            <h2 className="text-lg font-bold text-gray-900 mb-5 flex items-center gap-2">
                <div className="p-1.5 bg-[#FFF0E6] rounded-lg">
                    <Activity className="w-5 h-5 text-[#FC6401]" />
                </div>
                Academic Performance Analysis
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                <ScoreCard 
                    title="Korean" 
                    score={student.academicScores.korean} 
                    prevAvg={student.targetUnivAvgScores.korean}
                    type="std"
                />
                <ScoreCard 
                    title="English" 
                    score={student.academicScores.english} 
                    prevAvg={student.targetUnivAvgScores.english}
                    type="grade"
                />
                <ScoreCard 
                    title="Math" 
                    score={student.academicScores.math} 
                    prevAvg={student.targetUnivAvgScores.math}
                    type="std"
                />
                <ScoreCard 
                    title="Social 1" 
                    subtitle={student.academicScores.social1.subjectName}
                    score={student.academicScores.social1} 
                    prevAvg={student.targetUnivAvgScores.social1}
                    type="std"
                />
                <ScoreCard 
                    title="Social 2" 
                    subtitle={student.academicScores.social2.subjectName}
                    score={student.academicScores.social2} 
                    prevAvg={student.targetUnivAvgScores.social2}
                    type="std"
                />
            </div>
        </div>

        {/* --- SECTION 2: MAIN DASHBOARD GRID --- */}
        <div className="grid grid-cols-12 gap-8 min-h-[500px]">
            
            {/* Left Column: Admission & Radar (3 cols) */}
            <div className="col-span-12 lg:col-span-3 flex flex-col gap-8">
                
                {/* Admission Probability Enhanced */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm relative overflow-hidden flex flex-col h-full">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-6 flex items-center gap-2 tracking-wider">
                         Admission Probability
                    </h3>
                    <div className="flex-1 flex flex-col items-center justify-center py-2">
                        <div className="relative w-48 h-48 flex items-center justify-center mb-6">
                            {/* Outer ring */}
                            <svg className="w-full h-full transform -rotate-90">
                                <circle cx="96" cy="96" r="80" stroke="#F3F4F6" strokeWidth="16" fill="none" />
                                <circle cx="96" cy="96" r="80" stroke="#FC6401" strokeWidth="16" fill="none" strokeDasharray="502.65" strokeDashoffset={502.65 * (1 - 0.82)} className="transition-all duration-1000 ease-out drop-shadow-md" />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-5xl font-bold text-gray-900 tracking-tighter">82<span className="text-2xl">%</span></span>
                                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full mt-2">Safe</span>
                            </div>
                        </div>
                        
                        <div className="w-full space-y-4 mt-2 bg-gray-50 p-4 rounded-xl">
                             <div className="flex justify-between items-center text-xs">
                                <span className="text-gray-500 font-medium">Academic Gap</span>
                                <span className="font-bold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded">+4.5 pts</span>
                             </div>
                             <div className="flex justify-between items-center text-xs">
                                <span className="text-gray-500 font-medium">Practical Gap</span>
                                <span className="font-bold text-rose-500 bg-rose-100 px-2 py-0.5 rounded">-1.2 pts</span>
                             </div>
                             <div className="pt-3 border-t border-gray-200">
                                <p className="text-xs text-gray-600 text-center leading-relaxed">
                                    <span className="font-bold text-[#FC6401]">Tip:</span> Raising practical score to <strong>A0</strong> increases probability to <strong className="text-emerald-600">92%</strong>.
                                </p>
                             </div>
                        </div>
                    </div>
                </div>

                {/* Radar Chart */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex-1">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                         Skill Balance
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                <PolarGrid stroke="#e5e7eb" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 11, fontWeight: 600 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 10]} tick={false} axisLine={false} />
                                <Radar name="Student" dataKey="A" stroke="#FC6401" strokeWidth={3} fill="#FC6401" fillOpacity={0.2} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Center Column: Artwork Carousel (6 cols) */}
            <div className="col-span-12 lg:col-span-6">
                <div className="bg-white border border-gray-200 rounded-2xl shadow-sm h-full flex flex-col overflow-hidden relative group">
                    <div className="absolute top-6 left-6 z-10 bg-white/90 backdrop-blur px-4 py-1.5 rounded-full text-xs font-bold text-gray-800 shadow-sm border border-gray-200">
                        Weekly Artwork
                    </div>
                    <div className="flex-1 bg-[#F7F9FB] relative flex items-center justify-center p-8">
                        {hasImages ? (
                            <>
                                <img 
                                    src={student.artworks[currentImageIndex]} 
                                    alt="Artwork" 
                                    className="w-full h-full object-contain max-h-[600px] shadow-lg rounded-lg"
                                />
                                {/* Navigation Arrows */}
                                <button 
                                    onClick={prevImage}
                                    className="absolute left-6 top-1/2 -translate-y-1/2 p-3 bg-white hover:text-[#FC6401] text-gray-400 rounded-full shadow-xl opacity-0 group-hover:opacity-100 transition-all transform hover:scale-110"
                                >
                                    <ChevronLeft className="w-6 h-6" />
                                </button>
                                <button 
                                    onClick={nextImage}
                                    className="absolute right-6 top-1/2 -translate-y-1/2 p-3 bg-white hover:text-[#FC6401] text-gray-400 rounded-full shadow-xl opacity-0 group-hover:opacity-100 transition-all transform hover:scale-110"
                                >
                                    <ChevronRight className="w-6 h-6" />
                                </button>
                                
                                {/* Image Indicators */}
                                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex gap-2">
                                    {student.artworks.map((_, idx) => (
                                        <div 
                                            key={idx} 
                                            className={`w-2.5 h-2.5 rounded-full shadow-sm transition-all ${idx === currentImageIndex ? 'bg-[#FC6401] w-6' : 'bg-gray-300'}`} 
                                        />
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="text-gray-400 flex flex-col items-center">
                                <Maximize2 className="w-16 h-16 mb-4 opacity-20" />
                                <p>No artworks uploaded</p>
                            </div>
                        )}
                    </div>
                    <div className="p-6 border-t border-gray-100 bg-white">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="font-bold text-gray-900 text-sm mb-1.5">Evaluation #{evaluations.length - currentImageIndex} Notes</h4>
                                <p className="text-sm text-gray-500 leading-relaxed line-clamp-2 max-w-lg">{latestEval?.notes || "No notes available."}</p>
                            </div>
                            <div className="text-right pl-6 border-l border-gray-100">
                                <div className="text-[10px] text-gray-400 uppercase font-bold tracking-wide">Total Score</div>
                                <div className="text-3xl font-bold text-[#FC6401]">{latestEval?.totalScore || '-'}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Column: Weekly Report & Feedback (3 cols) */}
            <div className="col-span-12 lg:col-span-3 flex flex-col gap-8">
                
                {/* Growth Curve */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                     <h3 className="text-xs font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                        Weekly Growth
                    </h3>
                    <div className="h-40">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={progressData}>
                                <CartesianGrid stroke="#f3f4f6" strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 10}} />
                                <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 10}} />
                                <Tooltip 
                                    contentStyle={{backgroundColor: '#fff', borderColor: '#e5e7eb', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                                />
                                <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={3} dot={{r: 4, fill: '#10b981', strokeWidth: 2, stroke: '#fff'}} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* AI Feedback */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex-1 flex flex-col overflow-hidden">
                     <h3 className="text-xs font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                         AI Insights
                    </h3>
                    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-4">
                        {latestEval?.aiFeedback ? (
                            <>
                                <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100/50">
                                    <div className="text-xs font-bold text-emerald-700 mb-1 flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div> Strengths
                                    </div>
                                    <p className="text-xs text-emerald-800 leading-relaxed opacity-90">{latestEval.aiFeedback.strengths}</p>
                                </div>
                                <div className="p-4 bg-rose-50 rounded-xl border border-rose-100/50">
                                    <div className="text-xs font-bold text-rose-700 mb-1 flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-rose-500"></div> Weaknesses
                                    </div>
                                    <p className="text-xs text-rose-800 leading-relaxed opacity-90">{latestEval.aiFeedback.weaknesses}</p>
                                </div>
                                <div className="p-4 bg-[#FFF0E6] rounded-xl border border-[#FC6401]/10">
                                    <div className="text-xs font-bold text-[#FC6401] mb-1 flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-[#FC6401]"></div> Action Plan
                                    </div>
                                    <p className="text-xs text-orange-800 leading-relaxed opacity-90">{latestEval.aiFeedback.actionPlan}</p>
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-10">
                                <AlertCircle className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                                <p className="text-sm text-gray-400">No AI feedback generated yet.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>

        {/* --- SECTION 3: SIMILAR CASES --- */}
        {student.similarCases && student.similarCases.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden p-8">
                <div className="flex justify-between items-center mb-8">
                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                         <div className="p-1.5 bg-blue-50 rounded-lg">
                            <Users className="w-5 h-5 text-blue-600" />
                        </div>
                        Similar Cases Analysis
                    </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {student.similarCases.map((sc) => (
                        <div key={sc.id} className="border border-gray-200 rounded-xl p-5 hover:border-[#FC6401] hover:shadow-md transition-all group">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h4 className="font-bold text-gray-900">{sc.anonymizedName}</h4>
                                    <p className="text-xs text-gray-500">{sc.university} {sc.year}</p>
                                </div>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${
                                    sc.result === 'Accepted' ? 'bg-emerald-100 text-emerald-700' : 
                                    sc.result === 'Rejected' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                                }`}>
                                    {sc.result}
                                </span>
                            </div>
                            
                            <div className="space-y-2 mb-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-500">Match Rate</span>
                                    <span className="font-bold text-[#FC6401]">{sc.matchRate}%</span>
                                </div>
                                <div className="w-full bg-gray-100 rounded-full h-1.5">
                                    <div className="bg-[#FC6401] h-1.5 rounded-full" style={{ width: `${sc.matchRate}%` }}></div>
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-3 text-xs space-y-1 mb-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-500">Academic</span>
                                    <span className="font-medium text-gray-700">{sc.comparison.academic}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-500">Practical</span>
                                    <span className="font-medium text-gray-700">{sc.comparison.practical}</span>
                                </div>
                            </div>
                            
                            <p className="text-xs text-gray-500 italic border-t border-gray-100 pt-3">
                                "{sc.comparison.note}"
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        )}
      </div>
    </div>
  );
};

export default StudentDetail;