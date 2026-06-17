"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Zap, Loader2, AlertCircle, ChevronRight, Users, Settings, Phone, Monitor, Minus, Plus } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { StepIndicator } from "@/components/layout/StepIndicator";
import { interviewService } from "@/services/interviewService";
import { useInterviewStore } from "@/store/interviewStore";
import { InterviewType } from "@/types";
import { INTERVIEW_TYPES } from "@/lib/constants";

const TYPE_ICONS = { hr: Users, technical: Settings, telephonic: Phone, virtual: Monitor };

export default function ConfigurePage() {
  const router = useRouter();
  const { resumeId, jdId, interviewType, questionCount, setInterviewConfig, setSession } = useInterviewStore();

  const [selectedType, setSelectedType] = useState<InterviewType>(interviewType || "technical");
  const [count, setCount] = useState(questionCount || 10);

  const generateMutation = useMutation({
    mutationFn: () =>
      interviewService.generate({
        resume_id: resumeId!,
        jd_id: jdId!,
        interview_type: selectedType,
        question_count: count,
      }),
    onSuccess: (data) => {
      setInterviewConfig(selectedType, count);
      setSession(data.session_id, data.questions);
      toast.success(`${count} questions generated!`);
      router.push(`/interview/${data.session_id}`);
    },
    onError: (err: Error) => toast.error(err.message || "Failed to generate interview"),
  });

  const canGenerate = !!resumeId && !!jdId;

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full bg-amber-600/6 blur-[120px]" />
      </div>

      <main className="relative pt-24 pb-16 max-w-3xl mx-auto px-4 sm:px-6">
        <StepIndicator currentStep={2} />

        <div className="mt-8 animate-fade-in-up">
          <h1 className="text-3xl font-extrabold text-white mb-2">
            Configure <span className="gradient-text">Interview</span>
          </h1>
          <p className="text-white/40 mb-8">Choose the interview type and how many questions you want</p>

          {/* Prerequisites check */}
          {!canGenerate && (
            <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 mb-6">
              <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-amber-300 font-medium text-sm">Missing required uploads</p>
                <p className="text-amber-400/60 text-xs mt-0.5">
                  {!resumeId && "Resume not uploaded. "}
                  {!jdId && "Job description not added."}
                </p>
              </div>
            </div>
          )}

          {/* Interview type selection */}
          <div className="mb-8">
            <label className="block text-sm font-semibold text-white/60 uppercase tracking-widest mb-4">Interview Type</label>
            <div className="grid grid-cols-2 gap-3">
              {INTERVIEW_TYPES.map(({ value, label, description, icon }) => {
                const Icon = TYPE_ICONS[value as InterviewType];
                const active = selectedType === value;
                return (
                  <button
                    key={value}
                    onClick={() => setSelectedType(value as InterviewType)}
                    className={`relative text-left p-5 rounded-xl border transition-all duration-200 ${
                      active
                        ? "border-violet-500/60 bg-violet-500/10 shadow-lg shadow-violet-500/10"
                        : "border-white/8 bg-white/2 hover:border-white/15 hover:bg-white/4"
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${active ? "bg-violet-500" : "bg-white/5"}`}>
                        <Icon className={`w-5 h-5 ${active ? "text-white" : "text-white/40"}`} />
                      </div>
                      <div className={`w-4 h-4 rounded-full border-2 ml-auto ${active ? "border-violet-500 bg-violet-500" : "border-white/20"}`} />
                    </div>
                    <p className={`font-semibold text-sm ${active ? "text-white" : "text-white/60"}`}>{label}</p>
                    <p className={`text-xs mt-0.5 ${active ? "text-white/50" : "text-white/25"}`}>{description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Question count */}
          <div className="mb-8">
            <label className="block text-sm font-semibold text-white/60 uppercase tracking-widest mb-4">
              Question Count — <span className="text-violet-300">{count} questions</span>
            </label>
            <div className="glass rounded-xl p-5">
              <div className="flex items-center justify-between gap-4">
                <button
                  onClick={() => setCount(Math.max(5, count - 1))}
                  className="w-10 h-10 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors"
                >
                  <Minus className="w-4 h-4 text-white" />
                </button>

                <div className="flex-1">
                  <input
                    type="range"
                    min={5}
                    max={20}
                    value={count}
                    onChange={(e) => setCount(Number(e.target.value))}
                    className="w-full h-2 appearance-none bg-white/10 rounded-full outline-none cursor-pointer accent-violet-500"
                  />
                  <div className="flex justify-between text-xs text-white/25 mt-1">
                    <span>5</span><span>10</span><span>15</span><span>20</span>
                  </div>
                </div>

                <button
                  onClick={() => setCount(Math.min(20, count + 1))}
                  className="w-10 h-10 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors"
                >
                  <Plus className="w-4 h-4 text-white" />
                </button>
              </div>

              <div className="flex gap-2 mt-4 flex-wrap">
                {[5, 7, 10, 15, 20].map((n) => (
                  <button
                    key={n}
                    onClick={() => setCount(n)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${count === n ? "bg-violet-600 text-white" : "bg-white/5 text-white/40 hover:bg-white/10 hover:text-white"}`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Summary card */}
          <div className="glass rounded-xl p-5 mb-6 border border-violet-500/10">
            <p className="text-xs text-white/40 uppercase tracking-widest font-semibold mb-3">Interview Summary</p>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-violet-300">{count}</p>
                <p className="text-xs text-white/40">Questions</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-300 capitalize">{selectedType}</p>
                <p className="text-xs text-white/40">Type</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-emerald-300">~{Math.round(count * 3)}m</p>
                <p className="text-xs text-white/40">Est. time</p>
              </div>
            </div>
          </div>

          {/* Generate button */}
          <button
            onClick={() => generateMutation.mutate()}
            disabled={!canGenerate || generateMutation.isPending}
            className="w-full flex items-center justify-center gap-3 py-4 rounded-xl font-bold text-white text-lg bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5 disabled:hover:translate-y-0"
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating questions with AI...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Generate Interview
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </button>
          {generateMutation.isPending && (
            <p className="text-center text-xs text-white/30 mt-3">This may take 20-40 seconds as AI personalizes your questions</p>
          )}
        </div>
      </main>
    </div>
  );
}
