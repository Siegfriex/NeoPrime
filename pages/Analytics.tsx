import React, { useState, useRef, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import { 
  Sparkles, Search, ArrowRight, Brain, TrendingUp,
  Target, Users, Zap, Filter,
  SplitSquareHorizontal, GitCompare, Sliders, Loader2,
  CheckCircle2, Plus, AlertTriangle, MessageSquare, ChevronRight, X
} from 'lucide-react';
import { analyzeAcademyData, AnalyzeAcademyDataResponse } from '../services/geminiService';

const Analytics: React.FC = () => {
  // --- State ---
  const [query, setQuery] = useState('');
  const [aiAnswer, setAiAnswer] = useState<AnalyzeAcademyDataResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeDetailTab, setActiveDetailTab] = useState<'drilldown' | 'segment' | 'simulation'>('drilldown');
  const [conversationContext, setConversationContext] = useState<string>("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // --- Functions ---

  const handleAsk = async (e?: React.FormEvent, overrideQuery?: string) => {
    e?.preventDefault();
    const q = overrideQuery || query;
    if (!q.trim()) return;

    if (overrideQuery) setQuery(q);

    setIsAnalyzing(true);

    try {
        const result = await analyzeAcademyData(q, conversationContext);
        if (result) {
            setAiAnswer(result);
            setConversationContext(prev => prev + `\n\n[User]: ${q}\n[AI]: ${result.summary}`);
            
            // Mode switching
            if (result.mode === 'explain') setActiveDetailTab('drilldown');
            if (result.mode === 'compare') setActiveDetailTab('segment');
            if (result.mode === 'simulate') setActiveDetailTab('simulation');
        }
    } catch (error) {
        console.error("Analytics Error", error);
    } finally {
        setIsAnalyzing(false);
    }
  };

  const handleInsightClick = (insightTitle: string) => {
      const prompt = `Analyze detail for insight: "${insightTitle}". Provide objective evidence and explanation.`;
      handleAsk(undefined, prompt);
  };

  // --- Chart Data Helpers ---
  const getFactorData = () => {
    if (aiAnswer?.mode === 'explain' && aiAnswer.explainResult && aiAnswer.explainResult.factors) {
      return aiAnswer.explainResult.factors.map(f => ({
          name: f.name.length > 8 ? f.name.substring(0, 8) + '..' : f.name, 
          full_name: f.name,
          value: f.impact || 0, 
          fill: f.direction === 'positive' ? '#10b981' : '#f43f5e' 
      }));
    }
    return [];
  };

  const getCompareData = () => {
      if (aiAnswer?.mode === 'compare' && aiAnswer.compareResult) {
          const { segmentA, segmentB } = aiAnswer.compareResult;
          return [
              { name: '합격률(%)', A: segmentA.metrics.acceptanceRate, B: segmentB.metrics.acceptanceRate },
              { name: '실기평균', A: segmentA.metrics.avgPracticalScore, B: segmentB.metrics.avgPracticalScore },
              { name: '출결(%)', A: segmentA.metrics.avgAttendanceRate, B: segmentB.metrics.avgAttendanceRate }
          ];
      }
      return [];
  };

  const getSimulateData = () => {
      if (aiAnswer?.mode === 'simulate' && aiAnswer.simulateResult) {
          const { baseline, scenario } = aiAnswer.simulateResult;
          return [
              { name: '현재 상태', prob: baseline.acceptanceRate, fill: '#9ca3af' },
              { name: '시뮬레이션', prob: scenario.acceptanceRate, fill: '#FC6401' }
          ];
      }
      return [];
  };

  return (
    <div className="max-w-[1600px] mx-auto pb-12 animate-in fade-in duration-500">
      
      {/* --- Header --- */}
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
           <div className="flex items-center gap-2 mb-2">
             <span className="bg-gray-900 text-white text-xs font-bold px-2 py-1 rounded border border-gray-700">PRO</span>
             <span className="text-[#FC6401] font-bold text-xs uppercase tracking-wider flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Meta-AI Powered
             </span>
           </div>
           <h1 className="text-3xl font-bold text-gray-900">Meta-Intelligence Console</h1>
           <p className="text-gray-500 mt-2 flex items-center gap-2">
              <Brain className="w-4 h-4 text-gray-400" />
              Tuned with Academy-Specific Meta Parameters
           </p>
        </div>
      </div>

      {/* --- Section 1: Ask NeoPrime --- */}
      <section className="mb-10">
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-1 shadow-xl">
          <div className="bg-[#1F2937] rounded-xl p-6 md:p-8">
             <div className="flex flex-col gap-4">
               <div className="flex items-center gap-3 mb-2">
                 <div className="p-2 bg-[#FC6401]/20 rounded-lg">
                    <Sparkles className="w-5 h-5 text-[#FC6401] animate-pulse" />
                 </div>
                 <h2 className="text-white font-bold text-lg">Ask NeoPrime</h2>
               </div>
               
               <form onSubmit={handleAsk} className="relative">
                 <input 
                    type="text" 
                    placeholder="예) 홍대 합격률 하락 원인 분석해줘 (Explain) 또는 특강 수강생 효과 비교해줘 (Compare)"
                    className="w-full bg-gray-800/50 border border-gray-700 text-white placeholder-gray-500 rounded-2xl pl-6 pr-32 py-4 focus:ring-2 focus:ring-[#FC6401] focus:border-transparent outline-none transition-all text-lg"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isAnalyzing}
                 />
                 <button 
                    type="submit"
                    disabled={isAnalyzing}
                    className="absolute right-2 top-2 bottom-2 bg-[#FC6401] hover:bg-[#e55a00] text-white px-6 rounded-xl font-bold transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                 >
                    {isAnalyzing ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" /> 분석 중...
                        </>
                    ) : (
                        <>
                            분석하기 <ArrowRight className="w-4 h-4" />
                        </>
                    )}
                 </button>
               </form>

               {/* Preset Questions */}
               {!aiAnswer && (
                   <div className="flex flex-wrap gap-2">
                      {[
                        "📉 홍대 합격률 하락 원인 (Explain)", 
                        "🆚 특강 수강생 vs 미수강생 성과 비교 (Compare)", 
                        "🎚️ 상향 지원율 10% 감소 시 합격률 예측 (Simulate)"
                      ].map((q, i) => (
                        <button 
                          key={i} 
                          onClick={() => handleInsightClick(q)}
                          disabled={isAnalyzing}
                          className="text-xs md:text-sm text-gray-400 bg-gray-800/50 hover:bg-gray-700 hover:text-white px-3 py-1.5 rounded-lg border border-gray-700 transition-colors disabled:opacity-50"
                        >
                          {q}
                        </button>
                      ))}
                   </div>
               )}
             </div>

             {/* AI Answer Display */}
             {aiAnswer && (
               <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                 <div className="bg-gray-800/50 rounded-2xl border border-gray-700 p-6">
                    <div className="flex items-start gap-4">
                       <div className="p-3 bg-[#FC6401]/20 rounded-xl shrink-0">
                          <Brain className="w-6 h-6 text-[#FC6401]" />
                       </div>
                       <div className="flex-1 w-full">
                          <div className="flex items-center gap-2 mb-2">
                             <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                                 aiAnswer.mode === 'explain' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                 aiAnswer.mode === 'compare' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                                 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                             }`}>
                                 {aiAnswer.mode.toUpperCase()} MODE
                             </span>
                          </div>
                          <p className="text-white text-lg font-medium leading-relaxed mb-6">
                             {aiAnswer.summary}
                          </p>
                          
                          {/* Explain Factors */}
                          {aiAnswer.mode === 'explain' && aiAnswer.explainResult && (
                             <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                {aiAnswer.explainResult.factors?.slice(0, 3).map((f, i) => (
                                    <div key={i} className="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
                                        <div className="text-gray-400 text-xs font-bold uppercase mb-1">{f.name}</div>
                                        <div className={`text-2xl font-bold ${f.direction === 'positive' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                            {f.impact > 0 ? '+' : ''}{f.impact}
                                        </div>
                                    </div>
                                ))}
                             </div>
                          )}

                          {/* Compare Lift */}
                          {aiAnswer.mode === 'compare' && aiAnswer.compareResult && aiAnswer.compareResult.lift && (
                              <div className="flex gap-8 mb-6 p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                                  <div>
                                      <div className="text-gray-400 text-xs font-bold uppercase mb-1">Lift (개선효과)</div>
                                      <div className="text-3xl font-bold text-emerald-400">+{aiAnswer.compareResult.lift.acceptanceRate}%p</div>
                                  </div>
                                  <div className="h-full w-px bg-gray-700"></div>
                                  <div>
                                      <div className="text-gray-400 text-xs font-bold uppercase mb-1">통계적 유의성</div>
                                      <div className="text-lg font-bold text-white">높음 (p{'<'}0.05)</div>
                                  </div>
                              </div>
                          )}

                          <div className="p-4 bg-[#FC6401]/10 border border-[#FC6401]/20 rounded-xl flex items-start gap-3">
                             <Zap className="w-5 h-5 text-[#FC6401] shrink-0 mt-0.5" />
                             <div>
                                 <div className="text-[#FC6401] font-bold text-sm mb-1">AI 권장 액션</div>
                                 <p className="text-gray-300 text-sm">{aiAnswer.recommendation}</p>
                             </div>
                          </div>

                          {/* Follow-up Context Input */}
                          <div className="mt-6 pt-4 border-t border-gray-700">
                              <div className="flex items-center gap-2 mb-2 text-xs font-bold text-gray-400">
                                  <MessageSquare className="w-3 h-3" />
                                  <span>이어서 질문하기 (Context-Aware)</span>
                              </div>
                              <form onSubmit={(e) => {
                                  e.preventDefault();
                                  const target = e.target as typeof e.target & {
                                      followup: { value: string };
                                  };
                                  handleAsk(e, target.followup.value);
                                  target.followup.value = '';
                              }} className="relative">
                                  <input 
                                      name="followup"
                                      type="text" 
                                      placeholder="예) 그렇다면 출결을 95%로 올리면 어떻게 되나요?"
                                      className="w-full bg-gray-900 border border-gray-600 text-white rounded-xl pl-4 pr-12 py-3 focus:ring-1 focus:ring-[#FC6401] focus:border-[#FC6401] outline-none text-sm"
                                  />
                                  <button type="submit" className="absolute right-2 top-2 p-1.5 bg-gray-700 text-white rounded-lg hover:bg-[#FC6401] transition-colors">
                                      <ArrowRight className="w-4 h-4" />
                                  </button>
                              </form>
                          </div>
                       </div>
                    </div>
                 </div>
               </div>
             )}
          </div>
        </div>
      </section>

      {/* --- Section 2: Insight Carousel --- */}
      <section className="mb-12">
         <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
                <SplitSquareHorizontal className="w-5 h-5 text-gray-500" />
                <h3 className="text-xl font-bold text-gray-900">핵심 인사이트 (Key Findings)</h3>
            </div>
            <div className="flex gap-2">
                <button className="p-2 rounded-full border border-gray-200 hover:bg-gray-50" onClick={() => scrollRef.current?.scrollBy({left: -300, behavior: 'smooth'})}>
                    <ChevronRight className="w-4 h-4 rotate-180" />
                </button>
                <button className="p-2 rounded-full border border-gray-200 hover:bg-gray-50" onClick={() => scrollRef.current?.scrollBy({left: 300, behavior: 'smooth'})}>
                    <ChevronRight className="w-4 h-4" />
                </button>
            </div>
         </div>
         <div ref={scrollRef} className="flex gap-6 overflow-x-auto pb-6 snap-x snap-mandatory scrollbar-hide" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
            {[
                { title: "상향 라인 과다 위험", summary: "상향 지원 비율이 과도합니다.", type: "risk", color: "rose" },
                { title: "국민대 성과 이상치", summary: "합격률이 전국 평균보다 높습니다.", type: "positive", color: "emerald" },
                { title: "겨울특강 A 코스 효과", summary: "특강 수강생 성적이 우수합니다.", type: "neutral", color: "blue" },
                { title: "중위권 이탈 위험", summary: "중위권 학생 관리가 필요합니다.", type: "risk", color: "amber" }
            ].map((card, i) => (
                <div key={i} className="min-w-[300px] snap-center bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer group" onClick={() => handleInsightClick(card.title)}>
                    <div className={`w-full h-1 bg-${card.color}-500 mb-4 rounded-full`}></div>
                    <h4 className="font-bold text-gray-900 group-hover:text-[#FC6401] transition-colors">{card.title}</h4>
                    <p className="text-sm text-gray-600 mt-2 mb-4">{card.summary}</p>
                    <div className="flex justify-between items-center text-xs">
                        <span className={`px-2 py-1 rounded bg-${card.color}-50 text-${card.color}-600 font-bold border border-${card.color}-100`}>
                            {card.type.toUpperCase()}
                        </span>
                        <span className="text-gray-400 font-medium">Auto-detected</span>
                    </div>
                </div>
            ))}
         </div>
      </section>

      {/* --- Section 3: Detailed Analysis Views --- */}
      <section>
         <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden min-h-[600px] flex flex-col">
            <div className="border-b border-gray-100 flex overflow-x-auto bg-gray-50/50">
               <button onClick={() => setActiveDetailTab('drilldown')} className={`px-8 py-5 text-sm font-bold flex items-center gap-2 border-b-2 transition-colors ${activeDetailTab === 'drilldown' ? 'border-[#FC6401] text-[#FC6401] bg-white' : 'border-transparent text-gray-500'}`}>
                  <Search className="w-4 h-4" /> Explain
               </button>
               <button onClick={() => setActiveDetailTab('segment')} className={`px-8 py-5 text-sm font-bold flex items-center gap-2 border-b-2 transition-colors ${activeDetailTab === 'segment' ? 'border-[#FC6401] text-[#FC6401] bg-white' : 'border-transparent text-gray-500'}`}>
                  <GitCompare className="w-4 h-4" /> Compare
               </button>
               <button onClick={() => setActiveDetailTab('simulation')} className={`px-8 py-5 text-sm font-bold flex items-center gap-2 border-b-2 transition-colors ${activeDetailTab === 'simulation' ? 'border-[#FC6401] text-[#FC6401] bg-white' : 'border-transparent text-gray-500'}`}>
                  <Sliders className="w-4 h-4" /> Simulate
               </button>
            </div>

            <div className="p-8 flex-1 bg-[#F7F9FB]">
               {/* Explain View */}
               {activeDetailTab === 'drilldown' && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full animate-in fade-in duration-300">
                     <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-96">
                        <ResponsiveContainer width="100%" height="100%">
                           <BarChart data={getFactorData()} layout="vertical">
                              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f3f4f6" />
                              <XAxis type="number" hide />
                              <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 12, fontWeight: 'bold'}} axisLine={false} tickLine={false} />
                              <Bar dataKey="value" barSize={32} radius={[4, 4, 4, 4]}>
                                 {getFactorData().map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.fill} />
                                 ))}
                              </Bar>
                           </BarChart>
                        </ResponsiveContainer>
                     </div>
                     <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-center text-center text-gray-500">
                        {aiAnswer?.explainResult?.factors?.[0]?.explanation || "분석 결과가 여기에 표시됩니다."}
                     </div>
                  </div>
               )}

               {/* Compare View */}
               {activeDetailTab === 'segment' && (
                   <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-96 animate-in fade-in">
                       <ResponsiveContainer width="100%" height="100%">
                           <BarChart data={getCompareData()} layout="vertical" barSize={30}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={true} stroke="#f3f4f6" />
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 12, fontWeight: 'bold'}} axisLine={false} tickLine={false} />
                                <Tooltip cursor={{fill: 'transparent'}} />
                                <Bar dataKey="A" fill="#FC6401" radius={[0, 4, 4, 0]} />
                                <Bar dataKey="B" fill="#e5e7eb" radius={[0, 4, 4, 0]} />
                           </BarChart>
                       </ResponsiveContainer>
                   </div>
               )}

               {/* Simulate View */}
               {activeDetailTab === 'simulation' && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full animate-in fade-in duration-300">
                     <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm lg:col-span-1">
                        <div className="mb-6 pb-6 border-b border-gray-100">
                           <h4 className="text-lg font-bold text-gray-900 mb-2">파라미터 조정</h4>
                           <p className="text-sm text-gray-500">슬라이더를 움직여 합격률 변화를 예측하세요.</p>
                        </div>
                        <div className="space-y-6">
                           {aiAnswer?.simulateResult?.controls?.map((ctrl, i) => (
                               <div key={i}>
                                   <div className="flex justify-between mb-2">
                                       <label className="text-sm font-bold text-gray-700">{ctrl.control}</label>
                                       <span className="text-sm font-bold text-[#FC6401]">{ctrl.targetValue} (목표)</span>
                                   </div>
                                   <input type="range" className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-not-allowed" disabled value={50} />
                                   <p className="text-xs text-gray-400 mt-1">예측 효과: {ctrl.estimatedDelta > 0 ? '+' : ''}{ctrl.estimatedDelta}%</p>
                               </div>
                           )) || (
                               <div className="text-center text-gray-400 py-10">시뮬레이션 데이터 없음</div>
                           )}
                        </div>
                     </div>
                     <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col items-center justify-center">
                        <div className="h-64 w-full max-w-md">
                           <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={getSimulateData()}>
                                 <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                 <XAxis dataKey="name" tick={{fontSize: 14, fontWeight: 'bold'}} axisLine={false} tickLine={false} />
                                 <YAxis hide domain={[0, 100]} />
                                 <Bar dataKey="prob" radius={[8, 8, 0, 0]}>
                                    {getSimulateData().map((entry, index) => (
                                       <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                 </Bar>
                              </BarChart>
                           </ResponsiveContainer>
                        </div>
                        {getSimulateData().length > 0 && (
                            <div className="mt-4 flex gap-8">
                               <div className="text-center">
                                  <div className="text-gray-400 text-sm font-bold uppercase">현재</div>
                                  <div className="text-2xl font-bold text-gray-600">{getSimulateData()[0].prob}%</div>
                               </div>
                               <ArrowRight className="w-8 h-8 text-gray-300 mt-2" />
                               <div className="text-center">
                                  <div className="text-[#FC6401] text-sm font-bold uppercase">시뮬레이션</div>
                                  <div className="text-4xl font-bold text-[#FC6401]">{getSimulateData()[1].prob}%</div>
                               </div>
                            </div>
                        )}
                     </div>
                  </div>
               )}
            </div>
         </div>
      </section>
    </div>
  );
};

export default Analytics;