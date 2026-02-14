<template>
  <v-select
    :model-value="currentLocale"
    @update:model-value="setLocale"
    :items="localeOptions"
    item-title="label"
    item-value="code"
    density="compact"
    variant="outlined"
    prepend-inner-icon="mdi-translate"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { setAppLocale } from "../i18n";
import { SUPPORTED_LOCALES, type LocaleCode } from "../i18n/locale";

const { t, locale } = useI18n();

const currentLocale = computed(() => locale.value as LocaleCode);

const localeOptions = computed(() =>
  SUPPORTED_LOCALES.map((code) => ({
    code,
    label: t(`language.options.${code}`),
  }))
);

const setLocale = (code: LocaleCode) => {
  setAppLocale(code);
};
</script>
