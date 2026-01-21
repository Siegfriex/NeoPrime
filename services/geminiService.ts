import { GoogleGenAI, Type, Schema } from '@google/genai';
import { Student, EvaluationScore } from '../types';
import { STUDENTS } from './mockData';

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

// --- Type Definitions for Advanced Analytics ---

export type AnalysisMode = "explain" | "compare" | "simulate";

export interface Factor {
  name: string;                
  impact: number;              
  direction: "positive" | "negative";
  explanation: string;        
}

export interface ExplainResult {
  targetMetric: string;       
  baselineValue: number;     
  currentValue: number;      
  delta: number;             
  factors: Factor[];          
}

export interface SegmentMetrics {
  size: number;               
  acceptanceRate: number;    
  avgPracticalScore: number;  
  avgAttendanceRate: number;  
}

export interface CompareResult {
  segmentA: { name: string; metrics: SegmentMetrics }; 
  segmentB: { name: string; metrics: SegmentMetrics }; 
  lift: {
    acceptanceRate: number;  
  };
  explanation: string;        
}

export interface ControlEffect {
  control: string;            
  currentValue: number;       
  targetValue: number;        
  estimatedDelta: number;
}

export interface SimulateResult {
  baseline: { acceptanceRate: number };   
  scenario: { acceptanceRate: number };   
  controls: ControlEffect[];  
  explanation: string;        
}

export interface AnalyzeAcademyDataResponse {
  mode: AnalysisMode;
  summary: string;
  recommendation: string;
  explainResult?: ExplainResult;
  compareResult?: CompareResult;
  simulateResult?: SimulateResult;
}

// --- Feedback Generation ---
export const generateAIFeedback = async (
  student: Student,
  scores: EvaluationScore,
  notes: string,
  useThinking: boolean = false
) => {
  if (!apiKey) {
    console.warn("API Key is missing. Returning mock response.");
    return {
      strengths: "구도 밸런스가 뛰어나며 주제부의 대비(Contrast) 활용이 돋보입니다. 특히 화면 중앙에서 외곽으로 빠지는 시선 처리가 매끄럽습니다.",
      weaknesses: "배경부의 디테일 묘사가 다소 급하게 마무리되어 공간감이 부족합니다. 주제부와 배경 사이의 중간 톤 처리가 약해 깊이감이 덜 느껴집니다.",
      actionPlan: "다음 주에는 배경 요소의 외곽 정리를 통해 공간의 깊이를 더하는 연습에 집중하세요. 3단계 명도 단계를 활용하여 거리감을 표현하는 연습이 필요합니다.",
      comparisonInsight: {
        similarities: "구도의 안정성은 작년 홍익대 합격생 상위 30% 그룹의 초기 작품 패턴과 유사합니다.",
        differences: "합격작들은 배경 텍스처 활용에서 더 실험적인 시도를 보였으나, 현재 학생은 안정적인 톤에 머물러 있습니다.",
        usp: "과감한 원색 사용이 평균적인 합격 포트폴리오보다 더 높은 시각적 임팩트를 줍니다. 이를 입시 전략의 핵심(Key Visual)으로 삼아야 합니다."
      }
    };
  }

  const prompt = `
    당신은 전문 입시 미술 학원 원장입니다. 학생에게 평가 피드백을 제공해야 합니다.
    
    학생 정보: ${student.name} (${student.grade}, 목표: ${student.targetUniversity}, 전공: ${student.major})
    
    평가 점수 (0-10점):
    - 구도 (Composition): ${scores.composition}
    - 톤/명암 (Tone/Contrast): ${scores.tone}
    - 발상/연출 (Idea/Concept): ${scores.idea}
    - 완성도 (Completeness): ${scores.completeness}
    
    강사 노트: "${notes}"

    컨텍스트: 이 학생의 현재 작품을 ${student.targetUniversity}의 과거 합격 포트폴리오와 비교하여 분석하세요.
    
    점수와 노트를 바탕으로 구조화된 피드백 리포트를 한국어로 생성하세요.
    어조는 전문적이고 직설적이지만 격려하는 태도(원장님 스타일)를 유지하세요.
    각 항목은 최소 2문장 이상으로 구체적으로 작성하세요.
  `;

  // Use gemini-3-pro-preview for higher quality feedback
  const model = useThinking ? 'gemini-3-pro-preview' : 'gemini-3-flash-preview';

  const config: any = {
    responseMimeType: 'application/json',
    responseSchema: {
      type: Type.OBJECT,
      properties: {
        strengths: { type: Type.STRING, description: "학생이 잘한 점 (한국어)" },
        weaknesses: { type: Type.STRING, description: "핵심 보완 사항 (한국어)" },
        actionPlan: { type: Type.STRING, description: "다음 주 구체적인 행동 계획 (한국어)" },
        comparisonInsight: {
          type: Type.OBJECT,
          properties: {
            similarities: { type: Type.STRING, description: "합격생들과의 공통점" },
            differences: { type: Type.STRING, description: "합격생들에 비해 부족한 점" },
            usp: { type: Type.STRING, description: "이 학생만의 유니크한 강점 (USP)" }
          }
        }
      },
      required: ['strengths', 'weaknesses', 'actionPlan', 'comparisonInsight']
    }
  };

  if (useThinking) {
    config.thinkingConfig = { thinkingBudget: 32768 };
  }

  try {
    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config
    });

    const text = response.text;
    if (!text) throw new Error("No response from AI");
    
    return JSON.parse(text);
  } catch (error) {
    console.error("Gemini API Error:", error);
    return {
      strengths: "주제부 표현에 노력을 기울였습니다.",
      weaknesses: "연결 문제로 상세 피드백을 생성하지 못했습니다.",
      actionPlan: "담당 강사의 수기 노트를 확인해주세요.",
      comparisonInsight: { similarities: "N/A", differences: "N/A", usp: "N/A" }
    };
  }
};

// --- Chatbot Capabilities ---
const getAcademyContext = () => {
  const summary = STUDENTS.map(s => 
    `- ${s.name}(${s.grade}): 목표 ${s.targetUniversity} ${s.major}, 현재레벨 ${s.currentLevel}, 국어 ${s.academicScores.korean.standardScore}점`
  ).join('\n');
  
  return `
    현재 학원생 데이터 요약:
    ${summary}
    
    총 학생 수: ${STUDENTS.length}명
  `;
};

export const createChatSession = () => {
  const systemInstruction = `
    당신은 'NeoPrime' 미술학원의 AI 입시 분석 어시스턴트입니다.
    원장님(사용자)의 질문에 대해 학원 데이터를 기반으로 분석적인 답변을 제공해야 합니다.
    
    [데이터 컨텍스트]
    ${getAcademyContext()}
    
    [행동 지침]
    1. 데이터에 기반하여 구체적인 수치나 학생 이름을 언급하며 답변하세요.
    2. 입시 전문가스러운 톤(전문적, 분석적)을 유지하세요.
    3. 질문이 모호하면 데이터를 기반으로 역질문하거나 가능한 시나리오를 제시하세요.
  `;

  return ai.chats.create({
    model: 'gemini-3-pro-preview',
    config: {
      systemInstruction,
      temperature: 0.7,
    },
  });
};

// --- Advanced Analytics Query Capabilities ---
export const analyzeAcademyData = async (query: string, historyContext?: string): Promise<AnalyzeAcademyDataResponse | null> => {
  if (!apiKey) {
    // Fallback mock response for demo
    console.warn("No API Key. Returning mock for 'compare' mode demo.");
    return {
      mode: "simulate",
      summary: "상향 지원 비율 조정 시 합격률 변화 시뮬레이션입니다. 상향 지원을 줄이고 안정권 지원을 늘릴 경우 전체 합격률이 상승하는 경향을 보입니다.",
      recommendation: "상향 지원 비율을 20% 이하로 조정하고, 안정권 대학의 실기 준비 비중을 높이세요.",
      simulateResult: {
        baseline: { acceptanceRate: 52 },
        scenario: { acceptanceRate: 65 },
        controls: [
          { control: "상향 지원 비율", currentValue: 30, targetValue: 15, estimatedDelta: 8 },
          { control: "출결 달성률", currentValue: 85, targetValue: 95, estimatedDelta: 5 }
        ],
        explanation: "상향 지원 비율을 15%p 낮추면 합격률이 약 8%p 상승할 것으로 예측됩니다. 또한 출결을 95%까지 개선하면 추가적인 5%p 상승 효과가 기대됩니다."
      }
    };
  }

  const prompt = `
    당신은 NeoPrime 미술학원의 수석 데이터 분석가 AI입니다.
    원장님의 질문을 분석하여 다음 세 가지 모드 중 하나를 선택하고, JSON 형식으로 응답하세요.

    [분석 모드 정의]
    1. explain: "왜 떨어졌어?", "원인이 뭐야?", "상세 분석해줘" 등 인과관계 분석.
    2. compare: "A랑 B 비교해줘", "특강 효과 어때?" 등 세그먼트 비교.
    3. simulate: "만약 ~하면?", "상향 비율 줄이면?", "출결 올리면?" 등 가상 시나리오 예측.

    [학원생 데이터 컨텍스트]
    ${getAcademyContext()}

    [이전 대화 컨텍스트]
    ${historyContext || "없음"}

    [질문]
    "${query}"

    [응답 규칙]
    - 질문의 의도에 가장 적합한 'mode'를 선택하세요.
    - 선택한 mode에 해당하는 Result 필드(explainResult, compareResult, simulateResult) 중 하나를 반드시 채우세요.
    - summary는 분석 결과를 **최소 3문장 이상**으로 상세하고 논리적으로 작성하세요. 구체적인 수치와 근거를 포함해야 합니다.
    - recommendation은 원장님을 위한 구체적인 액션 아이템을 제안하세요.
  `;

  const config: any = {
    responseMimeType: 'application/json',
    responseSchema: {
      type: Type.OBJECT,
      properties: {
        mode: { type: Type.STRING, enum: ["explain", "compare", "simulate"] },
        summary: { type: Type.STRING },
        recommendation: { type: Type.STRING },
        
        // Explain Mode Schema
        explainResult: {
          type: Type.OBJECT,
          properties: {
            targetMetric: { type: Type.STRING },
            baselineValue: { type: Type.NUMBER },
            currentValue: { type: Type.NUMBER },
            delta: { type: Type.NUMBER },
            factors: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING },
                  impact: { type: Type.NUMBER },
                  direction: { type: Type.STRING, enum: ["positive", "negative"] },
                  explanation: { type: Type.STRING }
                }
              }
            }
          }
        },

        // Compare Mode Schema
        compareResult: {
          type: Type.OBJECT,
          properties: {
            segmentA: { 
              type: Type.OBJECT, 
              properties: {
                name: { type: Type.STRING },
                metrics: {
                  type: Type.OBJECT,
                  properties: {
                    size: { type: Type.NUMBER },
                    acceptanceRate: { type: Type.NUMBER },
                    avgPracticalScore: { type: Type.NUMBER },
                    avgAttendanceRate: { type: Type.NUMBER }
                  }
                }
              }
            },
            segmentB: { 
              type: Type.OBJECT, 
              properties: {
                name: { type: Type.STRING },
                metrics: {
                  type: Type.OBJECT,
                  properties: {
                    size: { type: Type.NUMBER },
                    acceptanceRate: { type: Type.NUMBER },
                    avgPracticalScore: { type: Type.NUMBER },
                    avgAttendanceRate: { type: Type.NUMBER }
                  }
                }
              }
            },
            lift: {
              type: Type.OBJECT,
              properties: { acceptanceRate: { type: Type.NUMBER } }
            },
            explanation: { type: Type.STRING }
          }
        },

        // Simulate Mode Schema
        simulateResult: {
          type: Type.OBJECT,
          properties: {
            baseline: { 
              type: Type.OBJECT, 
              properties: { acceptanceRate: { type: Type.NUMBER } } 
            },
            scenario: { 
              type: Type.OBJECT, 
              properties: { acceptanceRate: { type: Type.NUMBER } } 
            },
            controls: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  control: { type: Type.STRING },
                  currentValue: { type: Type.NUMBER },
                  targetValue: { type: Type.NUMBER },
                  estimatedDelta: { type: Type.NUMBER }
                }
              }
            },
            explanation: { type: Type.STRING }
          }
        }
      },
      required: ['mode', 'summary', 'recommendation']
    }
  };

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview', 
      contents: prompt,
      config
    });

    const text = response.text;
    if (!text) throw new Error("No response from AI");
    
    return JSON.parse(text);
  } catch (error) {
    console.error("Gemini Analytics Error:", error);
    return null;
  }
};