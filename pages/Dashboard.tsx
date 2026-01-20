import React, { useMemo } from 'react';
import { STUDENTS, EVALUATIONS } from '../services/mockData';
import { 
  Users, 
  TrendingUp, 
  Award, 
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
  ChevronRight
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
  Cell,
  Legend,
  AreaChart,
  Area
} from 'recharts';
import { Link } from 'react-router-dom';

// --- Types ---
interface UnivAggData {
  name: string;
  applicants: number;
  levels: { top: number; high: number; mid: number; low: number };
  predPassCount: number;
  predPassRate: number;
  lastYearPassRate: number; // Mocked historical data
  riskLevel: 'High' | 'Mid' | 'Low';
}

const Dashboard: React.FC = () => {
  // --- 1. Data Aggregation & Logic ---

  // Global Context Targets (Mocked for 2026 Season)
  const SEASON_TARGET_PASS = 52; 
  const SEASON_CURRENT_PRED = 45; // Calculated below normally, but mocked for context

  // University Grouping Logic
  const univStats = useMemo(() => {
    const stats: Record<string, UnivAggData> = {};

    STUDENTS.forEach(s => {
      if (!stats[s.targetUniversity]) {
        // Mocking Last Year Data based on univ name for demo
        let lastYearRate = 70;
        if (s.targetUniversity.includes('Hongik')) lastYearRate = 78;
        if (s.targetUniversity.includes('SNU')) lastYearRate = 65;
        
        stats[s.targetUniversity] = { 
          name: s.targetUniversity.split(' ')[0], // Short name
          applicants: 0, 
          levels: { top: 0, high: 0, mid: 0, low: 0 },
          predPassCount: 0,
          predPassRate: 0,
          lastYearPassRate: lastYearRate,
          riskLevel: 'Low'
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
        // Simple prediction model
        const weightedScore = (u.levels.top * 1.0) + (u.levels.high * 0.8) + (u.levels.mid * 0.4) + (u.levels.low * 0.1);
        u.predPassCount = Math.round(weightedScore);
        u.predPassRate = Math.round((u.predPassCount / u.applicants) * 100);

        // Risk Logic: If Gap vs Last Year is large OR Low level ratio is high
        const gap = u.predPassRate - u.lastYearPassRate;
        const lowRatio = (u.levels.low + u.levels.mid) / u.applicants;
        
        if (gap < -10 || lowRatio > 0.6) u.riskLevel = 'High';
        else if (gap < -5 || lowRatio > 0.4) u.riskLevel = 'Mid';
        else u.riskLevel = 'Low';
    });

    return Object.values(stats).sort((a, b) => b.applicants - a.applicants).slice(0, 5); // Top 5
  }, []);

  // Cohort Trend Data (Mocked Year-over-Year)
  const cohortTrendData = [
    { year: '2024', avgScore: 82, passRate: 75 },
    { year: '2025', avgScore: 84, passRate: 78 },
    { year: '2026 (Cur)', avgScore: 86, passRate: 82 }, // Current projection
  ];

  // Critical Students (Mock Filter)
  const criticalStudents = STUDENTS.filter(s => s.currentLevel === 'C' || s.currentLevel === 'B').slice(0, 4);

  // --- Components ---

  const SeasonContextBar = () => {
    const progress = (SEASON_CURRENT_PRED / SEASON_TARGET_PASS) * 100;
    const gap = SEASON_CURRENT_PRED - SEASON_TARGET_PASS;
    
    return (
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm mb-6">
        <div className="flex justify-between items-end mb-3">
            <div>
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide flex items-center gap-2">
                    <Calendar className="w-4 h-4" /> 2026 Season • Week 7
                </h3>
                <div className="flex items-baseline gap-3 mt-1">
                    <span className="text-3xl font-bold text-gray-900">{SEASON_CURRENT_PRED}</span>
                    <span className="text-sm font-medium text-gray-500">Predicted Accepted</span>
                    <span className="text-gray-300">/</span>
                    <span className="text-lg font-bold text-gray-700">{SEASON_TARGET_PASS}</span>
                    <span className="text-sm text-gray-500">Goal</span>
                </div>
            </div>
            <div className={`text-right ${gap >= 0 ? 'text-emerald-600' : 'text-rose-500'}`}>
                <div className="text-2xl font-bold">{gap >= 0 ? '+' : ''}{gap}</div>
                <div className="text-xs font-bold uppercase">vs Target</div>
            </div>
        </div>
        {/* Progress Bar */}
        <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
            <div 
                className="absolute top-0 left-0 h-full bg-[#FC6401] rounded-full transition-all duration-1000" 
                style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
            {/* Target Marker */}
            <div className="absolute top-0 bottom-0 w-0.5 bg-gray-800 z-10" style={{ left: '80%' }}></div> 
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-400">
            <span>Start</span>
            <span className="pl-6">Current Pace ({Math.round(progress)}%)</span>
            <span>Target</span>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-[1600px] mx-auto pb-12 animate-in fade-in duration-500">
      
      {/* 1. Header & Season Context */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          {/* Season Context (2 Cols) */}
          <div className="lg:col-span-2">
             <SeasonContextBar />
          </div>

          {/* Quick KPIs (2 Cols) */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-4">
               <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                   <div className="flex justify-between items-start">
                       <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Users className="w-5 h-5" /></div>
                       <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">+5% YoY</span>
                   </div>
                   <div>
                       <div className="text-2xl font-bold text-gray-900 mt-2">{STUDENTS.length}</div>
                       <div className="text-xs text-gray-500 font-medium">Total Active Students</div>
                   </div>
               </div>
               <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                   <div className="flex justify-between items-start">
                       <div className="p-2 bg-rose-50 text-rose-600 rounded-lg"><AlertTriangle className="w-5 h-5" /></div>
                       <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded">Action Req</span>
                   </div>
                   <div>
                       <div className="text-2xl font-bold text-gray-900 mt-2">{criticalStudents.length}</div>
                       <div className="text-xs text-gray-500 font-medium">Critical Risk Alerts</div>
                   </div>
               </div>
          </div>
      </div>

      {/* 2. Main Strategy & Intelligence (Grid) */}
      <div className="grid grid-cols-12 gap-8 mb-8">
        
        {/* Left Col: Univ Intelligence (8 cols) */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-6">
            
            {/* Chart: Line Strategy vs Last Year */}
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h3 className="text-lg font-bold text-gray-900">University Line Distribution & Strategy</h3>
                        <p className="text-xs text-gray-500 mt-1">
                            Current applicant breakdown (Bars) vs. Last Year's Pass Rate (Line).
                            <br/>Identify gaps where applicant quality (Top/High) is lower than historical success rates.
                        </p>
                    </div>
                    <div className="flex gap-4 text-xs font-medium">
                        <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-[#FC6401] rounded-sm"></div>Top</div>
                        <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-[#FFC199] rounded-sm"></div>Mid/Low</div>
                        <div className="flex items-center gap-1.5"><div className="w-6 h-0.5 bg-gray-800"></div>Last Year Pass Rate</div>
                    </div>
                </div>

                <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={univStats} margin={{ top: 10, right: 30, left: 0, bottom: 0 }} barSize={40}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 12, fontWeight: 600}} dy={10} />
                            <YAxis yAxisId="left" orientation="left" stroke="#9ca3af" axisLine={false} tickLine={false} />
                            <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" axisLine={false} tickLine={false} unit="%" />
                            <Tooltip 
                                cursor={{fill: '#F9FAFB'}}
                                contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                            />
                            {/* Stacked Bars for Current Volume */}
                            <Bar yAxisId="left" dataKey="levels.top" stackId="a" fill="#FC6401" name="Top Tier" radius={[0, 0, 4, 4]} />
                            <Bar yAxisId="left" dataKey="levels.high" stackId="a" fill="#FEA267" name="High Tier" />
                            <Bar yAxisId="left" dataKey="levels.mid" stackId="a" fill="#FFC199" name="Mid Tier" />
                            <Bar yAxisId="left" dataKey="levels.low" stackId="a" fill="#E5E7EB" name="Low Tier" radius={[4, 4, 0, 0]} />
                            
                            {/* Line for Last Year Comparison */}
                            <Line yAxisId="right" type="monotone" dataKey="lastYearPassRate" stroke="#1f2937" strokeWidth={2} dot={{r:4}} name="Last Year Pass Rate" />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* University KPI Table */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-500 font-medium uppercase text-xs">
                        <tr>
                            <th className="px-6 py-4">University</th>
                            <th className="px-6 py-4">Applicants</th>
                            <th className="px-6 py-4">Pred. Pass Rate</th>
                            <th className="px-6 py-4">vs Last Year</th>
                            <th className="px-6 py-4 text-right">Risk Level</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {univStats.map((u) => {
                            const gap = u.predPassRate - u.lastYearPassRate;
                            return (
                                <tr key={u.name} className="hover:bg-gray-50/50 transition-colors group cursor-pointer">
                                    <td className="px-6 py-4 font-bold text-gray-900 flex items-center gap-2">
                                        {u.name}
                                        <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-[#FC6401] transition-colors" />
                                    </td>
                                    <td className="px-6 py-4 text-gray-600">{u.applicants}</td>
                                    <td className="px-6 py-4 font-bold text-gray-900">{u.predPassRate}%</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1 font-bold ${gap >= 0 ? 'text-emerald-600' : 'text-rose-500'}`}>
                                            {gap >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                                            {Math.abs(gap)}%
                                        </span>
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

        </div>

        {/* Right Col: Strategy & Action (4 cols) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
            
            {/* Gap Insights */}
            <div className="bg-[#1F2937] p-6 rounded-2xl text-white shadow-lg relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-24 bg-[#FC6401] rounded-full blur-3xl opacity-10"></div>
                 <div className="relative z-10">
                     <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                         <Target className="w-5 h-5 text-[#FC6401]" />
                         Strategy Gaps
                     </h3>
                     <div className="space-y-4">
                         <div className="pb-4 border-b border-gray-700 last:border-0 last:pb-0">
                             <div className="text-xs text-gray-400 mb-1">Hongik Univ.</div>
                             <p className="text-sm font-medium leading-relaxed">
                                 <span className="text-[#FC6401]">Alert:</span> Top/High tier ratio is <span className="text-rose-400">18% lower</span> than last year's acceptance pool.
                             </p>
                             <button className="text-xs text-[#FC6401] mt-2 hover:underline">View Mid-Tier List →</button>
                         </div>
                         <div>
                             <div className="text-xs text-gray-400 mb-1">SNU</div>
                             <p className="text-sm font-medium leading-relaxed">
                                 On track. Current profile matches 2024 success patterns. Maintain strategy.
                             </p>
                         </div>
                     </div>
                 </div>
            </div>

            {/* Recommended Actions */}
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex-1">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-[#FC6401]" />
                        Action Queue
                    </h3>
                    <span className="text-xs font-bold bg-[#FC6401] text-white px-2 py-0.5 rounded-full">3 Pending</span>
                </div>
                
                <div className="space-y-3">
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
                
                <button className="w-full mt-4 py-2 text-xs font-bold text-gray-500 border border-dashed border-gray-300 rounded-lg hover:border-[#FC6401] hover:text-[#FC6401] transition-colors">
                    + Add Strategic Task
                </button>
            </div>
        </div>
      </div>

      {/* 3. Bottom Row: Cohort & Health (Grid) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Bottom Left: Cohort Performance */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
              <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-gray-500" />
                  Cohort Performance Trend (YoY)
              </h3>
              <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={cohortTrendData} margin={{top: 5, right: 0, left: -20, bottom: 0}}>
                          <defs>
                              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#FC6401" stopOpacity={0.1}/>
                                  <stop offset="95%" stopColor="#FC6401" stopOpacity={0}/>
                              </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                          <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#6b7280'}} />
                          <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#6b7280'}} domain={[60, 100]} />
                          <Tooltip contentStyle={{borderRadius: '12px'}} />
                          <Area type="monotone" dataKey="avgScore" stroke="#FC6401" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
                      </AreaChart>
                  </ResponsiveContainer>
              </div>
              <div className="mt-4 flex gap-4 text-sm">
                  <div className="flex flex-col">
                      <span className="text-xs text-gray-400">Current Avg</span>
                      <span className="font-bold text-gray-900">86 pts <span className="text-emerald-500 text-xs">(+2)</span></span>
                  </div>
                  <div className="w-px h-8 bg-gray-200"></div>
                  <div className="flex flex-col">
                      <span className="text-xs text-gray-400">Line Upgrade</span>
                      <span className="font-bold text-gray-900">18 Students <span className="text-xs text-gray-500">shifted up</span></span>
                  </div>
              </div>
          </div>

          {/* Bottom Right: Risk & Health & Report */}
          <div className="flex flex-col gap-6">
              
              {/* Critical Students */}
              <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex-1">
                  <div className="flex justify-between items-center mb-4">
                      <h3 className="font-bold text-gray-900 flex items-center gap-2">
                          <AlertCircle className="w-5 h-5 text-rose-500" />
                          Critical Students
                      </h3>
                  </div>
                  <div className="space-y-3">
                      {criticalStudents.map(s => (
                          <div key={s.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                              <div className="flex items-center gap-3">
                                  <img src={s.avatarUrl} className="w-8 h-8 rounded-full bg-white" alt="" />
                                  <div>
                                      <div className="text-sm font-bold text-gray-900">{s.name}</div>
                                      <div className="text-xs text-gray-500">{s.targetUniversity} • Level {s.currentLevel}</div>
                                  </div>
                              </div>
                              <Link to={`/students/${s.id}`} className="p-1.5 bg-white border border-gray-200 rounded-lg hover:border-[#FC6401] text-gray-400 hover:text-[#FC6401] transition-colors">
                                  <ChevronRight className="w-4 h-4" />
                              </Link>
                          </div>
                      ))}
                  </div>
              </div>

              {/* Data Health & Report */}
              <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm">
                      <div className="text-xs font-bold text-gray-400 uppercase mb-1">Data Health</div>
                      <div className="flex items-center gap-2 text-emerald-600 font-bold">
                          <CheckCircle2 className="w-4 h-4" /> 94% Valid
                      </div>
                      <div className="text-[10px] text-gray-400 mt-1">12 evaluations missing this week</div>
                  </div>
                  <button className="bg-[#FC6401] hover:bg-[#e55a00] text-white p-4 rounded-2xl shadow-lg shadow-[#FC6401]/20 flex flex-col items-center justify-center transition-all active:scale-95">
                      <FileText className="w-6 h-6 mb-1" />
                      <span className="text-xs font-bold">Generate Report</span>
                  </button>
              </div>

          </div>

      </div>

    </div>
  );
};

export default Dashboard;