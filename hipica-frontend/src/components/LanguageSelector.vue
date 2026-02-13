<template>
  <label style="display: inline-flex; gap: 8px; align-items: center;">
    <span>{{ t("language.label") }}</span>
    <select v-model="currentLocale" style="padding: 4px 6px;">
      <option
        v-for="localeCode in SUPPORTED_LOCALES"
        :key="localeCode"
        :value="localeCode"
      >
        {{ t(`language.options.${localeCode}`) }}
      </option>
    </select>
  </label>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { setAppLocale } from "../i18n";
import { SUPPORTED_LOCALES, type LocaleCode } from "../i18n/locale";

const { t, locale } = useI18n();

const currentLocale = computed<LocaleCode>({
  get: () => locale.value as LocaleCode,
  set: (value) => {
    setAppLocale(value);
  },
});
</script>
