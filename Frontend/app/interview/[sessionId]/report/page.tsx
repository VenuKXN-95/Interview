"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Navbar } from "@/components/layout/Navbar";
import { reportService } from "@/services/reportService";
import { Recommendation, ScoreBreakdown } from "@/types";
import { RECOMMENDATION_CONFIG } from "@/lib/constants";
import { Download, Loader2, AlertCircle, Star, TrendingUp, Lightbulb, Target, RotateCcw, CheckCircle2 } from "lucide-react";

function ScoreRing({ score, label }: { score: number; label: string }) {
  const pct = (score / 10) * 100;
  const r = 36;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const color = score >= 8 ? "#34d399" : score >= 6 ? "#60a5fa" : score >= 4 ? "#fbbf24" : "#f87171";
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-20 h-20">
        <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
          <circle
            cx="40" cy="40" r={r} fill="none"
            stroke={color} strokeWidth="8"
            strokeDasharray={`${dash} ${circ}`}
            strokeLinecap="round"
            style={{ transition: "stroke-dasharray 1s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-extrabold" style={{ color }}>{score.toFixed(1)}</span>
        </div>
      </div>
      <span className="text-xs text-white/50 text-center leading-tight">{label}</span>
    </div>
  );
}

function ScoreDimensionBar({ label, value }: { label: string; value: number }) {
  const color = value >= 8 ? "#34d399" : value >= 6 ? "#60a5fa" : value >= 4 ? "#fbbf24" : "#f87171";
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm text-white/60">{label}</span>
        <span className="text-sm font-bold" style={{ color }}>{value.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${(value / 10) * 100}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const { data: report, isLoading, error } = useQuery({
    queryKey: ["report", sessionId],
    queryFn: () => reportService.getJson(sessionId),
    retry: 1,
  });

  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    if (downloading) return;
    setDownloading(true);
    const toastId = toast.loading("Generating and downloading PDF report...");
    try {
      const blob = await reportService.downloadPdf(sessionId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `interview_report_${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("PDF downloaded successfully!", { id: toastId });
    } catch (err: any) {
      toast.error(err.message || "Failed to download PDF report", { id: toastId });
    } finally {
      setDownloading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-violet-400 animate-spin mx-auto mb-4" />
          <p className="text-white font-semibold mb-1">Generating your report...</p>
          <p className="text-white/40 text-sm">Calculating scores and preparing feedback</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-white font-semibold mb-2">Report not available yet</p>
          <p className="text-white/40 text-sm mb-6">Complete your interview session first, or the evaluation may still be processing.</p>
          <button onClick={() => router.push(`/interview/${sessionId}/feedback`)} className="text-violet-400 hover:text-violet-300 text-sm">← View question feedback</button>
        </div>
      </div>
    );
  }

  const rec = RECOMMENDATION_CONFIG[report.recommendation as Recommendation];
  const scores: ScoreBreakdown = report.scores;

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px]" />
      </div>

      <main className="relative pt-24 pb-20 max-w-4xl mx-auto px-4 sm:px-6">

        {/* Header */}
        <div className="flex items-start justify-between mb-8 animate-fade-in-up">
          <div>
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-1">Interview Report</p>
            <h1 className="text-3xl font-extrabold text-white">
              {report.candidate_name || "Your"} <span className="gradient-text">Results</span>
            </h1>
            <p className="text-white/40 mt-1 capitalize">{report.interview_type} Interview · {report.answered_questions}/{report.total_questions} answered</p>
          </div>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-lg transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            {downloading ? "Downloading..." : "Download PDF"}
          </button>
        </div>

        {/* Overall + Recommendation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          {/* Overall score */}
          <div className="glass rounded-2xl p-6 flex items-center gap-6 animate-fade-in-up delay-100" style={{ opacity: 0 }}>
            <div className="relative">
              <div className="w-28 h-28">
                <svg className="w-28 h-28 -rotate-90" viewBox="0 0 112 112">
                  <circle cx="56" cy="56" r="48" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                  <circle
                    cx="56" cy="56" r="48" fill="none"
                    stroke="url(#grad)" strokeWidth="10"
                    strokeDasharray={`${(scores.overall_score / 10) * (2 * Math.PI * 48)} ${2 * Math.PI * 48}`}
                    strokeLinecap="round"
                    style={{ transition: "stroke-dasharray 1.5s ease" }}
                  />
                  <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#7c3aed" />
                      <stop offset="100%" stopColor="#60a5fa" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-extrabold text-white">{scores.overall_score.toFixed(1)}</span>
                  <span className="text-xs text-white/40">/10</span>
                </div>
              </div>
            </div>
            <div>
              <p className="text-sm text-white/40 uppercase tracking-widest font-semibold mb-1">Overall Score</p>
              <p className="text-2xl font-extrabold gradient-text">{scores.overall_score.toFixed(1)} / 10</p>
              <p className="text-xs text-white/30 mt-2">Technical 35% · Communication 25% · Problem Solving 25% · Projects 15%</p>
            </div>
          </div>

          {/* Recommendation */}
          <div className={`glass rounded-2xl p-6 border ${rec.border} animate-fade-in-up delay-200`} style={{ opacity: 0 }}>
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-3">Hiring Recommendation</p>
            <div className={`inline-flex items-center gap-3 px-5 py-3 rounded-xl ${rec.bg} border ${rec.border} mb-4`}>
              <span className="text-2xl">{rec.icon}</span>
              <span className={`text-xl font-extrabold ${rec.color}`}>{rec.label}</span>
            </div>
            {report.session_feedback?.overall_assessment && (
              <p className="text-sm text-white/50 leading-relaxed">{report.session_feedback.overall_assessment}</p>
            )}
          </div>
        </div>

        {/* Score breakdown */}
        <div className="glass rounded-2xl p-6 mb-6 animate-fade-in-up delay-200" style={{ opacity: 0 }}>
          <div className="flex items-center gap-2 mb-6">
            <Target className="w-5 h-5 text-violet-400" />
            <h2 className="font-bold text-white">Score Breakdown</h2>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mb-8 justify-items-center">
            <ScoreRing score={scores.technical_score} label="Technical" />
            <ScoreRing score={scores.communication_score} label="Communication" />
            <ScoreRing score={scores.problem_solving_score} label="Problem Solving" />
            <ScoreRing score={scores.project_score} label="Projects" />
          </div>

          <div className="space-y-3">
            <ScoreDimensionBar label="Technical Accuracy" value={scores.technical_score} />
            <ScoreDimensionBar label="Communication" value={scores.communication_score} />
            <ScoreDimensionBar label="Problem Solving" value={scores.problem_solving_score} />
            <ScoreDimensionBar label="Project Experience" value={scores.project_score} />
          </div>
        </div>

        {/* Session feedback */}
        {report.session_feedback && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
            {report.session_feedback.key_strengths?.length > 0 && (
              <div className="glass rounded-xl p-5 animate-fade-in-up delay-300" style={{ opacity: 0 }}>
                <div className="flex items-center gap-2 mb-3">
                  <Star className="w-4 h-4 text-emerald-400" />
                  <h3 className="font-semibold text-emerald-400 text-sm">Key Strengths</h3>
                </div>
                <ul className="space-y-1.5">
                  {report.session_feedback.key_strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-white/60">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" /> {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {report.session_feedback.priority_improvements?.length > 0 && (
              <div className="glass rounded-xl p-5 animate-fade-in-up delay-300" style={{ opacity: 0 }}>
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-amber-400" />
                  <h3 className="font-semibold text-amber-400 text-sm">Areas to Improve</h3>
                </div>
                <ul className="space-y-1.5">
                  {report.session_feedback.priority_improvements.map((p, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-white/60">
                      <span className="text-amber-400 shrink-0">•</span> {p}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {report.session_feedback.next_steps?.length > 0 && (
              <div className="glass rounded-xl p-5 animate-fade-in-up delay-300" style={{ opacity: 0 }}>
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-blue-400" />
                  <h3 className="font-semibold text-blue-400 text-sm">Next Steps</h3>
                </div>
                <ul className="space-y-1.5">
                  {report.session_feedback.next_steps.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-white/60">
                      <span className="text-blue-400 shrink-0">{i + 1}.</span> {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4 flex-wrap animate-fade-in-up delay-400" style={{ opacity: 0 }}>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl font-bold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-xl transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {downloading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
            {downloading ? "Downloading Report..." : "Download PDF Report"}
          </button>
          <button
            onClick={() => { router.push("/"); }}
            className="flex items-center justify-center gap-2 px-6 py-4 rounded-xl font-semibold text-white/60 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 transition-all duration-200"
          >
            <RotateCcw className="w-4 h-4" />
            New Interview
          </button>
        </div>
      </main>
    </div>
  );
}
