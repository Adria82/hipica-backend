<template>
  <v-container fluid>
    <!-- Header -->
    <div class="d-flex align-center mb-4 flex-wrap">

      <!-- IZQUIERDA -->
      <div class="flex-grow-1">
        <h2 class="text-h5">{{ t("lessons.title") }}</h2>
      </div>

      <!-- CENTRO -->
      <div class="d-flex align-center gap-2 justify-center">
        <template v-if="viewMode === 'week'">
          <v-btn variant="tonal" size="small" prepend-icon="mdi-chevron-left" @click="prevWeek">
            {{ t("lessons.prevWeek") }}
          </v-btn>
          <v-btn variant="tonal" size="small" @click="goToday">
            {{ t("lessons.today") }}
          </v-btn>
          <v-btn variant="tonal" size="small" append-icon="mdi-chevron-right" @click="nextWeek">
            {{ t("lessons.nextWeek") }}
          </v-btn>
        </template>
        <template v-else>
          <v-btn variant="tonal" size="small" prepend-icon="mdi-chevron-left" @click="prevMonth">
            {{ t("lessons.prevMonth") }}
          </v-btn>
          <v-btn variant="tonal" size="small" @click="goTodayMonth">
            {{ t("lessons.today") }}
          </v-btn>
          <v-btn variant="tonal" size="small" append-icon="mdi-chevron-right" @click="nextMonth">
            {{ t("lessons.nextMonth") }}
          </v-btn>
        </template>
      </div>

      <!-- PERIODO ACTIVO -->
      <div class="flex-grow-1 d-flex justify-center">
        <span class="text-body-2 font-weight-medium text-medium-emphasis">{{ periodLabel }}</span>
      </div>

      <!-- DERECHA -->
      <div class="flex-grow-1 d-flex justify-end align-center">
        <v-btn-toggle v-model="viewMode" mandatory density="compact" class="mr-2">
          <v-btn value="week" size="small">{{ t("lessons.weekView") }}</v-btn>
          <v-btn value="month" size="small">{{ t("lessons.monthView") }}</v-btn>
        </v-btn-toggle>
        <v-btn
          v-if="canManage"
          color="primary"
          prepend-icon="mdi-plus"
          @click="openCreateDialog(null)"
        >
          {{ t("lessons.addButton") }}
        </v-btn>
      </div>

    </div>

    <!-- Error -->
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

    <!-- Week grid -->
    <v-card v-if="viewMode === 'week'" variant="outlined">
      <div class="week-grid">
        <!-- Day headers -->
        <div
          v-for="day in weekDays"
          :key="day.iso"
          class="week-day-header"
          :class="{ 'today-col': day.isToday }"
        >
          <div class="text-caption font-weight-bold text-uppercase">{{ day.label }}</div>
          <div class="text-h6" :class="day.isToday ? 'text-primary' : ''">{{ day.dayNum }}</div>
        </div>

        <!-- Day cells -->
        <div
          v-for="day in weekDays"
          :key="'cell-' + day.iso"
          class="week-day-cell"
          :class="{ 'today-col': day.isToday }"
          @click="canManage && openCreateDialog(day.iso)"
        >
          <div v-if="lessonsForDay(day.iso).length === 0" class="text-caption text-disabled pa-2">
            {{ t("lessons.noLessonsDay") }}
          </div>
          <v-chip
            v-for="lesson in lessonsForDay(day.iso)"
            :key="lesson.id"
            class="lesson-chip ma-1"
            color="primary"
            variant="tonal"
            size="small"
            @click.stop="openEditDialog(lesson)"
          >
            <v-icon start size="12">mdi-clock-outline</v-icon>
            {{ formatTime(lesson.date_time) }}
            <span v-if="lesson.track_name" class="ml-1 text-caption">({{ lesson.track_name }})</span>
            <br />
            <span class="text-caption">{{ lesson.instructor_email }}</span>
          </v-chip>
        </div>
      </div>
    </v-card>

    <!-- Month grid -->
    <v-card v-if="viewMode === 'month'" variant="outlined">
      <div class="month-grid">
        <!-- Weekday headers -->
        <div
          v-for="header in monthWeekHeaders"
          :key="'mh-' + header"
          class="week-day-header"
        >
          <div class="text-caption font-weight-bold text-uppercase">{{ header }}</div>
        </div>

        <!-- Day cells -->
        <div
          v-for="day in monthDays"
          :key="'m-' + day.iso"
          class="week-day-cell"
          :class="{ 'today-col': day.isToday }"
          :style="!day.isCurrentMonth ? 'opacity: 0.4' : ''"
          @click="canManage && openCreateDialog(day.iso)"
        >
          <div class="text-caption font-weight-medium pa-1">{{ day.dayNum }}</div>
          <v-chip
            v-for="lesson in lessonsForDay(day.iso)"
            :key="lesson.id"
            class="lesson-chip ma-1"
            color="primary"
            variant="tonal"
            size="small"
            @click.stop="openEditDialog(lesson)"
          >
            <v-icon start size="12">mdi-clock-outline</v-icon>
            {{ formatTime(lesson.date_time) }}
            <span v-if="lesson.track_name" class="ml-1 text-caption">({{ lesson.track_name }})</span>
            <br />
            <span class="text-caption">{{ lesson.instructor_email }}</span>
          </v-chip>
        </div>
      </div>
    </v-card>

    <!-- Loading overlay -->
    <div v-if="loading" class="d-flex justify-center mt-6">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Create / Edit dialog -->
    <v-dialog v-model="dialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingLesson ? t("lessons.dialog.titleEdit") : t("lessons.dialog.titleCreate") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-row dense>
            <v-col v-if="isAppAdmin" cols="12">
              <v-select
                v-model="form.stable_id"
                :items="stables"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.stable')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.start_date"
                :label="t('lessons.dialog.startDate')"
                type="date"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.start_time"
                :label="t('lessons.dialog.startTime')"
                type="time"
                step="300"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.end_date"
                :label="t('lessons.dialog.endDate')"
                type="date"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.end_time_input"
                :label="t('lessons.dialog.endTimeLabel')"
                type="time"
                step="300"
                variant="outlined"
                density="compact"
                :error-messages="dateTimeError"
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-select
                v-model="form.instructor_id"
                :items="instructorOptions"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.instructor')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.helper_id"
                :items="helperOptions"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.helper')"
                variant="outlined"
                density="compact"
                clearable
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-select
                v-model="form.track_id"
                :items="trackOptionsWithNone"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.track')"
                variant="outlined"
                density="compact"
                clearable
              />
            </v-col>

            <v-col cols="12">
              <v-select
                v-model="form.horse_ids"
                :items="horseOptions"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.horses')"
                variant="outlined"
                density="compact"
                multiple
                chips
                closable-chips
              />
            </v-col>

            <v-col cols="12">
              <v-select
                v-model="form.student_ids"
                :items="studentOptions"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.students')"
                variant="outlined"
                density="compact"
                multiple
                chips
                closable-chips
              />
            </v-col>

            <!-- Asignación alumno-caballo: visible solo cuando hay alumnos seleccionados -->
            <v-col v-if="studentHorsePairs.length > 0" cols="12">
              <div class="text-caption font-weight-medium text-medium-emphasis mb-2">
                {{ t("lessons.dialog.studentHorseAssignment") }}
              </div>
              <v-row
                v-for="pair in studentHorsePairs"
                :key="pair.student_id"
                dense
                class="align-center"
              >
                <v-col cols="5" class="text-body-2">
                  {{ students.find((s) => s.id === pair.student_id)?.name ?? pair.student_id }}
                </v-col>
                <v-col cols="7">
                  <v-select
                    v-model="pair.horse_id"
                    :items="[
                      { id: null, name: t('lessons.dialog.noHorse') },
                      ...horseOptions.filter((h) => form.horse_ids.includes(h.id)),
                    ]"
                    item-title="name"
                    item-value="id"
                    variant="outlined"
                    density="compact"
                    hide-details
                    :error="!!duplicateHorseError && pair.horse_id !== null && studentHorsePairs.filter((p) => p.horse_id === pair.horse_id).length > 1"
                  />
                </v-col>
              </v-row>
            </v-col>

            <v-col v-if="duplicateHorseError" cols="12">
              <v-alert type="error" variant="tonal" density="compact">
                {{ duplicateHorseError }}
              </v-alert>
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.description"
                :label="t('lessons.dialog.description')"
                variant="outlined"
                density="compact"
                rows="2"
                auto-grow
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-btn
            v-if="editingLesson"
            color="error"
            variant="text"
            :disabled="saving"
            @click="confirmDeleteDialog = true"
          >
            {{ t("lessons.dialog.delete") }}
          </v-btn>
          <v-spacer />
          <v-btn variant="text" :disabled="saving" @click="dialog = false">
            {{ t("lessons.dialog.cancel") }}
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="save">
            {{ saving ? t("lessons.dialog.saving") : t("lessons.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirm delete dialog -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400">
      <v-card>
        <v-card-text class="pa-4">{{ t("lessons.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="confirmDeleteDialog = false">
            {{ t("lessons.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteLesson">
            {{ t("lessons.dialog.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000" location="top">
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "@/api/http";
import { canManage, isAppAdmin } from "@/auth/profile";
import type { Lesson, LessonCreate, LessonUpdate, Track, Horse, UserRead, Stable, StudentHorsePair } from "@/types/api";

const { t } = useI18n();

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const lessons = ref<Lesson[]>([]);
const tracks = ref<Track[]>([]);
const horses = ref<Horse[]>([]);
const students = ref<UserRead[]>([]);
const users = ref<UserRead[]>([]);
const stables = ref<Stable[]>([]);

const loading = ref(false);
const error = ref<string | null>(null);
const saving = ref(false);
const deleting = ref(false);

const dialog = ref(false);
const confirmDeleteDialog = ref(false);
const editingLesson = ref<Lesson | null>(null);

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref<"success" | "error">("success");

// ---------------------------------------------------------------------------
// View mode
// ---------------------------------------------------------------------------
const viewMode = ref<"week" | "month">("week");

// ---------------------------------------------------------------------------
// Week navigation
// ---------------------------------------------------------------------------
function getMonday(d: Date): Date {
  const date = new Date(d);
  const day = date.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  date.setDate(date.getDate() + diff);
  date.setHours(0, 0, 0, 0);
  return date;
}

const weekStart = ref(getMonday(new Date()));

const weekDays = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart.value);
    d.setDate(d.getDate() + i);
    const iso = d.toISOString().slice(0, 10);
    return {
      iso,
      label: d.toLocaleDateString(undefined, { weekday: "short" }),
      dayNum: d.getDate(),
      isToday: d.getTime() === today.getTime(),
    };
  });
});

function prevWeek() {
  const d = new Date(weekStart.value);
  d.setDate(d.getDate() - 7);
  weekStart.value = d;
}

function nextWeek() {
  const d = new Date(weekStart.value);
  d.setDate(d.getDate() + 7);
  weekStart.value = d;
}

function goToday() {
  weekStart.value = getMonday(new Date());
}

// ---------------------------------------------------------------------------
// Month navigation
// ---------------------------------------------------------------------------
const monthStart = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1));

function prevMonth() {
  const d = new Date(monthStart.value);
  d.setMonth(d.getMonth() - 1);
  monthStart.value = d;
}

function nextMonth() {
  const d = new Date(monthStart.value);
  d.setMonth(d.getMonth() + 1);
  monthStart.value = d;
}

function goTodayMonth() {
  monthStart.value = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
}

// Weekday header labels derived from a fixed reference week (Mon–Sun)
const monthWeekHeaders = computed(() => {
  const monday = getMonday(new Date());
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(d.getDate() + i);
    return d.toLocaleDateString(undefined, { weekday: "short" });
  });
});

const monthDays = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const year = monthStart.value.getFullYear();
  const month = monthStart.value.getMonth();

  // First day of the month
  const firstDay = new Date(year, month, 1);
  // Last day of the month
  const lastDay = new Date(year, month + 1, 0);

  // Day of week for first day (0=Sun..6=Sat), convert to Mon-based (0=Mon..6=Sun)
  const firstWeekDay = (firstDay.getDay() + 6) % 7;
  // Day of week for last day, Mon-based
  const lastWeekDay = (lastDay.getDay() + 6) % 7;

  // Total cells: pad start + month days + pad end to complete last row
  const paddingStart = firstWeekDay;
  const paddingEnd = lastWeekDay === 6 ? 0 : 6 - lastWeekDay;

  const days: { iso: string; dayNum: number; isToday: boolean; isCurrentMonth: boolean }[] = [];

  // Days from previous month
  for (let i = paddingStart - 1; i >= 0; i--) {
    const d = new Date(year, month, -i);
    days.push({
      iso: d.toISOString().slice(0, 10),
      dayNum: d.getDate(),
      isToday: d.getTime() === today.getTime(),
      isCurrentMonth: false,
    });
  }

  // Days of current month
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const d = new Date(year, month, i);
    days.push({
      iso: d.toISOString().slice(0, 10),
      dayNum: d.getDate(),
      isToday: d.getTime() === today.getTime(),
      isCurrentMonth: true,
    });
  }

  // Days from next month
  for (let i = 1; i <= paddingEnd; i++) {
    const d = new Date(year, month + 1, i);
    days.push({
      iso: d.toISOString().slice(0, 10),
      dayNum: d.getDate(),
      isToday: d.getTime() === today.getTime(),
      isCurrentMonth: false,
    });
  }

  return days;
});

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------
function lessonsForDay(iso: string): Lesson[] {
  return lessons.value.filter((l) => l.date_time.slice(0, 10) === iso);
}

function formatTime(dt: string): string {
  return new Date(dt).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

// ---------------------------------------------------------------------------
// Period label (centro del header)
// ---------------------------------------------------------------------------
const periodLabel = computed(() => {
  if (viewMode.value === "week") {
    const end = new Date(weekStart.value);
    end.setDate(end.getDate() + 6);
    const shortOpts: Intl.DateTimeFormatOptions = { day: "numeric", month: "short" };
    const start = weekStart.value.toLocaleDateString(undefined, shortOpts);
    const endStr = end.toLocaleDateString(undefined, { ...shortOpts, year: "numeric" });
    return `${start} – ${endStr}`;
  } else {
    return monthStart.value.toLocaleDateString(undefined, { month: "long", year: "numeric" });
  }
});

// ---------------------------------------------------------------------------
// Select options
// ---------------------------------------------------------------------------
const instructorOptions = computed(() => users.value.filter((u) => u.role === "monitor"));
const helperOptions = computed(() => users.value.filter((u) => u.role === "assistant"));
const trackOptionsWithNone = computed(() => tracks.value.filter((tr) => tr.is_active));
const horseOptions = computed(() => horses.value.filter((h) => h.is_active));
const studentOptions = computed(() => students.value.filter((s) => s.is_active));

// Helpers para componer/descomponer datetime-local
function toDateTimeLocal(iso: string): { date: string; time: string } {
  const s = iso.slice(0, 16); // "YYYY-MM-DDTHH:MM"
  return { date: s.slice(0, 10), time: s.slice(11) };
}

function fromDateAndTime(date: string, time: string): string {
  if (!date || !time) return "";
  return `${date}T${time}`;
}

// Validación: fin no puede ser anterior al inicio
const dateTimeError = computed(() => {
  const start = fromDateAndTime(form.value.start_date, form.value.start_time);
  const end   = fromDateAndTime(form.value.end_date, form.value.end_time_input);
  if (!start || !end) return "";
  return new Date(end) <= new Date(start) ? t("lessons.dialog.endBeforeStart") : "";
});

// Validación: no asignar el mismo caballo a dos alumnos distintos
const duplicateHorseError = computed(() => {
  const assigned = studentHorsePairs.value
    .map((p) => p.horse_id)
    .filter((id): id is number => id !== null);
  const hasDuplicate = assigned.length !== new Set(assigned).size;
  return hasDuplicate ? t("lessons.dialog.duplicateHorse") : "";
});

// Computed: datetime ISO strings para los payloads
const computedDateTime = computed(() =>
  fromDateAndTime(form.value.start_date, form.value.start_time)
);
const computedEndTime = computed(() =>
  fromDateAndTime(form.value.end_date, form.value.end_time_input) || null
);

// ---------------------------------------------------------------------------
// Form
// ---------------------------------------------------------------------------
interface LessonForm {
  start_date: string;
  start_time: string;
  end_date: string;
  end_time_input: string;
  instructor_id: number | null;
  helper_id: number | null;
  track_id: number | null;
  horse_ids: number[];
  student_ids: number[];
  description: string;
  stable_id: number | null;
}

function emptyForm(dateIso?: string | null): LessonForm {
  return {
    start_date: dateIso ?? "",
    start_time: "09:00",
    end_date: dateIso ?? "",
    end_time_input: "",
    instructor_id: null,
    helper_id: null,
    track_id: null,
    horse_ids: [],
    student_ids: [],
    description: "",
    stable_id: null,
  };
}

const form = ref<LessonForm>(emptyForm());

// Pairs alumno-caballo gestionados en el diálogo
const studentHorsePairs = ref<StudentHorsePair[]>([]);

// Cuando cambia la lista de alumnos seleccionados, recalcula los pares
// preservando asignaciones existentes y eliminando las de alumnos deseleccionados
watch(
  () => form.value.student_ids,
  (newIds) => {
    const existing = new Map(studentHorsePairs.value.map((p) => [p.student_id, p.horse_id]));
    studentHorsePairs.value = newIds.map((id) => ({
      student_id: id,
      horse_id: existing.has(id) ? existing.get(id)! : null,
    }));
  },
);

// Cuando cambia la lista de caballos, limpia asignaciones a caballos ya no disponibles
watch(
  () => form.value.horse_ids,
  (newHorseIds) => {
    studentHorsePairs.value = studentHorsePairs.value.map((p: StudentHorsePair) => ({
      ...p,
      horse_id: p.horse_id !== null && newHorseIds.includes(p.horse_id) ? p.horse_id : null,
    }));
  },
);

function openCreateDialog(dateIso: string | null) {
  editingLesson.value = null;
  form.value = emptyForm(dateIso);
  studentHorsePairs.value = [];
  dialog.value = true;
}

function openEditDialog(lesson: Lesson) {
  editingLesson.value = lesson;
  const horseIds = horses.value
    .filter((h) => lesson.horse_names.includes(h.name))
    .map((h) => h.id);
  const studentIds = students.value
    .filter((s) => lesson.student_names.includes(s.name))
    .map((s) => s.id);
  const startParts = toDateTimeLocal(lesson.date_time);
  const endParts   = lesson.end_time ? toDateTimeLocal(lesson.end_time) : { date: "", time: "" };
  form.value = {
    start_date:     startParts.date,
    start_time:     startParts.time,
    end_date:       endParts.date,
    end_time_input: endParts.time,
    instructor_id: lesson.instructor_id,
    helper_id: lesson.helper_id,
    track_id: lesson.track_id,
    horse_ids: horseIds,
    student_ids: studentIds,
    description: lesson.description ?? "",
    stable_id: null,
  };
  // Poblar pares desde los datos de la lección; si no hay, crear pares vacíos
  if (lesson.student_horse_pairs && lesson.student_horse_pairs.length > 0) {
    studentHorsePairs.value = lesson.student_horse_pairs.map((p) => ({ ...p }));
  } else {
    studentHorsePairs.value = studentIds.map((id) => ({ student_id: id, horse_id: null }));
  }
  dialog.value = true;
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------
async function loadAll() {
  loading.value = true;
  error.value = null;
  try {
    const requests: Promise<any>[] = [
      http.get<Lesson[]>("/api/v1/lessons"),
      http.get<Track[]>("/api/v1/tracks"),
      http.get<Horse[]>("/api/v1/horses"),
      http.get<UserRead[]>("/api/v1/users?role=client"),
      http.get<UserRead[]>("/api/v1/users"),
    ];

    if (isAppAdmin.value) {
      requests.push(http.get<Stable[]>("/api/v1/stables"));
    }

    const [lessonsRes, tracksRes, horsesRes, studentsRes, usersRes, stablesRes] =
      await Promise.all(requests);

    lessons.value = lessonsRes.data;
    tracks.value = tracksRes.data;
    horses.value = horsesRes.data;
    students.value = studentsRes.data;
    users.value = usersRes.data;
    if (stablesRes) {
      stables.value = stablesRes.data;
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("lessons.error");
  } finally {
    loading.value = false;
  }
}

async function save() {
  if (!form.value.instructor_id || !form.value.start_date || !form.value.start_time) return;
  if (dateTimeError.value) { showSnackbar(dateTimeError.value, "error"); return; }
  if (duplicateHorseError.value) { showSnackbar(duplicateHorseError.value, "error"); return; }
  saving.value = true;
  try {
    if (editingLesson.value) {
      const payload: LessonUpdate = {
        date_time: computedDateTime.value,
        end_time: computedEndTime.value,
        instructor_id: form.value.instructor_id ?? undefined,
        helper_id: form.value.helper_id,
        track_id: form.value.track_id,
        description: form.value.description || null,
        horse_ids: form.value.horse_ids,
        student_horse_pairs: studentHorsePairs.value,
      };
      await http.put(`/api/v1/lessons/${editingLesson.value.id}`, payload);
    } else {
      const payload: LessonCreate = {
        date_time: computedDateTime.value,
        end_time: computedEndTime.value,
        instructor_id: form.value.instructor_id!,
        helper_id: form.value.helper_id,
        track_id: form.value.track_id,
        description: form.value.description || null,
        horse_ids: form.value.horse_ids,
        student_horse_pairs: studentHorsePairs.value,
        ...(isAppAdmin.value && form.value.stable_id ? { stable_id: form.value.stable_id } : {}),
      };
      await http.post("/api/v1/lessons/", payload);
    }
    dialog.value = false;
    showSnackbar(t("lessons.saveSuccess"), "success");
    await loadAll();
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("lessons.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteLesson() {
  if (!editingLesson.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/lessons/${editingLesson.value.id}`);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("lessons.deleteSuccess"), "success");
    await loadAll();
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("lessons.deleteError"), "error");
  } finally {
    deleting.value = false;
  }
}

function showSnackbar(text: string, color: "success" | "error") {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

onMounted(loadAll);
</script>

<style scoped>
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: auto 1fr;
  min-height: 400px;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.week-day-header {
  padding: 8px;
  text-align: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(0, 0, 0, 0.02);
}

.week-day-header:last-child {
  border-right: none;
}

.week-day-cell {
  padding: 4px;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  min-height: 120px;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex-wrap: wrap;
}

.week-day-cell:last-child {
  border-right: none;
}

.week-day-cell:hover {
  background: rgba(var(--v-theme-primary), 0.04);
}

.today-col {
  background: rgba(var(--v-theme-primary), 0.06);
}

.lesson-chip {
  cursor: pointer;
  max-width: 100%;
  white-space: normal;
  height: auto !important;
  padding: 4px 8px !important;
}
</style>
