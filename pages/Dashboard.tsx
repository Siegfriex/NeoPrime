import React, { useMemo } from 'react';
import { STUDENTS } from '../services/mockData';
import { 
  Users, 
  AlertTriangle, 
  FileText, 
  Target,
  Zap,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  TrendingDown,
  TrendingUp,
  Layout
} from 'lucide-react';
import { 
  ComposedChart, 
  Bar, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart,
  Area,
  LineChart
} from 'recharts';
import { Link } from 'react-router-dom';

// --- Types ---
interface UnivAggData {
  name: string;
  applicants: number;
  levels: { top: number; high: number; mid: number; low: number };
  predPassCount: number;
  predPassRate: number;
  lastYearPassRate: number; 
  riskLevel: 'High' | 'Mid' | 'Low';
  trend: { i: number; v: number }[]; // Updated for Recharts
}

const Dashboard: React.FC = () => {
  // --- 1. Data Aggregation & Logic ---

  // Global Context Targets (Mocked for 2026 Season)
  const SEASON_TARGET_PASS = 52; 
  const SEASON_CURRENT_PRED = 45; 

  // University Grouping Logic
  const univStats = useMemo(() => {
    const stats: Record<string, UnivAggData> = {};

    STUDENTS.forEach(s => {
      if (!stats[s.targetUniversity]) {
        // Mocking Last Year Data
        let lastYearRate = 70;
        // Mock Sparkline Data (5 points)
        let rawTrend = [65, 68, 70, 72, 73]; 

        if (s.targetUniversity.includes('Hongik')) {
             lastYearRate = 78;
             rawTrend = [78, 76, 75, 74, 72]; // Downward
        }
        if (s.targetUniversity.includes('SNU')) {
            lastYearRate = 65;
            rawTrend = [60, 62, 65, 68, 70]; // Upward
        }
        
        stats[s.targetUniversity] = { 
          name: s.targetUniversity.split(' ')[0], // Short name
          applicants: 0, 
          levels: { top: 0, high: 0, mid: 0, low: 0 },
          predPassCount: 0,
          predPassRate: 0,
          lastYearPassRate: lastYearRate,
          riskLevel: 'Low',
          trend: rawTrend.map((v, i) => ({ i, v }))
        };
      }
      
      const u = stats[s.targetUniversity];
      u.applicants += 1;
      
      // Categorize Level
      if (s.currentLevel === 'A+') u.levels.top += 1;
      else if (s.currentLevel === 'A') u.levels.high += 1;
      else if (s.currentLevel === 'B+') u.levels.mid += 1;
      else u.levels.low += 1;
    });

    // Calculate Predictions & Risk
    Object.values(stats).forEach(u => {
        const weightedScore = (u.levels.top * 1.0) + (u.levels.high * 0.8) + (u.levels.mid * 0.4) + (u.levels.low * 0.1);
        u.predPassCount = Math.round(weightedScore);
        u.predPassRate = Math.round((u.predPassCount / u.applicants) * 100);

        const gap = u.predPassRate - u.lastYearPassRate;
        const lowRatio = (u.levels.low + u.levels.mid) / u.applicants;
        
        if (gap < -10 || lowRatio > 0.6) u.riskLevel = 'High';
        else if (gap < -5 || lowRatio > 0.4) u.riskLevel = 'Mid';
        else u.riskLevel = 'Low';
    });

    return Object.values(stats).sort((a, b) => b.applicants - a.applicants).slice(0, 5); // Top 5
  }, []);

  // Cohort Seasonal Trend Data (Dual Line: 2025 vs 2026)
  const cohortSeasonalData = [
    { month: 'Mar', curScore: 72, prevScore: 70 },
    { month: 'Apr', curScore: 74, prevScore: 72 },
    { month: 'May', curScore: 75, prevScore: 73 },
    { month: 'Jun', curScore: 78, prevScore: 75 },
    { month: 'Jul', curScore: 80, prevScore: 77 },
    { month: 'Aug', curScore: 82, prevScore: 78 },
    { month: 'Sep', curScore: 85, prevScore: 80 },
    { month: 'Oct', curScore: 86, prevScore: 82 },
  ];

  // Critical Students
  const criticalStudents = STUDENTS.filter(s => s.currentLevel === 'C' || s.currentLevel === 'B').slice(0, 5);

  // --- Components ---

  const SeasonContextBar = () => {
    const progress = (SEASON_CURRENT_PRED / SEASON_TARGET_PASS) * 100;
    const gap = SEASON_CURRENT_PRED - SEASON_TARGET_PASS;
    
    return (
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-full flex flex-col justify-center">
        <div className="flex justify-between items-end mb-4">
            <div>
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide flex items-center gap-2">
                    <Calendar className="w-4 h-4" /> 2026 Season • Week 7
                </h3>
                <div className="flex items-baseline gap-3 mt-2">
                    <span className="text-4xl font-bold text-gray-900">{SEASON_CURRENT_PRED}</span>
                    <span className="text-sm font-medium text-gray-500">Predicted Accepted</span>
                    <span className="text-gray-300 mx-1">/</span>
                    <span className="text-xl font-bold text-gray-700">{SEASON_TARGET_PASS}</span>
                    <span className="text-sm text-gray-500">Goal</span>
                </div>
            </div>
            <div className={`text-right ${gap >= 0 ? 'text-emerald-600' : 'text-rose-500'}`}>
                <div className="text-3xl font-bold">{gap >= 0 ? '+' : ''}{gap}</div>
                <div className="text-xs font-bold uppercase">vs Target</div>
            </div>
        </div>
        {/* Progress Bar */}
        <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden">
            <div 
                className="absolute top-0 left-0 h-full bg-[#FC6401] rounded-full transition-all duration-1000" 
                style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
            <div className="absolute top-0 bottom-0 w-0.5 bg-gray-800 z-10" style={{ left: '80%' }}></div> 
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-400 font-medium">
            <span>Start</span>
            <span>Current Pace ({Math.round(progress)}%)</span>
            <span>Target</span>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full pb-12 animate-in fade-in duration-500">
      
      {/* 1. KPI Strip (Full Width) */}
      <div className="grid grid-cols-12 gap-6 mb-8">
          <div className="col-span-12 lg:col-span-8">
             <SeasonContextBar />
          </div>
          <div className="col-span-12 lg:col-span-2">
               <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-full flex flex-col justify-between">
                   <div className="flex justify-between items-start">
                       <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl"><Users className="w-6 h-6" /></div>
                       <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-100">+5% YoY</span>
                   </div>
                   <div>
                       <div className="text-3xl font-bold text-gray-900 mt-2">{STUDENTS.length}</div>
                       <div className="text-sm text-gray-500 font-medium">Active Students</div>
                   </div>
               </div>
          </div>
          <div className="col-span-12 lg:col-span-2">
               <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-full flex flex-col justify-between">
                   <div className="flex justify-between items-start">
                       <div className="p-2.5 bg-rose-50 text-rose-600 rounded-xl"><AlertTriangle className="w-6 h-6" /></div>
                       <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-100">Action Req</span>
                   </div>
                   <div>
                       <div className="text-3xl font-bold text-gray-900 mt-2">{criticalStudents.length}</div>
                       <div className="text-sm text-gray-500 font-medium">Risk Alerts</div>
                   </div>
               </div>
          </div>
      </div>

      {/* 2. Strategy & Gaps (8/4 Split) */}
      <div className="grid grid-cols-12 gap-6 mb-8">
        {/* Left: University Line Strategy (8 cols) */}
        <div className="col-span-12 lg:col-span-8 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h3 className="text-lg font-bold text-gray-900">University Line Distribution & Strategy</h3>
                    <p className="text-sm text-gray-500">Current applicant tiers vs Historical Pass Rates.</p>
                </div>
                <div className="flex gap-4 text-xs font-medium bg-gray-50 p-2 rounded-lg border border-gray-100">
                    <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-[#FC6401] rounded-sm"></div>Top</div>
                    <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-[#FEA267] rounded-sm"></div>High</div>
                    <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-[#FFC199] rounded-sm"></div>Mid</div>
                    <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-[#E5E7EB] rounded-sm"></div>Low</div>
                    <div className="w-px h-3 bg-gray-300 mx-1"></div>
                    <div className="flex items-center gap-1.5"><div className="w-4 h-0.5 bg-gray-800 border-t border-dashed border-gray-800"></div>Last Year Pass %</div>
                </div>
            </div>

            <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={univStats} margin={{ top: 10, right: 30, left: 0, bottom: 0 }} barSize={48}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 12, fontWeight: 600}} dy={10} />
                        <YAxis yAxisId="left" orientation="left" stroke="#9ca3af" axisLine={false} tickLine={false} />
                        <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" axisLine={false} tickLine={false} unit="%" />
                        <Tooltip 
                            cursor={{fill: '#F9FAFB'}}
                            contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                        />
                        <Bar yAxisId="left" dataKey="levels.top" stackId="a" fill="#FC6401" name="Top Tier" radius={[0, 0, 4, 4]} />
                        <Bar yAxisId="left" dataKey="levels.high" stackId="a" fill="#FEA267" name="High Tier" />
                        <Bar yAxisId="left" dataKey="levels.mid" stackId="a" fill="#FFC199" name="Mid Tier" />
                        <Bar yAxisId="left" dataKey="levels.low" stackId="a" fill="#E5E7EB" name="Low Tier" radius={[4, 4, 0, 0]} />
                        <Line yAxisId="right" type="monotone" dataKey="lastYearPassRate" stroke="#1f2937" strokeWidth={2} strokeDasharray="4 4" dot={{r:4, fill: '#1f2937'}} name="Last Year Pass Rate" />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </div>

        {/* Right: Strategy Gaps (4 cols) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
            <div className="bg-[#1F2937] p-8 rounded-2xl text-white shadow-lg relative overflow-hidden h-full flex flex-col">
                 <div className="absolute top-0 right-0 p-32 bg-[#FC6401] rounded-full blur-[80px] opacity-15"></div>
                 <div className="relative z-10 flex flex-col h-full">
                     <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                         <Target className="w-5 h-5 text-[#FC6401]" />
                         Strategy Gaps
                     </h3>
                     
                     <div className="space-y-8 flex-1">
                         <div className="pb-6 border-b border-gray-700/50 last:border-0 last:pb-0">
                             <div className="flex justify-between items-start mb-3">
                                <div className="text-sm font-bold text-[#FC6401] uppercase tracking-wide">Hongik Univ.</div>
                                <div className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-1 rounded border border-rose-500/20">-18%p Tier Gap</div>
                             </div>
                             
                             <p className="text-sm text-gray-300 font-medium leading-relaxed mb-4">
                                 Top/High tier applicant ratio is significantly lower than last year's acceptance pool.
                             </p>

                             <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                                        <span>2025 Acceptance Profile</span>
                                        <span>42% Top/High</span>
                                    </div>
                                    <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-emerald-500 w-[42%]"></div>
                                    </div>
                                </div>
                                
                                <div>
                                    <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                                        <span>2026 Current Profile</span>
                                        <span className="text-rose-400 font-bold">24% Top/High</span>
                                    </div>
                                    <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-[#FC6401] w-[24%]"></div>
                                    </div>
                                </div>
                             </div>
                             
                             <button className="text-xs text-[#FC6401] mt-6 font-bold hover:text-[#ff8a3d] transition-colors flex items-center gap-1">
                                View Mid-Tier Candidates <ArrowUpRight className="w-3 h-3" />
                             </button>
                         </div>
                     </div>
                 </div>
            </div>
        </div>
      </div>

      {/* 3. Risk Programs & Actions (8/4 Split) */}
      <div className="grid grid-cols-12 gap-6 mb-8">
          {/* Risk Programs Table (8 cols) */}
          <div className="col-span-12 lg:col-span-8 bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="font-bold text-gray-900">Risk Assessment by Program</h3>
                    <button className="text-xs font-bold text-gray-500 hover:text-[#FC6401]">View All</button>
                </div>
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-500 font-medium uppercase text-xs">
                        <tr>
                            <th className="px-6 py-4">University</th>
                            <th className="px-6 py-4">Applicants</th>
                            <th className="px-6 py-4">Pred. Pass %</th>
                            <th className="px-6 py-4">vs Last Year</th>
                            <th className="px-6 py-4">Recent Trend</th>
                            <th className="px-6 py-4 text-right">Risk Level</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {univStats.map((u) => {
                            const gap = u.predPassRate - u.lastYearPassRate;
                            const trendValues = u.trend.map(t => t.v);
                            const isTrendUp = trendValues[trendValues.length - 1] > trendValues[0];
                            return (
                                <tr key={u.name} className="hover:bg-gray-50/50 transition-colors group cursor-pointer">
                                    <td className="px-6 py-4 font-bold text-gray-900 flex items-center gap-2">
                                        {u.name}
                                    </td>
                                    <td className="px-6 py-4 text-gray-600">{u.applicants}</td>
                                    <td className="px-6 py-4 font-bold text-gray-900">{u.predPassRate}%</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1 font-bold ${gap >= 0 ? 'text-emerald-600' : 'text-rose-500'}`}>
                                            {gap >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                                            {Math.abs(gap)}%
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="h-8 w-24">
                                            <ResponsiveContainer width="100%" height="100%">
                                                <LineChart data={u.trend}>
                                                    <Line type="monotone" dataKey="v" stroke={isTrendUp ? '#10b981' : '#f43f5e'} strokeWidth={2} dot={false} />
                                                </LineChart>
                                            </ResponsiveContainer>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                                            u.riskLevel === 'High' ? 'bg-rose-50 text-rose-600 border-rose-100' :
                                            u.riskLevel === 'Mid' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                                            'bg-emerald-50 text-emerald-600 border-emerald-100'
                                        }`}>
                                            {u.riskLevel}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
          </div>

          {/* Action Queue (4 cols) */}
          <div className="col-span-12 lg:col-span-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-[#FC6401]" />
                        Action Queue
                    </h3>
                    <span className="text-xs font-bold bg-[#FC6401] text-white px-2 py-0.5 rounded-full">3 Pending</span>
                </div>
                
                <div className="space-y-3 flex-1">
                    <div className="flex gap-3 items-start p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-[#FC6401]/30 transition-colors cursor-pointer group">
                        <div className="mt-0.5">
                            <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-[#FC6401] focus:ring-[#FC6401]" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <span className="text-[10px] font-bold bg-rose-100 text-rose-600 px-1.5 py-0.5 rounded">P0</span>
                                <h4 className="text-sm font-bold text-gray-900 group-hover:text-[#FC6401] transition-colors">Hongik Idea Workshop</h4>
                            </div>
                            <p className="text-xs text-gray-500">Assign 'Mid' tier students (12) to specialized Idea generation session.</p>
                        </div>
                    </div>

                    <div className="flex gap-3 items-start p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-[#FC6401]/30 transition-colors cursor-pointer group">
                        <div className="mt-0.5">
                            <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-[#FC6401] focus:ring-[#FC6401]" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <span className="text-[10px] font-bold bg-amber-100 text-amber-600 px-1.5 py-0.5 rounded">P1</span>
                                <h4 className="text-sm font-bold text-gray-900 group-hover:text-[#FC6401] transition-colors">SNU Eval Check</h4>
                            </div>
                            <p className="text-xs text-gray-500">Review missing evaluations for 3 SNU candidates.</p>
                        </div>
                    </div>
                </div>
                
                <button className="w-full mt-4 py-3 text-xs font-bold text-gray-500 border border-dashed border-gray-300 rounded-xl hover:border-[#FC6401] hover:text-[#FC6401] transition-colors">
                    + Add Strategic Task
                </button>
          </div>
      </div>

      {/* 4. Bottom Row: Trend & Health (6/6 Split) */}
      <div className="grid grid-cols-12 gap-6">
          
          {/* Cohort Performance Trend (Dual Line) */}
          <div className="col-span-12 lg:col-span-6 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
              <div className="flex justify-between items-start mb-6">
                  <div>
                      <h3 className="font-bold text-gray-900 flex items-center gap-2">
                          <Activity className="w-5 h-5 text-gray-500" />
                          Cohort Performance Trend
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">Comparing 2026 Season (Current) vs 2025 Season (Past).</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-medium">
                        <div className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full bg-[#FC6401]"></span>
                            <span>2026 (Cur)</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <span className="w-6 h-0.5 bg-gray-400 border-t border-dashed border-gray-400"></span>
                            <span>2025 (Last Year)</span>
                        </div>
                   </div>
              </div>
              <div className="h-56 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={cohortSeasonalData} margin={{top: 5, right: 0, left: -20, bottom: 0}}>
                          <defs>
                              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#FC6401" stopOpacity={0.1}/>
                                  <stop offset="95%" stopColor="#FC6401" stopOpacity={0}/>
                              </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                          <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#6b7280'}} />
                          <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#6b7280'}} domain={[60, 90]} />
                          <Tooltip contentStyle={{borderRadius: '12px'}} />
                          <Area type="monotone" dataKey="curScore" name="2026 Avg" stroke="#FC6401" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
                          <Line type="monotone" dataKey="prevScore" name="2025 Avg" stroke="#9ca3af" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                      </AreaChart>
                  </ResponsiveContainer>
              </div>
              <div className="mt-4 flex gap-6 text-sm">
                  <div className="flex flex-col">
                      <span className="text-xs text-gray-400 font-bold uppercase">Current Avg</span>
                      <span className="font-bold text-gray-900 text-lg">86 pts <span className="text-emerald-500 text-xs">(+4)</span></span>
                  </div>
                  <div className="w-px h-10 bg-gray-200"></div>
                  <div className="flex flex-col">
                      <span className="text-xs text-gray-400 font-bold uppercase">Momentum</span>
                      <span className="font-bold text-emerald-600 text-lg flex items-center gap-1">
                          <TrendingUp className="w-4 h-4" /> Accelerating
                      </span>
                  </div>
              </div>
          </div>

          {/* Critical Students & Health (Split inside 6) */}
          <div className="col-span-12 lg:col-span-6 flex flex-col gap-6">
              
              {/* Critical Students List */}
              <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex-1">
                  <div className="flex justify-between items-center mb-4">
                      <h3 className="font-bold text-gray-900 flex items-center gap-2">
                          <AlertCircle className="w-5 h-5 text-rose-500" />
                          Critical Students
                      </h3>
                      <Link to="/students" className="text-xs font-bold text-gray-500 hover:text-[#FC6401]">View List</Link>
                  </div>
                  <div className="space-y-3">
                      {criticalStudents.slice(0, 3).map(s => (
                          <div key={s.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-white hover:shadow-sm hover:border-gray-200 border border-transparent transition-all group">
                              <div className="flex items-center gap-3">
                                  <img src={s.avatarUrl} className="w-10 h-10 rounded-full bg-white border border-gray-100" alt="" />
                                  <div>
                                      <div className="text-sm font-bold text-gray-900 group-hover:text-[#FC6401] transition-colors">{s.name}</div>
                                      <div className="text-xs text-gray-500">{s.targetUniversity} • Level {s.currentLevel}</div>
                                  </div>
                              </div>
                              <Link to={`/students/${s.id}`} className="p-2 bg-white border border-gray-200 rounded-lg text-gray-400 hover:text-[#FC6401] hover:border-[#FC6401] transition-all">
                                  <ChevronRight className="w-4 h-4" />
                              </Link>
                          </div>
                      ))}
                  </div>
              </div>

              {/* Data Health & Report Button */}
              <div className="grid grid-cols-2 gap-6">
                  <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
                      <div className="text-xs font-bold text-gray-400 uppercase mb-2">Data Health</div>
                      <div className="flex items-center gap-2 text-emerald-600 font-bold text-xl">
                          <CheckCircle2 className="w-5 h-5" /> 94% Valid
                      </div>
                      <div className="text-xs text-gray-400 mt-1 font-medium">12 evaluations missing this week</div>
                  </div>
                  <button className="bg-[#FC6401] hover:bg-[#e55a00] text-white p-5 rounded-2xl shadow-lg shadow-[#FC6401]/20 flex flex-col items-center justify-center transition-all active:scale-95 group">
                      <FileText className="w-6 h-6 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-sm font-bold">Generate Report</span>
                  </button>
              </div>

          </div>

      </div>

    </div>
  );
};

export default Dashboard;