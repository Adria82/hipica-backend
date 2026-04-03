<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("lessons.title") }}</h2>

    <v-alert type="info" variant="tonal" class="mt-4">
      {{ t("lessons.comingSoon") }}
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>
