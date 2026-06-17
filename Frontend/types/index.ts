// ── Resume Types ─────────────────────────────────────────────
export interface ExperienceItem {
  company: string;
  role: string;
  duration: string;
  description: string;
}

export interface ProjectItem {
  name: string;
  description: string;
  technologies: string[];
}

export interface EducationItem {
  institution: string;
  degree: string;
  year: string;
}

export interface ParsedResume {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  experience: ExperienceItem[];
  projects: ProjectItem[];
  education: EducationItem[];
}

export interface ResumeUploadResponse {
  resume_id: string;
  filename: string;
  file_type: string;
  parsed_data: ParsedResume;
}

export interface ResumeGetResponse extends ResumeUploadResponse {
  created_at: string;
}

// ── JD Types ─────────────────────────────────────────────────
export interface ParsedJD {
  role: string;
  company: string;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  experience_required: string;
}

export interface JDUploadResponse {
  jd_id: string;
  source: "file" | "raw_text";
  filename?: string;
  parsed_data: ParsedJD;
}

// ── Session / Interview Types ─────────────────────────────────
export type InterviewType = "hr" | "technical" | "telephonic" | "virtual";
export type SessionStatus = "created" | "running" | "completed" | "abandoned";
export type Difficulty = "easy" | "medium" | "hard";
export type QuestionSource = "ai_generated" | "bank" | "generic";

export interface InterviewQuestion {
  question_id: string;
  source: QuestionSource;
  question_text: string;
  category: string;
  difficulty: Difficulty;
  order: number;
  rationale?: string;
}

export interface GenerateInterviewRequest {
  resume_id: string;
  jd_id: string;
  interview_type: InterviewType;
  question_count: number;
}

export interface GenerateInterviewResponse {
  session_id: string;
  interview_type: InterviewType;
  question_count: number;
  questions: InterviewQuestion[];
  status: SessionStatus;
  created_at: string;
}

export interface SessionResponse {
  session_id: string;
  resume_id: string;
  jd_id: string;
  interview_type: InterviewType;
  status: SessionStatus;
  question_count: number;
  questions: InterviewQuestion[];
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

// ── Answer / Evaluation Types ─────────────────────────────────
export interface CategoryScores {
  technical_accuracy: number;
  completeness: number;
  relevance: number;
  communication: number;
}

export interface AnswerFeedback {
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
}

export interface EvaluationResult {
  score: number;
  category_scores: CategoryScores;
  strengths: string[];
  weaknesses: string[];
  missing_points: string[];
  summary: string;
  feedback: AnswerFeedback;
}

export interface SubmitAnswerRequest {
  session_id: string;
  question_id: string;
  question_text: string;
  answer_text: string;
  time_taken_seconds: number;
}

export interface SubmitAnswerResponse {
  answer_id: string;
  session_id: string;
  question_id: string;
  evaluation: EvaluationResult;
  submitted_at: string;
}

export interface AnswerListResponse {
  session_id: string;
  answers: SubmitAnswerResponse[];
  total: number;
}

// ── Report Types ──────────────────────────────────────────────
export type Recommendation = "strong_hire" | "hire" | "maybe" | "no_hire";

export interface ScoreBreakdown {
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  project_score: number;
  overall_score: number;
}

export interface SessionFeedback {
  overall_assessment: string;
  key_strengths: string[];
  priority_improvements: string[];
  interview_readiness: "ready" | "almost_ready" | "needs_preparation";
  next_steps: string[];
}

export interface ReportResponse {
  session_id: string;
  candidate_name: string;
  interview_type: string;
  scores: ScoreBreakdown;
  recommendation: Recommendation;
  session_feedback: SessionFeedback;
  total_questions: number;
  answered_questions: number;
  generated_at: string;
}

// ── API Error ─────────────────────────────────────────────────
export interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}
