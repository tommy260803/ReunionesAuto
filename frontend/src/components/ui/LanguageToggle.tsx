"use client";

import { Languages } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import { cn } from "@/lib/utils";

export function LanguageToggle({ className }: { className?: string }) {
  const { language, setLanguage, t } = useLanguage();

  return (
    <div className={cn("inline-flex items-center gap-1 rounded-full border border-border bg-card/80 p-1 text-xs font-bold shadow-sm backdrop-blur", className)} aria-label={t("common.language")}>
      <Languages className="ml-2 h-4 w-4 text-cyan-500" aria-hidden="true" />
      <button
        type="button"
        onClick={() => setLanguage("es")}
        aria-pressed={language === "es"}
        className={cn("rounded-full px-2.5 py-1 transition", language === "es" ? "bg-brand-600 text-white shadow-sm" : "text-slate-500 hover:text-foreground dark:text-slate-300")}
      >
        ES
      </button>
      <button
        type="button"
        onClick={() => setLanguage("en")}
        aria-pressed={language === "en"}
        className={cn("rounded-full px-2.5 py-1 transition", language === "en" ? "bg-brand-600 text-white shadow-sm" : "text-slate-500 hover:text-foreground dark:text-slate-300")}
      >
        EN
      </button>
    </div>
  );
}
