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
              :items="instructorRows"
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
              :items="helperRows"
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
              :items="studentRows"
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
              @click:row="onTrackRowClick"
              style="cursor: pointer"
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
              <!-- Selector de entidades con multiselección -->
              <v-select
                v-if="weekdayFilterType !== 'all'"
                v-model="weekdayFilterIds"
                :items="weekdayFilterOptions"
                item-title="name"
                item-value="id"
                density="compact"
                variant="outlined"
                hide-details
                multiple
                chips
                closable-chips
                style="max-width: 280px"
              >
                <template #prepend-item>
                  <v-list-item
                    :title="allWeekdayFiltersSelected ? t('reports.charts.unselectAll') : t('reports.charts.selectAll')"
                    @click="toggleAllWeekdayFilters"
                  >
                    <template #prepend>
                      <v-checkbox-btn
                        :model-value="allWeekdayFiltersSelected"
                        :indeterminate="someWeekdayFiltersSelected && !allWeekdayFiltersSelected"
                      />
                    </template>
                  </v-list-item>
                  <v-divider class="mb-1" />
                </template>
              </v-select>
            </v-card-title>
            <VueApexCharts
              :key="`weekday-${weekdayFilterType}-${weekdayFilterIds.join(',')}-${allLessonsDetailMap.size}`"
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
import type { LessonReport, LessonDetail, InstructorHours, HelperHours, StudentClasses, HorseHours, TrackHours, Stable } from "@/types/api";

const { t, locale } = useI18n();

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
// Datos enriquecidos con nombre completo para tablas
// ---------------------------------------------------------------------------
const instructorRows = computed(() =>
  report.value?.instructor_hours.map((i) => ({ ...i, fullName: userFullName(i) })) ?? []
);
const helperRows = computed(() =>
  report.value?.helper_hours.map((h) => ({ ...h, fullName: userFullName(h) })) ?? []
);
const studentRows = computed(() =>
  report.value?.student_classes.map((s) => ({ ...s, fullName: userFullName(s) })) ?? []
);

// ---------------------------------------------------------------------------
// Table headers
// ---------------------------------------------------------------------------
const instructorHeaders = computed(() => [
  { title: t("reports.instructorHours.name"), key: "fullName", sortable: true },
  { title: t("reports.instructorHours.hours"), key: "hours", sortable: true },
  { title: t("reports.instructorHours.classCount"), key: "class_count", sortable: true },
]);

const helperHeaders = computed(() => [
  { title: t("reports.helperHours.name"), key: "fullName", sortable: true },
  { title: t("reports.helperHours.hours"), key: "hours", sortable: true },
  { title: t("reports.helperHours.classCount"), key: "class_count", sortable: true },
]);

const studentHeaders = computed(() => [
  { title: t("reports.studentClasses.name"), key: "fullName", sortable: true },
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
// Etiquetas de día de la semana en el idioma activo, comenzando por lunes
// Se usan como categorías del eje X de la gráfica de días
const weekdayLabels = computed(() => {
  // 2024-01-01 es lunes — sirve como ancla para generar 7 etiquetas Mon→Sun
  const anchor = new Date(2024, 0, 1);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(anchor);
    d.setDate(d.getDate() + i);
    return d.toLocaleDateString(locale.value, { weekday: "short" });
  });
});

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
    ...report.value.instructor_hours.map((i) => ({ name: userFullName(i), hours: i.hours })),
    ...report.value.helper_hours.map((h) => ({ name: userFullName(h), hours: h.hours })),
  ]
    .sort((a, b) => b.hours - a.hours)
    .slice(0, 5);
  return [{ name: t("reports.instructorHours.hours"), data: combined.map((x) => x.hours) }];
});

const staffChartOptions = computed(() => {
  if (!report.value) return { chart: { toolbar: { show: false } }, xaxis: { categories: [] } };
  const combined = [
    ...report.value.instructor_hours.map((i) => ({ name: userFullName(i), hours: i.hours })),
    ...report.value.helper_hours.map((h) => ({ name: userFullName(h), hours: h.hours })),
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
// Multiselección de entidades (IDs seleccionados)
const weekdayFilterIds = ref<number[]>([]);

// Detalle de clases del período agrupado por entidad: entityId → LessonDetail[]
// En modo "all" se usa la clave 0
const allLessonsDetailMap = ref<Map<number, LessonDetail[]>>(new Map());

const weekdayFilterTypeItems = computed(() => [
  { title: t("reports.charts.weekdayFilterAll"),        value: "all"        },
  { title: t("reports.charts.weekdayFilterHorse"),      value: "horse"      },
  { title: t("reports.charts.weekdayFilterStudent"),    value: "student"    },
  { title: t("reports.charts.weekdayFilterInstructor"), value: "instructor" },
  { title: t("reports.charts.weekdayFilterHelper"),     value: "helper"     },
  { title: t("reports.charts.weekdayFilterTrack"),      value: "track"      },
]);

function userFullName(u: { name: string; apellidos?: string | null }): string {
  return u.apellidos ? `${u.name} ${u.apellidos}` : u.name;
}

const weekdayFilterOptions = computed((): { id: number; name: string }[] => {
  if (!report.value) return [];
  switch (weekdayFilterType.value) {
    case "horse":      return report.value.horse_hours.map((h) => ({ id: h.horse_id, name: h.name }));
    case "student":    return report.value.student_classes.map((s) => ({ id: s.user_id, name: userFullName(s) }));
    case "instructor": return report.value.instructor_hours.map((i) => ({ id: i.user_id, name: userFullName(i) }));
    case "helper":     return report.value.helper_hours.map((h) => ({ id: h.user_id, name: userFullName(h) }));
    case "track":      return report.value.track_hours.map((tr) => ({ id: tr.track_id, name: tr.name }));
    default:           return [];
  }
});

const allWeekdayFilterOptionIds = computed(() => weekdayFilterOptions.value.map((option) => option.id));

const allWeekdayFiltersSelected = computed(() =>
  allWeekdayFilterOptionIds.value.length > 0 &&
  allWeekdayFilterOptionIds.value.every((id) => weekdayFilterIds.value.includes(id))
);

const someWeekdayFiltersSelected = computed(() => weekdayFilterIds.value.length > 0);

function toggleAllWeekdayFilters() {
  weekdayFilterIds.value = allWeekdayFiltersSelected.value ? [] : [...allWeekdayFilterOptionIds.value];
}

// Al cambiar el tipo de filtro, se reinicia la selección de entidades
watch(weekdayFilterType, () => { weekdayFilterIds.value = []; });

// Colores para las series de la gráfica
const CHART_COLORS = [
  "#008FFB","#00E396","#FEB019","#FF4560","#775DD0",
  "#546E7A","#26a69a","#D10CE8","#F86624","#2b908f",
];

const weekdayChartSeries = computed(() => {
  // Convierte el índice JS (0=Dom,...,6=Sáb) a índice lunes-primero (0=Lun,...,6=Dom)
  const toMondayFirst = (jsDay: number) => (jsDay + 6) % 7;

  if (weekdayFilterType.value === "all" || weekdayFilterIds.value.length === 0) {
    // Serie única con todas las clases
    const counts = new Array(7).fill(0);
    const lessons = allLessonsDetailMap.value.get(0) ?? [];
    lessons.forEach((l) => {
      const dayIndex = toMondayFirst(new Date(l.date_time).getDay());
      counts[dayIndex] = (counts[dayIndex] ?? 0) + 1;
    });
    return [{ name: t("reports.charts.byWeekday"), data: counts }];
  }
  // Una serie por entidad seleccionada, con nombre de la entidad
  return weekdayFilterIds.value.map((id, idx) => {
    const counts = new Array(7).fill(0);
    const lessons = allLessonsDetailMap.value.get(id) ?? [];
    lessons.forEach((l) => {
      const dayIndex = toMondayFirst(new Date(l.date_time).getDay());
      counts[dayIndex] = (counts[dayIndex] ?? 0) + 1;
    });
    const opcion = weekdayFilterOptions.value.find((o) => o.id === id);
    return {
      name: opcion?.name ?? String(id),
      data: counts,
      color: CHART_COLORS[idx % CHART_COLORS.length],
    };
  });
});

const weekdayChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, stacked: false },
  xaxis: { categories: weekdayLabels.value },
  plotOptions: { bar: { horizontal: false, borderRadius: 4 } },
  dataLabels: { enabled: false },
  tooltip: {
    y: {
      formatter: (val: number) => `${val} ${t("reports.charts.classes")}`,
    },
  },
}));

function formatDateInput(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getPreviousMonthRange() {
  const today = new Date();
  const firstDayPreviousMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const lastDayPreviousMonth = new Date(today.getFullYear(), today.getMonth(), 0);

  return {
    from: formatDateInput(firstDayPreviousMonth),
    to: formatDateInput(lastDayPreviousMonth),
  };
}

function ensureDefaultReportDates() {
  if (fromDate.value || toDate.value) return;

  const previousMonthRange = getPreviousMonthRange();
  fromDate.value = previousMonthRange.from;
  toDate.value = previousMonthRange.to;
}

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
  ensureDefaultReportDates();
  loadStables();
});

// ---------------------------------------------------------------------------
// Load report
// ---------------------------------------------------------------------------
async function loadReport() {
  ensureDefaultReportDates();
  loading.value = true;
  error.value = null;
  allLessonsDetailMap.value = new Map();
  weekdayFilterType.value = "all";
  weekdayFilterIds.value = [];
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
    loadAllLessonsForChart(params);
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } };
    error.value = err?.response?.data?.detail || t("reports.error");
  } finally {
    loading.value = false;
  }
}

// Carga datos de clases para una entidad concreta y los guarda en el mapa por entityKey
async function loadEntityLessons(entityKey: number, url: string, params: Record<string, string | number>) {
  try {
    const { data } = await http.get<LessonDetail[]>(url, { params });
    const mapa = new Map(allLessonsDetailMap.value);
    mapa.set(entityKey, data);
    allLessonsDetailMap.value = mapa;
  } catch {
    // Si falla, deja la entrada vacía
    const mapa = new Map(allLessonsDetailMap.value);
    mapa.set(entityKey, []);
    allLessonsDetailMap.value = mapa;
  }
}

// Carga todas las clases del período agrupando por instructores (clave 0)
async function loadAllLessonsForChart(params: Record<string, string | number>) {
  if (!report.value) return;
  const peticiones = report.value.instructor_hours.map((i: InstructorHours) =>
    http.get<LessonDetail[]>(`/api/v1/reports/lessons/by-user/${i.user_id}`, { params })
      .then((r: { data: LessonDetail[] }) => r.data)
      .catch(() => [] as LessonDetail[])
  );
  const resultados: LessonDetail[][] = await Promise.all(peticiones);
  // Deduplicar por lesson_id
  const vistos = new Set<number>();
  const todas: LessonDetail[] = [];
  ([] as LessonDetail[]).concat(...resultados).forEach((l: LessonDetail) => {
    if (!vistos.has(l.lesson_id)) { vistos.add(l.lesson_id); todas.push(l); }
  });
  const mapa = new Map(allLessonsDetailMap.value);
  mapa.set(0, todas);
  allLessonsDetailMap.value = mapa;
}

// Al cambiar la selección de entidades, carga los datos que falten en el mapa
watch(weekdayFilterIds, (ids) => {
  const params = buildDetailParams();
  if (ids.length === 0) return;
  const tipo = weekdayFilterType.value;
  ids.forEach((id) => {
    if (allLessonsDetailMap.value.has(id)) return; // ya cargado
    let url = "";
    if (tipo === "horse") url = `/api/v1/reports/lessons/by-horse/${id}`;
    else if (tipo === "track") url = `/api/v1/reports/lessons/by-track/${id}`;
    else url = `/api/v1/reports/lessons/by-user/${id}`; // student / instructor / helper
    loadEntityLessons(id, url, params);
  });
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

function onTrackRowClick(_evt: MouseEvent, row: { item: TrackHours }) {
  openTrackDetail(row.item.track_id);
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

async function openTrackDetail(trackId: number) {
  detailDialog.value = true;
  detailLoading.value = true;
  detailItems.value = [];
  try {
    const { data } = await http.get<LessonDetail[]>(
      `/api/v1/reports/lessons/by-track/${trackId}`,
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
