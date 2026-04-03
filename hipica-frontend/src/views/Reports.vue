<template>
  <v-container fluid>
    <h2 class="text-h5 mb-1">{{ t("reports.title") }}</h2>
    <p class="text-body-2 text-medium-emphasis mb-4">{{ t("reports.subtitle") }}</p>

    <!-- Date range filter -->
    <v-row dense class="mb-4" align="center">
      <v-col cols="12" sm="4" md="3">
        <v-text-field
          v-model="fromDate"
          :label="t('reports.fromDate')"
          type="date"
          variant="outlined"
          density="compact"
          hide-details
        />
      </v-col>
      <v-col cols="12" sm="4" md="3">
        <v-text-field
          v-model="toDate"
          :label="t('reports.toDate')"
          type="date"
          variant="outlined"
          density="compact"
          hide-details
        />
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="primary"
          prepend-icon="mdi-chart-bar"
          :loading="loading"
          @click="loadReport"
        >
          {{ t("reports.search") }}
        </v-btn>
      </v-col>
    </v-row>

    <!-- Error -->
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

    <!-- Empty state -->
    <v-alert v-else-if="loaded && isEmpty" type="info" variant="tonal" class="mb-4">
      {{ t("reports.empty") }}
    </v-alert>

    <!-- Report tables (visible once loaded) -->
    <template v-if="loaded && report">
      <v-row>
        <!-- Instructor hours -->
        <v-col cols="12" md="6">
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="text-subtitle-1 pa-3">
              <v-icon start>mdi-account-tie</v-icon>
              {{ t("reports.instructorHours.title") }}
            </v-card-title>
            <v-divider />
            <v-data-table
              :headers="instructorHeaders"
              :items="report.instructor_hours"
              density="compact"
              hide-default-footer
              :no-data-text="t('reports.empty')"
            />
          </v-card>
        </v-col>

        <!-- Helper hours -->
        <v-col cols="12" md="6">
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="text-subtitle-1 pa-3">
              <v-icon start>mdi-account-multiple</v-icon>
              {{ t("reports.helperHours.title") }}
            </v-card-title>
            <v-divider />
            <v-data-table
              :headers="helperHeaders"
              :items="report.helper_hours"
              density="compact"
              hide-default-footer
              :no-data-text="t('reports.empty')"
            />
          </v-card>
        </v-col>

        <!-- Student classes -->
        <v-col cols="12" md="6">
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="text-subtitle-1 pa-3">
              <v-icon start>mdi-account-group</v-icon>
              {{ t("reports.studentClasses.title") }}
            </v-card-title>
            <v-divider />
            <v-data-table
              :headers="studentHeaders"
              :items="report.student_classes"
              density="compact"
              hide-default-footer
              :no-data-text="t('reports.empty')"
            />
          </v-card>
        </v-col>

        <!-- Horse hours -->
        <v-col cols="12" md="6">
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="text-subtitle-1 pa-3">
              <v-icon start>mdi-horse</v-icon>
              {{ t("reports.horseHours.title") }}
            </v-card-title>
            <v-divider />
            <v-data-table
              :headers="horseHeaders"
              :items="report.horse_hours"
              density="compact"
              hide-default-footer
              :no-data-text="t('reports.empty')"
            />
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "@/api/http";
import type { LessonReport } from "@/types/api";

const { t } = useI18n();

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const fromDate = ref("");
const toDate = ref("");
const loading = ref(false);
const error = ref<string | null>(null);
const loaded = ref(false);
const report = ref<LessonReport | null>(null);

const isEmpty = computed(() =>
  !report.value ||
  (
    report.value.instructor_hours.length === 0 &&
    report.value.helper_hours.length === 0 &&
    report.value.student_classes.length === 0 &&
    report.value.horse_hours.length === 0
  )
);

// ---------------------------------------------------------------------------
// Table headers
// ---------------------------------------------------------------------------
const instructorHeaders = computed(() => [
  { title: t("reports.instructorHours.email"), key: "email", sortable: true },
  { title: t("reports.instructorHours.hours"), key: "hours", sortable: true },
]);

const helperHeaders = computed(() => [
  { title: t("reports.helperHours.email"), key: "email", sortable: true },
  { title: t("reports.helperHours.hours"), key: "hours", sortable: true },
]);

const studentHeaders = computed(() => [
  { title: t("reports.studentClasses.name"), key: "name", sortable: true },
  { title: t("reports.studentClasses.classCount"), key: "class_count", sortable: true },
]);

const horseHeaders = computed(() => [
  { title: t("reports.horseHours.name"), key: "name", sortable: true },
  { title: t("reports.horseHours.hours"), key: "hours", sortable: true },
]);

// ---------------------------------------------------------------------------
// Load
// ---------------------------------------------------------------------------
async function loadReport() {
  loading.value = true;
  error.value = null;
  try {
    const params: Record<string, string> = {};
    if (fromDate.value) params.from_date = fromDate.value;
    if (toDate.value) params.to_date = toDate.value;
    const { data } = await http.get<LessonReport>("/api/v1/reports/lessons", { params });
    report.value = data;
    loaded.value = true;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("reports.error");
  } finally {
    loading.value = false;
  }
}
</script>
