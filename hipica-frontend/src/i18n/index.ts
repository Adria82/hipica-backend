import { createI18n } from "vue-i18n";
import messages from "./messages";
import {
  getInitialLocale,
  normalizeLocale,
  persistLocale,
  type LocaleCode,
} from "./locale";

const initialLocale = getInitialLocale();

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: "ca",
  messages,
});

export function setAppLocale(locale: string): LocaleCode {
  const normalized = normalizeLocale(locale);
  i18n.global.locale.value = normalized;
  persistLocale(normalized);
  return normalized;
}

export function getAppLocale(): LocaleCode {
  return normalizeLocale(i18n.global.locale.value as string);
}
