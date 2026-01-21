
import React, { useState, useRef, useEffect } from 'react';
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, 
  ResponsiveContainer, Tooltip as RechartsTooltip, Legend, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Cell, PieChart, Pie
} from 'recharts';
import { 
  Terminal, Send, FileText, Zap, Activity, Share2, Download, 
  Sparkles, RotateCcw, PanelTopClose, PanelBottomOpen, 
  Command, ChevronDown, ChevronRight, Bot, LayoutTemplate,
  FolderOpen, MoreHorizontal, Search, Sliders, AlertTriangle, 
  ArrowRight, Folder, User, FileBarChart, Database, Layers, Hash, Gauge,
  Target, Clock
} from 'lucide-react';

// --- Types & Interfaces ---
interface LogMessage {
  id: string;
  timestamp: string;
  type: 'system' | 'user' | 'ai';
  content: string;
  artifactLink?: string;
}

interface DataNode {
  id: string;
  name: string;
  type: 'folder' | 'file';
  level: number;
  isOpen?: boolean;
  children?: DataNode[];
  meta?: {
    season: string;
    risk: 'Low' | 'Mid' | 'High';
  };
}

// --- Mock Data ---

// Tree Data
const DATA_TREE: DataNode[] = [
  {
    id: 'root_2026', name: '2026 정시 시즌', type: 'folder', level: 0, isOpen: true,
    children: [
      { 
        id: 'univ_hongik', name: '홍익대 (Hongik Univ)', type: 'folder', level: 1, isOpen: true,
        children: [
          { id: 'cohort_hongik_all', name: '전체 지원자 분석.dta', type: 'file', level: 2, meta: { season: '2026', risk: 'Mid' } },
          { id: 'cohort_hongik_high', name: '상위권(High) 그룹.dta', type: 'file', level: 2, meta: { season: '2026', risk: 'Low' } },
        ]
      },
      {
        id: 'univ_snu', name: '서울대 (SNU)', type: 'folder', level: 1, isOpen: false,
        children: [
          { id: 'cohort_snu_craft', name: '공예과 지원자.dta', type: 'file', level: 2, meta: { season: '2026', risk: 'High' } }
        ]
      },
      { id: 'student_kim', name: '개인: 김지민.std', type: 'file', level: 1, meta: { season: '2026', risk: 'Low' } }
    ]
  },
  {
    id: 'root_2025', name: '2025 합격 데이터 (Ref)', type: 'folder', level: 0, isOpen: false,
    children: []
  },
  {
    id: 'shared_drive', name: '공유 드라이브', type: 'folder', level: 0, isOpen: false,
    children: []
  }
];

// Chart Data
const WATERFALL_DATA = [
  { name: '기본 점수', value: 80, fill: '#E5E7EB' },
  { name: '수능', value: 12, fill: '#10B981' }, // Positive
  { name: '내신', value: 3, fill: '#10B981' }, // Positive
  { name: '실기(구도)', value: 5, fill: '#3B82F6' }, // Positive
  { name: '실기(완성도)', value: -4, fill: '#F43F5E' }, // Negative
  { name: '최종 예측', value: 96, isTotal: true, fill: '#FF5F00' },
];

const RADAR_DATA = [
  { subject: '구도', A: 92, B: 85, full: 100 },
  { subject: '톤/명암', A: 88, B: 90, full: 100 },
  { subject: '발상', A: 75, B: 88, full: 100 },
  { subject: '완성도', A: 95, B: 80, full: 100 },
  { subject: '학업', A: 85, B: 82, full: 100 },
];

// --- Main Component ---
const Analytics: React.FC = () => {
  // Layout State
  const [consoleHeight, setConsoleHeight] = useState(35); // Reduced default height slightly
  const [isConsoleCollapsed, setIsConsoleCollapsed] = useState(false);
  
  // Logic State
  const [selectedFileId, setSelectedFileId] = useState<string>('cohort_hongik_all');
  const [activeTab, setActiveTab] = useState<'explain' | 'compare' | 'simulate'>('explain');
  const [treeData, setTreeData] = useState(DATA_TREE);
  
  // Simulation State
  const [simValues, setSimValues] = useState({ practical: 50, sat: 50, competition: 50 });
  
  // Console State
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<LogMessage[]>([
    { id: '1', timestamp: '14:00:01', type: 'system', content: 'Analysis Lab Environment v2.0 Loaded.' },
    { id: '2', timestamp: '14:00:02', type: 'ai', content: '데이터 탐색기가 준비되었습니다. 좌측에서 분석할 대상(파일)을 선택하거나, 바로 질문해 주세요.' },
  ]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  // --- Handlers ---

  const toggleNode = (id: string) => {
    const newTree = [...treeData];
    const toggleRecursive = (nodes: DataNode[]): boolean => {
      for (const node of nodes) {
        if (node.id === id) {
          node.isOpen = !node.isOpen;
          return true;
        }
        if (node.children && toggleRecursive(node.children)) return true;
      }
      return false;
    };
    toggleRecursive(newTree);
    setTreeData(newTree);
  };

  const handleFileClick = (id: string) => {
    setSelectedFileId(id);
    setActiveTab('explain');
    addLog('system', `Loaded data artifact: [${id}]`);
    addLog('ai', `${id.split('_')[1] || '선택된'} 데이터 로드 완료. 주요 변동 요인을 분석합니다.`);
  };

  const addLog = (type: LogMessage['type'], content: string, link?: string) => {
    const now = new Date();
    const timeString = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`;
    setLogs(prev => [...prev, { id: Date.now().toString(), timestamp: timeString, type, content, artifactLink: link }]);
  };

  const handleCommand = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;
    const cmd = input.trim();
    setInput('');
    addLog('user', cmd);
    setIsProcessing(true);

    // Mock Logic
    setTimeout(() => {
      setIsProcessing(false);
      if (cmd.includes('비교') || cmd.includes('compare')) {
        setActiveTab('compare');
        addLog('system', 'Switched to [Compare] mode.');
        addLog('ai', '경쟁 그룹(국민대 지원자 평균) 데이터를 오버레이했습니다. 실기 완성도 측면에서 -4점 차이가 발생하고 있습니다.');
      } else if (cmd.includes('시뮬') || cmd.includes('simulate') || cmd.includes('가정')) {
        setActiveTab('simulate');
        addLog('system', 'Switched to [Simulate] mode.');
        addLog('ai', '전략 시뮬레이터를 실행합니다. 우측 슬라이더를 조정하여 합격 확률 변화를 확인하세요.');
      } else {
        addLog('ai', '요청하신 내용을 분석 중입니다. 잠시만 기다려주세요...');
      }
    }, 1000);
  };

  // --- Sub Components ---

  const MetricCard = ({ label, value, trend, icon: Icon }: any) => (
    <div className="flex items-center gap-3 px-4 py-2 border-r border-gray-100 last:border-0 min-w-[140px]">
      <div className="p-2 bg-gray-50 rounded-lg">
        <Icon className="w-4 h-4 text-gray-400" />
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider leading-tight">{label}</span>
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-mono font-bold text-gray-900 leading-none">{value}</span>
          {trend && <span className="text-[10px] font-mono text-emerald-600 font-bold">{trend}</span>}
        </div>
      </div>
    </div>
  );

  const FileTreeItem = ({ node }: { node: DataNode }) => {
    const isSelected = selectedFileId === node.id;
    
    // --- Icon Selection Logic ---
    const getIcon = () => {
      if (node.type === 'folder') {
        return node.isOpen 
          ? <FolderOpen className={`w-4 h-4 ${isSelected ? 'text-[#FF5F00]' : 'text-amber-400'}`} />
          : <Folder className={`w-4 h-4 ${isSelected ? 'text-[#FF5F00]' : 'text-amber-400'}`} />;
      }
      // File Types
      if (node.name.endsWith('.std')) return <User className="w-4 h-4 text-blue-500" />;
      if (node.name.endsWith('.dta')) return <FileBarChart className="w-4 h-4 text-emerald-600" />;
      return <Database className="w-4 h-4 text-gray-400" />;
    };

    return (
      <div className="select-none">
        <div 
          className={`group flex items-center gap-2 py-2 px-3 cursor-pointer text-[13px] transition-all relative ${
            isSelected 
              ? 'bg-[#FFF0E6]/60 text-gray-900' 
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
          style={{ paddingLeft: `${node.level * 14 + 16}px` }}
          onClick={() => node.type === 'folder' ? toggleNode(node.id) : handleFileClick(node.id)}
        >
          {/* Active Indicator Bar */}
          {isSelected && <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-[#FF5F00]" />}

          {/* Toggle Caret / Spacer */}
          <div className="w-4 h-4 flex items-center justify-center shrink-0">
             {node.type === 'folder' && (
                node.isOpen 
                  ? <ChevronDown className="w-3 h-3 text-gray-400 group-hover:text-gray-600" /> 
                  : <ChevronRight className="w-3 h-3 text-gray-400 group-hover:text-gray-600" />
             )}
          </div>

          {/* Icon */}
          <div className="shrink-0 transition-transform group-hover:scale-105">
            {getIcon()}
          </div>

          {/* Name - Applied Pretendard Medium equivalent via Tailwind */}
          <span className={`truncate flex-1 leading-none pt-0.5 ${isSelected ? 'font-bold' : 'font-medium'}`}>
            {node.name}
          </span>
          
          {/* Metadata Badges (Risk) - distinct styling */}
          {node.meta?.risk === 'High' && (
            <div className="flex items-center gap-1 bg-rose-50 border border-rose-100 px-1.5 py-0.5 rounded ml-auto">
               <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0"></span>
               <span className="text-[9px] font-bold text-rose-600 uppercase">High</span>
            </div>
          )}
          {node.meta?.risk === 'Mid' && (
            <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-sm shrink-0 ml-auto" title="Mid Risk" />
          )}
        </div>

        {/* Recursive Children */}
        {node.type === 'folder' && node.isOpen && node.children && (
          <div className="relative">
            {node.children.map(child => <FileTreeItem key={child.id} node={child} />)}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-full w-full bg-[#F9FAFB] overflow-hidden font-sans text-[15px]">
      
      {/* ----------------------------------------------------------------------------------
          PANE 1: DATA EXPLORER (Left, Fixed Width)
         ---------------------------------------------------------------------------------- */}
      <div className="w-[280px] flex flex-col border-r border-gray-200 bg-white shrink-0 z-20 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.05)]">
        {/* Header */}
        <div className="h-14 border-b border-gray-100 flex items-center justify-between px-4 bg-gray-50/50 backdrop-blur-sm">
           <span className="font-bold text-gray-800 text-xs tracking-wide uppercase flex items-center gap-2">
             <Layers className="w-4 h-4 text-[#FF5F00]" /> Data Explorer
           </span>
           <button className="text-gray-400 hover:text-gray-700 p-1 hover:bg-gray-100 rounded transition-colors"><MoreHorizontal className="w-4 h-4" /></button>
        </div>
        
        {/* Toolbar */}
        <div className="p-3 border-b border-gray-100 bg-white">
           <div className="relative group">
             <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-gray-400 group-focus-within:text-[#FF5F00] transition-colors" />
             <input type="text" placeholder="Search data..." className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-2 py-2 text-xs font-medium focus:border-[#FF5F00] focus:ring-1 focus:ring-[#FF5F00]/20 outline-none transition-all placeholder:text-gray-400" />
           </div>
        </div>

        {/* Tree Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar py-3">
           <div className="px-4 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1 flex items-center gap-2">
              <Database className="w-3 h-3" /> Project Root
           </div>
           {treeData.map(node => <FileTreeItem key={node.id} node={node} />)}
        </div>

        {/* Footer Info */}
        <div className="p-3 border-t border-gray-100 bg-gray-50/50 flex justify-between items-center text-[10px] text-gray-400 font-mono">
           <span>/cloud/2026/main</span>
           <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="font-bold text-emerald-600">Connected</span>
           </div>
        </div>
      </div>

      {/* ----------------------------------------------------------------------------------
          RIGHT COLUMN CONTAINER
         ---------------------------------------------------------------------------------- */}
      <div className="flex-1 flex flex-col min-w-0 relative bg-white">
        
        {/* ----------------------------------------------------------------------------------
            PANE 2: VISUAL WORKSPACE (Top-Right)
           ---------------------------------------------------------------------------------- */}
        <div 
          className="flex flex-col transition-all duration-300 z-10"
          style={{ height: isConsoleCollapsed ? 'calc(100% - 60px)' : `${100 - consoleHeight}%` }}
        >
           {/* Tab Bar */}
           <div className="h-12 border-b border-gray-200 flex items-center px-4 select-none bg-white">
              <div className="flex h-full gap-6">
                {[
                  { id: 'explain', label: 'Explain', icon: Activity },
                  { id: 'compare', label: 'Compare', icon: LayoutTemplate },
                  { id: 'simulate', label: 'Simulate', icon: Zap }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-2 h-full text-xs font-bold border-b-2 transition-all px-1 ${
                      activeTab === tab.id 
                        ? 'border-[#FF5F00] text-[#FF5F00]' 
                        : 'border-transparent text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <tab.icon className="w-3.5 h-3.5" />
                    {tab.label}
                  </button>
                ))}
              </div>
              <div className="ml-auto flex items-center gap-2">
                 <button className="p-2 text-gray-400 hover:text-[#FF5F00] hover:bg-gray-50 rounded-md transition-colors"><Share2 className="w-4 h-4"/></button>
                 <button className="p-2 text-gray-400 hover:text-[#FF5F00] hover:bg-gray-50 rounded-md transition-colors"><Download className="w-4 h-4"/></button>
              </div>
           </div>

           {/* Metrics Row (High Density) */}
           <div className="h-16 border-b border-gray-200 bg-white flex items-center px-6 overflow-x-auto no-scrollbar">
              <MetricCard label="Prediction Accuracy" value="92.4%" trend="+1.2%" icon={Target} />
              <MetricCard label="Sample Size" value="1,420" icon={User} />
              <MetricCard label="Confidence Score" value="High" icon={Gauge} />
              <MetricCard label="Last Updated" value="14:02" icon={Clock} />
           </div>

           {/* Canvas Area */}
           <div className="flex-1 overflow-hidden p-8 bg-gray-50/30 relative">
              
              {/* VIEW: EXPLAIN */}
              {activeTab === 'explain' && (
                <div className="h-full flex flex-col animate-in fade-in zoom-in-95 duration-300">
                   <div className="mb-6">
                      <h2 className="text-xl font-bold text-gray-900 tracking-tight">합격 예측 스코어 워터폴</h2>
                      <p className="text-gray-500 mt-1 font-medium text-xs">현재 점수(80)에서 긍정/부정 요인을 합산한 최종 예측 점수입니다.</p>
                   </div>
                   <div className="flex-1 w-full min-h-0 relative bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                      <ResponsiveContainer width="100%" height="100%">
                         <BarChart data={WATERFALL_DATA}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" strokeOpacity={0.5} />
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 11, fontWeight: 600}} dy={10} />
                            <YAxis axisLine={false} tickLine={false} hide />
                            <RechartsTooltip 
                               cursor={{fill: '#F9FAFB'}}
                               contentStyle={{borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', fontSize: '12px'}} 
                            />
                            <Bar dataKey="value" radius={[4, 4, 4, 4]}>
                               {WATERFALL_DATA.map((entry, index) => (
                                 <Cell key={`cell-${index}`} fill={entry.fill} />
                               ))}
                            </Bar>
                         </BarChart>
                      </ResponsiveContainer>
                      
                      {/* Annotation Overlay */}
                      <div className="absolute top-6 right-6 bg-white/95 backdrop-blur border border-gray-200 p-4 rounded-xl shadow-lg max-w-xs ring-1 ring-gray-100">
                         <div className="flex items-start gap-3">
                            <div className="p-1.5 bg-rose-100 rounded-lg text-rose-600 mt-0.5"><AlertTriangle className="w-4 h-4"/></div>
                            <div>
                               <h4 className="text-sm font-bold text-gray-900">리스크 감지</h4>
                               <p className="text-xs text-gray-600 mt-1 leading-relaxed font-medium">
                                  실기 완성도 부족(-4)이 합격권 진입의 가장 큰 장애물입니다. 마감 30분 전 밀도 보강 훈련이 필요합니다.
                               </p>
                            </div>
                         </div>
                      </div>
                   </div>
                </div>
              )}

              {/* VIEW: COMPARE */}
              {activeTab === 'compare' && (
                <div className="h-full grid grid-cols-12 gap-6 animate-in fade-in zoom-in-95 duration-300">
                   <div className="col-span-8 flex flex-col">
                      <div className="mb-4 flex justify-between items-end">
                         <h2 className="text-xl font-bold text-gray-900">코호트 역량 비교</h2>
                      </div>
                      <div className="flex-1 bg-white rounded-xl border border-gray-200 p-4 shadow-sm relative">
                         <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
                         <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={RADAR_DATA}>
                               <PolarGrid stroke="#E5E7EB" strokeDasharray="3 3" />
                               <PolarAngleAxis dataKey="subject" tick={{ fill: '#6B7280', fontSize: 12, fontWeight: 'bold' }} />
                               <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                               <Radar name="내 점수" dataKey="A" stroke="#FF5F00" strokeWidth={3} fill="#FF5F00" fillOpacity={0.1} />
                               <Radar name="경쟁 그룹 평균" dataKey="B" stroke="#9CA3AF" strokeWidth={2} fill="#9CA3AF" fillOpacity={0.1} />
                               <Legend wrapperStyle={{fontSize: '12px', fontWeight: 600}} />
                               <RechartsTooltip contentStyle={{fontSize: '12px', borderRadius: '8px'}} />
                            </RadarChart>
                         </ResponsiveContainer>
                      </div>
                   </div>
                   <div className="col-span-4 space-y-3 overflow-y-auto">
                      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Gap Analysis</h3>
                      {RADAR_DATA.map((item, idx) => {
                         const gap = item.A - item.B;
                         return (
                           <div key={idx} className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-[#FF5F00] transition-colors group">
                              <span className="text-xs font-bold text-gray-700">{item.subject}</span>
                              <div className="flex items-center gap-2">
                                 <div className="h-1.5 w-16 bg-gray-100 rounded-full overflow-hidden">
                                    <div className={`h-full ${gap > 0 ? 'bg-emerald-500' : 'bg-rose-500'}`} style={{width: `${Math.abs(gap) * 5}%`}}></div>
                                 </div>
                                 <div className={`text-xs font-mono font-bold w-8 text-right ${gap > 0 ? 'text-emerald-600' : 'text-rose-500'}`}>
                                    {gap > 0 ? `+${gap}` : gap}
                                 </div>
                              </div>
                           </div>
                         );
                      })}
                   </div>
                </div>
              )}

              {/* VIEW: SIMULATE */}
              {activeTab === 'simulate' && (
                <div className="h-full grid grid-cols-12 gap-6 animate-in fade-in zoom-in-95 duration-300">
                   {/* Left: Controls */}
                   <div className="col-span-4 bg-white rounded-xl p-6 border border-gray-200 flex flex-col gap-8 shadow-sm">
                      <div>
                         <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                            <Sliders className="w-5 h-5 text-[#FF5F00]" /> 변수 조절
                         </h2>
                         {[
                           { label: '실기 점수 향상', key: 'practical', min: 0, max: 100 },
                           { label: '수능 등급 컷', key: 'sat', min: 0, max: 100 },
                           { label: '경쟁률 변동', key: 'competition', min: 0, max: 100 },
                         ].map((control) => (
                           <div key={control.key} className="mb-6">
                              <div className="flex justify-between mb-2">
                                 <span className="text-xs font-bold text-gray-500 uppercase">{control.label}</span>
                                 <span className="text-xs font-mono font-bold text-[#FF5F00]">
                                    {(simValues as any)[control.key]}%
                                 </span>
                              </div>
                              <input 
                                type="range" 
                                min={control.min} max={control.max} 
                                value={(simValues as any)[control.key]} 
                                onChange={(e) => setSimValues({...simValues, [control.key]: parseInt(e.target.value)})}
                                className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#FF5F00]"
                              />
                           </div>
                         ))}
                      </div>
                      <div className="mt-auto p-4 bg-gray-50 rounded-xl border border-gray-200">
                         <div className="text-xs text-gray-400 font-bold uppercase mb-1">AI 예측 코멘트</div>
                         <p className="text-sm text-gray-700 leading-snug font-medium">
                            실기 점수가 5% 향상되면 합격 확률이 <span className="text-emerald-600 font-bold">12%p 상승</span>하여 안정권에 진입합니다.
                         </p>
                      </div>
                   </div>

                   {/* Right: Outcome */}
                   <div className="col-span-8 flex items-center justify-center relative bg-white rounded-xl border border-gray-200 shadow-sm">
                      <ResponsiveContainer width="100%" height="100%">
                         <PieChart>
                            <Pie
                               data={[{ value: simValues.practical + 20 }, { value: 100 - (simValues.practical + 20) }]}
                               cx="50%" cy="70%"
                               startAngle={180} endAngle={0}
                               innerRadius="120%" outerRadius="160%"
                               paddingAngle={0}
                               dataKey="value"
                            >
                               <Cell fill="#FF5F00" />
                               <Cell fill="#E5E7EB" />
                            </Pie>
                         </PieChart>
                      </ResponsiveContainer>
                      <div className="absolute bottom-10 text-center">
                         <div className="text-6xl font-mono font-bold text-gray-900 tracking-tighter">
                            {Math.min(99, Math.floor(simValues.practical * 0.6 + 30))}%
                         </div>
                         <div className="text-sm text-gray-400 font-bold uppercase mt-2 tracking-widest">예상 합격 확률</div>
                      </div>
                   </div>
                </div>
              )}

           </div>
        </div>

        {/* Resizer Handle */}
        <div className="h-0 relative z-30 group">
           <div 
             className="absolute -top-3 left-0 right-0 h-6 cursor-row-resize flex items-center justify-center hover:bg-[#FF5F00]/5 transition-colors"
             onMouseDown={(e) => {
               // Simple drag implementation could go here, for now strictly UI
             }}
           >
              <div className="w-16 h-1 rounded-full bg-gray-300 group-hover:bg-[#FF5F00] transition-colors shadow-sm border border-white"></div>
           </div>
        </div>

        {/* ----------------------------------------------------------------------------------
            PANE 3: AI COMMAND CONSOLE (Bottom-Right)
           ---------------------------------------------------------------------------------- */}
        <div 
          className="bg-white flex flex-col border-t border-gray-200 transition-all duration-300 z-20 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.1)] relative"
          style={{ height: isConsoleCollapsed ? '60px' : `${consoleHeight}%` }}
        >
           {/* Console Header / Toggle */}
           {!isConsoleCollapsed && (
             <div className="h-10 border-b border-gray-100 px-4 flex items-center justify-between shrink-0 bg-gray-50/50">
                <div className="flex items-center gap-3">
                   <div className="flex items-center gap-2">
                      <Terminal className="w-3.5 h-3.5 text-[#FF5F00]" />
                      <span className="text-xs font-bold text-gray-500 font-mono">AI_CONSOLE</span>
                   </div>
                </div>
                <button 
                   onClick={() => setIsConsoleCollapsed(true)}
                   className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded transition-colors"
                >
                   <PanelBottomOpen className="w-3.5 h-3.5" />
                </button>
             </div>
           )}

           {/* Log Content */}
           {!isConsoleCollapsed && (
             <div 
               className="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-[13px] custom-scrollbar bg-white"
               ref={scrollRef}
             >
                {logs.map((log) => (
                   <div key={log.id} className="flex gap-4 group animate-in slide-in-from-left-1 duration-200">
                      <div className="text-gray-300 shrink-0 select-none w-16 text-right pt-0.5 text-[11px]">{log.timestamp}</div>
                      <div className="flex-1 flex flex-col gap-1 items-start max-w-4xl">
                         <div className="shrink-0 flex items-center gap-2">
                            {log.type === 'system' && <span className="text-[10px] text-blue-500 font-bold">SYSTEM</span>}
                            {log.type === 'user' && <span className="text-[10px] text-gray-800 font-bold">USER</span>}
                            {log.type === 'ai' && <span className="text-[10px] text-[#FF5F00] font-bold">AI</span>}
                         </div>
                         <div className={`break-all whitespace-pre-wrap leading-relaxed ${
                            log.type === 'user' ? 'text-gray-900 font-medium' : 
                            log.type === 'ai' ? 'text-gray-600' : 'text-gray-400'
                         }`}>
                            {log.content}
                         </div>
                         {log.artifactLink && (
                            <button className="mt-1 flex items-center gap-2 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded hover:border-[#FF5F00] hover:text-[#FF5F00] transition-colors group/btn">
                               <FileText className="w-3 h-3 text-gray-400 group-hover/btn:text-[#FF5F00]" />
                               <span className="text-xs font-bold">View Artifact</span>
                               <ArrowRight className="w-3 h-3 opacity-50" />
                            </button>
                         )}
                      </div>
                   </div>
                ))}
                {isProcessing && (
                   <div className="pl-20 flex items-center gap-2 text-gray-400 text-xs">
                      <Bot className="w-4 h-4 animate-bounce text-[#FF5F00]" />
                      <span>Thinking...</span>
                   </div>
                )}
             </div>
           )}

           {/* Full Width Input Bar (Sticky Bottom) */}
           <div className={`border-t border-gray-200 bg-white shrink-0 ${isConsoleCollapsed ? 'h-full flex items-center' : 'h-[60px]'}`}>
              {isConsoleCollapsed ? (
                 <div className="w-full px-6 flex justify-between items-center cursor-pointer" onClick={() => setIsConsoleCollapsed(false)}>
                    <div className="flex items-center gap-3 text-gray-400">
                        <Terminal className="w-4 h-4" />
                        <span className="font-mono text-sm">Open Terminal...</span>
                    </div>
                    <PanelTopClose className="w-4 h-4 text-gray-400" />
                 </div>
              ) : (
                 <form onSubmit={handleCommand} className="flex items-center h-full px-6 relative group">
                    <span className="text-gray-300 mr-4 font-mono text-lg select-none group-focus-within:text-[#FF5F00] transition-colors">{'>_'}</span>
                    <input 
                       type="text" 
                       className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-[15px] font-mono text-gray-900 placeholder-gray-400 h-full leading-normal"
                       placeholder="AI에게 분석을 요청하세요..."
                       value={input}
                       onChange={(e) => setInput(e.target.value)}
                       autoFocus
                    />
                    <div className="ml-4 flex items-center gap-3 text-gray-400">
                        <div className="hidden group-focus-within:flex items-center gap-2 animate-in fade-in duration-200">
                            {['#Risk', '#Trend', '#Comp'].map(chip => (
                                <button 
                                    key={chip} type="button"
                                    onClick={() => setInput(prev => prev + chip + ' ')}
                                    className="px-2 py-0.5 bg-gray-100 hover:bg-gray-200 hover:text-gray-700 rounded text-[10px] font-bold font-mono transition-colors"
                                >
                                    {chip}
                                </button>
                            ))}
                        </div>
                        <div className="h-4 w-px bg-gray-200 mx-2"></div>
                        <button type="submit" disabled={!input.trim()} className="text-gray-300 hover:text-[#FF5F00] disabled:opacity-50 transition-colors">
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                 </form>
              )}
           </div>
        </div>

      </div>
    </div>
  );
};

export default Analytics;
