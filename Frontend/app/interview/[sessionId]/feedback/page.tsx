"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Navbar } from "@/components/layout/Navbar";
import { answerService } from "@/services/answerService";
import { useInterviewStore } from "@/store/interviewStore";
import { EvaluationResult } from "@/types";
import { ChevronRight, Star, AlertTriangle, Lightbulb, Loader2, MessageSquare, ArrowRight } from "lucide-react";

function ScoreBar({ score }: { score: number }) {
  const pct = (score / 10) * 100;
  const color = score >= 8 ? "#34d399" : score >= 6 ? "#60a5fa" : score >= 4 ? "#fbbf24" : "#f87171";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-sm font-bold w-8 text-right" style={{ color }}>{score.toFixed(1)}</span>
    </div>
  );
}

function EvalCard({ question, answer, evaluation, index }: {
  question: string;
  answer: string;
  evaluation: EvaluationResult;
  index: number;
}) {
  const score = evaluation.score;
  const scoreColor = score >= 8 ? "text-emerald-400" : score >= 6 ? "text-blue-400" : score >= 4 ? "text-amber-400" : "text-red-400";

  return (
    <div className="glass rounded-2xl overflow-hidden animate-fade-in-up" style={{ animationDelay: `${index * 0.05}s`, opacity: 0 }}>
      {/* Header */}
      <div className="flex items-start justify-between p-5 border-b border-white/5">
        <div className="flex-1 mr-4">
          <span className="text-xs text-white/30 uppercase tracking-widest font-semibold">Q{index + 1}</span>
          <p className="text-white font-medium mt-1 leading-relaxed">{question}</p>
        </div>
        <div className={`text-3xl font-extrabold shrink-0 ${scoreColor}`}>
          {score.toFixed(1)}
          <span className="text-sm text-white/30">/10</span>
        </div>
      </div>

      {/* Answer */}
      <div className="p-5 border-b border-white/5">
        <div className="flex items-center gap-2 mb-2">
          <MessageSquare className="w-3.5 h-3.5 text-white/30" />
          <span className="text-xs text-white/30 uppercase tracking-wider font-semibold">Your Answer</span>
        </div>
        <p className="text-sm text-white/50 leading-relaxed line-clamp-4">{answer}</p>
      </div>

      {/* Category scores */}
      <div className="p-5 border-b border-white/5">
        <p className="text-xs text-white/30 uppercase tracking-wider font-semibold mb-3">Score Breakdown</p>
        <div className="space-y-2">
          {Object.entries(evaluation.category_scores).map(([key, val]) => (
            <div key={key} className="grid grid-cols-[1fr,auto] gap-2 items-center">
              <div>
                <p className="text-xs text-white/50 capitalize mb-1">{key.replace(/_/g, " ")}</p>
                <ScoreBar score={val} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-0 divide-y sm:divide-y-0 sm:divide-x divide-white/5">
        {evaluation.strengths.length > 0 && (
          <div className="p-4">
            <div className="flex items-center gap-1.5 mb-2">
              <Star className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Strengths</span>
            </div>
            <ul className="space-y-1">
              {evaluation.strengths.map((s, i) => (
                <li key={i} className="text-xs text-white/50 flex gap-1.5"><span className="text-emerald-400 shrink-0">•</span>{s}</li>
              ))}
            </ul>
          </div>
        )}
        {evaluation.weaknesses.length > 0 && (
          <div className="p-4">
            <div className="flex items-center gap-1.5 mb-2">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Improve</span>
            </div>
            <ul className="space-y-1">
              {evaluation.weaknesses.map((w, i) => (
                <li key={i} className="text-xs text-white/50 flex gap-1.5"><span className="text-amber-400 shrink-0">•</span>{w}</li>
              ))}
            </ul>
          </div>
        )}
        {evaluation.feedback.recommendations.length > 0 && (
          <div className="p-4">
            <div className="flex items-center gap-1.5 mb-2">
              <Lightbulb className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Tips</span>
            </div>
            <ul className="space-y-1">
              {evaluation.feedback.recommendations.slice(0, 3).map((r, i) => (
                <li key={i} className="text-xs text-white/50 flex gap-1.5"><span className="text-blue-400 shrink-0">•</span>{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default function FeedbackPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const { answers, questions } = useInterviewStore();

  // Prefer local store answers, fall back to API
  const { data: apiAnswers, isLoading } = useQuery({
    queryKey: ["answers", sessionId],
    queryFn: () => answerService.getSessionAnswers(sessionId),
    enabled: Object.keys(answers).length === 0,
  });

  const qaList = questions.map((q) => {
    const localAnswer = answers[q.question_id];
    if (localAnswer) return { question: q.question_text, answer: localAnswer.evaluation.summary, evaluation: localAnswer.evaluation };
    const apiAnswer = apiAnswers?.answers.find((a) => a.question_id === q.question_id);
    if (apiAnswer) return { question: q.question_text, answer: apiAnswer.evaluation.summary, evaluation: apiAnswer.evaluation };
    return null;
  }).filter(Boolean) as { question: string; answer: string; evaluation: EvaluationResult }[];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-violet-400 animate-spin mx-auto mb-4" />
          <p className="text-white/60">Loading feedback...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] rounded-full bg-emerald-600/5 blur-[100px]" />
      </div>

      <main className="relative pt-24 pb-16 max-w-4xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-white">
              Question <span className="gradient-text">Feedback</span>
            </h1>
            <p className="text-white/40 mt-1">{qaList.length} answers evaluated</p>
          </div>
          <button
            onClick={() => router.push(`/interview/${sessionId}/report`)}
            className="flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-lg transition-all duration-300"
          >
            View Report
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-5">
          {qaList.map((item, i) => (
            <EvalCard key={i} question={item.question} answer={item.answer} evaluation={item.evaluation} index={i} />
          ))}
        </div>

        <div className="mt-8 flex justify-center">
          <button
            onClick={() => router.push(`/interview/${sessionId}/report`)}
            className="flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-white text-lg bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-xl transition-all duration-300 hover:-translate-y-0.5"
          >
            View Final Report & Download PDF
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </main>
    </div>
  );
}
