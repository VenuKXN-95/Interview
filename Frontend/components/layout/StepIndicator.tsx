"use client";

import { Check } from "lucide-react";

interface Step {
  label: string;
  description: string;
}

const STEPS: Step[] = [
  { label: "Resume", description: "Upload & parse" },
  { label: "Job Description", description: "Upload or paste" },
  { label: "Configure", description: "Select type" },
  { label: "Interview", description: "Answer questions" },
  { label: "Report", description: "View results" },
];

interface StepIndicatorProps {
  currentStep: number; // 0-indexed
}

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <div className="w-full py-4">
      <div className="flex items-center justify-center gap-0">
        {STEPS.map((step, i) => {
          const done = i < currentStep;
          const active = i === currentStep;
          return (
            <div key={i} className="flex items-center">
              {/* Circle */}
              <div className="flex flex-col items-center gap-1.5">
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-500 ${
                    done
                      ? "step-done text-white"
                      : active
                      ? "step-active text-white animate-pulse-glow"
                      : "bg-white/5 border border-white/10 text-white/30"
                  }`}
                >
                  {done ? <Check className="w-4 h-4" /> : i + 1}
                </div>
                <div className="text-center">
                  <p className={`text-xs font-semibold ${active ? "text-violet-300" : done ? "text-emerald-400" : "text-white/30"}`}>
                    {step.label}
                  </p>
                  <p className="text-[10px] text-white/20 hidden sm:block">{step.description}</p>
                </div>
              </div>

              {/* Connector */}
              {i < STEPS.length - 1 && (
                <div
                  className={`w-12 sm:w-20 h-[2px] mb-6 mx-1 transition-all duration-500 ${
                    i < currentStep
                      ? "bg-gradient-to-r from-emerald-500 to-violet-500"
                      : "bg-white/5"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
