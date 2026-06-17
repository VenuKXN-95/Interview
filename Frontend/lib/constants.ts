export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const INTERVIEW_TYPES = [
  { value: "hr", label: "HR Interview", description: "Behavioral & culture fit questions", icon: "👥" },
  { value: "technical", label: "Technical Interview", description: "Deep technical & system design", icon: "⚙️" },
  { value: "telephonic", label: "Telephonic Screening", description: "Quick screening & resume validation", icon: "📞" },
  { value: "virtual", label: "Virtual Interview", description: "Mixed technical & behavioral", icon: "💻" },
] as const;

export const QUESTION_COUNT_OPTIONS = [5, 7, 10, 12, 15, 20];

export const RECOMMENDATION_CONFIG = {
  strong_hire: { label: "Strong Hire", color: "text-emerald-400", bg: "bg-emerald-500/20", border: "border-emerald-500/30", icon: "⭐" },
  hire: { label: "Hire", color: "text-blue-400", bg: "bg-blue-500/20", border: "border-blue-500/30", icon: "✓" },
  maybe: { label: "Maybe", color: "text-amber-400", bg: "bg-amber-500/20", border: "border-amber-500/30", icon: "~" },
  no_hire: { label: "No Hire", color: "text-red-400", bg: "bg-red-500/20", border: "border-red-500/30", icon: "✗" },
} as const;

export const DIFFICULTY_CONFIG = {
  easy: { label: "Easy", color: "text-emerald-400", bg: "bg-emerald-500/10" },
  medium: { label: "Medium", color: "text-amber-400", bg: "bg-amber-500/10" },
  hard: { label: "Hard", color: "text-red-400", bg: "bg-red-500/10" },
} as const;

export const ACCEPTED_FILE_TYPES = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "text/plain": [".txt"],
};

export const MAX_FILE_SIZE_MB = 10;
export const MAX_ANSWER_LENGTH = 5000;
