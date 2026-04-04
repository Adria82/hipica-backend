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

      </v-row>

      <!-- Weekday chart row with filters -->
      <v-row v-if="!isEmpty">
        <v-col cols="12">
          <v-card variant="outlined" class="mb-4 pa-2">
            <v-card-title class="text-subtitle-2 pa-2 d-flex align-center flex-wrap ga-2">
              {{ t("reports.charts.byWeekday") }}
              <v-spacer />
              <!-- Filter type -->
              <v-select
                v-model="weekdayFilterType"
                :items="weekdayFilterTypeItems"
                density="compact"
                variant="outlined"
                hide-details
                style="max-width: 200px"
              />
              <!-- Filter value (entity selector) -->
              <v-select
                v-if="weekdayFilterType !== 'all'"
                v-model="weekdayFilterId"
                :items="weekdayFilterOptions"
                item-title="name"
                item-value="id"
                density="compact"
                variant="outlined"
                hide-details
                clearable
                style="max-width: 200px"
              />
            </v-card-title>
            <VueApexCharts
              type="bar"
              height="240"
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
import { ref, computed, onMounted, watch } from "vue";
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

// ---------------------------------------------------------------------------
// Gráfica de clases por día de la semana — calculada desde el informe global
// ---------------------------------------------------------------------------
// Estado del filtro de la gráfica de días de la semana
type WeekdayFilterType = "all" | "horse" | "student" | "instructor" | "helper" | "track";
const weekdayFilterType = ref<WeekdayFilterType>("all");
const weekdayFilterId = ref<number | null>(null);

// Detalle de clases del período (cargado al generar informe, reutilizado por la gráfica)
const allLessonsDetail = ref<import("@/types/api").LessonDetail[]>([]);

const weekdayFilterTypeItems = computed(() => [
  { title: t("reports.charts.weekdayFilterAll"),        value: "all"        },
  { title: t("reports.charts.weekdayFilterHorse"),      value: "horse"      },
  { title: t("reports.charts.weekdayFilterStudent"),    value: "student"    },
  { title: t("reports.charts.weekdayFilterInstructor"), value: "instructor" },
  { title: t("reports.charts.weekdayFilterHelper"),     value: "helper"     },
  { title: t("reports.charts.weekdayFilterTrack"),      value: "track"      },
]);

const weekdayFilterOptions = computed((): { id: number; name: string }[] => {
  if (!report.value) return [];
  switch (weekdayFilterType.value) {
    case "horse":      return report.value.horse_hours.map((h) => ({ id: h.horse_id, name: h.name }));
    case "student":    return report.value.student_classes.map((s) => ({ id: s.user_id, name: s.name }));
    case "instructor": return report.value.instructor_hours.map((i) => ({ id: i.user_id, name: i.name }));
    case "helper":     return report.value.helper_hours.map((h) => ({ id: h.user_id, name: h.name }));
    case "track":      return report.value.track_hours.map((tr) => ({ id: tr.track_id, name: tr.name }));
    default:           return [];
  }
});

// Al cambiar el tipo de filtro, se reinicia el valor seleccionado
watch(weekdayFilterType, () => { weekdayFilterId.value = null; });

const weekdayChartSeries = computed(() => {
  const counts = new Array(7).fill(0);
  const lessons = allLessonsDetail.value;
  lessons.forEach((l) => {
    const dayIndex = new Date(l.date_time).getDay();
    counts[dayIndex] = (counts[dayIndex] ?? 0) + 1;
  });
  return [{ name: t("reports.charts.byWeekday"), data: counts }];
});

const weekdayChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  xaxis: { categories: WEEKDAY_KEYS },
  plotOptions: { bar: { horizontal: false, borderRadius: 4 } },
  dataLabels: { enabled: false },
}));

// ---------------------------------------------------------------------------
// Cargar hípicas (solo app_admin)
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
  allLessonsDetail.value = [];
  weekdayFilterType.value = "all";
  weekdayFilterId.value = null;
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
    // Carga el detalle de clases para la gráfica de días de la semana
    loadWeekdayChartData(params);
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } };
    error.value = err?.response?.data?.detail || t("reports.error");
  } finally {
    loading.value = false;
  }
}

async function loadWeekdayChartData(params: Record<string, string | number>, userId?: number, horseId?: number) {
  try {
    let lessons: LessonDetail[] = [];
    if (userId != null) {
      const { data } = await http.get<LessonDetail[]>(`/api/v1/reports/lessons/by-user/${userId}`, { params });
      lessons = data;
    } else if (horseId != null) {
      const { data } = await http.get<LessonDetail[]>(`/api/v1/reports/lessons/by-horse/${horseId}`, { params });
      lessons = data;
    } else {
      // Sin filtro: carga todas las clases del período agrupando por instructor (deduplicadas)
      if (report.value) {
        const peticiones = report.value.instructor_hours.map((i: InstructorHours) =>
          http.get<LessonDetail[]>(`/api/v1/reports/lessons/by-user/${i.user_id}`, { params })
            .then((r: { data: LessonDetail[] }) => r.data)
            .catch(() => [] as LessonDetail[])
        );
        const resultados: LessonDetail[][] = await Promise.all(peticiones);
        // Deduplicar por lesson_id
        const vistos = new Set<number>();
        ([] as LessonDetail[]).concat(...resultados).forEach((l: LessonDetail) => {
          if (!vistos.has(l.lesson_id)) { vistos.add(l.lesson_id); lessons.push(l); }
        });
      }
    }
    allLessonsDetail.value = lessons;
  } catch {
    allLessonsDetail.value = [];
  }
}

// Al cambiar el filtro de la gráfica, recarga los datos de días de la semana
watch([weekdayFilterType, weekdayFilterId], ([tipo, id]) => {
  const params = buildDetailParams();
  if (tipo === "all") {
    loadWeekdayChartData(params);
  } else if (tipo === "horse" && id != null) {
    loadWeekdayChartData(params, undefined, id);
  } else if (id != null) {
    loadWeekdayChartData(params, id, undefined);
  } else {
    // Tipo cambiado pero sin entidad seleccionada aún — vaciar
    allLessonsDetail.value = [];
  }
});

// ---------------------------------------------------------------------------
// Detalle por registro (drill-down)
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
// Adaptadores de clic en filas (v-data-table pasa (_event, { item }))
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
  } catch {
    detailItems.value = [];
  } finally {
    detailLoading.value = false;
  }
}
</script>
