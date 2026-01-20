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
      strengths: "Excellent composition balance and strong use of contrast in the focal point.",
      weaknesses: "Detail rendering in the background is slightly rushed, affecting overall depth.",
      actionPlan: "Focus on refining the edges of the background elements next week to improve spatial depth."
    };
  }

  const prompt = `
    You are an expert art academy director providing feedback to a student.
    
    Student: ${student.name} (${student.grade}, Target: ${student.targetUniversity}, Major: ${student.major})
    
    Evaluation Scores (0-10):
    - Composition: ${scores.composition}
    - Tone/Contrast: ${scores.tone}
    - Idea/Concept: ${scores.idea}
    - Completeness/Attitude: ${scores.completeness}
    
    Instructor Notes: "${notes}"
    
    Based on the scores and notes, generate a structured feedback report.
    The tone should be professional, direct yet encouraging (Director style).
  `;

  // Select model based on thinking mode
  const model = useThinking ? 'gemini-3-pro-preview' : 'gemini-3-flash-preview';

  const config: any = {
    responseMimeType: 'application/json',
    responseSchema: {
      type: Type.OBJECT,
      properties: {
        strengths: { type: Type.STRING, description: "What the student did well" },
        weaknesses: { type: Type.STRING, description: "Core issues to address" },
        actionPlan: { type: Type.STRING, description: "Specific actionable advice for next week" }
      },
      required: ['strengths', 'weaknesses', 'actionPlan']
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
      strengths: "Good effort on the main subject.",
      weaknesses: "Failed to generate detailed feedback due to connection issues.",
      actionPlan: "Please review the instructor's manual notes."
    };
  }
};