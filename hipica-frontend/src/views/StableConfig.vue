<template>
  <v-container fluid style="max-width: 600px">
    <h2 class="text-h5 mb-6">{{ t("stableConfig.title") }}</h2>

    <v-card class="mb-4">
      <v-card-text>
        <v-text-field
          v-model.number="form.cancel_deadline_hours"
          type="number"
          :label="t('stableConfig.cancelDeadlineHours')"
          density="compact"
          min="0"
          class="mb-4"
        />
        <v-switch
          v-model="form.auto_attendance"
          :label="t('stableConfig.autoAttendance')"
          :hint="t('stableConfig.autoAttendanceHint')"
          persistent-hint
          color="primary"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" :loading="saving" @click="doSave">
          {{ t("stableConfig.save") }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-divider class="my-4" />

    <v-btn
      color="warning"
      variant="tonal"
      :loading="processing"
      prepend-icon="mdi-clock-check-outline"
      @click="processAttendance"
    >
      {{ t("stableConfig.processAttendance") }}
    </v-btn>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "@/api/http";
import type { StableConfig } from "@/types/api";

const { t } = useI18n();

const saving = ref(false);
const processing = ref(false);
const form = ref({ cancel_deadline_hours: 24, auto_attendance: false });

async function loadConfig() {
  try {
    const { data } = await http.get<StableConfig>("/api/v1/stable-config");
    form.value.cancel_deadline_hours = data.cancel_deadline_hours;
    form.value.auto_attendance = data.auto_attendance;
  } catch {
    // usa valores por defecto
  }
}

async function doSave() {
  saving.value = true;
  try {
    await http.put("/api/v1/stable-config", form.value);
    showSnackbar(t("stableConfig.saveSuccess"), "success");
  } catch {
    showSnackbar(t("stableConfig.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function processAttendance() {
  processing.value = true;
  try {
    const { data } = await http.post<{ processed: number }>("/api/v1/admin/attendance/process");
    showSnackbar(t("stableConfig.processSuccess", { count: data.processed }), "success");
  } catch {
    showSnackbar(t("stableConfig.processError"), "error");
  } finally {
    processing.value = false;
  }
}

const snackbar = ref({ show: false, message: "", color: "success" });
function showSnackbar(message: string, color = "success") {
  snackbar.value = { show: true, message, color };
}

onMounted(loadConfig);
</script>
