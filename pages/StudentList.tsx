import React, { useState, useMemo } from 'react';
import { STUDENTS } from '../services/mockData';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, Plus, ChevronDown, ChevronRight, School, Users as UsersIcon, 
  TrendingUp, Crosshair, Layers, Filter, Brain,
  ArrowRight, Sparkles, X, Target, MoreHorizontal
} from 'lucide-react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, ReferenceLine, ReferenceArea, Cell, ReferenceDot,
  ComposedChart, Line
} from 'recharts';
import { Student } from '../types';

const StudentList: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  
  // UI States
  const [expandedUniv, setExpandedUniv] = useState<string | null>(null);
  const [isAnalysisOpen, setIsAnalysisOpen] = useState(false);
  
  // Advanced Chart Controls
  const [viewMode, setViewMode] = useState<'standard' | 'cluster'>('standard'); // standard | cluster
  const [showZones, setShowZones] = useState(true);
  const [showTrend, setShowTrend] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState<any>(null);

  // Group Students by University
  const groupedStudents = useMemo(() => {
    return STUDENTS.reduce((acc, student) => {
      const univ = student.targetUniversity;
      if (!acc[univ]) acc[univ] = [];
      acc[univ].push(student);
      return acc;
    }, {} as Record<string, Student[]>);
  }, []);

  // Filter Logic
  const filteredGroups = useMemo(() => {
    return Object.entries(groupedStudents).reduce((acc, [univ, students]) => {
      const filtered = students.filter(s => 
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.school.toLowerCase().includes(searchTerm.toLowerCase())
      );
      if (filtered.length > 0) {
        acc[univ] = filtered;
      }
      return acc;
    }, {} as Record<string, Student[]>);
  }, [groupedStudents, searchTerm]);

  const toggleUniv = (univ: string) => {
    if (expandedUniv === univ) {
      setExpandedUniv(null);
      setIsAnalysisOpen(false);
    } else {
      setExpandedUniv(univ);
      setIsAnalysisOpen(true); // Auto-open analysis for better UX on expand
      setSelectedPoint(null);
    }
  };

  // --- Analysis Helpers ---

  const getPracticalScore = (level: string) => {
    switch(level) {
      case 'A+': return 98;
      case 'A': return 92;
      case 'B+': return 85;
      case 'B': return 78;
      case 'C': return 65;
      default: return 50;
    }
  };

  const calculateTrendLine = (data: any[]) => {
    if (data.length < 2) return [];
    let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
    const n = data.length;
    data.forEach(d => {
      sumX += d.academicIndex;
      sumY += d.practicalIndex;
      sumXY += d.academicIndex * d.practicalIndex;
      sumXX += d.academicIndex * d.academicIndex;
    });
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    const x1 = 20; 
    const y1 = slope * x1 + intercept;
    const x2 = 100;
    const y2 = slope * x2 + intercept;
    return [{ academicIndex: x1, practicalIndex: y1 }, { academicIndex: x2, practicalIndex: y2 }];
  };

  const getAnalysisData = (students: Student[]) => {
    const avgAcademic = students.reduce((sum, s) => sum + (s.academicScores.korean.standardScore || 100), 0) / students.length;
    
    return students.map(s => {
      const rawAcademic = s.academicScores.korean.standardScore || 100;
      const rawPractical = getPracticalScore(s.currentLevel);
      
      // Normalize to 0-100 (Mock Logic)
      const academicIndex = Math.min(Math.max(50 + (rawAcademic - avgAcademic) * 2.5, 20), 98);
      const practicalIndex = Math.min(Math.max(rawPractical, 20), 98);
      
      let lineType: 'Safe' | 'Reach' | 'Stable' = 'Reach';
      let predictedProb = 30;

      if (academicIndex > 75 && practicalIndex > 75) {
        lineType = 'Safe';
        predictedProb = 85 + Math.random() * 10;
      } else if (academicIndex > 60 || practicalIndex > 80) {
        lineType = 'Stable';
        predictedProb = 60 + Math.random() * 15;
      }

      // Assign Cluster (Mock)
      let cluster = 0; // 0: Balanced/Low, 1: Elite, 2: Academic, 3: Practical
      if (academicIndex > 70 && practicalIndex > 70) cluster = 1;
      else if (academicIndex > practicalIndex + 10) cluster = 2;
      else if (practicalIndex > academicIndex + 10) cluster = 3;

      return {
        id: s.id,
        name: s.name,
        grade: s.grade,
        academicIndex: Math.round(academicIndex),
        practicalIndex: Math.round(practicalIndex),
        lineType,
        predictedProb: Math.round(predictedProb),
        cluster,
        originalLevel: s.currentLevel,
        avatarUrl: s.avatarUrl
      };
    });
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      if (!data.name) return null; // Trend line skip

      return (
        <div className="bg-white/95 backdrop-blur-md p-3 border border-gray-200 shadow-xl rounded-xl text-xs z-50 min-w-[160px]">
          <div className="flex items-center gap-2 mb-2">
             <div className={`w-2 h-2 rounded-full ${
                 data.lineType === 'Safe' ? 'bg-emerald-500' :
                 data.lineType === 'Stable' ? 'bg-blue-500' : 'bg-[#FC6401]'
             }`}></div>
             <span className="font-bold text-gray-900">{data.name}</span>
             <span className="text-gray-400">|</span>
             <span className="text-gray-500">{data.grade}</span>
          </div>
          <div className="space-y-1">
             <div className="flex justify-between">
                <span className="text-gray-500">학업 위치</span>
                <span className="font-bold text-gray-800">{data.academicIndex}</span>
             </div>
             <div className="flex justify-between">
                <span className="text-gray-500">실기 위치</span>
                <span className="font-bold text-gray-800">{data.practicalIndex}</span>
             </div>
             <div className="pt-2 mt-2 border-t border-gray-100 flex justify-between items-center">
                <span className="text-gray-400 text-[10px]">합격 확률</span>
                <span className={`font-bold ${data.predictedProb > 70 ? 'text-emerald-600' : 'text-[#FC6401]'}`}>
                    {data.predictedProb}%
                </span>
             </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-[1600px] mx-auto pb-12 animate-in slide-in-from-bottom-4 duration-500">
      
      {/* Page Header */}
      <div className="flex justify-between items-end mb-8">
        <div>
           <div className="flex items-center gap-2 mb-1">
             <span className="bg-[#FFF0E6] text-[#FC6401] text-[10px] font-bold px-2 py-0.5 rounded border border-[#FC6401]/20">
                DATA INTELLIGENCE
             </span>
           </div>
           <h1 className="text-3xl font-bold text-gray-900 tracking-tight">학생 분석 & 전략</h1>
           <p className="text-gray-500 mt-2">대학별 지원자 그룹 데이터 분석 및 개인별 맞춤 전략 수립</p>
        </div>
        <button 
          onClick={() => navigate('/students/new')}
          className="flex items-center px-5 py-2.5 bg-[#1F2937] text-white rounded-xl hover:bg-black transition-all shadow-lg shadow-gray-900/20 font-bold text-sm"
        >
            <Plus className="w-4 h-4 mr-2" />
            학생 추가
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="mb-8 relative max-w-2xl">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-11 pr-4 py-4 bg-white border border-gray-200 rounded-2xl placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#FC6401] focus:border-[#FC6401] text-sm shadow-sm transition-all hover:shadow-md"
          placeholder="학생 이름, 학교 또는 목표 대학 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* University Groups List */}
      <div className="space-y-6">
        {Object.keys(filteredGroups).length === 0 ? (
           <div className="text-center py-20 bg-white rounded-3xl border border-gray-200 border-dashed">
             <div className="bg-gray-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
               <UsersIcon className="w-10 h-10 text-gray-300" />
             </div>
             <p className="text-gray-500 font-medium">검색 조건에 맞는 학생이 없습니다.</p>
           </div>
        ) : (
          Object.entries(filteredGroups).map(([univ, students]) => {
            const isExpanded = expandedUniv === univ;
            const chartData = getAnalysisData(students);
            const trendData = calculateTrendLine(chartData);
            
            // Stats
            const safeCount = chartData.filter(d => d.lineType === 'Safe').length;
            const reachCount = chartData.filter(d => d.lineType === 'Reach').length;
            const avgProb = Math.round(chartData.reduce((acc, curr) => acc + curr.predictedProb, 0) / chartData.length);

            return (
              <div key={univ} className={`bg-white rounded-3xl border transition-all duration-500 overflow-hidden ${isExpanded ? 'border-gray-300 shadow-2xl ring-1 ring-gray-100' : 'border-gray-200 shadow-sm hover:shadow-md'}`}>
                
                {/* 1. Header Row */}
                <button 
                  onClick={() => toggleUniv(univ)}
                  className="w-full flex items-center justify-between p-6 bg-white hover:bg-gray-50 transition-colors z-10 relative"
                >
                  <div className="flex items-center gap-6">
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors border ${isExpanded ? 'bg-[#FC6401] text-white border-[#FC6401]' : 'bg-white text-gray-400 border-gray-200'}`}>
                      <School className="w-8 h-8" />
                    </div>
                    <div className="text-left">
                      <div className="flex items-center gap-3 mb-1">
                          <h3 className="text-xl font-bold text-gray-900">{univ}</h3>
                          <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-bold rounded-md border border-gray-200">{students.length}명 지원</span>
                      </div>
                      <div className="flex items-center gap-3 text-sm">
                          <span className="text-gray-500">평균 합격 확률 <strong className="text-gray-900">{avgProb}%</strong></span>
                          <span className="w-1 h-1 rounded-full bg-gray-300"></span>
                          <span className="text-emerald-600 font-medium text-xs">안정 {safeCount}</span>
                          <span className="text-[#FC6401] font-medium text-xs">상향 {reachCount}</span>
                      </div>
                    </div>
                  </div>
                  <div className={`p-3 rounded-full transition-all duration-300 ${isExpanded ? 'bg-gray-100 rotate-180' : 'bg-white border border-gray-100'}`}>
                      <ChevronDown className={`w-5 h-5 transition-colors ${isExpanded ? 'text-gray-900' : 'text-gray-400'}`} />
                  </div>
                </button>

                {/* 2. Expanded Content Area */}
                {isExpanded && (
                  <div className="border-t border-gray-100 bg-[#F9FAFB] animate-in slide-in-from-top-4 duration-300">
                    
                    {/* A. Analysis Dashboard Header */}
                    <div className="px-8 pt-8 pb-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-[#FC6401]/10 rounded-lg">
                                <Crosshair className="w-5 h-5 text-[#FC6401]" />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900 text-lg">상대적 위치 분석 (Relative Positioning)</h4>
                                <p className="text-xs text-gray-500">학업(X)과 실기(Y) 지표를 통한 지원자 분포 및 전략 수립</p>
                            </div>
                        </div>

                        {/* Toolbar */}
                        <div className="flex bg-white p-1 rounded-xl border border-gray-200 shadow-sm">
                            <button 
                                onClick={() => setViewMode('standard')}
                                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${viewMode === 'standard' ? 'bg-gray-900 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-50'}`}
                            >
                                <Target className="w-3.5 h-3.5" /> 기본 보기
                            </button>
                            <button 
                                onClick={() => setViewMode('cluster')}
                                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${viewMode === 'cluster' ? 'bg-purple-600 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-50'}`}
                            >
                                <Filter className="w-3.5 h-3.5" /> 군집(Cluster)
                            </button>
                            <div className="w-px bg-gray-200 mx-1 my-1"></div>
                            <button 
                                onClick={() => setShowZones(!showZones)}
                                className={`px-3 py-2 rounded-lg text-xs font-bold transition-all ${showZones ? 'text-emerald-600 bg-emerald-50' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                Zone
                            </button>
                            <button 
                                onClick={() => setShowTrend(!showTrend)}
                                className={`px-3 py-2 rounded-lg text-xs font-bold transition-all ${showTrend ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                Trend
                            </button>
                        </div>
                    </div>

                    {/* B. Main Content Grid (Chart + Side Panel) */}
                    <div className="px-8 pb-8 flex flex-col lg:flex-row gap-6 h-[550px]">
                        
                        {/* Chart Area */}
                        <div className={`bg-white rounded-3xl border border-gray-200 shadow-sm relative transition-all duration-500 ease-in-out flex flex-col ${selectedPoint ? 'lg:w-2/3' : 'w-full'}`}>
                            
                            {/* AI Insight Overlay */}
                            <div className="absolute top-4 left-4 right-4 z-10 pointer-events-none">
                                <div className="bg-gradient-to-r from-blue-50/90 to-white/90 backdrop-blur-sm p-3 rounded-2xl border border-blue-100 flex gap-3 items-center shadow-sm pointer-events-auto max-w-2xl">
                                    <div className="p-1.5 bg-blue-100 rounded-lg shrink-0">
                                        <Brain className="w-4 h-4 text-blue-600" />
                                    </div>
                                    <p className="text-xs text-blue-900 leading-relaxed">
                                        <span className="font-bold">Insight:</span> 상위권 학생일수록 실기와 학업이 동반 상승하는 <strong>'Elite' 패턴</strong>이 뚜렷합니다. 
                                        현재 상향 지원자의 60%가 <strong>Risk Zone</strong>에 위치하여 학업 보완 전략이 필요합니다.
                                    </p>
                                </div>
                            </div>

                            {/* Chart Container */}
                            <div className="flex-1 w-full p-4 pt-16">
                                <ResponsiveContainer width="100%" height="100%">
                                    <ComposedChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} stroke="#f3f4f6" />
                                        <XAxis 
                                            type="number" 
                                            dataKey="academicIndex" 
                                            domain={[20, 100]} 
                                            tick={{fontSize: 11, fill: '#9ca3af'}}
                                            label={{ value: '학업 상대 위치 (Academic)', position: 'bottom', offset: 0, fontSize: 11, fill: '#9ca3af', fontWeight: 'bold' }}
                                            axisLine={false} tickLine={false}
                                        />
                                        <YAxis 
                                            type="number" 
                                            dataKey="practicalIndex" 
                                            domain={[20, 100]} 
                                            tick={{fontSize: 11, fill: '#9ca3af'}}
                                            label={{ value: '실기 상대 위치 (Practical)', angle: -90, position: 'left', fontSize: 11, fill: '#9ca3af', fontWeight: 'bold' }}
                                            axisLine={false} tickLine={false}
                                        />
                                        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                                        
                                        {/* Quadrant Backgrounds (Using ReferenceArea) */}
                                        <ReferenceArea x1={70} x2={100} y1={70} y2={100} fill="#f0fdf4" fillOpacity={0.4} /> {/* Elite */}
                                        <ReferenceArea x1={20} x2={70} y1={20} y2={70} fill="#fef2f2" fillOpacity={0.4} /> {/* Risk */}
                                        
                                        {/* Quadrant Labels */}
                                        <ReferenceDot x={95} y={97} r={0} label={{ value: 'Elite Group', fill: '#166534', fontSize: 12, fontWeight: 'bold', opacity: 0.5 }} />
                                        <ReferenceDot x={30} y={25} r={0} label={{ value: 'Risk Group', fill: '#991b1b', fontSize: 12, fontWeight: 'bold', opacity: 0.5 }} />
                                        <ReferenceDot x={95} y={30} r={0} label={{ value: 'Academic Driven', fill: '#1e40af', fontSize: 12, fontWeight: 'bold', opacity: 0.3 }} />
                                        <ReferenceDot x={30} y={95} r={0} label={{ value: 'Practical Driven', fill: '#c2410c', fontSize: 12, fontWeight: 'bold', opacity: 0.3 }} />

                                        {/* Dynamic Zones */}
                                        {showZones && (
                                            <>
                                                <ReferenceArea x1={75} x2={100} y1={75} y2={100} stroke="#10b981" strokeDasharray="3 3" fill="none" />
                                                <ReferenceDot x={87.5} y={87.5} r={0} label={{ value: 'TARGET ZONE', fill: '#10b981', fontSize: 10, fontWeight: 'bold', position: 'center' }} />
                                            </>
                                        )}

                                        {/* Trend Line */}
                                        {showTrend && (
                                            <Line data={trendData} type="monotone" dataKey="practicalIndex" stroke="#1f2937" strokeWidth={2} dot={false} activeDot={false} strokeDasharray="5 5" />
                                        )}

                                        {/* Students */}
                                        <Scatter 
                                            name="Students" 
                                            data={chartData} 
                                            onClick={(data) => setSelectedPoint(data)} 
                                            className="cursor-pointer transition-all duration-300"
                                        >
                                            {chartData.map((entry, index) => {
                                                let fill = '#9ca3af';
                                                let stroke = '#fff';
                                                
                                                if (viewMode === 'cluster') {
                                                    fill = entry.cluster === 1 ? '#7c3aed' : entry.cluster === 2 ? '#3b82f6' : entry.cluster === 3 ? '#ea580c' : '#9ca3af';
                                                } else {
                                                    fill = entry.lineType === 'Safe' ? '#10b981' : entry.lineType === 'Stable' ? '#3b82f6' : '#FC6401';
                                                }

                                                const isSelected = selectedPoint?.id === entry.id;
                                                
                                                return (
                                                    <Cell 
                                                        key={`cell-${index}`} 
                                                        fill={fill} 
                                                        r={isSelected ? 8 : (entry.predictedProb > 80 ? 6 : 4)} 
                                                        stroke={isSelected ? '#1f2937' : stroke}
                                                        strokeWidth={isSelected ? 2 : 1}
                                                        opacity={selectedPoint && !isSelected ? 0.3 : 1} 
                                                    />
                                                );
                                            })}
                                        </Scatter>
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Interactive Side Panel (Strategy Dock) */}
                        {selectedPoint ? (
                            <div className="lg:w-1/3 bg-white rounded-3xl border border-gray-200 shadow-xl flex flex-col overflow-hidden animate-in slide-in-from-right-4 fade-in duration-300 relative z-20">
                                {/* Header */}
                                <div className="p-6 bg-gray-900 text-white relative overflow-hidden">
                                    <div className="absolute top-0 right-0 w-32 h-32 bg-[#FC6401] rounded-full blur-3xl opacity-20 -mr-10 -mt-10"></div>
                                    <button onClick={() => setSelectedPoint(null)} className="absolute top-4 right-4 text-gray-400 hover:text-white"><X className="w-5 h-5"/></button>
                                    
                                    <div className="flex items-center gap-4 relative z-10">
                                        <img src={selectedPoint.avatarUrl} className="w-14 h-14 rounded-full border-2 border-white/20" alt="" />
                                        <div>
                                            <h3 className="text-xl font-bold">{selectedPoint.name}</h3>
                                            <p className="text-sm text-gray-300">{univ} <span className="mx-1">•</span> {selectedPoint.grade}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Body */}
                                <div className="p-6 flex-1 overflow-y-auto">
                                    {/* Probability Badge */}
                                    <div className="flex justify-between items-center mb-6">
                                        <span className="text-xs font-bold text-gray-400 uppercase">합격 예측 확률</span>
                                        <div className="flex items-center gap-2">
                                            <div className="h-2 w-24 bg-gray-100 rounded-full overflow-hidden">
                                                <div className="h-full bg-emerald-500 rounded-full" style={{width: `${selectedPoint.predictedProb}%`}}></div>
                                            </div>
                                            <span className="font-bold text-xl text-gray-900">{selectedPoint.predictedProb}%</span>
                                        </div>
                                    </div>

                                    {/* Gap Analysis */}
                                    <div className="bg-gray-50 rounded-2xl p-5 mb-6 border border-gray-100">
                                        <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                                            <Target className="w-4 h-4 text-[#FC6401]" /> Target Zone 거리 (Gap)
                                        </h4>
                                        
                                        <div className="space-y-4">
                                            <div>
                                                <div className="flex justify-between text-xs mb-1.5">
                                                    <span className="font-bold text-gray-500">학업 지수</span>
                                                    <span className="font-bold text-blue-600">{selectedPoint.academicIndex} / 85 (Target)</span>
                                                </div>
                                                <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                                                    <div className="h-full bg-blue-500" style={{width: `${(selectedPoint.academicIndex/100)*100}%`}}></div>
                                                </div>
                                                {selectedPoint.academicIndex < 85 && (
                                                    <p className="text-[10px] text-rose-500 font-medium mt-1 text-right">+ {85 - selectedPoint.academicIndex}점 필요</p>
                                                )}
                                            </div>
                                            
                                            <div>
                                                <div className="flex justify-between text-xs mb-1.5">
                                                    <span className="font-bold text-gray-500">실기 지수</span>
                                                    <span className="font-bold text-[#FC6401]">{selectedPoint.practicalIndex} / 85 (Target)</span>
                                                </div>
                                                <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                                                    <div className="h-full bg-[#FC6401]" style={{width: `${(selectedPoint.practicalIndex/100)*100}%`}}></div>
                                                </div>
                                                {selectedPoint.practicalIndex < 85 && (
                                                    <p className="text-[10px] text-rose-500 font-medium mt-1 text-right">+ {85 - selectedPoint.practicalIndex}점 필요</p>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Strategic Advice */}
                                    <div className="mb-6">
                                        <h4 className="text-xs font-bold text-gray-400 uppercase mb-3">전략 가이드</h4>
                                        <div className="p-4 bg-[#FFF0E6]/50 rounded-xl border border-[#FC6401]/10 text-sm text-gray-700 leading-relaxed">
                                            이 학생은 <strong>{selectedPoint.academicIndex > selectedPoint.practicalIndex ? '학업 우위형' : '실기 우위형'}</strong> 패턴을 보입니다. 
                                            안정권 진입을 위해 
                                            {selectedPoint.academicIndex < 85 ? <span className="font-bold text-blue-600 mx-1">학업 보완</span> : <span className="font-bold text-[#FC6401] mx-1">실기 디테일</span>} 
                                            전략이 우선되어야 합니다.
                                        </div>
                                    </div>
                                </div>

                                {/* Footer Action */}
                                <div className="p-4 border-t border-gray-100">
                                    <Link 
                                        to={`/students/${selectedPoint.id}`}
                                        className="w-full py-3.5 bg-gray-900 hover:bg-black text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all"
                                    >
                                        상세 프로필 및 리포트 <ArrowRight className="w-4 h-4" />
                                    </Link>
                                </div>
                            </div>
                        ) : (
                            // Placeholder Panel when no student selected
                            <div className="hidden lg:flex w-1/3 bg-gray-50 rounded-3xl border border-gray-200 border-dashed items-center justify-center flex-col text-gray-400 gap-4">
                                <div className="p-4 bg-white rounded-full shadow-sm">
                                    <Crosshair className="w-8 h-8 text-gray-300" />
                                </div>
                                <div className="text-center">
                                    <p className="font-bold text-gray-500">학생을 선택하세요</p>
                                    <p className="text-xs mt-1">그래프 위의 점을 클릭하여 상세 전략을 확인하세요.</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* C. Student List Table Section */}
                    <div className="px-8 pb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h4 className="font-bold text-gray-900 flex items-center gap-2">
                                <UsersIcon className="w-4 h-4 text-gray-500" /> 목록 보기
                            </h4>
                            <span className="text-xs font-bold text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                {students.length}명
                            </span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {students.map(student => (
                                <Link 
                                key={student.id} 
                                to={`/students/${student.id}`}
                                className={`flex items-center p-3 bg-white rounded-xl border transition-all cursor-pointer hover:shadow-md hover:border-[#FC6401] active:scale-98 ${selectedPoint?.id === student.id ? 'border-[#FC6401] ring-1 ring-[#FC6401]' : 'border-gray-200'}`}
                                >
                                    <img src={student.avatarUrl} className="w-10 h-10 rounded-full border border-gray-100 mr-3" alt="" />
                                    <div className="flex-1">
                                        <div className="font-bold text-sm text-gray-900 flex items-center gap-2">
                                            {student.name}
                                            <ChevronRight className="w-3 h-3 text-gray-300" />
                                        </div>
                                        <div className="text-xs text-gray-500">{student.major}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-xs font-bold ${student.currentLevel.startsWith('A') ? 'text-[#FC6401]' : 'text-gray-600'}`}>
                                            {student.currentLevel}
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>

                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default StudentList;