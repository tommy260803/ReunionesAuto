"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { defaultLanguage, type Language, translations } from "@/lib/i18n";

interface LanguageContextType {
  language: Language;
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  language: defaultLanguage,
  setLanguage: () => {},
  toggleLanguage: () => {},
  t: (key) => translations[defaultLanguage][key] || key,
});

const storageKey = "zoom2.language";

const isLanguage = (value: string | null): value is Language => value === "es" || value === "en";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);

  useEffect(() => {
    const savedLanguage = localStorage.getItem(storageKey);
    if (isLanguage(savedLanguage)) setLanguageState(savedLanguage);
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
    localStorage.setItem(storageKey, language);
  }, [language]);

  const setLanguage = (nextLanguage: Language) => setLanguageState(nextLanguage);
  const toggleLanguage = () => setLanguageState((current) => current === "es" ? "en" : "es");
  const t = (key: string) => translations[language][key] || translations[defaultLanguage][key] || key;

  return <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>{children}</LanguageContext.Provider>;
}

export const useLanguage = () => useContext(LanguageContext);
