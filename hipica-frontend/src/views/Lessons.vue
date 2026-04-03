<template>
  <v-container fluid>
    <!-- Header -->
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <h2 class="text-h5">{{ t("lessons.title") }}</h2>
      <div class="d-flex align-center gap-2 flex-wrap">
        <v-btn variant="tonal" size="small" prepend-icon="mdi-chevron-left" @click="prevWeek">
          {{ t("lessons.prevWeek") }}
        </v-btn>
        <v-btn variant="tonal" size="small" @click="goToday">
          {{ t("lessons.today") }}
        </v-btn>
        <v-btn variant="tonal" size="small" append-icon="mdi-chevron-right" @click="nextWeek">
          {{ t("lessons.nextWeek") }}
        </v-btn>
        <span class="text-body-2 text-medium-emphasis ml-2">
          {{ t("lessons.weekOf") }} {{ weekLabel }}
        </span>
        <v-spacer />
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
    <v-card variant="outlined">
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
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.date_time"
                :label="t('lessons.dialog.dateTime')"
                type="datetime-local"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.end_time"
                :label="t('lessons.dialog.endTime')"
                type="datetime-local"
                variant="outlined"
                density="compact"
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-select
                v-model="form.instructor_id"
                :items="userOptions"
                item-title="email"
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
                :items="userOptionsWithNone"
                item-title="email"
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
                v-model="form.client_ids"
                :items="clientOptions"
                item-title="name"
                item-value="id"
                :label="t('lessons.dialog.clients')"
                variant="outlined"
                density="compact"
                multiple
                chips
                closable-chips
              />
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
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "@/api/http";
import { canManage } from "@/auth/profile";
import type { Lesson, LessonCreate, LessonUpdate, Track, Horse, Client, UserRead } from "@/types/api";

const { t } = useI18n();

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const lessons = ref<Lesson[]>([]);
const tracks = ref<Track[]>([]);
const horses = ref<Horse[]>([]);
const clients = ref<Client[]>([]);
const users = ref<UserRead[]>([]);

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

const weekLabel = computed(() => {
  const start = weekDays.value[0]!;
  const end = weekDays.value[6]!;
  return `${start.iso} — ${end.iso}`;
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

function lessonsForDay(iso: string): Lesson[] {
  return lessons.value.filter((l) => l.date_time.slice(0, 10) === iso);
}

function formatTime(dt: string): string {
  return new Date(dt).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

// ---------------------------------------------------------------------------
// Select options
// ---------------------------------------------------------------------------
const userOptions = computed(() => users.value);
const userOptionsWithNone = computed(() => users.value);
const trackOptionsWithNone = computed(() => tracks.value.filter((tr) => tr.is_active));
const horseOptions = computed(() => horses.value.filter((h) => h.is_active));
const clientOptions = computed(() => clients.value.filter((c) => c.is_active));

// ---------------------------------------------------------------------------
// Form
// ---------------------------------------------------------------------------
interface LessonForm {
  date_time: string;
  end_time: string;
  instructor_id: number | null;
  helper_id: number | null;
  track_id: number | null;
  horse_ids: number[];
  client_ids: number[];
  description: string;
}

function emptyForm(dateIso?: string | null): LessonForm {
  const base = dateIso ? `${dateIso}T09:00` : "";
  return {
    date_time: base,
    end_time: "",
    instructor_id: null,
    helper_id: null,
    track_id: null,
    horse_ids: [],
    client_ids: [],
    description: "",
  };
}

const form = ref<LessonForm>(emptyForm());

function openCreateDialog(dateIso: string | null) {
  editingLesson.value = null;
  form.value = emptyForm(dateIso);
  dialog.value = true;
}

function openEditDialog(lesson: Lesson) {
  editingLesson.value = lesson;
  form.value = {
    date_time: lesson.date_time.slice(0, 16),
    end_time: lesson.end_time ? lesson.end_time.slice(0, 16) : "",
    instructor_id: lesson.instructor_id,
    helper_id: lesson.helper_id,
    track_id: lesson.track_id,
    horse_ids: horses.value
      .filter((h) => lesson.horse_names.includes(h.name))
      .map((h) => h.id),
    client_ids: clients.value
      .filter((c) => lesson.client_names.includes(c.name))
      .map((c) => c.id),
    description: lesson.description ?? "",
  };
  dialog.value = true;
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------
async function loadAll() {
  loading.value = true;
  error.value = null;
  try {
    const [lessonsRes, tracksRes, horsesRes, clientsRes, usersRes] = await Promise.all([
      http.get<Lesson[]>("/api/v1/lessons"),
      http.get<Track[]>("/api/v1/tracks"),
      http.get<Horse[]>("/api/v1/horses"),
      http.get<Client[]>("/api/v1/clients"),
      http.get<UserRead[]>("/api/v1/users"),
    ]);
    lessons.value = lessonsRes.data;
    tracks.value = tracksRes.data;
    horses.value = horsesRes.data;
    clients.value = clientsRes.data;
    users.value = usersRes.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("lessons.error");
  } finally {
    loading.value = false;
  }
}

async function save() {
  if (!form.value.instructor_id || !form.value.date_time) return;
  saving.value = true;
  try {
    if (editingLesson.value) {
      const payload: LessonUpdate = {
        date_time: form.value.date_time,
        end_time: form.value.end_time || null,
        instructor_id: form.value.instructor_id ?? undefined,
        helper_id: form.value.helper_id,
        track_id: form.value.track_id,
        description: form.value.description || null,
        horse_ids: form.value.horse_ids,
        client_ids: form.value.client_ids,
      };
      await http.put(`/api/v1/lessons/${editingLesson.value.id}`, payload);
    } else {
      const payload: LessonCreate = {
        date_time: form.value.date_time,
        end_time: form.value.end_time || null,
        instructor_id: form.value.instructor_id!,
        helper_id: form.value.helper_id,
        track_id: form.value.track_id,
        description: form.value.description || null,
        horse_ids: form.value.horse_ids,
        client_ids: form.value.client_ids,
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
