"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Navbar } from "@/components/layout/Navbar";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { interviewService } from "@/services/interviewService";
import { Brain, FileText, Briefcase, Zap, ArrowRight, Sparkles, TrendingUp, Clock, CheckCircle2, Loader2, AlertCircle, PlayCircle, Award, HelpCircle, Phone, Monitor, Users, Settings } from "lucide-react";

const STEPS = [
  {
    step: 1,
    href: "/upload/resume",
    icon: FileText,
    color: "from-violet-600 to-purple-600",
    glow: "group-hover:shadow-violet-500/30",
    label: "Upload Resume",
    description: "PDF, DOCX, or TXT — parsed instantly by AI",
  },
  {
    step: 2,
    href: "/upload/jd",
    icon: Briefcase,
    color: "from-blue-600 to-cyan-600",
    glow: "group-hover:shadow-blue-500/30",
    label: "Add Job Description",
    description: "Upload a file or paste raw text",
  },
  {
    step: 3,
    href: "/interview/configure",
    icon: Zap,
    color: "from-amber-600 to-orange-600",
    glow: "group-hover:shadow-amber-500/30",
    label: "Configure & Generate",
    description: "Choose type, count — AI crafts your questions",
  },
];

const FEATURES = [
  {
    icon: Brain,
    label: "100% AI Questions",
    desc: "Questions personalized to your resume & the job",
    color: "text-violet-400",
    bg: "bg-violet-500/10",
  },
  {
    icon: TrendingUp,
    label: "Instant Evaluation",
    desc: "LLM scores every answer with detailed feedback",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    icon: Clock,
    label: "4 Interview Types",
    desc: "HR, Technical, Telephonic & Virtual covered",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
  {
    icon: CheckCircle2,
    label: "PDF Reports",
    desc: "Download a complete evaluation report",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
  },
];

export default function DashboardPage() {
  const router = useRouter();

  const { data: history = [], isLoading } = useQuery({
    queryKey: ["interviewHistory"],
    queryFn: () => interviewService.getHistory(),
    retry: 1,
  });

  const getInterviewIcon = (type: string) => {
    switch (type) {
      case "hr":
        return Users;
      case "technical":
        return Settings;
      case "telephonic":
        return Phone;
      case "virtual":
        return Monitor;
      default:
        return HelpCircle;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/15">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Completed
          </span>
        );
      case "running":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/15 animate-pulse">
            <PlayCircle className="w-3.5 h-3.5" />
            Running
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/5 text-white/40 border border-white/10">
            <Clock className="w-3.5 h-3.5" />
            Pending
          </span>
        );
    }
  };

  return (
    <AuthGuard>
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />

      {/* Background glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-violet-600/8 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-blue-600/8 blur-[120px]" />
      </div>

      <main className="relative pt-24 pb-16 max-w-7xl mx-auto px-4 sm:px-6">
        {/* Hero */}
        <div className="text-center mb-16 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            Powered by DeepSeek R1 & Qwen3
          </div>

          <h1 className="text-5xl sm:text-6xl font-extrabold leading-tight mb-5">
            <span className="gradient-text">AI-Powered</span>
            <br />
            Mock Interview Platform
          </h1>

          <p className="text-lg text-white/50 max-w-2xl mx-auto mb-8">
            Upload your resume, paste the job description, and get a fully
            personalized interview with instant expert-level feedback on every answer.
          </p>

          <Link
            href="/upload/resume"
            className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-lg hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
          >
            Start Your Interview
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-16">
          {STEPS.map(({ step, href, icon: Icon, color, glow, label, description }, i) => (
            <Link
              key={step}
              href={href}
              className={`group relative glass rounded-2xl p-6 hover:border-white/12 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${glow} animate-fade-in-up`}
              style={{ animationDelay: `${i * 0.1}s`, opacity: 0 }}
            >
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center shrink-0 shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-white/30 uppercase tracking-widest">Step {step}</span>
                  </div>
                  <h3 className="font-bold text-white text-lg leading-tight mb-1">{label}</h3>
                  <p className="text-sm text-white/40">{description}</p>
                </div>
                <ArrowRight className="w-5 h-5 text-white/20 group-hover:text-white/60 group-hover:translate-x-1 transition-all duration-300 shrink-0 mt-1" />
              </div>
            </Link>
          ))}
        </div>

        {/* Interview History */}
        <div className="mb-16">
          <h2 className="text-xl font-bold text-white mb-6">Your Interview History</h2>
          {isLoading ? (
            <div className="glass rounded-2xl p-12 text-center flex flex-col items-center justify-center border border-white/5">
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin mb-3" />
              <p className="text-white/50 text-sm">Fetching your previous sessions...</p>
            </div>
          ) : history.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center border border-white/5">
              <AlertCircle className="w-10 h-10 text-white/20 mx-auto mb-3" />
              <h3 className="font-bold text-white mb-1">No sessions yet</h3>
              <p className="text-white/40 text-sm mb-4">You haven't generated any mock interview sessions yet.</p>
              <Link
                href="/upload/resume"
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-violet-400 hover:text-violet-300 transition-colors"
              >
                Start your first interview <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {history.map((session: any) => {
                const Icon = getInterviewIcon(session.interview_type);
                return (
                  <div
                    key={session.session_id}
                    className="group relative glass rounded-2xl p-5 border border-white/5 hover:border-white/12 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center shrink-0 border border-white/10 group-hover:bg-violet-600/10 group-hover:border-violet-600/30 transition-all duration-300">
                        <Icon className="w-5 h-5 text-white/60 group-hover:text-violet-400 transition-colors" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="font-bold text-white text-base capitalize">
                            {session.interview_type} Interview
                          </span>
                          {getStatusBadge(session.status)}
                        </div>
                        <p className="text-xs text-white/30 mb-4">
                          Generated on {new Date(session.created_at).toLocaleDateString()} · {session.question_count} questions
                        </p>
                        <div className="flex gap-2">
                          {session.status === "completed" ? (
                            <>
                              <button
                                onClick={() => router.push(`/interview/${session.session_id}/report`)}
                                className="flex-1 text-center py-2 px-4 rounded-lg font-semibold text-xs text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-md transition-all duration-200"
                              >
                                View Report
                              </button>
                              <button
                                onClick={() => router.push(`/interview/${session.session_id}/feedback`)}
                                className="flex-1 text-center py-2 px-4 rounded-lg font-semibold text-xs text-white/70 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 transition-all duration-200"
                              >
                                Question Feedback
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => router.push(`/interview/${session.session_id}`)}
                              className="w-full flex items-center justify-center gap-1.5 py-2 px-4 rounded-lg font-bold text-xs text-white bg-violet-600 hover:bg-violet-500 transition-all duration-200"
                            >
                              <PlayCircle className="w-4 h-4" />
                              {session.status === "running" ? "Resume Interview" : "Start Session"}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Features */}
        <div className="glass rounded-2xl p-8 animate-fade-in-up delay-300" style={{ opacity: 0 }}>
          <h2 className="text-xl font-bold text-white mb-6 text-center">Platform Features</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {FEATURES.map(({ icon: Icon, label, desc, color, bg }) => (
              <div key={label} className="text-center p-4 rounded-xl hover:bg-white/3 transition-colors">
                <div className={`w-12 h-12 rounded-xl ${bg} flex items-center justify-center mx-auto mb-3`}>
                  <Icon className={`w-6 h-6 ${color}`} />
                </div>
                <p className="font-semibold text-white text-sm mb-1">{label}</p>
                <p className="text-xs text-white/40 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
    </AuthGuard>
  );
}
