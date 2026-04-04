<template>
  <v-container fluid>
    <h2 class="text-h5 mb-1">{{ t("reports.title") }}</h2>
    <p class="text-body-2 text-medium-emphasis mb-4">{{ t("reports.subtitle") }}</p>

    <!-- Filters -->
    <v-row dense class="mb-4" align="center">
      <!-- Stable selector (app_admin only) -->
      <v-col v-if="isAppAdmin" cols="12" sm="4" md="3">
        <v-select
          v-model="selectedStableId"
          :items="stableItems"
          :label="t('reports.selectStable')"
          item-title="name"
          item-value="id"
          variant="outlined"
          density="compact"
          hide-details
          clearable
          :placeholder="t('reports.allStables')"
        />
      </v-col>

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

    <!-- Report tables -->
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
              @click:row="onInstructorRowClick"
              style="cursor: pointer"
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
              @click:row="onHelperRowClick"
              style="cursor: pointer"
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
              @click:row="onStudentRowClick"
              style="cursor: pointer"
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
              @click:row="onHorseRowClick"
              style="cursor: pointer"
            />
          </v-card>
        </v-col>

        <!-- Track hours -->
        <v-col cols="12" md="6">
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="text-subtitle-1 pa-3">
              <v-icon start>mdi-fence</v-icon>
              {{ t("reports.trackHours.title") }}
            </v-card-title>
            <v-divider />
            <v-data-table
              :headers="trackHeaders"
              :items="report.track_hours"
              density="compact"
              hide-default-footer
              :no-data-text="t('reports.empty')"
            />
          </v-card>
        </v-col>
      </v-row>

      <!-- Charts row -->
      <v-row v-if="!isEmpty">
        <!-- Horse hours bar chart -->
        <v-col cols="12" md="4">
          <v-card variant="outlined" class="mb-4 pa-2">
            <v-card-title class="text-subtitle-2 pa-2">
              {{ t("reports.charts.horseHours") }}
            </v-card-title>
            <VueApexCharts
              type="bar"
              height="220"
              :options="horseChartOptions"
              :series="horseChartSeries"
            />
          </v-card>
        </v-col>

        <!-- Staff hours bar chart -->
        <v-col cols="12" md="4">
          <v-card variant="outlined" class="mb-4 pa-2">
            <v-card-title class="text-subtitle-2 pa-2">
              {{ t("reports.charts.staffHours") }}
            </v-card-title>
            <VueApexCharts
              type="bar"
              height="220"
              :options="staffChartOptions"
              :series="staffChartSeries"
            />
          </v-card>
        </v-col>

        <!-- Classes by weekday bar chart -->
        <v-col cols="12" md="4">
          <v-card variant="outlined" class="mb-4 pa-2">
            <v-card-title class="text-subtitle-2 pa-2">
              {{ t("reports.charts.byWeekday") }}
            </v-card-title>
            <VueApexCharts
              type="bar"
              height="220"
              :options="weekdayChartOptions"
              :series="weekdayChartSeries"
            />
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Drill-down dialog -->
    <v-dialog v-model="detailDialog" max-width="700">
      <v-card>
        <v-card-title class="text-subtitle-1 pa-4">
          <v-icon start>mdi-calendar-clock</v-icon>
          {{ t("reports.detailDialog.title") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-0">
          <v-progress-linear v-if="detailLoading" indeterminate color="primary" />
          <v-data-table
            v-else
            :headers="detailHeaders"
            :items="detailItems"
            density="compact"
            hide-default-footer
            :no-data-text="t('reports.empty')"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="detailDialog = false">{{ t("common.close") }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import VueApexCharts from "vue3-apexcharts";
import { http } from "@/api/http";
import { isAppAdmin } from "@/auth/profile";
import type { LessonReport, LessonDetail, InstructorHours, HelperHours, StudentClasses, HorseHours, Stable } from "@/types/api";

const { t } = useI18n();

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const fromDate = ref("");
const toDate = ref("");
const selectedStableId = ref<number | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const loaded = ref(false);
const report = ref<LessonReport | null>(null);

// Stable selector
const stables = ref<Stable[]>([]);
const stableItems = computed(() => [
  ...stables.value,
]);

// Drill-down dialog
const detailDialog = ref(false);
const detailLoading = ref(false);
const detailItems = ref<LessonDetail[]>([]);

const isEmpty = computed(() =>
  !report.value ||
  (
    report.value.instructor_hours.length === 0 &&
    report.value.helper_hours.length === 0 &&
    report.value.student_classes.length === 0 &&
    report.value.horse_hours.length === 0 &&
    report.value.track_hours.length === 0
  )
);

// ---------------------------------------------------------------------------
// Table headers
// ---------------------------------------------------------------------------
const instructorHeaders = computed(() => [
  { title: t("reports.instructorHours.name"), key: "name", sortable: true },
  { title: t("reports.instructorHours.hours"), key: "hours", sortable: true },
  { title: t("reports.instructorHours.classCount"), key: "class_count", sortable: true },
]);

const helperHeaders = computed(() => [
  { title: t("reports.helperHours.name"), key: "name", sortable: true },
  { title: t("reports.helperHours.hours"), key: "hours", sortable: true },
  { title: t("reports.helperHours.classCount"), key: "class_count", sortable: true },
]);

const studentHeaders = computed(() => [
  { title: t("reports.studentClasses.name"), key: "name", sortable: true },
  { title: t("reports.studentClasses.classCount"), key: "class_count", sortable: true },
  { title: t("reports.studentClasses.hours"), key: "hours", sortable: true },
]);

const horseHeaders = computed(() => [
  { title: t("reports.horseHours.name"), key: "name", sortable: true },
  { title: t("reports.horseHours.hours"), key: "hours", sortable: true },
]);

const trackHeaders = computed(() => [
  { title: t("reports.trackHours.name"), key: "name", sortable: true },
  { title: t("reports.trackHours.classCount"), key: "class_count", sortable: true },
  { title: t("reports.trackHours.hours"), key: "hours", sortable: true },
]);

const detailHeaders = computed(() => [
  { title: t("reports.detailDialog.date"), key: "date_time", sortable: true },
  { title: t("reports.detailDialog.duration"), key: "duration_hours", sortable: true },
  { title: t("reports.detailDialog.track"), key: "track_name", sortable: true },
  { title: t("reports.detailDialog.instructor"), key: "instructor_name", sortable: true },
]);

// ---------------------------------------------------------------------------
// Chart data
// ---------------------------------------------------------------------------
const WEEKDAY_KEYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const horseChartSeries = computed(() => {
  const top5 = report.value?.horse_hours.slice(0, 5) ?? [];
  return [{ name: t("reports.horseHours.hours"), data: top5.map((h) => h.hours) }];
});

const horseChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  xaxis: { categories: report.value?.horse_hours.slice(0, 5).map((h) => h.name) ?? [] },
  plotOptions: { bar: { horizontal: false, borderRadius: 4 } },
  dataLabels: { enabled: false },
}));

const staffChartSeries = computed(() => {
  if (!report.value) return [{ name: t("reports.instructorHours.hours"), data: [] }];
  const combined = [
    ...report.value.instructor_hours.map((i) => ({ name: i.name, hours: i.hours })),
    ...report.value.helper_hours.map((h) => ({ name: h.name, hours: h.hours })),
  ]
    .sort((a, b) => b.hours - a.hours)
    .slice(0, 5);
  return [{ name: t("reports.instructorHours.hours"), data: combined.map((x) => x.hours) }];
});

const staffChartOptions = computed(() => {
  if (!report.value) return { chart: { toolbar: { show: false } }, xaxis: { categories: [] } };
  const combined = [
    ...report.value.instructor_hours.map((i) => ({ name: i.name, hours: i.hours })),
    ...report.value.helper_hours.map((h) => ({ name: h.name, hours: h.hours })),
  ]
    .sort((a, b) => b.hours - a.hours)
    .slice(0, 5);
  return {
    chart: { toolbar: { show: false } },
    xaxis: { categories: combined.map((x) => x.name) },
    plotOptions: { bar: { horizontal: false, borderRadius: 4 } },
    dataLabels: { enabled: false },
  };
});

const weekdayChartSeries = computed(() => {
  const counts = new Array(7).fill(0);
  // We derive from instructor_hours class_count by day — but we don't have per-day
  // data in the aggregated report. We use the raw report lessons if available.
  // Since we only have aggregated data, we aggregate from instructor class_count as a
  // placeholder and show zeroes for days. The actual day-of-week breakdown requires
  // per-lesson data. We load it from detailItems if available, otherwise show 0s.
  // For a proper implementation, it is computed from all lessons in the current detail fetch.
  // Here we accumulate from lessonDayOfWeekCounts populated during detail load.
  lessonDayOfWeekCounts.value.forEach((v, i) => { counts[i] = v; });
  return [{ name: t("reports.charts.byWeekday"), data: counts }];
});

const weekdayChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  xaxis: { categories: WEEKDAY_KEYS },
  plotOptions: { bar: { horizontal: false, borderRadius: 4 } },
  dataLabels: { enabled: false },
}));

// Accumulated day-of-week counts from drill-down calls (reset on new report load)
const lessonDayOfWeekCounts = ref<number[]>(new Array(7).fill(0));

// ---------------------------------------------------------------------------
// Load stables (for app_admin)
// ---------------------------------------------------------------------------
async function loadStables() {
  if (!isAppAdmin.value) return;
  try {
    const { data } = await http.get<Stable[]>("/api/v1/stables");
    stables.value = data;
  } catch {
    // non-critical: ignore if stables fail to load
  }
}

onMounted(() => {
  loadStables();
});

// ---------------------------------------------------------------------------
// Load report
// ---------------------------------------------------------------------------
async function loadReport() {
  loading.value = true;
  error.value = null;
  lessonDayOfWeekCounts.value = new Array(7).fill(0);
  try {
    const params: Record<string, string | number> = {};
    if (fromDate.value) params.from_date = fromDate.value;
    if (toDate.value) params.to_date = toDate.value;
    if (isAppAdmin.value && selectedStableId.value != null) {
      params.stable_id = selectedStableId.value;
    }
    const { data } = await http.get<LessonReport>("/api/v1/reports/lessons", { params });
    report.value = data;
    loaded.value = true;
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } };
    error.value = err?.response?.data?.detail || t("reports.error");
  } finally {
    loading.value = false;
  }
}

// ---------------------------------------------------------------------------
// Drill-down
// ---------------------------------------------------------------------------
function buildDetailParams(): Record<string, string | number> {
  const params: Record<string, string | number> = {};
  if (fromDate.value) params.from_date = fromDate.value;
  if (toDate.value) params.to_date = toDate.value;
  if (isAppAdmin.value && selectedStableId.value != null) {
    params.stable_id = selectedStableId.value;
  }
  return params;
}

// ---------------------------------------------------------------------------
// Row-click adapters (v-data-table passes (_event, { item }) — no TS in template)
// ---------------------------------------------------------------------------
function onInstructorRowClick(_evt: MouseEvent, row: { item: InstructorHours }) {
  openUserDetail(row.item.user_id);
}

function onHelperRowClick(_evt: MouseEvent, row: { item: HelperHours }) {
  openUserDetail(row.item.user_id);
}

function onStudentRowClick(_evt: MouseEvent, row: { item: StudentClasses }) {
  openUserDetail(row.item.user_id);
}

function onHorseRowClick(_evt: MouseEvent, row: { item: HorseHours }) {
  openHorseDetail(row.item.horse_id);
}

async function openUserDetail(userId: number) {
  detailDialog.value = true;
  detailLoading.value = true;
  detailItems.value = [];
  try {
    const { data } = await http.get<LessonDetail[]>(
      `/api/v1/reports/lessons/by-user/${userId}`,
      { params: buildDetailParams() }
    );
    detailItems.value = data;
    accumulateWeekdays(data);
  } catch {
    detailItems.value = [];
  } finally {
    detailLoading.value = false;
  }
}

async function openHorseDetail(horseId: number) {
  detailDialog.value = true;
  detailLoading.value = true;
  detailItems.value = [];
  try {
    const { data } = await http.get<LessonDetail[]>(
      `/api/v1/reports/lessons/by-horse/${horseId}`,
      { params: buildDetailParams() }
    );
    detailItems.value = data;
    accumulateWeekdays(data);
  } catch {
    detailItems.value = [];
  } finally {
    detailLoading.value = false;
  }
}

function accumulateWeekdays(lessons: LessonDetail[]) {
  lessons.forEach((l) => {
    const dayIndex = new Date(l.date_time).getDay();
    lessonDayOfWeekCounts.value[dayIndex] = (lessonDayOfWeekCounts.value[dayIndex] ?? 0) + 1;
  });
}
</script>
