"use client";

import { useState } from "react";
import { AxiosError } from "axios";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Bot, Loader2, Lock, Mail, Radio, ShieldCheck, Sparkles } from "lucide-react";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useLanguage } from "@/context/LanguageContext";

type ApiError = { detail?: string };

const getErrorMessage = (err: unknown, fallback: string) => {
  if (err instanceof AxiosError) return (err.response?.data as ApiError | undefined)?.detail || fallback;
  return fallback;
};

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { t } = useLanguage();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await api.post("/auth/login", { email, password });
      login(data.access_token, data.user);
    } catch (err) {
      setError(getErrorMessage(err, t("auth.loginError")));
      setLoading(false);
    }
  };

  return (
    <main className="auth-screen text-white">
      <div className="future-grid" />
      <div className="future-orb future-orb-a" />
      <div className="future-orb future-orb-b" />

      <Link href="/" className="auth-home-link"><ArrowLeft className="h-4 w-4" /> {t("common.backHome")}</Link>
      <div className="absolute right-4 top-4 z-10 md:right-8"><LanguageToggle className="border-white/10 bg-white/[0.06] text-white" /></div>

      <section className="auth-layout">
        <div className="auth-visual-panel">
          <div className="future-pill mb-6"><Radio className="h-4 w-4" /> {t("auth.loginAccessPill")}</div>
          <h1 className="text-5xl font-semibold leading-none tracking-[-0.055em] text-white md:text-6xl">{t("auth.loginHeroTitle")}</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">{t("auth.loginHeroText")}</p>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <AuthSignal icon={Bot} label={t("auth.ai")} value={t("auth.drafts")} />
            <AuthSignal icon={ShieldCheck} label={t("auth.jwt")} value={t("auth.secureSession")} />
            <AuthSignal icon={Sparkles} label="n8n" value={t("auth.automated")} />
          </div>
          <div className="auth-orbit mt-12">
            <div className="orbit-ring orbit-ring-one" />
            <div className="orbit-ring orbit-ring-two" />
            <div className="orbit-core"><Bot className="h-8 w-8" /></div>
          </div>
        </div>

        <div className="auth-form-card">
          <div className="mb-8 text-center">
            <div className="auth-brand-mark mx-auto mb-5">Z2</div>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/70">{t("auth.loginAccess")}</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white">{t("auth.welcomeBack")}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">{t("auth.loginSubtitle")}</p>
          </div>

          {error && <div role="alert" className="auth-alert auth-alert-error">{error}</div>}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label htmlFor="login-email" className="auth-label">{t("common.email")}</label>
              <div className="auth-input-wrap">
                <Mail className="auth-input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  id="login-email"
                  placeholder={t("auth.emailPlaceholder")}
                  className="auth-input"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password" className="auth-label">{t("common.password")}</label>
              <div className="auth-input-wrap">
                <Lock className="auth-input-icon" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  id="login-password"
                  placeholder={t("auth.passwordPlaceholder")}
                  className="auth-input"
                  required
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="future-button flex w-full items-center justify-center gap-2">
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <>{t("common.signIn")} <ArrowRight className="h-4 w-4" /></>}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-slate-300">
            {t("auth.noAccount")} <Link href="/register" className="font-semibold text-cyan-200 transition hover:text-white">{t("auth.registerHere")}</Link>
          </div>
        </div>
      </section>
    </main>
  );
}

function AuthSignal({ icon: Icon, label, value }: { icon: typeof Bot; label: string; value: string }) {
  return <div className="rounded-2xl border border-white/10 bg-white/[0.045] p-4 backdrop-blur"><Icon className="mb-3 h-5 w-5 text-cyan-200" /><p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p><p className="mt-1 text-sm font-semibold text-white">{value}</p></div>;
}
