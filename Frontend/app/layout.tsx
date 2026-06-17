import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "MockIQ — AI-Powered Mock Interview Platform",
  description:
    "Practice interviews with AI. Upload your resume, paste a job description, and get personalized questions with instant expert feedback.",
  keywords: ["mock interview", "AI interview", "interview practice", "job preparation"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-[#0a0a0f] text-white min-h-screen`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
