/**
 * Cliente HTTP centralizado (Axios) para el frontend.
 *
 * Funcionalidades:
 *  - Define el baseURL de la API usando .env (VITE_API_BASE_URL)
 *  - Añade automáticamente el header Authorization: Bearer <access_token>
 *  - Si una petición devuelve 401 (token caducado), intenta refrescar el access token
 *    usando /api/v1/auth/refresh y reintenta la petición original.
 *  - Si varias peticiones fallan a la vez por 401, se encolan mientras se refresca el token,
 *    evitando ejecutar múltiples refresh simultáneos.
 * 
 *
 * Autor: Adrià Bofill
 * Proyecto: Gestión de Hípica
 */

import axios from "axios";
import type {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";

import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
} from "../auth/tokens";
import { getAppLocale } from "../i18n";

import type { RefreshRequest, TokenResponse } from "../types/api";

/**
 * URL base de la API (backend).
 * Se obtiene desde .env:
 *   VITE_API_BASE_URL=http://localhost:8000
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

/**
 * Instancia principal de Axios.
 * - baseURL: para evitar repetir http://localhost:8000 en cada llamada
 */
export const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Interceptor de request:
 * - Antes de enviar cualquier petición, añade el access token si existe.
 */
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  const locale = getAppLocale();

  config.headers["Accept-Language"] = locale;

  // Si tenemos access token, lo enviamos como Bearer token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

/**
 * Control para evitar lanzar múltiples refresh a la vez.
 */
let isRefreshing = false;

/**
 * Cola de peticiones que han fallado con 401 mientras se refrescaba el token.
 * Cada elemento guarda un resolve/reject para reanudar la petición cuando tengamos token nuevo.
 */
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

/**
 * Resuelve/rechaza todas las promesas encoladas cuando termina el refresh.
 *
 * @param error Error si el refresh falla (null si ha ido bien)
 * @param token Nuevo access token si el refresh ha ido bien (null si falla)
 */
function resolveQueue(error: unknown, token: string | null) {
  refreshQueue.forEach((p) => {
    if (error) p.reject(error);
    else p.resolve(token as string);
  });
  refreshQueue = [];
}

/**
 * Interceptor de response:
 * - Si una respuesta devuelve 401, intenta refrescar el access token con el refresh token.
 * - Si el refresh funciona: reintenta la petición original con el nuevo access token.
 * - Si el refresh falla: limpia tokens (logout técnico) y devuelve error.
 */
http.interceptors.response.use(
  (response) => response,
  async (err: AxiosError) => {
    // Config original de la request que falló
    const originalRequest =
      err.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    // Si no tenemos config, no podemos reintentar
    if (!originalRequest) return Promise.reject(err);

    // Solo actuamos si es 401 (no autorizado)
    const statusCode = err.response?.status;
    if (statusCode !== 401) return Promise.reject(err);

    // Evitar bucles infinitos (si ya se reintentó una vez, no insistimos)
    if (originalRequest._retry) return Promise.reject(err);
    originalRequest._retry = true;

    // Si no hay refresh token, no podemos refrescar → logout técnico
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      return Promise.reject(err);
    }

    /**
     * Si ya hay un refresh en marcha:
     * - No lanzamos otro refresh
     * - Encolamos la petición y esperamos a que termine el refresh actual
     */
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push({
          resolve: (newAccessToken) => resolve(newAccessToken),
          reject,
        });
      }).then((newAccessToken) => {
        // Reintentamos la petición original con el token nuevo
        originalRequest.headers.Authorization = `Bearer ${newAccessToken as string}`;
        return http(originalRequest);
      });
    }

    /**
     * Si no hay refresh en marcha, lo iniciamos.
     */
    isRefreshing = true;

    try {
      // Payload esperado por el backend: {"refresh_token": "..."}
      const payload: RefreshRequest = { refresh_token: refreshToken };

      // Llamada al endpoint de refresh (se usa axios "directo" para no entrar en este mismo interceptor)
      const res = await axios.post<TokenResponse>(
        `${API_BASE_URL}/api/v1/auth/refresh`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            "Accept-Language": getAppLocale(),
          },
        }
      );

      // Guardamos nuevos tokens
      setTokens(res.data);

      // Nuevo access token para reintentos
      const newAccessToken = res.data.access_token;

      // Liberamos la cola de peticiones en espera
      resolveQueue(null, newAccessToken);

      // Reintentamos la petición original con el token nuevo
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return http(originalRequest);
    } catch (refreshErr) {
      // Si el refresh falla, rechazamos la cola y limpiamos tokens
      resolveQueue(refreshErr, null);
      clearTokens();
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
);
