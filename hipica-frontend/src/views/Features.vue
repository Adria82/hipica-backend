<template>
  <v-container>
    <h2 class="text-h5 mb-2">{{ t("features.title") }}</h2>
    <p class="text-body-2 text-medium-emphasis mb-4">{{ t("features.subtitle") }}</p>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <!-- Selector de hípica -->
    <v-select
      v-model="selectedStableId"
      :label="t('features.selectStable')"
      :items="stables"
      item-title="name"
      item-value="id"
      variant="outlined"
      density="compact"
      class="mb-4"
      style="max-width: 400px"
      @update:model-value="loadFeatures"
    />

    <!-- Lista de features como checkboxes -->
    <v-card v-if="selectedStableId" variant="outlined">
      <v-list>
        <v-list-item
          v-for="code in ALL_FEATURES"
          :key="code"
          :title="t(`features.codes.${code}`)"
          :subtitle="code"
        >
          <template #append>
            <v-switch
              v-model="activeFeatures"
              :value="code"
              color="primary"
              hide-details
              density="compact"
            />
          </template>
        </v-list-item>
      </v-list>
      <v-divider />
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="primary"
          variant="flat"
          :loading="saving"
          @click="saveFeatures"
        >
          {{ t("features.save") }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000" location="top">
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "../api/http";
import type { Stable } from "../types/api";

const { t } = useI18n();
const stables = ref<Stable[]>([]);
const selectedStableId = ref<number | null>(null);
const activeFeatures = ref<string[]>([]);
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const ALL_FEATURES = ["HORSES", "CLIENTS", "LESSONS", "BOOKINGS", "BILLING", "REPORTING"];

async function load() {
  try {
    const res = await http.get<Stable[]>("/api/v1/stables");
    stables.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("features.error");
  }
}

async function loadFeatures(stableId: number | null) {
  if (!stableId) return;
  loading.value = true;
  try {
    const res = await http.get<string[]>(`/api/v1/stables/${stableId}/features`);
    activeFeatures.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("features.error");
  } finally {
    loading.value = false;
  }
}

async function saveFeatures() {
  if (!selectedStableId.value) return;
  saving.value = true;
  try {
    await http.put(`/api/v1/stables/${selectedStableId.value}/features`, activeFeatures.value);
    showSnackbar(t("features.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("features.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

function showSnackbar(text: string, color: string) {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

onMounted(load);
</script>
