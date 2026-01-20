import { GoogleGenAI, Type } from '@google/genai';
import { Student, EvaluationScore } from '../types';

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

export const generateAIFeedback = async (
  student: Student,
  scores: EvaluationScore,
  notes: string,
  useThinking: boolean = false
) => {
  if (!apiKey) {
    console.warn("API Key is missing. Returning mock response.");
    return {
      strengths: "구도 밸런스가 뛰어나며 주제부의 대비(Contrast) 활용이 돋보입니다.",
      weaknesses: "배경부의 디테일 묘사가 다소 급하게 마무리되어 공간감이 부족합니다.",
      actionPlan: "다음 주에는 배경 요소의 외곽 정리를 통해 공간의 깊이를 더하는 연습에 집중하세요.",
      comparisonInsight: {
        similarities: "구도의 안정성은 작년 합격생 상위 30%와 유사합니다.",
        differences: "합격작들은 배경 텍스처 활용에서 더 실험적인 시도를 보였습니다.",
        usp: "과감한 원색 사용이 평균적인 합격 포트폴리오보다 더 높은 시각적 임팩트를 줍니다."
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
  `;

  // Select model based on thinking mode
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

  // Add thinking config if enabled
  if (useThinking) {
    config.thinkingConfig = { thinkingBudget: 32768 };
    // Explicitly not setting maxOutputTokens as requested
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
    // Fallback for demo purposes if API fails
    return {
      strengths: "주제부 표현에 노력을 기울였습니다.",
      weaknesses: "연결 문제로 상세 피드백을 생성하지 못했습니다.",
      actionPlan: "담당 강사의 수기 노트를 확인해주세요.",
      comparisonInsight: {
         similarities: "N/A",
         differences: "N/A",
         usp: "N/A"
      }
    };
  }
};