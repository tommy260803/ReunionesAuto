"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

type Theme = "light" | "dark";

const getTheme = (): Theme => {
  if (typeof window === "undefined") return "light";
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
};

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => { setTheme(getTheme()); }, []);

  const toggleTheme = () => {
    const nextTheme: Theme = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem("zoom2.theme", nextTheme);
    setTheme(nextTheme);
  };

  const isDark = theme === "dark";
  return <button type="button" onClick={toggleTheme} aria-label={isDark ? "Activar modo claro" : "Activar modo oscuro"} title={isDark ? "Modo claro" : "Modo oscuro"} className="relative inline-flex h-10 w-[4.5rem] items-center rounded-full border border-border bg-slate-100 p-1 dark:bg-slate-800">
    <span className={`absolute grid h-8 w-8 place-items-center rounded-full bg-card text-brand-600 shadow-sm transition-transform duration-300 ease-out ${isDark ? "translate-x-8" : "translate-x-0"}`}>{isDark ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}</span>
    <Sun className="ml-1 h-3.5 w-3.5 text-amber-600" />
    <Moon className="ml-auto mr-1 h-3.5 w-3.5 text-slate-500 dark:text-slate-300" />
  </button>;
}
