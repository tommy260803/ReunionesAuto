"use client";

import { useState } from "react";
import { AxiosError } from "axios";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import Link from "next/link";
import { ArrowLeft, ArrowRight, CheckCircle2, Loader2, Lock, Mail, Sparkles, User, Users } from "lucide-react";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useLanguage } from "@/context/LanguageContext";

type ApiError = { detail?: string };

const getErrorMessage = (err: unknown, fallback: string) => {
  if (err instanceof AxiosError) return (err.response?.data as ApiError | undefined)?.detail || fallback;
  return fallback;
};

export default function RegisterPage() {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { t } = useLanguage();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/auth/register", { email, password, nombre });
      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err) {
      setError(getErrorMessage(err, t("auth.registerError")));
      setLoading(false);
    }
  };

  return (
    <main className="auth-screen text-white">
      <div className="future-grid" />
      <div className="future-orb future-orb-a" />
      <div className="future-orb future-orb-c" />

      <Link href="/" className="auth-home-link"><ArrowLeft className="h-4 w-4" /> {t("common.backHome")}</Link>
      <div className="absolute right-4 top-4 z-10 md:right-8"><LanguageToggle className="border-white/10 bg-white/[0.06] text-white" /></div>

      <section className="auth-layout auth-layout-register">
        <div className="auth-visual-panel">
          <div className="future-pill mb-6"><Sparkles className="h-4 w-4" /> {t("auth.newOperator")}</div>
          <h1 className="text-5xl font-semibold leading-none tracking-[-0.055em] text-white md:text-6xl">{t("auth.registerHeroTitle")}</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">{t("auth.registerHeroText")}</p>
          <div className="mt-10 space-y-4">
            <AuthStep number="01" title={t("auth.stepIdentity")} text={t("auth.stepIdentityText")} />
            <AuthStep number="02" title={t("auth.stepAccess")} text={t("auth.stepAccessText")} />
            <AuthStep number="03" title={t("auth.stepOperation")} text={t("auth.stepOperationText")} />
          </div>
        </div>

        <div className="auth-form-card">
          <div className="mb-8 text-center">
            <div className="auth-brand-mark mx-auto mb-5"><Users className="h-6 w-6" /></div>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/70">{t("auth.registry")}</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white">{t("auth.createAccountTitle")}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">{t("auth.registerSubtitle")}</p>
          </div>

          {error && <div role="alert" className="auth-alert auth-alert-error">{error}</div>}
          {success && <div role="status" className="auth-alert auth-alert-success"><CheckCircle2 className="h-4 w-4" /> {t("auth.success")}</div>}

          <form onSubmit={handleRegister} className="space-y-5">
            <div>
              <label htmlFor="register-name" className="auth-label">{t("common.fullName")}</label>
              <div className="auth-input-wrap">
                <User className="auth-input-icon" />
                <input
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  id="register-name"
                  placeholder={t("auth.namePlaceholder")}
                  className="auth-input"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="register-email" className="auth-label">{t("common.email")}</label>
              <div className="auth-input-wrap">
                <Mail className="auth-input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  id="register-email"
                  placeholder={t("auth.emailPlaceholder")}
                  className="auth-input"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="register-password" className="auth-label">{t("common.password")}</label>
              <div className="auth-input-wrap">
                <Lock className="auth-input-icon" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  id="register-password"
                  placeholder={t("auth.passwordMinPlaceholder")}
                  className="auth-input"
                  required
                  minLength={6}
                />
              </div>
            </div>

            <button type="submit" disabled={loading || success} className="future-button flex w-full items-center justify-center gap-2">
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <>{t("common.register")} <ArrowRight className="h-4 w-4" /></>}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-slate-300">
            {t("auth.hasAccount")} <Link href="/login" className="font-semibold text-cyan-200 transition hover:text-white">{t("common.signIn")}</Link>
          </div>
        </div>
      </section>
    </main>
  );
}

function AuthStep({ number, title, text }: { number: string; title: string; text: string }) {
  return <div className="flex gap-4 rounded-2xl border border-white/10 bg-white/[0.045] p-4 backdrop-blur"><div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-cyan-300/10 text-sm font-semibold text-cyan-100 ring-1 ring-cyan-200/20">{number}</div><div><h3 className="text-sm font-semibold text-white">{title}</h3><p className="mt-1 text-sm leading-6 text-slate-300">{text}</p></div></div>;
}
