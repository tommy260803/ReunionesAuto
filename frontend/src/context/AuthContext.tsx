"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";
import api from "@/lib/api";

interface User {
  id: string;
  correo: string;
  nombre: string;
  nivel_suscripcion: string;
  estado_suscripcion: string;
  rol: "USUARIO" | "EVALUADOR" | "INVESTIGADOR" | "ADMIN";
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

const publicPaths = ["/", "/login", "/register"];

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const fetchUser = async () => {
      const token = Cookies.get("access_token");
      if (!token) {
        setLoading(false);
        if (!publicPaths.includes(pathname)) {
          router.push("/login");
        }
        return;
      }
      
      try {
        const { data } = await api.get<User>("/auth/me");
        setUser(data);
        if (pathname === "/login" || pathname === "/register") {
          router.push("/dashboard");
        }
      } catch (error: any) {
        const status = error?.response?.status;
        if (status === 401) {
          Cookies.remove("access_token");
          setUser(null);
          if (!publicPaths.includes(pathname)) {
            router.push("/login");
          }
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, []);

  const login = (token: string, userData: User) => {
    Cookies.set("access_token", token, { expires: 1 }); // 1 día
    setUser(userData);
    router.push("/dashboard");
  };

  const logout = () => {
    Cookies.remove("access_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
