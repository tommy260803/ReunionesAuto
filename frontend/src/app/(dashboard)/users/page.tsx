"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { format, parseISO } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Download, Loader2, Users, ShieldAlert, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/context/LanguageContext";

interface User {
  id: string;
  nombre: string;
  correo: string;
  nivel_suscripcion: string;
  estado_suscripcion: string;
  fecha_creacion: string;
}

export default function UsersPage() {
  const { user, loading: authLoading } = useAuth();
  const { language, t } = useLanguage();
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading) {
      if (!user?.is_admin) {
        router.push("/dashboard");
      } else {
        fetchUsers();
      }
    }
  }, [user, authLoading, router]);

  const fetchUsers = async () => {
    try {
      const { data } = await api.get<User[]>("/users");
      setUsers(data);
    } catch (err) {
      setError(t("users.loadError"));
    } finally {
      setLoading(false);
    }
  };

  const handleLevelChange = async (userId: string, newLevel: string) => {
    try {
      await api.patch(`/users/${userId}`, { nivel_suscripcion: newLevel });
      fetchUsers();
    } catch (err) {
      alert(t("users.updateError"));
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm(t("users.deleteConfirm"))) return;
    try {
      await api.delete(`/users/${userId}`);
      fetchUsers();
    } catch (err) {
      alert(t("users.deleteError"));
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.get("/reports/users/pdf", { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = "reporte_usuarios.pdf";
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setError(t("users.reportError"));
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
      </div>
    );
  }

  if (!user?.is_admin) {
    return null; // Next.js is redirecting
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between sm:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            <Users className="w-8 h-8 text-brand-500" />
            {t("users.title")}
          </h1>
          <p className="text-slate-500">{t("users.subtitle")}</p>
        </div>
        <button onClick={handleExport} className="btn-primary inline-flex items-center gap-2 shrink-0"><Download className="w-4 h-4" />{t("common.exportPdf")}</button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5" />
          {error}
        </div>
      )}

      <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 border-b border-border">
              <tr>
                <th className="px-6 py-4 font-medium">{t("common.name")}</th>
                <th className="px-6 py-4 font-medium">{t("common.emailShort")}</th>
                <th className="px-6 py-4 font-medium">{t("users.subscription")}</th>
                <th className="px-6 py-4 font-medium">{t("common.status")}</th>
                <th className="px-6 py-4 font-medium">{t("users.registration")}</th>
                <th className="px-6 py-4 font-medium text-right">{t("common.actions")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-medium text-foreground">{u.nombre}</td>
                  <td className="px-6 py-4 text-slate-500">{u.correo}</td>
                  <td className="px-6 py-4">
                    <select
                      value={u.nivel_suscripcion.toLowerCase()}
                      onChange={(e) => handleLevelChange(u.id, e.target.value)}
                      className="bg-slate-100 dark:bg-slate-800 border-none rounded-md px-2 py-1 outline-none text-xs font-medium uppercase tracking-wider text-slate-600 dark:text-slate-300 cursor-pointer hover:bg-slate-200 transition-colors"
                    >
                      <option value="basico">{t("users.basic")}</option>
                      <option value="pro">Pro</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 px-2 py-1 rounded-full text-xs font-semibold capitalize tracking-wide">
                      {u.estado_suscripcion}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500 text-xs">
                    {u.fecha_creacion ? format(parseISO(u.fecha_creacion), "dd MMM yyyy", { locale: language === "es" ? es : enUS }) : "—"}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(u.id)}
                      className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors inline-flex"
                      title={t("users.deleteUser")}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                    {t("users.empty")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
