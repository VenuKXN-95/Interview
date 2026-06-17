import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  ParsedResume,
  ParsedJD,
  InterviewType,
  InterviewQuestion,
  SubmitAnswerResponse,
} from "@/types";

interface InterviewStore {
  // Step 1 — Resume
  resumeId: string | null;
  resumeData: ParsedResume | null;

  // Step 2 — JD
  jdId: string | null;
  jdData: ParsedJD | null;

  // Step 3 — Config
  interviewType: InterviewType | null;
  questionCount: number;

  // Step 4+ — Session
  sessionId: string | null;
  questions: InterviewQuestion[];
  currentQuestionIndex: number;

  // Answers keyed by question_id
  answers: Record<string, SubmitAnswerResponse>;

  // Actions
  setResume: (id: string, data: ParsedResume) => void;
  setJD: (id: string, data: ParsedJD) => void;
  setInterviewConfig: (type: InterviewType, count: number) => void;
  setSession: (id: string, questions: InterviewQuestion[]) => void;
  recordAnswer: (questionId: string, response: SubmitAnswerResponse) => void;
  nextQuestion: () => void;
  reset: () => void;
}

const initialState = {
  resumeId: null,
  resumeData: null,
  jdId: null,
  jdData: null,
  interviewType: null,
  questionCount: 10,
  sessionId: null,
  questions: [],
  currentQuestionIndex: 0,
  answers: {},
};

export const useInterviewStore = create<InterviewStore>()(
  persist(
    (set) => ({
      ...initialState,

      setResume: (id, data) => set({ resumeId: id, resumeData: data }),

      setJD: (id, data) => set({ jdId: id, jdData: data }),

      setInterviewConfig: (type, count) =>
        set({ interviewType: type, questionCount: count }),

      setSession: (id, questions) =>
        set({ sessionId: id, questions, currentQuestionIndex: 0, answers: {} }),

      recordAnswer: (questionId, response) =>
        set((state) => ({
          answers: { ...state.answers, [questionId]: response },
        })),

      nextQuestion: () =>
        set((state) => ({
          currentQuestionIndex: Math.min(
            state.currentQuestionIndex + 1,
            state.questions.length - 1
          ),
        })),

      reset: () => set(initialState),
    }),
    {
      name: "mock-interview-store",
      partialize: (state) => ({
        resumeId: state.resumeId,
        jdId: state.jdId,
        interviewType: state.interviewType,
        questionCount: state.questionCount,
        sessionId: state.sessionId,
      }),
    }
  )
);
