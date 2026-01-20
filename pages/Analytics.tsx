import React, { useState, useMemo } from 'react';
import { 
  ComposedChart, 
  Line, 
  Scatter, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  ReferenceLine,
  Legend
} from 'recharts';
import { STUDENTS, EVALUATIONS } from '../services/mockData';
import { ChevronDown, ChevronUp, Users, User, School, Filter, TrendingUp } from 'lucide-react';
import { Student } from '../types';

// --- Helper Types & Generators for Visualization ---

interface ChartPoint {
  date: number; // timestamp
  dateStr: string;
  score: number;
  studentId: string;
  type: 'target' | 'peer' | 'trend';
  name?: string;
}

// Helper to generate "Ghost" data to simulate a full cohort based on reference image
const generateMockCohortData = (univName: string, count: number = 50): ChartPoint[] => {
  const points: ChartPoint[] = [];
  const now = new Date().getTime();
  const threeMonthsAgo = now - 90 * 24 * 60 * 60 * 1000;

  for (let i = 0; i < count; i++) {
    const randomTime = threeMonthsAgo + Math.random() * (now - threeMonthsAgo);
    // Simulate scores somewhat correlated with time (slight upward trend generally)
    const timeProgress = (randomTime - threeMonthsAgo) / (now - threeMonthsAgo);
    const baseScore = 60 + (Math.random() * 20); // Random base between 60-80
    const growth = timeProgress * 15; // Up to 15 points growth
    const noise = (Math.random() * 10) - 5;
    
    points.push({
      date: randomTime,
      dateStr: new Date(randomTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      score: Math.min(100, Math.max(0, baseScore + growth + noise)),
      studentId: `ghost-${i}`,
      type: 'peer'
    });
  }
  return points.sort((a, b) => a.date - b.date);
};

// Simple Linear Regression for Trend Line
const calculateTrendLine = (data: ChartPoint[]) => {
  const n = data.length;
  if (n === 0) return [];

  const x = data.map(p => p.date);
  const y = data.map(p => p.score);

  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.map((k, i) => k * y[i]).reduce((a, b) => a + b, 0);
  const sumXX = x.map(k => k * k).reduce((a, b) => a + b, 0);

  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;

  const startX = Math.min(...x);
  const endX = Math.max(...x);

  return [
    { date: startX, score: slope * startX + intercept, type: 'trend' },
    { date: endX, score: slope * endX + intercept, type: 'trend' }
  ];
};


const Analytics: React.FC = () => {
  // State
  const [expandedUniv, setExpandedUniv] = useState<string | null>('Hongik Univ.'); // Default open
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [viewMode, setViewMode] = useState<'single' | 'cohort'>('cohort');

  // Group Students by University
  const groupedStudents = useMemo(() => {
    return STUDENTS.reduce((acc, student) => {
      const univ = student.targetUniversity;
      if (!acc[univ]) acc[univ] = [];
      acc[univ].push(student);
      return acc;
    }, {} as Record<string, Student[]>);
  }, []);

  // Handle Accordion Toggle
  const toggleUniv = (univ: string) => {
    if (expandedUniv === univ) {
      setExpandedUniv(null);
    } else {
      setExpandedUniv(univ);
      // Automatically select the first student of that univ
      const firstStudent = groupedStudents[univ]?.[0];
      if (firstStudent) setSelectedStudentId(firstStudent.id);
    }
  };

  // Prepare Chart Data based on selection
  const chartData = useMemo(() => {
    if (!expandedUniv || !selectedStudentId) return { points: [], trend: [] };

    // 1. Get Target Student Data (Real Data)
    const studentEvals = EVALUATIONS.filter(e => e.studentId === selectedStudentId);
    const targetPoints: ChartPoint[] = studentEvals.map(e => ({
      date: new Date(e.date).getTime(),
      dateStr: new Date(e.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      score: e.totalScore,
      studentId: selectedStudentId,
      type: 'target',
      name: 'My Score'
    }));

    let allPoints = [...targetPoints];
    let trendLineData: any[] = [];

    // 2. If Cohort Mode, generate peer data
    if (viewMode === 'cohort') {
      const peerPoints = generateMockCohortData(expandedUniv);
      allPoints = [...peerPoints, ...targetPoints];
      
      // Calculate Trend Line based on Peers + Target
      trendLineData = calculateTrendLine(allPoints);
    } else {
      // Single mode trend is just the student's own trajectory
      trendLineData = calculateTrendLine(targetPoints);
    }

    // Sort by date for proper X-Axis rendering
    allPoints.sort((a, b) => a.date - b.date);

    return { points: allPoints, trend: trendLineData };
  }, [expandedUniv, selectedStudentId, viewMode]);


  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-6xl mx-auto pb-20">
      
      {/* Header */}
      <div>
         <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Analytics Center</h1>
         <p className="text-gray-500 mt-2">Deep dive into time-series performance and cohort comparison.</p>
      </div>

      {/* University Accordions */}
      <div className="space-y-4">
        {Object.entries(groupedStudents).map(([univ, data]) => {
          const students = data as Student[];
          const isExpanded = expandedUniv === univ;
          
          return (
            <div key={univ} className={`bg-white border transition-all duration-300 overflow-hidden ${isExpanded ? 'border-[#FC6401] shadow-lg ring-1 ring-[#FC6401]/20 rounded-2xl' : 'border-gray-200 hover:border-gray-300 rounded-xl'}`}>
              
              {/* Accordion Header */}
              <button 
                onClick={() => toggleUniv(univ)}
                className="w-full flex items-center justify-between p-6 bg-white hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl transition-colors ${isExpanded ? 'bg-[#FFF0E6] text-[#FC6401]' : 'bg-gray-100 text-gray-500'}`}>
                    <School className="w-6 h-6" />
                  </div>
                  <div className="text-left">
                    <h3 className={`text-lg font-bold ${isExpanded ? 'text-gray-900' : 'text-gray-700'}`}>{univ}</h3>
                    <p className="text-sm text-gray-500">{students.length} Applicants Tracked</p>
                  </div>
                </div>
                {isExpanded ? <ChevronUp className="w-5 h-5 text-[#FC6401]" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
              </button>

              {/* Accordion Content */}
              {isExpanded && (
                <div className="border-t border-gray-100 bg-[#F7F9FB] p-6">
                  
                  {/* Toolbar */}
                  <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    
                    {/* Student Selector */}
                    <div className="flex items-center gap-3 w-full md:w-auto">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <User className="w-4 h-4 text-gray-600" />
                      </div>
                      <select 
                        className="bg-transparent font-semibold text-gray-900 outline-none w-full md:w-48 cursor-pointer"
                        value={selectedStudentId}
                        onChange={(e) => setSelectedStudentId(e.target.value)}
                      >
                        {students.map(s => (
                          <option key={s.id} value={s.id}>{s.name}</option>
                        ))}
                      </select>
                    </div>

                    {/* View Mode Toggle */}
                    <div className="flex bg-gray-100 p-1 rounded-lg w-full md:w-auto">
                      <button 
                        onClick={() => setViewMode('single')}
                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${viewMode === 'single' ? 'bg-white text-[#FC6401] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                      >
                        <User className="w-4 h-4" />
                        Single View
                      </button>
                      <button 
                        onClick={() => setViewMode('cohort')}
                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${viewMode === 'cohort' ? 'bg-white text-[#FC6401] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                      >
                        <Users className="w-4 h-4" />
                        Cohort Comparison
                      </button>
                    </div>
                  </div>

                  {/* Chart Container */}
                  <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm relative min-h-[500px]">
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                          <TrendingUp className="w-5 h-5 text-[#FC6401]" />
                          Performance Trajectory
                        </h4>
                        <p className="text-sm text-gray-500">
                          {viewMode === 'single' 
                            ? "Analyzing individual growth over time." 
                            : "Comparing student performance against the applicant cohort."}
                        </p>
                      </div>
                      <div className="flex items-center gap-4 text-xs font-medium">
                         <div className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full bg-[#FC6401]"></span>
                            <span className="text-gray-700">Selected Student</span>
                         </div>
                         {viewMode === 'cohort' && (
                           <>
                            <div className="flex items-center gap-1.5">
                                <span className="w-3 h-3 rounded-full bg-gray-300/50 border border-gray-400"></span>
                                <span className="text-gray-500">Cohort</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <span className="w-6 h-0.5 bg-blue-400"></span>
                                <span className="text-blue-500">Avg. Trend</span>
                            </div>
                           </>
                         )}
                      </div>
                    </div>

                    <div className="w-full h-[400px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart
                          data={chartData.points}
                          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
                          <XAxis 
                            dataKey="date" 
                            type="number"
                            domain={['dataMin', 'dataMax']}
                            tickFormatter={(unixTime) => new Date(unixTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                            tick={{ fontSize: 12, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                            dy={10}
                          />
                          <YAxis 
                            domain={[0, 100]} 
                            tick={{ fontSize: 12, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                            label={{ value: 'Score', angle: -90, position: 'insideLeft', fill: '#9ca3af', fontSize: 12 }}
                          />
                          <Tooltip 
                            cursor={{ strokeDasharray: '3 3' }}
                            labelFormatter={(label) => new Date(label).toLocaleDateString()}
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                          />

                          {/* Cohort Scatter Points (Ghost Data) */}
                          {viewMode === 'cohort' && (
                            <Scatter 
                              name="Cohort" 
                              data={chartData.points.filter(p => p.type === 'peer')} 
                              fill="#9ca3af" 
                              fillOpacity={0.3}
                              shape="circle"
                            />
                          )}

                          {/* Trend Line (Regression) */}
                          {viewMode === 'cohort' && (
                             <Line
                                data={chartData.trend}
                                dataKey="score"
                                stroke="#60a5fa" 
                                strokeWidth={3}
                                strokeDasharray="5 5"
                                dot={false}
                                activeDot={false}
                                type="monotone"
                                isAnimationActive={true}
                             />
                          )}

                          {/* Target Student Line & Points */}
                          <Line
                            data={chartData.points.filter(p => p.type === 'target')}
                            type="monotone"
                            dataKey="score"
                            stroke="#FC6401"
                            strokeWidth={3}
                            dot={{ r: 6, fill: '#FC6401', stroke: '#fff', strokeWidth: 2 }}
                            activeDot={{ r: 8, stroke: '#FC6401', strokeWidth: 4 }}
                            connectNulls
                          />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Footer Insight */}
                    <div className="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-200 flex items-start gap-3">
                        <div className="p-1.5 bg-white rounded-md border border-gray-200 shadow-sm mt-0.5">
                            <TrendingUp className="w-4 h-4 text-[#FC6401]" />
                        </div>
                        <div>
                            <h5 className="text-sm font-bold text-gray-900">Analysis Summary</h5>
                            <p className="text-sm text-gray-600 mt-1 leading-relaxed">
                                {viewMode === 'cohort' 
                                  ? `The selected student is tracking within the top percentile of the ${expandedUniv} applicant cohort. The trend line indicates a consistent upward trajectory compared to the peer average.`
                                  : `Showing individual progress over the current semester. Evaluation consistency has improved by 15% since the initial assessment.`
                                }
                            </p>
                        </div>
                    </div>

                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Analytics;