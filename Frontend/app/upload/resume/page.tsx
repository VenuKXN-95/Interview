"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Upload, FileText, X, CheckCircle2, Loader2, User, Briefcase, Code2, GraduationCap, ChevronRight } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { StepIndicator } from "@/components/layout/StepIndicator";
import { resumeService } from "@/services/resumeService";
import { useInterviewStore } from "@/store/interviewStore";
import { ParsedResume } from "@/types";
import { MAX_FILE_SIZE_MB } from "@/lib/constants";

export default function ResumeUploadPage() {
  const router = useRouter();
  const { setResume } = useInterviewStore();
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [parsed, setParsed] = useState<ParsedResume | null>(null);

  const uploadMutation = useMutation({
    mutationFn: (f: File) => resumeService.upload(f),
    onSuccess: (data) => {
      setResume(data.resume_id, data.parsed_data);
      setParsed(data.parsed_data);
      toast.success("Resume parsed successfully!");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to parse resume");
    },
  });

  const handleFile = useCallback((f: File) => {
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "docx", "txt"].includes(ext || "")) {
      toast.error("Only PDF, DOCX, or TXT files are supported");
      return;
    }
    if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      toast.error(`File must be under ${MAX_FILE_SIZE_MB}MB`);
      return;
    }
    setFile(f);
    setParsed(null);
    uploadMutation.mutate(f);
  }, [uploadMutation]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full bg-violet-600/6 blur-[120px]" />
      </div>

      <main className="relative pt-24 pb-16 max-w-4xl mx-auto px-4 sm:px-6">
        <StepIndicator currentStep={0} />

        <div className="mt-8 animate-fade-in-up">
          <h1 className="text-3xl font-extrabold text-white mb-2">
            Upload Your <span className="gradient-text">Resume</span>
          </h1>
          <p className="text-white/40 mb-8">Our AI will extract your skills, experience, and projects</p>

          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => document.getElementById("resume-input")?.click()}
            className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300 p-12 text-center mb-8 ${
              dragOver
                ? "border-violet-500 bg-violet-500/10"
                : file
                ? "border-emerald-500/50 bg-emerald-500/5"
                : "border-white/10 hover:border-violet-500/50 hover:bg-violet-500/5 bg-white/2"
            }`}
          >
            <input
              id="resume-input"
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />

            {uploadMutation.isPending ? (
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-12 h-12 text-violet-400 animate-spin" />
                <p className="text-white/60 font-medium">Parsing with AI...</p>
                <p className="text-sm text-white/30">Extracting skills, experience & projects</p>
              </div>
            ) : file && parsed ? (
              <div className="flex flex-col items-center gap-3">
                <CheckCircle2 className="w-12 h-12 text-emerald-400" />
                <p className="text-white font-semibold">{file.name}</p>
                <p className="text-sm text-emerald-400">Parsed successfully</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="w-16 h-16 rounded-2xl bg-violet-500/15 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-violet-400" />
                </div>
                <div>
                  <p className="text-white font-semibold text-lg">Drop your resume here</p>
                  <p className="text-white/40 text-sm mt-1">or click to browse</p>
                </div>
                <div className="flex gap-2 mt-2">
                  {["PDF", "DOCX", "TXT"].map((ext) => (
                    <span key={ext} className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white/50 font-medium">
                      {ext}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-white/25 mt-1">Max {MAX_FILE_SIZE_MB}MB</p>
              </div>
            )}
          </div>

          {/* Parsed preview */}
          {parsed && (
            <div className="space-y-4 animate-fade-in">
              {/* Name & contact */}
              <div className="glass rounded-xl p-5">
                <div className="flex items-center gap-3 mb-1">
                  <User className="w-5 h-5 text-violet-400" />
                  <span className="font-semibold text-white">{parsed.name || "Unknown"}</span>
                </div>
                <p className="text-sm text-white/40 ml-8">{parsed.email} {parsed.phone && `· ${parsed.phone}`}</p>
              </div>

              {/* Skills */}
              {parsed.skills.length > 0 && (
                <div className="glass rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Code2 className="w-4 h-4 text-blue-400" />
                    <span className="font-semibold text-white text-sm">Skills ({parsed.skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {parsed.skills.map((s) => (
                      <span key={s} className="px-2.5 py-1 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience */}
              {parsed.experience.length > 0 && (
                <div className="glass rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Briefcase className="w-4 h-4 text-emerald-400" />
                    <span className="font-semibold text-white text-sm">Experience ({parsed.experience.length} roles)</span>
                  </div>
                  <div className="space-y-3">
                    {parsed.experience.map((e, i) => (
                      <div key={i} className="border-l-2 border-emerald-500/30 pl-4">
                        <p className="font-medium text-white text-sm">{e.role}</p>
                        <p className="text-emerald-400 text-xs">{e.company} · {e.duration}</p>
                        {e.description && <p className="text-white/40 text-xs mt-0.5 line-clamp-2">{e.description}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {parsed.education.length > 0 && (
                <div className="glass rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <GraduationCap className="w-4 h-4 text-amber-400" />
                    <span className="font-semibold text-white text-sm">Education</span>
                  </div>
                  {parsed.education.map((e, i) => (
                    <p key={i} className="text-sm text-white/60">{e.degree} · {e.institution} {e.year && `(${e.year})`}</p>
                  ))}
                </div>
              )}

              {/* CTA */}
              <button
                onClick={() => router.push("/upload/jd")}
                className="w-full flex items-center justify-center gap-2 py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-lg transition-all duration-300 hover:-translate-y-0.5"
              >
                Continue to Job Description
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
