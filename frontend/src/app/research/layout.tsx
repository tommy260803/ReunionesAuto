"use client";

import { ReactNode } from "react";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, FlaskConical, MessageSquare, FileText, Award, FileDown, LayoutDashboard, ArrowLeft } from "lucide-react";

const navItems = [
  { href: "/research", label: "Dashboard", icon: LayoutDashboard },
  { href: "/research/analyses", label: "Análisis", icon: BarChart3 },
  { href: "/research/experiments", label: "Experimentos", icon: FlaskConical },
  { href: "/research/evaluations", label: "Evaluaciones", icon: MessageSquare },
  { href: "/research/prompts", label: "Prompts", icon: FileText },
  { href: "/research/gold-standard", label: "Gold Standard", icon: Award },
  { href: "/research/reports", label: "Reportes", icon: FileDown },
];

export default function ResearchLayout({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-1">
              <Link href="/dashboard" className="flex items-center gap-1 text-gray-400 hover:text-gray-600 transition-colors mr-4" title="Volver al Dashboard Principal">
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <div className="h-6 w-px bg-gray-200 mr-2" />
              {navItems.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/research" && pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-indigo-50 text-indigo-700"
                        : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </Link>
                );
              })}
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500 hidden md:block">{user?.nombre}</span>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
