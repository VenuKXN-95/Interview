"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Eye, EyeOff, Loader2, Zap, Mail, Lock, User } from "lucide-react";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [showPw, setShowPw] = useState(false);

  const pwMismatch = confirmPw.length > 0 && password !== confirmPw;
  const pwTooShort = password.length > 0 && password.length < 8;
  const pwNoUpper = password.length > 0 && !/[A-Z]/.test(password);
  const pwNoDigit = password.length > 0 && !/\d/.test(password);

  const mutation = useMutation({
    mutationFn: () =>
      authService.register({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
      }),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      toast.success("Account created! Welcome to MockIQ 🎉");
      router.push("/");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (pwMismatch || pwTooShort || pwNoUpper || pwNoDigit) return;
    mutation.mutate();
  };

  const isValid =
    fullName.trim().length >= 2 &&
    email.includes("@") &&
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /\d/.test(password) &&
    password === confirmPw;

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10 py-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center mx-auto mb-4 shadow-2xl shadow-violet-500/30">
            <Zap className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold text-white mb-1">Create account</h1>
          <p className="text-white/40 text-sm">Start your AI-powered interview prep</p>
        </div>

        {/* Card */}
        <div className="glass rounded-2xl p-8 border border-white/8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Full Name */}
            <div>
              <label className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2 block">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type="text"
                  id="register-name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Jane Doe"
                  required
                  minLength={2}
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/20 text-sm focus:outline-none focus:border-violet-500/60 focus:bg-white/8 transition-all"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2 block">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type="email"
                  id="register-email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/20 text-sm focus:outline-none focus:border-violet-500/60 focus:bg-white/8 transition-all"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2 block">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type={showPw ? "text" : "password"}
                  id="register-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-12 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/20 text-sm focus:outline-none focus:border-violet-500/60 focus:bg-white/8 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
                >
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {/* Password hints */}
              {password.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {[
                    { ok: password.length >= 8, label: "8+ chars" },
                    { ok: /[A-Z]/.test(password), label: "Uppercase" },
                    { ok: /\d/.test(password), label: "Number" },
                  ].map(({ ok, label }) => (
                    <span
                      key={label}
                      className={`text-xs px-2 py-0.5 rounded-full border ${
                        ok
                          ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                          : "border-white/10 text-white/30 bg-white/3"
                      }`}
                    >
                      {ok ? "✓" : "○"} {label}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2 block">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type={showPw ? "text" : "password"}
                  id="register-confirm-password"
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                  placeholder="••••••••"
                  required
                  className={`w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border text-white placeholder-white/20 text-sm focus:outline-none focus:bg-white/8 transition-all ${
                    pwMismatch
                      ? "border-red-500/50 focus:border-red-500/70"
                      : "border-white/10 focus:border-violet-500/60"
                  }`}
                />
              </div>
              {pwMismatch && (
                <p className="text-xs text-red-400 mt-1.5">Passwords do not match</p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              id="register-submit"
              disabled={mutation.isPending || !isValid}
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg transition-all duration-300 hover:-translate-y-0.5 mt-2"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <p className="text-center text-white/40 text-sm mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-violet-400 hover:text-violet-300 font-semibold transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
