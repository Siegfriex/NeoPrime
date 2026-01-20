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
import { ChevronDown, ChevronUp, Users, User, School, TrendingUp, Target, Activity, Info, CheckCircle2 } from 'lucide-react';
import { Student } from '../types';

// --- Helper Types & Generators ---

interface ChartPoint {
  date: number;
  dateStr: string;
  score: number;
  studentId: string;
  type: 'target' | 'avg';
  rankPercentile?: number; // Calculated for the target
}

interface ScatterPoint {
  id: string;
  academic: number; // Y-axis
  practical: number; // X-axis
  type: 'target' | 'peer';
}

// Generate consistent cohort data for a session
const generateCohortSnapshot = (univName: string, count: number = 30): ScatterPoint[] => {
  const points: ScatterPoint[] = [];
  
  // Baseline scores based on Univ tier (mock logic)
  let baseAcad = 80;
  let basePrac = 80;
  
  if (univName.includes('서울대')) { baseAcad = 92; basePrac = 88; }
  else if (univName.includes('홍익')) { baseAcad = 88; basePrac = 84; }
  else if (univName.includes('이화')) { baseAcad = 86; basePrac = 82; }
  
  for (let i = 0; i < count; i++) {
    points.push({
      id: `peer-${i}`,
      // Randomize around the baseline with some variance
      academic: Math.min(100, Math.max(50, baseAcad + (Math.random() * 20 - 10))),
      practical: Math.min(100, Math.max(50, basePrac + (Math.random() * 20 - 10))),
      type: 'peer'
    });
  }
  return points;
};

// Calculate trend lines for Trajectory Chart
const calculateTrajectoryData = (studentId: string) => {
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
      // Mock percentile calculation: correlated with score roughly
      rankPercentile: Math.max(1, Math.round(100 - ((e.totalScore - 60) / 40) * 100)) 
    });
  });

  // 2. Cohort Average Line
  // Mocking a smooth curve generally slightly lower or higher depending on student
  if (dataPoints.length > 0) {
    const start = dataPoints[0].date;
    const end = dataPoints[dataPoints.length - 1].date;
    const steps = 5;
    const stepSize = (end - start) / steps;
    
    // Cohort starts at 75 and ends at 85 (linear growth mock)
    for (let i = 0; i <= steps; i++) {
      const d = start + stepSize * i;
      const trendScore = 75 + (i * 2); 
      
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
  const [expandedUniv, setExpandedUniv] = useState<string | null>('홍익대');
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
  const { trajectoryData, scatterData, percentileStats } = useMemo(() => {
    if (!expandedUniv || !selectedStudent) return { trajectoryData: [], scatterData: [], percentileStats: null };

    // 1. Snapshot Scatter Data
    const peers = generateCohortSnapshot(expandedUniv);
    
    // Add current student to scatter
    // Using mock average of academic scores for Y-axis (Standard Score or Percentile)
    const studentAcadAvg = selectedStudent.academicScores.korean.percentile || 80; 
    // Using latest eval total score for X-axis
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
    const trajectory = calculateTrajectoryData(selectedStudentId);

    // 3. Percentile Stats (Based on Scatter Practical Score)
    // Sort all by practical
    const sortedByPrac = [...combinedScatter].sort((a, b) => b.practical - a.practical);
    const rank = sortedByPrac.findIndex(p => p.type === 'target') + 1;
    const total = sortedByPrac.length;
    const percentile = Math.round(((total - rank) / total) * 100); 
    const topRankPercent = Math.round((rank / total) * 100);

    // Stats for distribution bar
    const values = sortedByPrac.map(p => p.practical);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const median = values[Math.floor(values.length / 2)];

    return {
      trajectoryData: trajectory,
      scatterData: combinedScatter,
      percentileStats: { rank, total, percentile, topRankPercent, min, max, median, score: latestScore }
    };

  }, [expandedUniv, selectedStudent, selectedStudentId]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto pb-20">
      
      {/* Header */}
      <div>
         <h1 className="text-3xl font-bold text-gray-900 tracking-tight">데이터 분석 센터</h1>
         <p className="text-gray-500 mt-2">학생의 성과 추이와 코호트 내 위치를 비교 분석합니다.</p>
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
                    <p className="text-sm text-gray-500">{students.length}명 데이터 추적 중</p>
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
                        <span>{univ} 2026 합격 코호트와 비교 중</span>
                    </div>
                  </div>

                  {/* Dashboard Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* 1. Trajectory Chart (Full Width Top) */}
                    <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-[400px]">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5 text-[#FC6401]" />
                                    성과 추이 그래프
                                </h4>
                                <p className="text-sm text-gray-500">본인의 점수 상승세 vs 코호트 평균 성장세 비교</p>
                            </div>
                            <div className="flex items-center gap-4 text-xs font-medium">
                                <div className="flex items-center gap-1.5">
                                    <span className="w-3 h-3 rounded-full bg-[#FC6401]"></span>
                                    <span>본인</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="w-6 h-0.5 bg-gray-300 border-t border-dashed border-gray-400"></span>
                                    <span>코호트 평균</span>
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
                                                                <span className="text-gray-500">점수</span>
                                                                <span className="font-bold text-[#FC6401]">{studentPoint.value}</span>
                                                            </div>
                                                        )}
                                                        {avgPoint && (
                                                            <div className="flex items-center justify-between gap-4">
                                                                <span className="text-gray-500">코호트 평균</span>
                                                                <span className="font-medium text-gray-600">{avgPoint.value}</span>
                                                            </div>
                                                        )}
                                                        {studentPoint?.payload.rankPercentile && (
                                                            <div className="mt-2 pt-2 border-t border-gray-100 font-bold text-emerald-600">
                                                                상위 {100 - studentPoint.payload.rankPercentile}% 랭크
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

                    {/* 2. Snapshot Scatter (Bottom Left) */}
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-[350px]">
                        <div className="mb-6">
                            <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Target className="w-5 h-5 text-blue-600" />
                                스냅샷: 코호트 내 위치
                            </h4>
                            <p className="text-sm text-gray-500">실기(X) vs 학업(Y) 분포도</p>
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
                                        label={{ value: '실기 점수', position: 'insideBottom', offset: -10, fontSize: 10, fill: '#9ca3af' }}
                                    />
                                    <YAxis 
                                        type="number" 
                                        dataKey="academic" 
                                        name="Academic" 
                                        domain={[50, 100]} 
                                        tick={{fontSize: 10, fill: '#9ca3af'}}
                                        axisLine={false}
                                        tickLine={false}
                                        label={{ value: '학업 점수', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#9ca3af', offset: 0 }}
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
                                                            {data.type === 'target' ? '본인' : '경쟁자'}
                                                        </div>
                                                        <div>실기: {Math.round(data.practical)}</div>
                                                        <div>학업: {Math.round(data.academic)}</div>
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
                                    
                                    {/* Reference Lines (Mock Admission Cut-offs) */}
                                    <ReferenceLine x={85} stroke="#10b981" strokeDasharray="3 3">
                                        <text x={87} y={55} fill="#10b981" fontSize={10} fontWeight="bold">실기 컷</text>
                                    </ReferenceLine>
                                    <ReferenceLine y={88} stroke="#10b981" strokeDasharray="3 3">
                                        <text x={55} y={85} fill="#10b981" fontSize={10} fontWeight="bold">학업 컷</text>
                                    </ReferenceLine>
                                </ScatterChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* 3. Percentile Summary (Bottom Right) */}
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-[350px] flex flex-col">
                        <div className="mb-4">
                            <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-emerald-600" />
                                랭킹 및 분포
                            </h4>
                            <p className="text-sm text-gray-500">현재 {univ} 지원자 그룹 내 순위</p>
                        </div>

                        {percentileStats && (
                            <div className="flex-1 flex flex-col justify-center">
                                {/* Text Summary */}
                                <div className="mb-6 bg-gray-50 rounded-xl p-4 border border-gray-100">
                                    <p className="text-sm text-gray-800 leading-relaxed">
                                        전체 <span className="font-bold">{percentileStats.total}</span>명의 추적 지원자 중, 
                                        당신은 <span className="font-bold text-[#FC6401]">{percentileStats.rank}위</span>입니다.
                                    </p>
                                    <div className="mt-2 flex items-center gap-2">
                                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                        <span className="text-xs font-bold text-emerald-600">코호트 상위 {percentileStats.topRankPercent}%</span>
                                    </div>
                                </div>

                                {/* Visual Distribution Bar (Box Plot Simulation) */}
                                <div className="relative pt-8 pb-4 px-2">
                                    {/* Range Line */}
                                    <div className="absolute top-1/2 left-0 right-0 h-1.5 bg-gray-100 rounded-full"></div>
                                    
                                    {/* Min/Max Ticks */}
                                    <div className="absolute top-1/2 left-0 w-0.5 h-4 bg-gray-300 transform -translate-y-1/2"></div>
                                    <div className="absolute top-1/2 right-0 w-0.5 h-4 bg-gray-300 transform -translate-y-1/2"></div>
                                    
                                    {/* Median Tick */}
                                    <div 
                                        className="absolute top-1/2 w-0.5 h-4 bg-gray-400 transform -translate-y-1/2 z-0"
                                        style={{ left: `${((percentileStats.median - percentileStats.min) / (percentileStats.max - percentileStats.min)) * 100}%` }}
                                    ></div>
                                    <div 
                                        className="absolute -top-6 text-[10px] text-gray-400 font-medium transform -translate-x-1/2"
                                        style={{ left: `${((percentileStats.median - percentileStats.min) / (percentileStats.max - percentileStats.min)) * 100}%` }}
                                    >
                                        평균
                                    </div>

                                    {/* Target Student Marker */}
                                    <div 
                                        className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 flex flex-col items-center group cursor-pointer transition-all hover:scale-110 z-10"
                                        style={{ left: `${((percentileStats.score - percentileStats.min) / (percentileStats.max - percentileStats.min)) * 100}%` }}
                                    >
                                        <div className="w-4 h-4 rounded-full bg-[#FC6401] border-2 border-white shadow-md mb-1 relative z-10"></div>
                                        <div className="bg-[#FC6401] text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm">
                                            본인
                                        </div>
                                    </div>

                                    {/* Labels */}
                                    <div className="absolute -bottom-6 left-0 text-[10px] text-gray-400 font-medium">최저 ({Math.round(percentileStats.min)})</div>
                                    <div className="absolute -bottom-6 right-0 text-[10px] text-gray-400 font-medium">최고 ({Math.round(percentileStats.max)})</div>
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