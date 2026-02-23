/**
 * Cliente HTTP centralizado (Axios) para el frontend.
 *
 * Funcionalidades:
 *  - Define baseURL desde VITE_API_BASE_URL
 *  - Añade automáticamente Authorization Bearer
 *  - Refresca el token cuando hay 401
 *  - Encola peticiones mientras se refresca (anti-race condition)
 *
 * Autor: Adrià Bofill
 * Proyecto: Gestión de Hípica
 */

import axios from "axios";
import { getAccessToken } from "@/auth/tokens";
import { getAppLocale } from "@/i18n";

/**
 * URL base backend
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

/**
 * Instancia Axios
 */
export const http = axios.create({
  baseURL: API_BASE_URL,
});


/**
 * ============================================================
 * Request interceptor
 * Añade automáticamente Authorization Bearer y locale
 * ============================================================
 */
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // mantener idioma actual
  config.headers["Accept-Language"] = getAppLocale();

  return config;
});