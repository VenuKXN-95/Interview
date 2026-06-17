"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Brain, LayoutDashboard, FileText, Briefcase, Zap, LogOut, ChevronDown } from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { toast } from "sonner";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/upload/resume", icon: FileText, label: "Resume" },
  { href: "/upload/jd", icon: Briefcase, label: "Job Description" },
  { href: "/interview/configure", icon: Zap, label: "Interview" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, clearAuth } = useAuthStore();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    clearAuth();
    toast.success("Signed out successfully");
    router.push("/login");
  };

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "??";

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-blue-500 flex items-center justify-center shadow-lg group-hover:shadow-violet-500/30 transition-all duration-300">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">
            Mock<span className="text-violet-400">IQ</span>
          </span>
        </Link>

        {/* Nav links — only shown when authenticated */}
        {isAuthenticated && (
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(({ href, icon: Icon, label }) => {
              const active = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? "bg-violet-500/15 text-violet-300 border border-violet-500/20"
                      : "text-white/50 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              );
            })}
          </nav>
        )}

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* API status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-emerald-400 font-medium">API Live</span>
          </div>

          {/* User menu */}
          {isAuthenticated && user ? (
            <div className="relative">
              <button
                onClick={() => setDropdownOpen((o) => !o)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/8 transition-all"
              >
                {/* Avatar */}
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-600 to-blue-500 flex items-center justify-center text-xs font-bold text-white">
                  {initials}
                </div>
                <span className="text-sm text-white/70 font-medium hidden sm:block max-w-[120px] truncate">
                  {user.full_name}
                </span>
                <ChevronDown className={`w-3.5 h-3.5 text-white/40 transition-transform ${dropdownOpen ? "rotate-180" : ""}`} />
              </button>

              {/* Dropdown */}
              {dropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-52 glass rounded-xl border border-white/10 shadow-2xl overflow-hidden z-50">
                  <div className="px-4 py-3 border-b border-white/5">
                    <p className="text-xs text-white/40">Signed in as</p>
                    <p className="text-sm text-white font-medium truncate">{user.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              href="/login"
              className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 transition-all"
            >
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
