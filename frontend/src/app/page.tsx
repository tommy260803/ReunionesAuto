"use client";

import Link from "next/link";
import { ArrowRight, Bot, CalendarCheck2, CheckCircle2, FileText, Gauge, Network, Radio, Sparkles, Users, Video, Zap } from "lucide-react";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useLanguage } from "@/context/LanguageContext";

const capabilities = [
  { icon: Bot, titleKey: "landing.capAiTitle", textKey: "landing.capAiText" },
  { icon: CalendarCheck2, titleKey: "landing.capAgendaTitle", textKey: "landing.capAgendaText" },
  { icon: FileText, titleKey: "landing.capSummariesTitle", textKey: "landing.capSummariesText" },
  { icon: Gauge, titleKey: "landing.capMetricsTitle", textKey: "landing.capMetricsText" },
];

const orbitItems = ["Zoom API", "Supabase", "FastAPI", "Next.js"];

export default function Home() {
  const { t } = useLanguage();

  return (
    <main className="future-shell text-white">
      <div className="future-grid" />
      <div className="future-orb future-orb-a" />
      <div className="future-orb future-orb-b" />
      <div className="future-orb future-orb-c" />

      <nav className="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-5 md:px-8">
        <Link href="/" className="group flex items-center gap-3" aria-label={t("landing.logoAria")}>
          <div className="future-logo">Z2</div>
          <div>
            <p className="text-base font-semibold tracking-tight text-white">Zoom2</p>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/70">Meeting OS</p>
          </div>
        </Link>
        <div className="hidden items-center gap-3 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-cyan-50/80 backdrop-blur md:flex">
          <Radio className="h-4 w-4 text-emerald-300" />
          {t("landing.status")}
        </div>
        <div className="flex items-center gap-2">
          <LanguageToggle className="border-white/10 bg-white/[0.06] text-white" />
          <Link href="/register" className="hidden rounded-full border border-white/12 px-4 py-2 text-sm font-semibold text-white/85 hover:bg-white/10 sm:inline-flex">{t("common.createAccount")}</Link>
          <Link href="/login" className="future-button future-button-compact">{t("common.signIn")}</Link>
        </div>
      </nav>

      <section className="relative z-10 mx-auto grid min-h-[calc(100svh-5.5rem)] w-full max-w-7xl items-center gap-10 overflow-hidden px-5 pb-10 pt-6 md:px-8 lg:grid-cols-[0.92fr_1.08fr] xl:gap-12">
        <div className="max-w-2xl">
          <div className="future-pill mb-6"><Sparkles className="h-4 w-4" /> {t("landing.pill")}</div>
          <h1 className="text-[clamp(3.2rem,6.3vw,6.35rem)] font-semibold leading-[0.94] tracking-[-0.06em] text-white">
            {t("landing.title")}
          </h1>
          <p className="mt-6 max-w-xl text-base leading-8 text-slate-300 md:text-lg">
            {t("landing.subtitle")}
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/login" className="future-button inline-flex items-center justify-center gap-2">
              {t("landing.enterPlatform")} <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/register" className="inline-flex min-h-12 items-center justify-center rounded-full border border-cyan-200/20 bg-white/[0.04] px-5 text-sm font-semibold text-cyan-50 backdrop-blur transition hover:border-cyan-200/45 hover:bg-white/[0.08]">
              {t("landing.requestAccess")}
            </Link>
          </div>
          <div className="mt-8 grid max-w-xl grid-cols-2 gap-3 sm:grid-cols-4">
            <Signal label={t("landing.signalMeetings")} value="360°" />
            <Signal label={t("landing.signalDrafts")} value="Live" />
            <Signal label={t("landing.signalLogs")} value="Real time" />
            <Signal label={t("landing.signalPdf")} value="Stream" />
          </div>
        </div>

        <div className="relative grid min-h-[31rem] place-items-center overflow-hidden py-6 lg:min-h-[38rem]">
          <div className="orbit-ring orbit-ring-one" />
          <div className="orbit-ring orbit-ring-two" />
          <div className="orbit-core orbit-core-landing"><Network className="h-8 w-8" /></div>
          {orbitItems.map((item, index) => <div key={item} className={`orbit-chip orbit-chip-${index + 1}`}>{item}</div>)}

          <div className="hologram-card relative z-10 w-full max-w-[31rem] p-4 md:p-5">
            <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/70">{t("landing.missionControl")}</p>
                <h2 className="mt-2 text-xl font-semibold text-white md:text-2xl">{t("landing.meetingFlow")}</h2>
              </div>
              <div className="rounded-full border border-emerald-300/30 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">{t("common.active")}</div>
            </div>
            <div className="mt-5 grid gap-3">
              <Telemetry icon={Bot} title={t("landing.aiRequest")} value="00.8s" synced={t("landing.syncedBackend")} />
              <Telemetry icon={Video} title={t("landing.zoomRoom")} value="API" synced={t("landing.syncedBackend")} />
              <Telemetry icon={Users} title={t("landing.transactionalParticipants")} value="RPC" synced={t("landing.syncedBackend")} />
              <Telemetry icon={CheckCircle2} title={t("landing.commitments")} value="OK" synced={t("landing.syncedBackend")} />
            </div>
            <div className="mt-5 rounded-2xl border border-cyan-200/15 bg-cyan-200/[0.05] p-3">
              <div className="mb-3 flex items-center justify-between text-xs uppercase tracking-[0.2em] text-cyan-100/60">
                <span>{t("landing.automation")}</span>
                <span>{t("landing.stableLatency")}</span>
              </div>
              <div className="future-wave" />
            </div>
          </div>
        </div>
      </section>

      <section className="relative z-10 mx-auto grid w-full max-w-7xl gap-4 px-5 pb-16 pt-2 md:grid-cols-4 md:px-8">
        {capabilities.map((item) => <Capability key={item.titleKey} icon={item.icon} title={t(item.titleKey)} text={t(item.textKey)} />)}
      </section>
    </main>
  );
}

function Signal({ label, value }: { label: string; value: string }) {
  return <div className="rounded-2xl border border-white/10 bg-white/[0.045] p-3 backdrop-blur"><p className="text-xs text-slate-400">{label}</p><p className="mt-1 text-sm font-semibold text-cyan-100">{value}</p></div>;
}

function Telemetry({ icon: Icon, title, value, synced }: { icon: typeof Bot; title: string; value: string; synced: string }) {
  return <div className="group flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.045] p-3 transition hover:border-cyan-200/35 hover:bg-white/[0.07]"><div className="grid h-10 w-10 place-items-center rounded-xl bg-cyan-300/10 text-cyan-200 ring-1 ring-cyan-200/20"><Icon className="h-5 w-5" /></div><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold text-white">{title}</p><p className="mt-1 text-xs text-slate-400">{synced}</p></div><span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-cyan-100">{value}</span></div>;
}

function Capability({ icon: Icon, title, text }: { icon: typeof Zap; title: string; text: string }) {
  return <article className="hologram-card p-5"><div className="mb-5 grid h-11 w-11 place-items-center rounded-xl bg-cyan-300/10 text-cyan-200 ring-1 ring-cyan-200/20"><Icon className="h-5 w-5" /></div><h3 className="text-lg font-semibold text-white">{title}</h3><p className="mt-3 text-sm leading-6 text-slate-300">{text}</p></article>;
}
