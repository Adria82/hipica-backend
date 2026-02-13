export const SUPPORTED_LOCALES = ["ca", "es", "en"] as const;
export type LocaleCode = (typeof SUPPORTED_LOCALES)[number];

export const DEFAULT_LOCALE: LocaleCode = "ca";
const LOCALE_STORAGE_KEY = "hipica.locale";

function extractBaseLocale(value: string): string {
  const [weightedValue = ""] = value.split(",");
  const [languageTag = ""] = weightedValue.split(";");
  const [baseLocale = ""] = languageTag.trim().toLowerCase().split("-");
  return baseLocale;
}

export function normalizeLocale(value?: string | null): LocaleCode {
  if (!value) return DEFAULT_LOCALE;

  const locale = extractBaseLocale(value);
  if ((SUPPORTED_LOCALES as readonly string[]).includes(locale)) {
    return locale as LocaleCode;
  }

  return DEFAULT_LOCALE;
}

function getStoredLocale(): LocaleCode | null {
  const raw = window.localStorage.getItem(LOCALE_STORAGE_KEY);
  return raw ? normalizeLocale(raw) : null;
}

function getBrowserLocale(): LocaleCode {
  return normalizeLocale(window.navigator.language);
}

export function getInitialLocale(): LocaleCode {
  return getStoredLocale() ?? getBrowserLocale();
}

export function persistLocale(locale: LocaleCode): void {
  window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
}
