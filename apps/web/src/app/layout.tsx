import type { Metadata } from "next";
import "./globals.css";
import { AppNav } from "@/components/layout/AppNav";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { AuthProvider } from "@/components/auth/AuthProvider";

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME || "Intel Hub",
  description: "全球情报资讯搜集中台",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        <ThemeProvider>
          <AuthProvider>
            <AppNav />
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
