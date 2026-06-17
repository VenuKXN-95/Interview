"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Send, ChevronRight, Loader2, Clock, CheckCircle2, AlertCircle, Star, TrendingUp, X, Zap, Brain } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { interviewService } from "@/services/interviewService";
import { answerService } from "@/services/answerService";
import { useInterviewStore } from "@/store/interviewStore";
import { EvaluationResult, InterviewQuestion } from "@/types";
import { DIFFICULTY_CONFIG } from "@/lib/constants";

export default function InterviewSessionPage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;

  const { questions, currentQuestionIndex, answers, recordAnswer, nextQuestion } = useInterviewStore();

  const [started, setStarted] = useState(false);
  const [answerText, setAnswerText] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const [lastEval, setLastEval] = useState<EvaluationResult | null>(null);
  const [showEval, setShowEval] = useState(false);

  // Evaluation wait timer (shown during LLM call)
  const [evalWait, setEvalWait] = useState(0);
  const evalWaitRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Guard against double-submits at ref level (faster than state)
  const isSubmittingRef = useRef(false);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentQ: InterviewQuestion | undefined = questions[currentQuestionIndex];
  const totalAnswered = Object.keys(answers).length;
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const alreadyAnswered = currentQ ? !!answers[currentQ.question_id] : false;

  // Answer timer (counts up while answering)
  useEffect(() => {
    if (started && !showEval && !isSubmittingRef.current) {
      timerRef.current = setInterval(() => setElapsed((p) => p + 1), 1000);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [started, showEval]);

  const startMutation = useMutation({
    mutationFn: () => interviewService.startSession(sessionId),
    onSuccess: () => { setStarted(true); toast.success("Interview started! Good luck!"); },
    onError: (err: Error) => toast.error(err.message),
  });

  const submitMutation = useMutation({
    mutationFn: () =>
      answerService.submit({
        session_id: sessionId,
        question_id: currentQ!.question_id,
        question_text: currentQ!.question_text,
        answer_text: answerText.trim(),
        time_taken_seconds: elapsed,
      }),
    onSuccess: (data) => {
      isSubmittingRef.current = false;
      if (evalWaitRef.current) clearInterval(evalWaitRef.current);
      setEvalWait(0);
      recordAnswer(currentQ!.question_id, data);
      setLastEval(data.evaluation);
      setShowEval(true);
      if (timerRef.current) clearInterval(timerRef.current);
    },
    onError: (err: Error) => {
      isSubmittingRef.current = false;
      if (evalWaitRef.current) clearInterval(evalWaitRef.current);
      setEvalWait(0);
      toast.error(err.message || "Failed to submit answer");
    },
  });

  const endMutation = useMutation({
    mutationFn: () => interviewService.endSession(sessionId),
    onSuccess: () => {
      toast.success("Interview completed!");
      router.push(`/interview/${sessionId}/feedback`);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const handleSubmit = () => {
    // Ref-level guard prevents any double-click regardless of React render cycle
    if (isSubmittingRef.current) return;
    if (!answerText.trim() || answerText.length > 5000 || alreadyAnswered) return;

    isSubmittingRef.current = true;
    setEvalWait(0);

    // Stop answer timer
    if (timerRef.current) clearInterval(timerRef.current);

    // Start evaluation wait timer
    evalWaitRef.current = setInterval(() => setEvalWait((p) => p + 1), 1000);

    submitMutation.mutate();
  };

  const handleNext = () => {
    if (isLastQuestion) {
      endMutation.mutate();
    } else {
      nextQuestion();
      setAnswerText("");
      setElapsed(0);
      setShowEval(false);
      setLastEval(null);
      isSubmittingRef.current = false;
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  };

  const formatTime = (s: number) =>
    `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;
  const scoreColor = (s: number) =>
    s >= 8 ? "text-emerald-400" : s >= 6 ? "text-blue-400" : s >= 4 ? "text-amber-400" : "text-red-400";

  if (!questions.length) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-amber-400 mx-auto mb-4" />
          <p className="text-white font-semibold mb-2">No questions loaded</p>
          <button onClick={() => router.push("/interview/configure")} className="text-violet-400 hover:text-violet-300 text-sm">
            ← Generate an interview first
          </button>
        </div>
      </div>
    );
  }

  // Pre-start screen
  if (!started) {
    return (
      <div className="min-h-screen bg-[#0a0a0f]">
        <Navbar />
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="max-w-lg w-full text-center animate-fade-in-up">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-violet-500/30">
              <Zap className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold text-white mb-3">Ready to Begin?</h1>
            <p className="text-white/50 mb-4">
              You have <span className="text-violet-300 font-semibold">{questions.length} questions</span> waiting.
              Take your time — quality matters more than speed.
            </p>
            {/* Upfront LLM latency warning */}
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-500/8 border border-amber-500/15 mb-8 text-left">
              <Clock className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-300/80 leading-relaxed">
                <span className="font-semibold">Note:</span> Each answer is evaluated by an AI model — this takes
                <span className="font-semibold text-amber-300"> 5–30 seconds</span>. Please wait for the result before clicking again.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 mb-8">
              {[
                { label: "Questions", value: questions.length, color: "text-violet-300" },
                { label: "Time limit", value: "None", color: "text-blue-300" },
                { label: "Feedback", value: "Per answer", color: "text-emerald-300" },
              ].map(({ label, value, color }) => (
                <div key={label} className="glass rounded-xl p-4">
                  <p className={`text-xl font-bold ${color}`}>{value}</p>
                  <p className="text-xs text-white/40 mt-0.5">{label}</p>
                </div>
              ))}
            </div>
            <button
              onClick={() => startMutation.mutate()}
              disabled={startMutation.isPending}
              className="w-full flex items-center justify-center gap-2 py-4 rounded-xl font-bold text-white text-lg bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-xl transition-all duration-300 hover:-translate-y-0.5"
            >
              {startMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
              Start Interview
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />

      {/* ── LLM Evaluation Overlay ──────────────────────────── */}
      {submitMutation.isPending && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0a0a0f]/90 backdrop-blur-sm">
          <div className="glass rounded-2xl p-10 text-center max-w-sm mx-4 border border-violet-500/20 shadow-2xl">
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 rounded-full border-4 border-violet-500/20" />
              <div className="absolute inset-0 rounded-full border-4 border-t-violet-500 animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Brain className="w-8 h-8 text-violet-400" />
              </div>
            </div>
            <h3 className="text-white font-bold text-lg mb-2">AI Evaluating Your Answer</h3>
            <p className="text-white/50 text-sm mb-4 leading-relaxed">
              The AI model is analysing your response for accuracy, completeness, and clarity.
            </p>
            <div className="flex items-center justify-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20">
              <Clock className="w-4 h-4 text-violet-400" />
              <span className="font-mono text-violet-300 font-semibold">{formatTime(evalWait)}</span>
              <span className="text-white/30 text-sm">elapsed</span>
            </div>
            <p className="text-xs text-white/25 mt-3">Do not close or refresh this page</p>
          </div>
        </div>
      )}

      {/* Progress bar */}
      <div className="fixed top-16 left-0 right-0 h-1 bg-white/5 z-40">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-blue-500 transition-all duration-700"
          style={{ width: `${(totalAnswered / questions.length) * 100}%` }}
        />
      </div>

      <main className="relative pt-20 pb-16 max-w-3xl mx-auto px-4 sm:px-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-6 mt-4">
          <div>
            <p className="text-white/40 text-sm">Question {currentQuestionIndex + 1} of {questions.length}</p>
            <p className="text-white font-semibold capitalize">{currentQ?.category}</p>
          </div>
          <div className="flex items-center gap-4">
            {/* Answer timer */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <Clock className="w-3.5 h-3.5 text-white/40" />
              <span className="text-sm font-mono text-white/60">{formatTime(elapsed)}</span>
            </div>
            {/* Difficulty */}
            {currentQ && (
              <span className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${DIFFICULTY_CONFIG[currentQ.difficulty].bg} ${DIFFICULTY_CONFIG[currentQ.difficulty].color}`}>
                {DIFFICULTY_CONFIG[currentQ.difficulty].label}
              </span>
            )}
          </div>
        </div>

        {/* Question card */}
        {currentQ && (
          <div className="gradient-border rounded-2xl p-6 mb-6 animate-fade-in">
            <p className="text-lg font-medium text-white leading-relaxed">{currentQ.question_text}</p>
          </div>
        )}

        {/* Eval result */}
        {showEval && lastEval ? (
          <div className="space-y-4 animate-fade-in">
            <div className="glass rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`text-4xl font-extrabold ${scoreColor(lastEval.score)}`}>
                    {lastEval.score.toFixed(1)}
                    <span className="text-lg text-white/30">/10</span>
                  </div>
                  <div>
                    <p className="text-white font-semibold">Your Score</p>
                    <p className="text-xs text-white/40">{lastEval.summary}</p>
                  </div>
                </div>
                <button onClick={() => setShowEval(false)} className="text-white/20 hover:text-white/60 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-2">
                {Object.entries(lastEval.category_scores).map(([key, val]) => (
                  <div key={key} className="flex items-center gap-3">
                    <span className="text-xs text-white/40 w-36 shrink-0 capitalize">{key.replace(/_/g, " ")}</span>
                    <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-violet-500 to-blue-500 rounded-full transition-all duration-700"
                        style={{ width: `${(val / 10) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-semibold text-white/60 w-8 text-right">{val.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {lastEval.strengths.length > 0 && (
                <div className="glass rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Star className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Strengths</span>
                  </div>
                  <ul className="space-y-1">
                    {lastEval.strengths.slice(0, 3).map((s, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-xs text-white/60">
                        <span className="text-emerald-400">•</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {lastEval.weaknesses.length > 0 && (
                <div className="glass rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-4 h-4 text-amber-400" />
                    <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Improve</span>
                  </div>
                  <ul className="space-y-1">
                    {lastEval.weaknesses.slice(0, 3).map((w, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-xs text-white/60">
                        <span className="text-amber-400">•</span>{w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <button
              onClick={handleNext}
              disabled={endMutation.isPending}
              className="w-full flex items-center justify-center gap-2 py-4 rounded-xl font-bold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-lg transition-all duration-300"
            >
              {endMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
              {isLastQuestion ? "Finish Interview & View Report" : "Next Question"}
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        ) : (
          /* Answer input */
          <div className="space-y-4">
            <textarea
              ref={textareaRef}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              placeholder="Type your answer here... Be specific and concise. Reference your actual experience where relevant."
              disabled={alreadyAnswered || submitMutation.isPending}
              className="w-full h-48 bg-white/3 border border-white/10 rounded-2xl p-5 text-white placeholder-white/20 text-sm resize-none focus:outline-none focus:border-violet-500/50 focus:bg-white/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <div className="flex items-center justify-between">
              <span className={`text-xs ${answerText.length > 4500 ? "text-red-400" : "text-white/30"}`}>
                {answerText.length}/5000
              </span>
              <button
                onClick={handleSubmit}
                disabled={!answerText.trim() || answerText.length > 5000 || submitMutation.isPending || alreadyAnswered}
                className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg transition-all duration-300"
              >
                <Send className="w-4 h-4" />
                Submit Answer
              </button>
            </div>

            {/* Already answered */}
            {alreadyAnswered && !showEval && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-300 text-sm">Already submitted. Click next to continue.</span>
                <button onClick={handleNext} className="ml-auto flex items-center gap-1 text-sm text-emerald-400 font-semibold hover:text-emerald-300">
                  {isLastQuestion ? "Finish" : "Next"} <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* Question progress pills */}
        <div className="flex gap-2 flex-wrap mt-8">
          {questions.map((q, i) => {
            const answered = !!answers[q.question_id];
            const current = i === currentQuestionIndex;
            return (
              <div
                key={q.question_id}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  current
                    ? "bg-violet-600 text-white scale-110"
                    : answered
                    ? "bg-emerald-600/50 text-emerald-300"
                    : "bg-white/5 text-white/30"
                }`}
              >
                {answered && !current ? "✓" : i + 1}
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
