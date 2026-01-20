import React, { useState, useMemo } from 'react';
import { 
  ComposedChart, 
  Line, 
  ScatterChart,
  Scatter, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  ReferenceLine,
  ZAxis,
  Area
} from 'recharts';
import { STUDENTS, EVALUATIONS } from '../services/mockData';
import { ChevronDown, ChevronUp, Users, User, School, TrendingUp, Target, Activity, Info, CheckCircle2, AlertTriangle } from 'lucide-react';
import { Student } from '../types';

// --- Helper Types & Generators ---

interface ChartPoint {
  date: number;
  dateStr: string;
  score: number;
  studentId: string;
  type: 'target' | 'avg';
  rankPercentile?: number; 
}

interface ScatterPoint {
  id: string;
  academic: number; 
  practical: number; 
  type: 'target' | 'peer';
}

interface AdmissionBaselines {
  academic: number;
  practical: number;
}

// Generate consistent cohort data
const generateCohortSnapshot = (univName: string, count: number = 30): { points: ScatterPoint[], baselines: AdmissionBaselines } => {
  const points: ScatterPoint[] = [];
  
  let baseAcad = 80;
  let basePrac = 80;
  
  if (univName.includes('SNU')) { baseAcad = 92; basePrac = 88; }
  else if (univName.includes('Hongik')) { baseAcad = 88; basePrac = 84; }
  else if (univName.includes('Ewha')) { baseAcad = 86; basePrac = 82; }
  
  for (let i = 0; i < count; i++) {
    points.push({
      id: `peer-${i}`,
      academic: Math.min(100, Math.max(50, baseAcad + (Math.random() * 25 - 15))),
      practical: Math.min(100, Math.max(50, basePrac + (Math.random() * 25 - 15))),
      type: 'peer'
    });
  }
  return { points, baselines: { academic: baseAcad, practical: basePrac } };
};

// Calculate trend lines
const calculateTrajectoryData = (studentId: string, cohortAvgBase: number) => {
  const studentEvals = EVALUATIONS.filter(e => e.studentId === studentId);
  const dataPoints: ChartPoint[] = [];

  // 1. Student Line
  studentEvals.forEach(e => {
    dataPoints.push({
      date: new Date(e.date).getTime(),
      dateStr: new Date(e.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      score: e.totalScore,
      studentId,
      type: 'target',
      rankPercentile: Math.max(1, Math.round(100 - ((e.totalScore - 60) / 40) * 100)) 
    });
  });

  // 2. Cohort Average Line
  if (dataPoints.length > 0) {
    const start = dataPoints[0].date;
    const end = dataPoints[dataPoints.length - 1].date;
    const steps = 5;
    const stepSize = (end - start) / steps;
    const startAvg = cohortAvgBase - 5; 

    for (let i = 0; i <= steps; i++) {
      const d = start + stepSize * i;
      const trendScore = startAvg + i; 
      dataPoints.push({
        date: d,
        dateStr: new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
        score: trendScore,
        studentId: 'avg',
        type: 'avg'
      });
    }
  }

  return dataPoints.sort((a, b) => a.date - b.date);
};

const Analytics: React.FC = () => {
  // State
  const [expandedUniv, setExpandedUniv] = useState<string | null>('Hongik Univ.');
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');

  // Group Students
  const groupedStudents = useMemo(() => {
    return STUDENTS.reduce((acc, student) => {
      const univ = student.targetUniversity;
      if (!acc[univ]) acc[univ] = [];
      acc[univ].push(student);
      return acc;
    }, {} as Record<string, Student[]>);
  }, []);

  // Toggle Accordion
  const toggleUniv = (univ: string) => {
    if (expandedUniv === univ) {
      setExpandedUniv(null);
    } else {
      setExpandedUniv(univ);
      const firstStudent = groupedStudents[univ]?.[0];
      if (firstStudent) setSelectedStudentId(firstStudent.id);
    }
  };

  // Selected Student Object
  const selectedStudent = useMemo(() => {
    return STUDENTS.find(s => s.id === selectedStudentId);
  }, [selectedStudentId]);

  // Chart Data Preparation
  const { trajectoryData, scatterData, percentileStats, admissionBaselines } = useMemo(() => {
    if (!expandedUniv || !selectedStudent) return { trajectoryData: [], scatterData: [], percentileStats: null, admissionBaselines: null };

    // 1. Snapshot Scatter Data & Baselines
    const { points: peers, baselines } = generateCohortSnapshot(expandedUniv);
    
    // Add current student
    const studentAcadAvg = selectedStudent.academicScores.korean.percentile || 80; 
    const studentEvals = EVALUATIONS.filter(e => e.studentId === selectedStudentId);
    const latestScore = studentEvals.length > 0 ? studentEvals[studentEvals.length - 1].totalScore : 75;

    const targetPoint: ScatterPoint = {
      id: selectedStudent.id,
      academic: studentAcadAvg,
      practical: latestScore,
      type: 'target'
    };

    const combinedScatter = [...peers, targetPoint];

    // 2. Trajectory Data
    const trajectory = calculateTrajectoryData(selectedStudentId, baselines.practical);

    // 3. Percentile Stats
    const sortedByPrac = [...combinedScatter].sort((a, b) => b.practical - a.practical);
    const rank = sortedByPrac.findIndex(p => p.type === 'target') + 1;
    const total = sortedByPrac.length;
    const percentile = Math.round(((total - rank) / total) * 100); 
    const topRankPercent = Math.round((rank / total) * 100);

    const values = sortedByPrac.map(p => p.practical);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const median = values[Math.floor(values.length / 2)];

    return {
      trajectoryData: trajectory,
      scatterData: combinedScatter,
      percentileStats: { rank, total, percentile, topRankPercent, min, max, median, score: latestScore },
      admissionBaselines: baselines
    };

  }, [expandedUniv, selectedStudent, selectedStudentId]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 w-full pb-20">
      
      {/* Header */}
      <div>
         <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Analytics Center</h1>
         <p className="text-gray-500 mt-2">Compare performance trajectories and cohort positioning.</p>
      </div>

      {/* University Accordions */}
      <div className="space-y-4">
        {Object.entries(groupedStudents).map(([univ, students]: [string, Student[]]) => {
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
                    <div className="hidden md:flex items-center gap-2 text-sm text-gray-500">
                        <Info className="w-4 h-4" />
                        <span>Viewing analysis against {univ} 2026 Cohort</span>
                    </div>
                  </div>

                  {/* Dashboard Grid */}
                  <div className="grid grid-cols-12 gap-6">

                    {/* 1. Trajectory Chart (Full Width Top - 12 cols) */}
                    <div className="col-span-12 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-[400px]">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5 text-[#FC6401]" />
                                    Performance Trajectory
                                </h4>
                                <p className="text-sm text-gray-500">Comparing your score growth vs. the admission baseline trend.</p>
                            </div>
                            <div className="flex items-center gap-4 text-xs font-medium">
                                <div className="flex items-center gap-1.5">
                                    <span className="w-3 h-3 rounded-full bg-[#FC6401]"></span>
                                    <span>You</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="w-6 h-0.5 bg-gray-300 border-t border-dashed border-gray-400"></span>
                                    <span>Admit Avg Trend</span>
                                </div>
                            </div>
                        </div>
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={trajectoryData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                    <XAxis 
                                        dataKey="date" 
                                        type="number" 
                                        domain={['dataMin', 'dataMax']} 
                                        tickFormatter={(t) => new Date(t).toLocaleDateString(undefined, {month:'short', day:'numeric'})}
                                        tick={{fontSize: 12, fill: '#9ca3af'}}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <YAxis 
                                        domain={[60, 100]} 
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{fontSize: 12, fill: '#9ca3af'}}
                                    />
                                    <Tooltip 
                                        labelFormatter={(t) => new Date(t).toLocaleDateString()}
                                        content={({ active, payload, label }: any) => {
                                            if (active && payload && payload.length) {
                                                const studentPoint = payload.find((p: any) => p.payload.type === 'target');
                                                const avgPoint = payload.find((p: any) => p.payload.type === 'avg');
                                                return (
                                                    <div className="bg-white p-3 border border-gray-200 shadow-lg rounded-xl text-xs">
                                                        <div className="font-bold text-gray-900 mb-2">{new Date(label).toLocaleDateString()}</div>
                                                        {studentPoint && (
                                                            <div className="flex items-center justify-between gap-4 mb-1">
                                                                <span className="text-gray-500">Score</span>
                                                                <span className="font-bold text-[#FC6401]">{studentPoint.value}</span>
                                                            </div>
                                                        )}
                                                        {avgPoint && (
                                                            <div className="flex items-center justify-between gap-4">
                                                                <span className="text-gray-500">Admit Baseline</span>
                                                                <span className="font-medium text-gray-600">{avgPoint.value}</span>
                                                            </div>
                                                        )}
                                                        {studentPoint?.payload.rankPercentile && (
                                                            <div className="mt-2 pt-2 border-t border-gray-100 font-bold text-emerald-600">
                                                                Top {100 - studentPoint.payload.rankPercentile}% Rank
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    <Line 
                                        dataKey="score" 
                                        data={trajectoryData.filter(d => d.type === 'avg')}
                                        stroke="#9ca3af" 
                                        strokeWidth={2} 
                                        strokeDasharray="5 5"
                                        dot={false}
                                        type="monotone"
                                    />
                                    <Line 
                                        dataKey="score" 
                                        data={trajectoryData.filter(d => d.type === 'target')}
                                        stroke="#FC6401" 
                                        strokeWidth={3} 
                                        dot={{r:5, fill:'#FC6401', stroke:'#fff', strokeWidth:2}}
                                        activeDot={{r:7}}
                                        type="monotone"
                                    />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* 2. Snapshot Scatter (Bottom Left - 6 cols) */}
                    <div className="col-span-12 lg:col-span-6 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-[350px]">
                        <div className="mb-6">
                            <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Target className="w-5 h-5 text-blue-600" />
                                Current Cohort Positioning
                            </h4>
                            <p className="text-sm text-gray-500">Practical (X) vs Academic (Y) with Admission Lines.</p>
                        </div>
                        <div className="h-[250px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                    <XAxis 
                                        type="number" 
                                        dataKey="practical" 
                                        name="Practical" 
                                        domain={[50, 100]} 
                                        tick={{fontSize: 10, fill: '#9ca3af'}}
                                        axisLine={false}
                                        tickLine={false}
                                        label={{ value: 'Practical Score', position: 'insideBottom', offset: -10, fontSize: 10, fill: '#9ca3af' }}
                                    />
                                    <YAxis 
                                        type="number" 
                                        dataKey="academic" 
                                        name="Academic" 
                                        domain={[50, 100]} 
                                        tick={{fontSize: 10, fill: '#9ca3af'}}
                                        axisLine={false}
                                        tickLine={false}
                                        label={{ value: 'Academic Score', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#9ca3af', offset: 0 }}
                                    />
                                    <ZAxis type="number" range={[60, 400]} />
                                    <Tooltip 
                                        cursor={{ strokeDasharray: '3 3' }} 
                                        content={({ active, payload }: any) => {
                                            if (active && payload && payload.length) {
                                                const data = payload[0].payload;
                                                return (
                                                    <div className="bg-white p-2 border border-gray-200 shadow-md rounded-lg text-xs z-50">
                                                        <div className={`font-bold ${data.type === 'target' ? 'text-[#FC6401]' : 'text-gray-700'}`}>
                                                            {data.type === 'target' ? 'You' : 'Peer'}
                                                        </div>
                                                        <div>Prac: {Math.round(data.practical)}</div>
                                                        <div>Acad: {Math.round(data.academic)}</div>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    {/* Peers */}
                                    <Scatter name="Cohort" data={scatterData.filter(d => d.type === 'peer')} fill="#cbd5e1" shape="circle" />
                                    {/* Target */}
                                    <Scatter name="You" data={scatterData.filter(d => d.type === 'target')} fill="#FC6401" shape="circle" />
                                    
                                    {/* Admission Benchmarks */}
                                    {admissionBaselines && (
                                        <>
                                            <ReferenceLine x={admissionBaselines.practical} stroke="#10b981" strokeDasharray="3 3">
                                                <text x={admissionBaselines.practical + 2} y={55} fill="#10b981" fontSize={10} fontWeight="bold">Avg Admit Prac</text>
                                            </ReferenceLine>
                                            <ReferenceLine y={admissionBaselines.academic} stroke="#10b981" strokeDasharray="3 3">
                                                <text x={55} y={admissionBaselines.academic - 5} fill="#10b981" fontSize={10} fontWeight="bold">Avg Admit Acad</text>
                                            </ReferenceLine>
                                        </>
                                    )}
                                </ScatterChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* 3. Percentile Summary (Bottom Right - 6 cols) */}
                    <div className="col-span-12 lg:col-span-6 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-[350px] flex flex-col">
                        <div className="mb-4">
                            <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-emerald-600" />
                                Rank & Distribution
                            </h4>
                            <p className="text-sm text-gray-500">Your standing vs Univ Benchmarks.</p>
                        </div>

                        {percentileStats && admissionBaselines && (
                            <div className="flex-1 flex flex-col justify-center">
                                {/* Text Summary */}
                                <div className="mb-6 bg-gray-50 rounded-xl p-4 border border-gray-100">
                                    <p className="text-sm text-gray-800 leading-relaxed">
                                        Among <span className="font-bold">{percentileStats.total}</span> tracked applicants for {univ}, 
                                        you are ranked <span className="font-bold text-[#FC6401]">#{percentileStats.rank}</span>.
                                    </p>
                                    <div className="mt-2 flex items-center gap-4">
                                        <div className="flex items-center gap-1.5">
                                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                            <span className="text-xs font-bold text-gray-600">Top {percentileStats.topRankPercent}%</span>
                                        </div>
                                        {percentileStats.score >= admissionBaselines.practical ? (
                                            <div className="flex items-center gap-1.5">
                                                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                                <span className="text-xs font-bold text-emerald-600">Above Cut-off</span>
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-1.5">
                                                <AlertTriangle className="w-4 h-4 text-amber-500" />
                                                <span className="text-xs font-bold text-amber-600">
                                                    -{admissionBaselines.practical - percentileStats.score} pts to Avg
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Visual Distribution Bar (Box Plot Simulation) */}
                                <div className="relative pt-8 pb-4 px-2">
                                    {/* Range Line */}
                                    <div className="absolute top-1/2 left-0 right-0 h-1.5 bg-gray-100 rounded-full"></div>
                                    
                                    {/* Min/Max Ticks */}
                                    <div className="absolute top-1/2 left-0 w-0.5 h-4 bg-gray-300 transform -translate-y-1/2"></div>
                                    <div className="absolute top-1/2 right-0 w-0.5 h-4 bg-gray-300 transform -translate-y-1/2"></div>
                                    
                                    {/* Admission Baseline Marker */}
                                    <div 
                                        className="absolute top-1/2 w-0.5 h-8 bg-emerald-500 transform -translate-y-1/2 z-0"
                                        style={{ left: `${((admissionBaselines.practical - percentileStats.min) / (percentileStats.max - percentileStats.min)) * 100}%` }}
                                    ></div>
                                    <div 
                                        className="absolute -top-8 text-[10px] text-emerald-600 font-bold transform -translate-x-1/2 whitespace-nowrap"
                                        style={{ left: `${((admissionBaselines.practical - percentileStats.min) / (percentileStats.max - percentileStats.min)) * 100}%` }}
                                    >
                                        Admit Avg ({admissionBaselines.practical})
                                    </div>

                                    {/* Target Student Marker */}
                                    <div 
                                        className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 flex flex-col items-center group cursor-pointer transition-all hover:scale-110 z-10"
                                        style={{ left: `${((percentileStats.score - percentileStats.min) / (percentileStats.max - percentileStats.min)) * 100}%` }}
                                    >
                                        <div className="w-4 h-4 rounded-full bg-[#FC6401] border-2 border-white shadow-md mb-1 relative z-10"></div>
                                        <div className="bg-[#FC6401] text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm">
                                            You
                                        </div>
                                    </div>

                                    {/* Labels */}
                                    <div className="absolute -bottom-6 left-0 text-[10px] text-gray-400 font-medium">Low ({Math.round(percentileStats.min)})</div>
                                    <div className="absolute -bottom-6 right-0 text-[10px] text-gray-400 font-medium">High ({Math.round(percentileStats.max)})</div>
                                </div>
                            </div>
                        )}
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