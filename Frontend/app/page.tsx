"use client";

import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Brain, FileText, Briefcase, Zap, ArrowRight, Sparkles, TrendingUp, Clock, CheckCircle2 } from "lucide-react";

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
