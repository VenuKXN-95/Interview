"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Upload, FileText, Loader2, CheckCircle2, ChevronRight, AlignLeft, Code2, ListChecks, Building2 } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { StepIndicator } from "@/components/layout/StepIndicator";
import { jdService } from "@/services/jdService";
import { useInterviewStore } from "@/store/interviewStore";
import { ParsedJD } from "@/types";
import { MAX_FILE_SIZE_MB } from "@/lib/constants";

export default function JDUploadPage() {
  const router = useRouter();
  const { jdId, setJD } = useInterviewStore();
  const [mode, setMode] = useState<"file" | "text">("file");
  const [file, setFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [parsed, setParsed] = useState<ParsedJD | null>(null);

  const uploadMutation = useMutation({
    mutationFn: (payload: File | string) =>
      typeof payload === "string" ? jdService.submitRaw(payload) : jdService.upload(payload),
    onSuccess: (data) => {
      setJD(data.jd_id, data.parsed_data);
      setParsed(data.parsed_data);
      toast.success("Job description parsed!");
    },
    onError: (err: Error) => toast.error(err.message || "Failed to parse JD"),
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

  const handleTextSubmit = () => {
    if (rawText.trim().length < 20) {
      toast.error("Please enter at least 20 characters");
      return;
    }
    setParsed(null);
    uploadMutation.mutate(rawText.trim());
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] rounded-full bg-blue-600/6 blur-[120px]" />
      </div>

      <main className="relative pt-24 pb-16 max-w-4xl mx-auto px-4 sm:px-6">
        <StepIndicator currentStep={1} />

        <div className="mt-8 animate-fade-in-up">
          <h1 className="text-3xl font-extrabold text-white mb-2">
            Add <span className="gradient-text">Job Description</span>
          </h1>
          <p className="text-white/40 mb-8">Upload a file or paste the JD text — AI extracts requirements</p>

          {/* Mode toggle */}
          <div className="flex gap-2 mb-6 p-1 bg-white/3 rounded-xl w-fit border border-white/8">
            {[
              { key: "file" as const, icon: Upload, label: "Upload File" },
              { key: "text" as const, icon: AlignLeft, label: "Paste Text" },
            ].map(({ key, icon: Icon, label }) => (
              <button
                key={key}
                onClick={() => { setMode(key); setParsed(null); }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  mode === key
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-white/40 hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" /> {label}
              </button>
            ))}
          </div>

          {mode === "file" ? (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
              onClick={() => document.getElementById("jd-input")?.click()}
              className={`cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300 p-12 text-center mb-6 ${
                dragOver ? "border-blue-500 bg-blue-500/10"
                : file && parsed ? "border-emerald-500/50 bg-emerald-500/5"
                : "border-white/10 hover:border-blue-500/50 hover:bg-blue-500/5 bg-white/2"
              }`}
            >
              <input id="jd-input" type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />

              {uploadMutation.isPending ? (
                <div className="flex flex-col items-center gap-3">
                  <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
                  <p className="text-white/60">Parsing with AI...</p>
                </div>
              ) : file && parsed ? (
                <div className="flex flex-col items-center gap-3">
                  <CheckCircle2 className="w-12 h-12 text-emerald-400" />
                  <p className="text-white font-semibold">{file.name}</p>
                  <p className="text-sm text-emerald-400">Parsed successfully</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-2xl bg-blue-500/15 flex items-center justify-center">
                    <FileText className="w-8 h-8 text-blue-400" />
                  </div>
                  <p className="text-white font-semibold text-lg">Drop JD file here</p>
                  <p className="text-white/40 text-sm">or click to browse</p>
                  <div className="flex gap-2">
                    {["PDF", "DOCX", "TXT"].map((e) => (
                      <span key={e} className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white/50 font-medium">{e}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="mb-6">
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Paste the full job description here...&#10;&#10;We are looking for a Senior Python Engineer with 3+ years of experience in FastAPI, MongoDB, and cloud infrastructure. You will be responsible for..."
                className="w-full h-56 bg-white/3 border border-white/10 rounded-2xl p-5 text-white placeholder-white/20 text-sm resize-none focus:outline-none focus:border-blue-500/50 focus:bg-white/5 transition-all"
              />
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-white/30">{rawText.length} characters</span>
                <button
                  onClick={handleTextSubmit}
                  disabled={uploadMutation.isPending || rawText.trim().length < 20}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300"
                >
                  {uploadMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                  Parse JD
                </button>
              </div>
            </div>
          )}

          {/* Parsed preview */}
          {parsed && (
            <div className="space-y-4 animate-fade-in">
              <div className="glass rounded-xl p-5">
                <div className="flex items-center gap-3 mb-1">
                  <Building2 className="w-5 h-5 text-blue-400" />
                  <span className="font-bold text-white text-lg">{parsed.role || "Unknown Role"}</span>
                </div>
                {parsed.company && <p className="text-blue-400 text-sm ml-8">{parsed.company}</p>}
                {parsed.experience_required && <p className="text-white/40 text-xs ml-8 mt-0.5">Experience: {parsed.experience_required}</p>}
              </div>

              {parsed.required_skills.length > 0 && (
                <div className="glass rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Code2 className="w-4 h-4 text-violet-400" />
                    <span className="font-semibold text-white text-sm">Required Skills</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {parsed.required_skills.map((s) => (
                      <span key={s} className="px-2.5 py-1 rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {parsed.responsibilities.length > 0 && (
                <div className="glass rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <ListChecks className="w-4 h-4 text-emerald-400" />
                    <span className="font-semibold text-white text-sm">Key Responsibilities</span>
                  </div>
                  <ul className="space-y-1.5">
                    {parsed.responsibilities.slice(0, 5).map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                        <span className="text-emerald-400 mt-0.5">•</span> {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <button
                onClick={() => router.push("/interview/configure")}
                className="w-full flex items-center justify-center gap-2 py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 shadow-lg transition-all duration-300 hover:-translate-y-0.5"
              >
                Continue to Configure
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
