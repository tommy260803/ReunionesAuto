"use client";

import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Activity, Bot, CheckSquare, FileText, LayoutDashboard, LogOut, Menu, PanelLeftClose, PanelLeftOpen, Radio, UserCircle, Users, Video, X } from "lucide-react";
import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useLanguage } from "@/context/LanguageContext";
import { cn } from "@/lib/utils";

const labels: Record<string, string> = {
  "/dashboard": "shell.controlPanel",
  "/chat": "shell.aiAssistant",
  "/meetings": "shell.meetings",
  "/participants": "shell.participants",
  "/tasks": "shell.tasks",
  "/summaries": "shell.summariesAi",
  "/users": "shell.users",
  "/metrics": "shell.metrics",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const { t } = useLanguage();
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => { setIsMobileMenuOpen(false); }, [pathname]);

  if (loading) return <div className="min-h-screen bg-background p-6"><div className="mx-auto mt-32 h-48 max-w-lg rounded-xl skeleton" aria-label={t("common.loadingApp")} /></div>;
  if (!user) return null;

  const navItems = [
    { name: t("shell.dashboard"), href: "/dashboard", icon: LayoutDashboard },
    { name: t("shell.aiAssistant"), href: "/chat", icon: Bot },
    { name: t("shell.meetings"), href: "/meetings", icon: Video },
    { name: t("shell.participants"), href: "/participants", icon: Users },
    { name: t("shell.tasks"), href: "/tasks", icon: CheckSquare },
    { name: t("shell.summaries"), href: "/summaries", icon: FileText },
  ];
  if (user.is_admin) {
    navItems.push({ name: t("shell.users"), href: "/users", icon: Users });
    navItems.push({ name: t("shell.metrics"), href: "/metrics", icon: Activity });
  }
  const pageLabel = labels[pathname] ? t(labels[pathname]) : "Zoom2";

  return <div className="min-h-screen bg-background text-foreground md:flex">
    <div className="md:hidden sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-card/95 px-4 backdrop-blur">
      <div><p className="text-sm font-semibold tracking-tight">Zoom</p><p className="text-xs app-muted">{pageLabel}</p></div>
      <div className="flex items-center gap-2"><LanguageToggle /><ThemeToggle /><button onClick={() => setIsMobileMenuOpen(true)} aria-label={t("common.openNav")} aria-expanded={isMobileMenuOpen} className="grid h-10 w-10 place-items-center rounded-lg border border-border bg-card"><Menu className="h-5 w-5" /></button></div>
    </div>

    <aside className={cn(
      "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-[var(--sidebar-border)] bg-[var(--sidebar)] text-[var(--sidebar-foreground)] transition-[width,transform] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] md:sticky md:translate-x-0",
      isCollapsed ? "w-20" : "w-72",
      isMobileMenuOpen ? "translate-x-0 w-72" : "-translate-x-full",
    )}>
      <div className="flex h-20 items-center border-b border-[var(--sidebar-border)] px-4">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-500 text-sm font-bold text-white shadow-lg shadow-brand-500/20">Z</div>
        <div className={cn("ml-3 min-w-0 transition-all duration-200", isCollapsed && "md:pointer-events-none md:w-0 md:opacity-0")}><p className="truncate text-base font-semibold tracking-tight text-white">Zoom</p><p className="truncate text-xs text-slate-400">{t("shell.smartOperations")}</p></div>
        <button onClick={() => setIsMobileMenuOpen(false)} aria-label={t("common.closeNav")} className="ml-auto grid h-9 w-9 place-items-center rounded-lg text-slate-300 hover:bg-white/10 md:hidden"><X className="h-5 w-5" /></button>
      </div>

      <div className={cn("px-4 pt-5", isCollapsed && "md:px-3")}><p className={cn("text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate-500", isCollapsed && "md:text-center")}>{isCollapsed ? "·" : t("common.operations")}</p></div>
      <nav aria-label={t("shell.mainNavigation")} className="flex-1 space-y-1 overflow-y-auto px-3 py-3">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return <Link key={item.name} href={item.href} title={isCollapsed ? item.name : undefined} className={cn("group relative flex h-11 items-center rounded-lg px-3 text-sm font-medium transition-colors", isActive ? "bg-[var(--sidebar-active)] text-white" : "text-slate-300 hover:bg-[var(--sidebar-hover)] hover:text-white", isCollapsed && "md:justify-center md:px-0")}>
            {isActive && <span className="absolute inset-y-2 left-0 w-[3px] rounded-r-full bg-brand-400 animate-[nav-indicator_180ms_ease-out]" />}
            <item.icon className={cn("h-5 w-5 shrink-0 transition-transform duration-200 group-hover:rotate-[-4deg]", isActive ? "text-brand-300" : "text-slate-400 group-hover:text-brand-300")} />
            <span className={cn("ml-3 truncate transition-all duration-200", isCollapsed && "md:pointer-events-none md:w-0 md:opacity-0")}>{item.name}</span>
          </Link>;
        })}
      </nav>

      <div className="border-t border-[var(--sidebar-border)] p-3">
        <div className={cn("mb-3 rounded-lg border border-white/8 bg-white/4 px-3 py-2", isCollapsed && "md:hidden")}><div className="status-beacon text-slate-300">{t("shell.operatingSystem")}</div></div>
        <button onClick={() => setIsCollapsed((value) => !value)} aria-label={isCollapsed ? t("common.expandNav") : t("common.collapseNav")} className="mb-3 hidden h-10 w-full items-center justify-center rounded-lg text-slate-400 hover:bg-white/10 hover:text-white md:flex"><span className="sr-only">{isCollapsed ? t("common.expandNav") : t("common.collapseNav")}</span>{isCollapsed ? <PanelLeftOpen className="h-5 w-5" /> : <PanelLeftClose className="h-5 w-5" />}</button>
        <div className={cn("flex items-center rounded-lg bg-white/5 p-2", isCollapsed && "md:justify-center md:bg-transparent md:p-0")}><UserCircle className="h-8 w-8 shrink-0 text-slate-400" /><div className={cn("ml-2 min-w-0 flex-1", isCollapsed && "md:hidden")}><p className="truncate text-sm font-medium text-white">{user.nombre}</p><p className="truncate text-xs text-slate-400">{user.correo}</p></div></div>
        <button onClick={logout} title={isCollapsed ? t("common.logout") : undefined} className={cn("mt-2 flex h-10 w-full items-center rounded-lg px-2 text-sm font-medium text-slate-300 hover:bg-white/10 hover:text-white", isCollapsed && "md:justify-center md:px-0")}><LogOut className="h-4 w-4 shrink-0" /><span className={cn("ml-2", isCollapsed && "md:hidden")}>{t("common.logout")}</span></button>
      </div>
    </aside>

    <main className="command-canvas min-w-0 flex-1">
      <header className="hidden h-20 items-center justify-between border-b border-border bg-card/82 px-8 backdrop-blur md:flex"><div><p className="command-eyebrow">Zoom2 workspace</p><p className="mt-1 text-sm app-muted">{t("shell.workspaceSubtitle")}</p></div><div className="flex items-center gap-4"><span className="status-beacon"><Radio className="h-3.5 w-3.5 text-emerald-500" />{t("shell.servicesOnline")}</span><span className="text-sm app-muted">{user.nombre}</span><LanguageToggle /><ThemeToggle /></div></header>
      <div className="page-enter mx-auto w-full max-w-[1600px] p-4 md:p-8">{children}</div>
    </main>
    {isMobileMenuOpen && <button aria-label={t("common.closeNav")} onClick={() => setIsMobileMenuOpen(false)} className="fixed inset-0 z-40 bg-slate-950/45 backdrop-blur-[1px] md:hidden" />}
  </div>;
}
