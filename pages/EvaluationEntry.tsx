import React, { useState, useEffect } from 'react';
import { STUDENTS } from '../services/mockData';
import { generateAIFeedback } from '../services/geminiService';
import { Sparkles, Save, Brain, X, Copy, Check, ChevronRight, Wand2, GraduationCap, ArrowUpRight, ArrowDownRight, LayoutTemplate, SplitSquareHorizontal } from 'lucide-react';
import { Student } from '../types';

const EvaluationEntry: React.FC = () => {
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [scores, setScores] = useState({ composition: 5, tone: 5, idea: 5, completeness: 5 });
  const [notes, setNotes] = useState('');
  const [useThinking, setUseThinking] = useState(false);
  
  // Modal & Generation State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedFeedback, setGeneratedFeedback] = useState<any>(null);
  const [thinkingStep, setThinkingStep] = useState(0);

  // Comparison State
  const [selectedComparisonCase, setSelectedComparisonCase] = useState<any>(null);

  const selectedStudent = STUDENTS.find(s => s.id === selectedStudentId);

  // Thinking Animation Steps
  const thinkingMessages = [
    "Analyzing composition balance...",
    "Retrieving academic standing...",
    "Fetching similar past portfolios...",
    "Comparing visual patterns...",
    "Synthesizing strategic advice..."
  ];

  useEffect(() => {
    let interval: any;
    if (isGenerating && useThinking) {
      interval = setInterval(() => {
        setThinkingStep((prev) => (prev + 1) % thinkingMessages.length);
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [isGenerating, useThinking]);

  const handleScoreChange = (key: string, value: number) => {
    setScores(prev => ({ ...prev, [key]: value }));
  };

  const handleGenerateAI = async () => {
    if (!selectedStudent) return;
    
    setIsModalOpen(true);
    setIsGenerating(true);
    setGeneratedFeedback(null);
    setThinkingStep(0);
    setSelectedComparisonCase(null);

    if (useThinking) {
        await new Promise(resolve => setTimeout(resolve, 2500));
    }

    const feedback = await generateAIFeedback(selectedStudent, scores, notes, useThinking);
    setGeneratedFeedback(feedback);
    setIsGenerating(false);
  };

  const handleSave = () => {
    alert('Evaluation saved! (Mock Action)');
    setNotes('');
    setGeneratedFeedback(null);
    setIsModalOpen(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  // Mock Academic Positioning Data Calculation
  const getAcademicPosition = (student: Student) => {
    // Just using Korean score as a proxy for the demo
    const studentScore = student.academicScores.korean.percentile || 0;
    const targetAvg = student.targetUnivAvgScores.korean.percentile || 0;
    const diff = studentScore - targetAvg;
    return { studentScore, targetAvg, diff };
  };

  // Mock Similar Cases (In a real app, this would come from the AI or DB based on embeddings)
  const mockSimilarCases = [
    { id: 'sc1', name: 'J.K.', year: 2025, result: 'Accepted', line: 'TOP', img: 'https://images.unsplash.com/photo-1544531586-fde5298cdd40?q=80&w=300&auto=format&fit=crop' },
    { id: 'sc2', name: 'M.S.', year: 2024, result: 'Accepted', line: 'HIGH', img: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=300&auto=format&fit=crop' },
    { id: 'sc3', name: 'H.L.', year: 2024, result: 'Waitlisted', line: 'MID', img: 'https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?q=80&w=300&auto=format&fit=crop' }
  ];

  return (
    <div className="max-w-4xl mx-auto relative animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">New Evaluation</h1>
        <p className="text-gray-500 mt-1">Record weekly progress and generate AI feedback.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Form */}
        <div className="lg:col-span-2 space-y-6">
            
            {/* Student Selection */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Student</label>
                <select 
                    className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] focus:border-[#FC6401] outline-none transition-all"
                    value={selectedStudentId}
                    onChange={(e) => setSelectedStudentId(e.target.value)}
                >
                    <option value="">-- Choose a student --</option>
                    {STUDENTS.map(s => (
                        <option key={s.id} value={s.id}>{s.name} ({s.grade})</option>
                    ))}
                </select>
                
                {selectedStudent && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-xl flex items-center gap-4">
                        <img src={selectedStudent.avatarUrl} alt="" className="w-12 h-12 rounded-full border-2 border-white shadow-sm" />
                        <div>
                            <p className="font-semibold text-gray-900">{selectedStudent.name}</p>
                            <p className="text-sm text-gray-500">{selectedStudent.targetUniversity} • {selectedStudent.major}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Scores */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 opacity-100 transition-opacity">
                <h3 className="text-lg font-bold text-gray-900 mb-6">4-Axis Scoring</h3>
                <div className="space-y-6">
                    {Object.entries(scores).map(([key, value]) => (
                        <div key={key}>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-medium text-gray-700 capitalize">{key}</label>
                                <span className="text-sm font-bold text-[#FC6401]">{value}/10</span>
                            </div>
                            <input 
                                type="range" 
                                min="0" 
                                max="10" 
                                step="0.5"
                                value={value}
                                onChange={(e) => handleScoreChange(key, parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#FC6401]"
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Notes */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Instructor Notes</h3>
                <textarea 
                    className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#FC6401] outline-none h-32 resize-none"
                    placeholder="Describe specific observations about the artwork..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                />
            </div>
        </div>

        {/* Right Column: Actions */}
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 sticky top-24">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    {useThinking ? <Brain className="w-5 h-5 text-[#FC6401]" /> : <Sparkles className="w-5 h-5 text-[#FC6401]" />}
                    {useThinking ? "Deep Feedback" : "AI Feedback Assistant"}
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                    {useThinking 
                        ? "Using Gemini 3.0 Pro with reasoning capabilities for complex analysis."
                        : "Generate structured feedback based on your scores and notes."
                    }
                </p>

                {/* Toggle for Thinking Mode */}
                <div className="flex items-center gap-2 mb-6 p-3 bg-gray-50 rounded-xl border border-gray-100">
                     <label className="relative inline-flex items-center cursor-pointer">
                        <input 
                            type="checkbox" 
                            className="sr-only peer" 
                            checked={useThinking}
                            onChange={(e) => setUseThinking(e.target.checked)}
                        />
                        <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-[#FC6401]/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#FC6401]"></div>
                        <span className="ml-3 text-sm font-medium text-gray-700">Thinking Mode</span>
                     </label>
                     <Brain className={`w-4 h-4 ${useThinking ? 'text-[#FC6401]' : 'text-gray-400'}`} />
                </div>

                <button 
                    onClick={handleGenerateAI}
                    disabled={!selectedStudent}
                    className={`w-full py-3 px-4 rounded-xl font-medium text-white flex items-center justify-center gap-2 transition-all
                        ${!selectedStudent 
                            ? 'bg-gray-300 cursor-not-allowed' 
                            : 'bg-[#FC6401] hover:bg-[#e55a00] shadow-lg shadow-[#FC6401]/30'}`}
                >
                    <Wand2 className="w-5 h-5" />
                    Generate Feedback
                </button>
            </div>
        </div>
      </div>

      {/* --- AI FEEDBACK MODAL --- */}
      {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              {/* Backdrop */}
              <div 
                  className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity"
                  onClick={() => setIsModalOpen(false)}
              ></div>

              {/* Modal Content */}
              <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[95vh] flex flex-col relative z-10 animate-in zoom-in-95 duration-200 overflow-hidden">
                  
                  {/* Header */}
                  <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                      <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-xl ${useThinking ? 'bg-[#FFF0E6] text-[#FC6401]' : 'bg-amber-50 text-amber-600'}`}>
                              {useThinking ? <Brain className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
                          </div>
                          <div>
                              <h3 className="font-bold text-gray-900 text-lg">AI Deep Feedback</h3>
                              <p className="text-xs text-gray-500">
                                  for {selectedStudent?.name} • {new Date().toLocaleDateString()}
                              </p>
                          </div>
                      </div>
                      <button 
                          onClick={() => setIsModalOpen(false)}
                          className="p-2 hover:bg-gray-200 rounded-full text-gray-500 transition-colors"
                      >
                          <X className="w-5 h-5" />
                      </button>
                  </div>

                  {/* Body - Scrollable */}
                  <div className="flex-1 overflow-y-auto custom-scrollbar bg-[#F7F9FB]">
                      {isGenerating ? (
                          <div className="flex flex-col items-center justify-center py-32 space-y-6">
                              <div className="relative">
                                  <div className="w-16 h-16 border-4 border-[#FFF0E6] border-t-[#FC6401] rounded-full animate-spin"></div>
                                  <div className="absolute inset-0 flex items-center justify-center">
                                      <Brain className="w-6 h-6 text-[#FC6401] animate-pulse" />
                                  </div>
                              </div>
                              <div className="text-center space-y-2">
                                  <h4 className="text-lg font-bold text-gray-900">Generating Insight...</h4>
                                  <p className="text-[#FC6401] font-medium animate-pulse">
                                      {useThinking ? thinkingMessages[thinkingStep] : "Processing evaluation data..."}
                                  </p>
                              </div>
                          </div>
                      ) : (
                          <div className="p-6 space-y-6">
                              
                              {/* Top Row: Score & Academic Positioning */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                  {/* Score Summary */}
                                  <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-center">
                                      <div className="flex justify-between items-center mb-3">
                                          <div className="text-xs text-gray-400 uppercase font-bold">Practical Score</div>
                                          <div className="text-xs font-bold text-[#FC6401] bg-[#FFF0E6] px-2 py-0.5 rounded">
                                              {scores.composition + scores.tone + scores.idea + scores.completeness} / 40
                                          </div>
                                      </div>
                                      <div className="flex gap-4 justify-between">
                                          {Object.entries(scores).map(([k, v]) => (
                                              <div key={k} className="flex flex-col items-center">
                                                  <span className="font-bold text-gray-900 text-lg">{v}</span>
                                                  <span className="text-[10px] text-gray-400 uppercase">{k.slice(0,3)}</span>
                                              </div>
                                          ))}
                                      </div>
                                  </div>

                                  {/* Academic Positioning */}
                                  {selectedStudent && (
                                      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                                          <div className="flex justify-between items-start mb-2">
                                              <div className="flex items-center gap-2">
                                                  <GraduationCap className="w-4 h-4 text-gray-400" />
                                                  <span className="text-xs font-bold text-gray-900 uppercase">Academic Positioning</span>
                                              </div>
                                              <span className="text-[10px] text-gray-400">{selectedStudent.targetUniversity}</span>
                                          </div>
                                          
                                          {(() => {
                                              const { studentScore, targetAvg, diff } = getAcademicPosition(selectedStudent);
                                              const isPositive = diff >= 0;
                                              return (
                                                  <div>
                                                      <div className="text-sm text-gray-600 mb-3">
                                                          Top <span className="font-bold text-gray-900">{100 - studentScore}%</span> range 
                                                          <span className={`ml-2 text-xs font-bold ${isPositive ? 'text-emerald-600' : 'text-rose-500'}`}>
                                                              ({isPositive ? '+' : ''}{diff}pts vs Median)
                                                          </span>
                                                      </div>
                                                      
                                                      {/* Visual Bar */}
                                                      <div className="relative h-2.5 bg-gray-100 rounded-full w-full mt-2">
                                                          {/* Median Marker */}
                                                          <div className="absolute top-0 bottom-0 w-0.5 bg-gray-400 z-10" style={{ left: `${targetAvg}%` }}></div>
                                                          <div className="absolute -top-4 text-[9px] text-gray-400 font-medium transform -translate-x-1/2" style={{ left: `${targetAvg}%` }}>Avg</div>
                                                          
                                                          {/* Student Marker */}
                                                          <div 
                                                              className={`absolute top-1/2 transform -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white shadow-sm ${isPositive ? 'bg-emerald-500' : 'bg-rose-500'}`} 
                                                              style={{ left: `${studentScore}%` }}
                                                          ></div>
                                                      </div>
                                                  </div>
                                              );
                                          })()}
                                      </div>
                                  )}
                              </div>

                              {/* Feedback Sections */}
                              <div className="space-y-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                                  <div className="flex gap-4 items-start">
                                      <div className="mt-1 w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                                          <Check className="w-3.5 h-3.5" />
                                      </div>
                                      <div>
                                          <h4 className="text-sm font-bold text-gray-900">Key Strengths</h4>
                                          <p className="text-sm text-gray-600 mt-1">{generatedFeedback?.strengths}</p>
                                      </div>
                                  </div>
                                  <div className="w-full h-px bg-gray-100"></div>
                                  
                                  <div className="flex gap-4 items-start">
                                      <div className="mt-1 w-6 h-6 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center shrink-0">
                                          <X className="w-3.5 h-3.5" />
                                      </div>
                                      <div>
                                          <h4 className="text-sm font-bold text-gray-900">Core Weaknesses</h4>
                                          <p className="text-sm text-gray-600 mt-1">{generatedFeedback?.weaknesses}</p>
                                      </div>
                                  </div>
                                  <div className="w-full h-px bg-gray-100"></div>

                                  <div className="flex gap-4 items-start">
                                      <div className="mt-1 w-6 h-6 rounded-full bg-[#FFF0E6] text-[#FC6401] flex items-center justify-center shrink-0">
                                          <ChevronRight className="w-3.5 h-3.5" />
                                      </div>
                                      <div>
                                          <h4 className="text-sm font-bold text-[#FC6401]">Action Plan</h4>
                                          <p className="text-sm text-gray-800 font-medium mt-1">{generatedFeedback?.actionPlan}</p>
                                      </div>
                                  </div>
                              </div>

                              {/* Similar Cases & Comparison */}
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                  {/* Left: Gallery */}
                                  <div className="md:col-span-1 space-y-3">
                                      <h4 className="text-xs font-bold text-gray-500 uppercase flex items-center gap-2">
                                          <LayoutTemplate className="w-3 h-3" /> Similar Portfolios
                                      </h4>
                                      <div className="grid grid-cols-1 gap-3">
                                          {mockSimilarCases.map((sc) => (
                                              <button 
                                                key={sc.id}
                                                onClick={() => setSelectedComparisonCase(sc)}
                                                className={`flex items-center gap-3 p-2 rounded-xl border transition-all text-left group
                                                    ${selectedComparisonCase?.id === sc.id 
                                                        ? 'bg-gray-800 border-gray-800 text-white' 
                                                        : 'bg-white border-gray-200 hover:border-[#FC6401]'}`}
                                              >
                                                  <img src={sc.img} alt="" className="w-12 h-12 rounded-lg object-cover bg-gray-200" />
                                                  <div>
                                                      <div className="font-bold text-sm">{sc.name} · {sc.year}</div>
                                                      <div className="flex items-center gap-2 mt-0.5">
                                                          <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                                                              sc.result === 'Accepted' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'
                                                          }`}>
                                                              {sc.result}
                                                          </span>
                                                          <span className="text-[10px] text-gray-400">{sc.line} Line</span>
                                                      </div>
                                                  </div>
                                              </button>
                                          ))}
                                      </div>
                                  </div>

                                  {/* Right: Insights */}
                                  <div className="md:col-span-2 bg-[#F0F4F8] rounded-2xl p-5 border border-gray-200 flex flex-col relative overflow-hidden">
                                      <div className="absolute top-0 right-0 p-16 bg-[#FC6401] opacity-5 blur-3xl rounded-full pointer-events-none"></div>
                                      
                                      <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2 relative z-10">
                                          <SplitSquareHorizontal className="w-4 h-4 text-gray-500" />
                                          Comparison Analysis
                                      </h4>

                                      {generatedFeedback?.comparisonInsight ? (
                                          <div className="space-y-4 relative z-10 text-sm">
                                              <div className="p-3 bg-white rounded-xl shadow-sm border border-gray-100">
                                                  <span className="text-xs font-bold text-emerald-600 uppercase mb-1 block">Similarities</span>
                                                  <p className="text-gray-600 leading-relaxed">{generatedFeedback.comparisonInsight.similarities}</p>
                                              </div>
                                              <div className="p-3 bg-white rounded-xl shadow-sm border border-gray-100">
                                                  <span className="text-xs font-bold text-gray-500 uppercase mb-1 block">Key Differences</span>
                                                  <p className="text-gray-600 leading-relaxed">{generatedFeedback.comparisonInsight.differences}</p>
                                              </div>
                                              <div className="p-3 bg-[#FFF0E6] rounded-xl shadow-sm border border-[#FC6401]/10">
                                                  <span className="text-xs font-bold text-[#FC6401] uppercase mb-1 block">Your Unique Advantage</span>
                                                  <p className="text-gray-800 font-medium leading-relaxed">{generatedFeedback.comparisonInsight.usp}</p>
                                              </div>
                                          </div>
                                      ) : (
                                          <div className="flex-1 flex items-center justify-center text-gray-400 text-sm italic">
                                              Generating comparative insights...
                                          </div>
                                      )}
                                  </div>
                              </div>
                          </div>
                      )}
                  </div>

                  {/* Footer */}
                  {!isGenerating && (
                      <div className="p-4 border-t border-gray-100 bg-white flex justify-between items-center gap-4">
                          <button 
                              onClick={() => copyToClipboard(JSON.stringify(generatedFeedback, null, 2))}
                              className="px-4 py-2.5 text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 font-medium text-sm flex items-center gap-2 transition-colors"
                          >
                              <Copy className="w-4 h-4" />
                              Copy Text
                          </button>
                          <button 
                              onClick={handleSave}
                              className="px-6 py-2.5 bg-[#FC6401] text-white rounded-xl hover:bg-[#e55a00] font-bold shadow-lg shadow-[#FC6401]/30 flex items-center gap-2 transition-all"
                          >
                              <Save className="w-4 h-4" />
                              Save & Close
                          </button>
                      </div>
                  )}

                  {/* Side-by-Side Overlay (When a case is selected) */}
                  {selectedComparisonCase && (
                      <div className="absolute inset-0 bg-white z-20 flex flex-col animate-in slide-in-from-right duration-300">
                          <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                              <h3 className="font-bold text-gray-900 flex items-center gap-2">
                                  <LayoutTemplate className="w-4 h-4" />
                                  Comparison View
                              </h3>
                              <button onClick={() => setSelectedComparisonCase(null)} className="p-2 hover:bg-gray-200 rounded-full">
                                  <X className="w-5 h-5" />
                              </button>
                          </div>
                          <div className="flex-1 grid grid-cols-2 gap-4 p-4 overflow-hidden">
                              {/* Current Student */}
                              <div className="flex flex-col h-full bg-gray-50 rounded-xl p-4">
                                  <div className="flex items-center gap-2 mb-3">
                                      <div className="w-2 h-2 rounded-full bg-[#FC6401]"></div>
                                      <span className="font-bold text-gray-900">{selectedStudent?.name}</span>
                                      <span className="text-xs text-gray-500">(Current)</span>
                                  </div>
                                  <div className="flex-1 bg-white rounded-lg border border-gray-200 flex items-center justify-center text-gray-400">
                                      {/* Placeholder for current artwork */}
                                      {selectedStudent?.artworks?.[0] ? (
                                        <img src={selectedStudent.artworks[0]} className="w-full h-full object-contain" alt="Current work" />
                                      ) : (
                                        <span>No Artwork</span>
                                      )}
                                  </div>
                                  <div className="mt-3 grid grid-cols-4 gap-2 text-center text-xs">
                                      <div className="bg-white p-2 rounded border">
                                          <div className="font-bold text-[#FC6401]">{scores.composition}</div>
                                          <div className="text-[9px] text-gray-400 uppercase">Comp</div>
                                      </div>
                                      <div className="bg-white p-2 rounded border">
                                          <div className="font-bold text-[#FC6401]">{scores.tone}</div>
                                          <div className="text-[9px] text-gray-400 uppercase">Tone</div>
                                      </div>
                                      <div className="bg-white p-2 rounded border">
                                          <div className="font-bold text-[#FC6401]">{scores.idea}</div>
                                          <div className="text-[9px] text-gray-400 uppercase">Idea</div>
                                      </div>
                                      <div className="bg-white p-2 rounded border">
                                          <div className="font-bold text-[#FC6401]">{scores.completeness}</div>
                                          <div className="text-[9px] text-gray-400 uppercase">Att</div>
                                      </div>
                                  </div>
                              </div>

                              {/* Comparison Case */}
                              <div className="flex flex-col h-full bg-gray-900 rounded-xl p-4 text-white">
                                  <div className="flex items-center gap-2 mb-3">
                                      <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
                                      <span className="font-bold">{selectedComparisonCase.name}</span>
                                      <span className="text-xs text-gray-400">({selectedComparisonCase.year})</span>
                                      <span className="ml-auto text-xs bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded">
                                          {selectedComparisonCase.result}
                                      </span>
                                  </div>
                                  <div className="flex-1 bg-black/50 rounded-lg border border-gray-700 overflow-hidden">
                                      <img src={selectedComparisonCase.img} className="w-full h-full object-contain" alt="Comparison work" />
                                  </div>
                                  <div className="mt-3">
                                      <p className="text-xs text-gray-400 leading-relaxed italic">
                                          "This piece was noted for its exceptional spatial depth and daring color choices in the focal area."
                                      </p>
                                  </div>
                              </div>
                          </div>
                      </div>
                  )}
              </div>
          </div>
      )}
    </div>
  );
};

export default EvaluationEntry;