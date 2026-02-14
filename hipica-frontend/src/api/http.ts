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

/**
 * IMPORTANTE:
 * Axios en Vite NO exporta los tipos como ESM reales.
 * Debemos importarlos como "type-only".
 */
import type { AxiosError, InternalAxiosRequestConfig } from "axios";

import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
} from "@/auth/tokens";

import { getAppLocale } from "@/i18n";
import type { RefreshRequest, TokenResponse } from "@/types/api";

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
