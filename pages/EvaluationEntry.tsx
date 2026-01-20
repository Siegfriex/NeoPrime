import React, { useState, useEffect } from 'react';
import { STUDENTS } from '../services/mockData';
import { generateAIFeedback } from '../services/geminiService';
import { Sparkles, Save, Brain, X, Copy, Check, ChevronRight, Wand2 } from 'lucide-react';

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

  const selectedStudent = STUDENTS.find(s => s.id === selectedStudentId);

  // Thinking Animation Steps
  const thinkingMessages = [
    "Analyzing composition balance...",
    "Checking tonal contrast and depth...",
    "Evaluating creative concept...",
    "Synthesizing actionable advice...",
    "Finalizing report..."
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
              <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col relative z-10 animate-in zoom-in-95 duration-200">
                  
                  {/* Header */}
                  <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 rounded-t-2xl">
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
                  <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                      {isGenerating ? (
                          <div className="flex flex-col items-center justify-center py-20 space-y-6">
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
                          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
                              
                              {/* Overall Score Summary */}
                              <div className="flex items-center gap-4 bg-[#F7F9FB] p-5 rounded-xl border border-gray-200">
                                  <div className="flex-1">
                                      <div className="text-xs text-gray-400 uppercase font-bold mb-1">Total Score</div>
                                      <div className="text-3xl font-bold text-gray-900">
                                          {scores.composition + scores.tone + scores.idea + scores.completeness}
                                          <span className="text-sm text-gray-400 font-medium"> / 40</span>
                                      </div>
                                  </div>
                                  <div className="h-10 w-px bg-gray-300"></div>
                                  <div className="flex gap-6 text-sm text-gray-600 px-4">
                                      <div className="flex flex-col items-center">
                                          <span className="font-bold text-lg">{scores.composition}</span>
                                          <span className="text-[10px] text-gray-400 uppercase tracking-wide">Comp</span>
                                      </div>
                                      <div className="flex flex-col items-center">
                                          <span className="font-bold text-lg">{scores.tone}</span>
                                          <span className="text-[10px] text-gray-400 uppercase tracking-wide">Tone</span>
                                      </div>
                                      <div className="flex flex-col items-center">
                                          <span className="font-bold text-lg">{scores.idea}</span>
                                          <span className="text-[10px] text-gray-400 uppercase tracking-wide">Idea</span>
                                      </div>
                                  </div>
                              </div>

                              {/* Feedback Sections */}
                              <div className="space-y-6">
                                  <div className="relative pl-6 border-l-2 border-emerald-200">
                                      <div className="absolute -left-[9px] top-0 w-4 h-4 bg-emerald-100 rounded-full border-2 border-emerald-400 flex items-center justify-center">
                                          <Check className="w-2 h-2 text-emerald-700" />
                                      </div>
                                      <h4 className="text-emerald-800 font-bold mb-2 flex items-center gap-2">
                                          Key Strengths
                                      </h4>
                                      <p className="text-gray-700 leading-relaxed text-sm bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                                          {generatedFeedback?.strengths}
                                      </p>
                                  </div>

                                  <div className="relative pl-6 border-l-2 border-rose-200">
                                      <div className="absolute -left-[9px] top-0 w-4 h-4 bg-rose-100 rounded-full border-2 border-rose-400 flex items-center justify-center">
                                          <X className="w-2 h-2 text-rose-700" />
                                      </div>
                                      <h4 className="text-rose-800 font-bold mb-2">Core Weaknesses</h4>
                                      <p className="text-gray-700 leading-relaxed text-sm bg-rose-50/50 p-4 rounded-xl border border-rose-100">
                                          {generatedFeedback?.weaknesses}
                                      </p>
                                  </div>

                                  <div className="relative pl-6 border-l-2 border-[#FC6401]/30">
                                      <div className="absolute -left-[9px] top-0 w-4 h-4 bg-[#FFF0E6] rounded-full border-2 border-[#FC6401] flex items-center justify-center">
                                          <ChevronRight className="w-3 h-3 text-[#FC6401]" />
                                      </div>
                                      <h4 className="text-[#FC6401] font-bold mb-2">Next Week's Action Plan</h4>
                                      <div className="bg-[#FFF0E6] p-5 rounded-xl border border-[#FC6401]/20">
                                          <p className="text-gray-800 font-medium leading-relaxed text-sm">
                                              {generatedFeedback?.actionPlan}
                                          </p>
                                      </div>
                                  </div>
                              </div>
                          </div>
                      )}
                  </div>

                  {/* Footer */}
                  {!isGenerating && (
                      <div className="p-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-between items-center gap-4">
                          <button 
                              onClick={() => copyToClipboard(JSON.stringify(generatedFeedback, null, 2))}
                              className="px-4 py-2.5 text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-100 font-medium text-sm flex items-center gap-2 transition-colors"
                          >
                              <Copy className="w-4 h-4" />
                              Copy Text
                          </button>
                          <button 
                              onClick={handleSave}
                              className="px-6 py-2.5 bg-[#FC6401] text-white rounded-xl hover:bg-[#e55a00] font-bold shadow-lg shadow-[#FC6401]/30 flex items-center gap-2 transition-all"
                          >
                              <Save className="w-4 h-4" />
                              Confirm & Save
                          </button>
                      </div>
                  )}
              </div>
          </div>
      )}
    </div>
  );
};

export default EvaluationEntry;