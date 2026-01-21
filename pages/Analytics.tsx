import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import { 
  Sparkles, Search, ArrowRight, Brain, TrendingUp, TrendingDown,
  Target, Users, Zap, Filter, Activity,
  GitCompare, Sliders, Loader2,
  CheckCircle2, AlertTriangle, ChevronRight, X,
  Layout, History, Bookmark, Share2, MoreHorizontal, Settings
} from 'lucide-react';
import { analyzeAcademyData, AnalyzeAcademyDataResponse } from '../services/geminiService';

// --- Types & Mock Data ---

interface KPICardProps {
  label: string;
  value: string;
  trend: string;
  trendValue: number;
  icon: React.ElementType;
}

const KPICard: React.FC<KPICardProps> = ({ label, value, trend, trendValue, icon: Icon }) => (
  <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between hover:border-[#FC6401]/30 transition-all">
    <div className="flex justify-between items-start mb-2">
      <div className="p-2 rounded-xl bg-gray-50 text-gray-500">
        <Icon className="w-4 h-4" />
      </div>
      <div className={`flex items-center gap-1 text-xs font-bold px-1.5 py-0.5 rounded ${trendValue >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
        {trendValue >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
        {trend}
      </div>
    </div>
    <div>
      <div className="text-2xl font-bold text-gray-900 tracking-tight">{value}</div>
      <div className="text-xs font-medium text-gray-400 mt-1 uppercase">{label}</div>
    </div>
  </div>
);

const Analytics: React.FC = () => {
  // --- State ---
  const [query, setQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<'explain' | 'compare' | 'simulate'>('explain');
  const [conversationContext, setConversationContext] = useState<string>("");
  const [showSessionHistory, setShowSessionHistory] = useState(false);
  
  // AI Response State
  const [aiData, setAiData] = useState<AnalyzeAcademyDataResponse | null>(null);

  // Simulation State
  const [simParams, setSimParams] = useState({
    riskRatio: 30,
    attendance: 85,
    lecture: 40
  });
  const [simResult, setSimResult] = useState({ current: 52, predicted: 52 });

  // --- Handlers ---

  const handleAsk = async (e?: React.FormEvent, overrideQuery?: string) => {
    e?.preventDefault();
    const q = overrideQuery || query;
    if (!q.trim()) return;

    if (overrideQuery) setQuery(q);
    setIsAnalyzing(true);

    try {
        const result = await analyzeAcademyData(q, conversationContext);
        if (result) {
            setAiData(result);
            setConversationContext(prev => prev + `\nQ: ${q}\nA: ${result.summary}`);
            if (result.mode) setActiveTab(result.mode);
        }
    } catch (error) {
        console.error("Analytics Error", error);
    } finally {
        setIsAnalyzing(false);
    }
  };

  const handleFindingClick = (text: string) => {
      handleAsk(undefined, `Insight 분석: "${text}"에 대해 자세히 설명해줘`);
  };

  // Real-time Simulation Mock Logic
  useEffect(() => {
    const base = 52;
    const riskEffect = (30 - simParams.riskRatio) * 0.5; 
    const attEffect = (simParams.attendance - 85) * 0.3;
    const lecEffect = (simParams.lecture - 40) * 0.2;
    setSimResult({
        current: 52,
        predicted: Math.min(99, Math.round(base + riskEffect + attEffect + lecEffect))
    });
  }, [simParams]);

  // --- Mock Data Helpers ---
  const explainData = aiData?.explainResult?.factors || [
    { name: '실기 평균', impact: 6.2, direction: 'positive' },
    { name: '출결율', impact: 2.1, direction: 'positive' },
    { name: '상향 지원', impact: -4.5, direction: 'negative' },
    { name: '수능 최저', impact: -1.8, direction: 'negative' },
    { name: '경쟁률', impact: -0.5, direction: 'negative' },
  ];

  const compareData = [
    { name: '합격률', A: 78, B: 45 },
    { name: '실기 A권', A: 60, B: 20 },
    { name: '출결 95%+', A: 92, B: 75 },
  ];

  return (
    <div className="min-h-screen bg-[#F7F8FA] font-sans text-gray-900 pb-12 relative animate-in fade-in duration-500">
      
      {/* ================= [1] COMMAND LAYER (Sticky Top) ================= */}
      <div className="sticky top-20 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
            
            {/* Main Search Bar Row */}
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-3 shrink-0">
                    <div className="w-10 h-10 bg-gray-900 rounded-xl flex items-center justify-center shadow-md">
                        <Brain className="w-5 h-5 text-[#FC6401]" />
                    </div>
                    <div className="hidden md:block">
                        <h1 className="text-lg font-bold text-gray-900 leading-none">Meta-Intelligence</h1>
                        <p className="text-[10px] text-gray-500 font-medium mt-1">AI Powered Console</p>
                    </div>
                </div>

                <div className="flex-1 max-w-3xl relative">
                    <form onSubmit={(e) => handleAsk(e)}>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <Sparkles className={`w-5 h-5 ${isAnalyzing ? 'text-[#FC6401] animate-pulse' : 'text-gray-400 group-focus-within:text-[#FC6401]'}`} />
                            </div>
                            <input 
                                type="text" 
                                className="w-full bg-gray-50 border border-gray-200 text-gray-900 text-sm rounded-2xl pl-11 pr-32 py-3.5 focus:ring-2 focus:ring-[#FC6401] focus:border-[#FC6401] focus:bg-white outline-none transition-all shadow-inner placeholder:text-gray-400 font-medium"
                                placeholder="무엇이든 물어보세요 (예: 홍대 합격률 하락 원인 Explain / 특강 효과 Compare)"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                disabled={isAnalyzing}
                            />
                            <div className="absolute right-2 top-2 bottom-2 flex gap-2">
                                <button 
                                    type="submit"
                                    disabled={!query.trim() || isAnalyzing}
                                    className="bg-[#FC6401] hover:bg-[#e55a00] text-white px-4 rounded-xl font-bold text-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-md shadow-[#FC6401]/20"
                                >
                                    {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Ask NeoPrime'}
                                </button>
                            </div>
                        </div>
                    </form>
                </div>

                <div className="flex items-center gap-3 ml-auto shrink-0">
                    <button 
                        onClick={() => setShowSessionHistory(!showSessionHistory)}
                        className={`p-2.5 rounded-xl border transition-colors ${showSessionHistory ? 'bg-gray-100 border-gray-300 text-gray-900' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}
                    >
                        <History className="w-5 h-5" />
                    </button>
                    <button className="p-2.5 bg-white border border-gray-200 text-gray-500 hover:bg-gray-50 rounded-xl transition-colors">
                        <Settings className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Context & Mode Sub-header */}
            <div className="flex items-center justify-between mt-4 pl-[3.25rem]">
                <div className="flex items-center gap-2">
                    {['2026 정시', '미대입시', '강남본원', '홍익대'].map((tag, i) => (
                        <button key={i} className="px-2.5 py-1 bg-white border border-gray-200 text-gray-600 text-xs font-bold rounded-lg hover:border-[#FC6401] hover:text-[#FC6401] transition-all">
                            {tag}
                        </button>
                    ))}
                    <div className="h-4 w-px bg-gray-300 mx-2"></div>
                    <button className="text-xs font-bold text-gray-400 hover:text-gray-600 flex items-center gap-1">
                        <Filter className="w-3 h-3" /> 필터 변경
                    </button>
                </div>

                <div className="flex bg-gray-100/50 p-1 rounded-lg border border-gray-200">
                    {[
                        { id: 'explain', label: 'Explain', icon: Search },
                        { id: 'compare', label: 'Compare', icon: GitCompare },
                        { id: 'simulate', label: 'Simulate', icon: Sliders },
                    ].map(mode => (
                        <button
                            key={mode.id}
                            onClick={() => setActiveTab(mode.id as any)}
                            className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-1.5 transition-all ${
                                activeTab === mode.id 
                                ? 'bg-white text-[#FC6401] shadow-sm ring-1 ring-black/5' 
                                : 'text-gray-500 hover:text-gray-900'
                            }`}
                        >
                            <mode.icon className="w-3 h-3" />
                            {mode.label}
                        </button>
                    ))}
                </div>
            </div>
        </div>
      </div>

      <div className="max-w-[1800px] mx-auto p-6 flex flex-col lg:flex-row gap-6">
        
        {/* ================= [2] INTELLIGENCE LAYER (Left 70%) ================= */}
        <div className="flex-1 space-y-6 min-w-0">
            
            {/* 2-1. Academy Pulse Strip */}
            <div className="space-y-3">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <KPICard label="예상 합격률" value="72%" trend="+4.2%p" trendValue={4.2} icon={Target} />
                    <KPICard label="재원생 수" value="142명" trend="+12%" trendValue={12} icon={Users} />
                    <KPICard label="위험군 학생" value="18명" trend="-5명" trendValue={5} icon={AlertTriangle} />
                    <KPICard label="상향 지원율" value="38%" trend="-2.1%p" trendValue={-2.1} icon={TrendingUp} />
                </div>
                {/* Pulse AI Summary */}
                <div className="bg-gray-100/50 rounded-xl px-4 py-3 flex items-start gap-3 border border-gray-200/50">
                    <Activity className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                    <p className="text-xs text-gray-600 font-medium leading-relaxed">
                        <strong className="text-gray-900">Pulse Insight:</strong> 전년 대비 합격률은 상승세(+4.2%p)이나, 상향 지원율이 여전히 높아(38%) 중위권 학생들의 리스크 관리가 필요합니다.
                    </p>
                </div>
            </div>

            {/* 2-2. Visual Analysis Panel */}
            <div className="bg-white rounded-3xl border border-gray-200 shadow-sm overflow-hidden flex flex-col min-h-[600px]">
                {/* Header */}
                <div className="px-8 py-6 border-b border-gray-100 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                            {activeTab === 'explain' && <Layout className="w-5 h-5 text-gray-400" />}
                            {activeTab === 'compare' && <GitCompare className="w-5 h-5 text-gray-400" />}
                            {activeTab === 'simulate' && <Sliders className="w-5 h-5 text-gray-400" />}
                            
                            {activeTab === 'explain' && "성과 요인 분석 (Waterfall)"}
                            {activeTab === 'compare' && "세그먼트 비교 분석"}
                            {activeTab === 'simulate' && "전략 시뮬레이터 (What-if)"}
                        </h2>
                        <p className="text-sm text-gray-500 mt-1">
                            {activeTab === 'explain' && "합격률 변화에 영향을 미친 긍정/부정 요인을 시각화합니다."}
                            {activeTab === 'compare' && "두 그룹 간의 성과 차이를 비교하여 특징을 도출합니다."}
                            {activeTab === 'simulate' && "주요 변수를 조정하여 예상 합격률 변화를 예측합니다."}
                        </p>
                    </div>
                    {/* Mode specific controls */}
                    {activeTab === 'explain' && (
                        <div className="flex gap-2">
                            <button className="px-3 py-1.5 text-xs font-bold bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200">전년 대비</button>
                            <button className="px-3 py-1.5 text-xs font-bold bg-white border border-gray-200 text-gray-400 rounded-lg hover:text-gray-600">목표 대비</button>
                        </div>
                    )}
                </div>

                {/* Content Body */}
                <div className="flex-1 p-8 bg-[#FDFDFD]">
                    
                    {/* MODE: EXPLAIN */}
                    {activeTab === 'explain' && (
                        <div className="h-full flex flex-col justify-center animate-in fade-in slide-in-from-bottom-2">
                            <div className="h-[400px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={explainData} layout="vertical" margin={{ left: 40, right: 40 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f3f4f6" />
                                        <XAxis type="number" hide domain={[-8, 8]} />
                                        <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 13, fontWeight: '600', fill: '#374151'}} axisLine={false} tickLine={false} />
                                        <Tooltip cursor={{fill: '#f9fafb'}} contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}} />
                                        <ReferenceLine x={0} stroke="#9ca3af" strokeWidth={2} />
                                        <Bar dataKey="impact" barSize={40} radius={[4, 4, 4, 4]}>
                                            {explainData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.direction === 'positive' ? '#10b981' : '#f43f5e'} cursor="pointer" />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="mt-8 grid grid-cols-3 gap-6">
                                <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                                    <div className="text-xs font-bold text-emerald-600 uppercase mb-1">최대 긍정 요인</div>
                                    <div className="font-bold text-gray-900">실기 평균 상승 (+6.2)</div>
                                    <p className="text-xs text-emerald-700/70 mt-1">A권대 학생 비중 15% 증가 기여</p>
                                </div>
                                <div className="p-4 bg-rose-50 rounded-xl border border-rose-100">
                                    <div className="text-xs font-bold text-rose-600 uppercase mb-1">최대 부정 요인</div>
                                    <div className="font-bold text-gray-900">상향 지원 과다 (-4.5)</div>
                                    <p className="text-xs text-rose-700/70 mt-1">소신 지원 비율 40% 초과로 상쇄</p>
                                </div>
                                <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-center">
                                    <button className="text-sm font-bold text-gray-500 hover:text-[#FC6401] flex items-center gap-2">
                                        세부 요인 더보기 <ChevronRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* MODE: COMPARE */}
                    {activeTab === 'compare' && (
                        <div className="h-full animate-in fade-in slide-in-from-bottom-2">
                            <div className="flex gap-4 mb-8">
                                <div className="flex-1 p-4 rounded-xl border-2 border-[#FC6401]/20 bg-[#FFF0E6]/10 flex justify-between items-center">
                                    <span className="text-sm font-bold text-gray-600">그룹 A: 특강 수강생</span>
                                    <span className="w-3 h-3 rounded-full bg-[#FC6401]"></span>
                                </div>
                                <div className="flex-1 p-4 rounded-xl border-2 border-gray-100 bg-gray-50 flex justify-between items-center">
                                    <span className="text-sm font-bold text-gray-600">그룹 B: 미수강생</span>
                                    <span className="w-3 h-3 rounded-full bg-gray-300"></span>
                                </div>
                            </div>
                            
                            <div className="h-[350px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={compareData} barSize={48} barGap={8}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                        <XAxis dataKey="name" tick={{fontSize: 12, fontWeight: 'bold', fill: '#4b5563'}} axisLine={false} tickLine={false} />
                                        <YAxis axisLine={false} tickLine={false} />
                                        <Tooltip cursor={{fill: '#f9fafb'}} contentStyle={{borderRadius: '12px'}} />
                                        <Bar dataKey="A" fill="#FC6401" radius={[6, 6, 0, 0]} name="특강 수강" />
                                        <Bar dataKey="B" fill="#E5E7EB" radius={[6, 6, 0, 0]} name="미수강" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-xl border border-gray-100">
                                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                <span>특강 수강 그룹의 합격률이 <strong className="text-[#FC6401]">+33%p</strong> 더 높습니다 (신뢰도 98%)</span>
                            </div>
                        </div>
                    )}

                    {/* MODE: SIMULATE */}
                    {activeTab === 'simulate' && (
                        <div className="h-full flex flex-col lg:flex-row gap-12 animate-in fade-in slide-in-from-bottom-2">
                            <div className="flex-1 space-y-8 py-4">
                                <div>
                                    <div className="flex justify-between mb-2">
                                        <label className="text-sm font-bold text-gray-700">상향 지원 비율 (Risk Tolerance)</label>
                                        <span className="text-sm font-bold text-[#FC6401]">{simParams.riskRatio}%</span>
                                    </div>
                                    <input 
                                        type="range" min="0" max="100" 
                                        value={simParams.riskRatio} 
                                        onChange={(e) => setSimParams({...simParams, riskRatio: parseInt(e.target.value)})}
                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#FC6401]" 
                                    />
                                    <div className="flex justify-between mt-1 text-[10px] text-gray-400 font-medium">
                                        <span>안정 지향 (Low)</span>
                                        <span>도전 지향 (High)</span>
                                    </div>
                                </div>

                                <div>
                                    <div className="flex justify-between mb-2">
                                        <label className="text-sm font-bold text-gray-700">출결 달성률 목표</label>
                                        <span className="text-sm font-bold text-blue-600">{simParams.attendance}%</span>
                                    </div>
                                    <input 
                                        type="range" min="50" max="100" 
                                        value={simParams.attendance} 
                                        onChange={(e) => setSimParams({...simParams, attendance: parseInt(e.target.value)})}
                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600" 
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between mb-2">
                                        <label className="text-sm font-bold text-gray-700">특강 수강률</label>
                                        <span className="text-sm font-bold text-emerald-600">{simParams.lecture}%</span>
                                    </div>
                                    <input 
                                        type="range" min="0" max="100" 
                                        value={simParams.lecture} 
                                        onChange={(e) => setSimParams({...simParams, lecture: parseInt(e.target.value)})}
                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600" 
                                    />
                                </div>
                            </div>

                            <div className="w-full lg:w-[320px] bg-gray-900 rounded-2xl p-8 flex flex-col items-center justify-center text-white relative overflow-hidden shadow-xl">
                                <div className="absolute top-0 right-0 p-24 bg-[#FC6401] rounded-full blur-[80px] opacity-20"></div>
                                <div className="relative z-10 text-center">
                                    <p className="text-sm text-gray-400 font-bold uppercase tracking-wider mb-6">Predicted Pass Rate</p>
                                    
                                    <div className="flex items-end justify-center gap-4 mb-2">
                                        <span className="text-3xl font-bold text-gray-500 line-through decoration-gray-500/50">{simResult.current}%</span>
                                        <ArrowRight className="w-6 h-6 text-gray-500 mb-2" />
                                        <span className="text-6xl font-bold text-[#FC6401]">{simResult.predicted}%</span>
                                    </div>
                                    
                                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold mt-4 ${
                                        simResult.predicted >= simResult.current ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                                    }`}>
                                        {simResult.predicted >= simResult.current ? '+' : ''}{simResult.predicted - simResult.current}%p 변동 예상
                                    </div>

                                    <button className="mt-8 w-full py-3 bg-white text-gray-900 rounded-xl font-bold text-sm hover:bg-gray-100 transition-colors shadow-lg">
                                        Action Queue에 시나리오 적용
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>

        {/* ================= [3] INSIGHT LAYER (Right 30%) ================= */}
        <div className="w-full lg:w-[380px] space-y-6 shrink-0">
            
            {/* 3-1. NeoPrime Insight (Sticky Note) */}
            <div className="bg-gradient-to-br from-[#FFF0E6] to-white p-6 rounded-2xl border border-[#FC6401]/20 shadow-sm sticky top-4">
                <div className="flex items-center gap-2 mb-4">
                    <div className="p-1.5 bg-[#FC6401] rounded-lg">
                        <Brain className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-bold text-[#FC6401] text-sm">NeoPrime Insight</span>
                </div>
                <div className="space-y-4">
                    <p className="text-sm text-gray-800 font-medium leading-relaxed">
                        {aiData?.summary || "전년 대비 합격률은 +4.2%p 상승했으며, 실기 평균 +6.2점이 주된 원인입니다. 다만 상향 지원 과다가 -4.5%p를 상쇄하고 있습니다."}
                    </p>
                    <div className="p-3 bg-white/60 rounded-xl border border-[#FC6401]/10">
                        <div className="flex items-center gap-2 mb-1">
                            <Zap className="w-3 h-3 text-[#FC6401]" />
                            <span className="text-xs font-bold text-gray-500 uppercase">권장 액션</span>
                        </div>
                        <p className="text-xs text-gray-700 font-bold">
                            {aiData?.recommendation || "상향 2개 이상 학생 9명의 라인 조정 상담을 우선 진행하세요."}
                        </p>
                    </div>
                </div>
            </div>

            {/* 3-2. Key Findings Cards */}
            <div>
                <div className="flex justify-between items-center mb-3 px-1">
                    <h3 className="text-xs font-bold text-gray-500 uppercase">Key Findings (Auto)</h3>
                    <span className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded text-gray-500">3 New</span>
                </div>
                <div className="space-y-3">
                    {[
                        { type: 'RISK', score: 85, title: '상향 라인 과다 위험', desc: '소신 지원 비율 40% 초과 구간 감지', color: 'rose' },
                        { type: 'OPPTY', score: 62, title: '국민대 실기 성과', desc: '평균 대비 +15% 성과 달성 중', color: 'emerald' },
                        { type: 'TREND', score: 78, title: '겨울특강 효과 검증', desc: 'A반 성적 급상승 패턴 확인', color: 'blue' },
                    ].map((item, i) => (
                        <div 
                            key={i} 
                            onClick={() => handleFindingClick(item.title)}
                            className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:border-[#FC6401] hover:shadow-md cursor-pointer transition-all group"
                        >
                            <div className="flex justify-between items-start mb-1.5">
                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
                                    item.color === 'rose' ? 'bg-rose-50 text-rose-600 border-rose-100' :
                                    item.color === 'emerald' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' :
                                    'bg-blue-50 text-blue-600 border-blue-100'
                                }`}>{item.type} {item.score}%</span>
                                <ArrowRight className="w-3 h-3 text-gray-300 group-hover:text-[#FC6401] transition-colors" />
                            </div>
                            <h4 className="text-sm font-bold text-gray-900 mb-1">{item.title}</h4>
                            <p className="text-xs text-gray-500">{item.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* 3-3. Risky Students List */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="px-4 py-3 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                    <h3 className="text-xs font-bold text-gray-500 uppercase">집중 관리 대상 (Top 5)</h3>
                    <button className="text-[10px] font-bold text-[#FC6401] hover:underline">전체보기</button>
                </div>
                <div className="divide-y divide-gray-100">
                    {['김민준', '이서연', '박지훈', '최예나', '정우성'].map((name, i) => (
                        <div key={i} className="px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors group">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-500">
                                    {name[0]}
                                </div>
                                <div>
                                    <div className="text-sm font-bold text-gray-900 leading-none mb-1">{name}</div>
                                    <div className="text-[10px] text-gray-400 font-medium">상향 과다 • 출결 위험</div>
                                </div>
                            </div>
                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button className="p-1.5 bg-[#FFF0E6] text-[#FC6401] rounded-lg hover:bg-[#FC6401] hover:text-white transition-colors" title="라인 조정">
                                    <Sliders className="w-3 h-3" />
                                </button>
                                <button className="p-1.5 bg-gray-100 text-gray-500 rounded-lg hover:bg-gray-200 transition-colors" title="상세 보기">
                                    <ChevronRight className="w-3 h-3" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

        </div>
      </div>

      {/* [4] Session History Slide-over (Optional Visual) */}
      {showSessionHistory && (
          <div className="fixed inset-y-0 left-0 w-80 bg-white shadow-2xl z-50 transform transition-transform duration-300 border-r border-gray-200 flex flex-col">
              <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                  <h3 className="font-bold text-gray-900">Session History</h3>
                  <button onClick={() => setShowSessionHistory(false)} className="text-gray-400 hover:text-gray-900"><X className="w-5 h-5"/></button>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                  <div className="text-xs font-bold text-gray-400 uppercase mb-4">Today</div>
                  <div className="space-y-4">
                      <div className="text-sm">
                          <p className="font-bold text-gray-900 mb-1">홍대 합격률 원인 분석</p>
                          <p className="text-xs text-gray-500 line-clamp-2">실기 평균 상승이 주된 원인으로 파악되었습니다...</p>
                      </div>
                      <div className="text-sm">
                          <p className="font-bold text-gray-900 mb-1">특강 효과 비교</p>
                          <p className="text-xs text-gray-500 line-clamp-2">수강생 그룹의 합격률이 33%p 더 높습니다...</p>
                      </div>
                  </div>
              </div>
              <div className="p-4 border-t border-gray-100 bg-gray-50 flex gap-2">
                  <button className="flex-1 py-2 bg-white border border-gray-200 rounded-xl text-xs font-bold text-gray-600 flex items-center justify-center gap-2 hover:bg-gray-50">
                      <Bookmark className="w-3 h-3" /> 저장
                  </button>
                  <button className="flex-1 py-2 bg-white border border-gray-200 rounded-xl text-xs font-bold text-gray-600 flex items-center justify-center gap-2 hover:bg-gray-50">
                      <Share2 className="w-3 h-3" /> 공유
                  </button>
              </div>
          </div>
      )}

    </div>
  );
};

export default Analytics;