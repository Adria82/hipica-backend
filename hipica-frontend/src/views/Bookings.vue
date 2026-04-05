<template>
  <v-container fluid>
    <div class="d-flex align-center mb-4">
      <h2 class="text-h5 flex-grow-1">{{ t("bookings.title") }}</h2>
    </div>

    <v-tabs v-model="activeTab" color="primary" class="mb-4">
      <v-tab value="available">{{ t("bookings.tabAvailable") }}</v-tab>
      <v-tab value="mine">{{ t("bookings.tabMine") }}</v-tab>
      <v-tab v-if="isStaff" value="manage">{{ t("bookings.tabManage") }}</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">

      <!-- TAB: Clases disponibles -->
      <v-window-item value="available">
        <div class="d-flex align-center mb-3 gap-3 flex-wrap">
          <v-text-field
            v-model="filterDate"
            type="date"
            :label="t('bookings.filterDate')"
            density="compact"
            hide-details
            style="max-width: 200px"
            clearable
          />
          <v-btn
            v-if="selectedLessons.length > 0"
            color="primary"
            :loading="bulkLoading"
            @click="openBulkDialog"
          >
            {{ t("bookings.reserveSelected") }} ({{ selectedLessons.length }})
          </v-btn>
        </div>

        <v-alert v-if="availableError" type="error" class="mb-3">{{ availableError }}</v-alert>

        <v-data-table
          v-model="selectedLessons"
          :headers="availableHeaders"
          :items="filteredAvailable"
          :loading="availableLoading"
          show-select
          item-value="id"
          density="compact"
        >
          <template #[`item.date_time`]="{ item }">
            {{ formatDate(item.date_time) }}
          </template>
          <template #[`item.time`]="{ item }">
            {{ formatTime(item.date_time) }}
            <span v-if="item.end_time"> – {{ formatTime(item.end_time) }}</span>
          </template>
          <template #[`item.available_slots`]="{ item }">
            <span v-if="item.available_slots !== null">{{ item.available_slots }}</span>
            <span v-else>{{ t("bookings.unlimited") }}</span>
          </template>
          <template #[`item.actions`]="{ item }">
            <v-btn size="small" color="primary" variant="tonal" @click="openReserveDialog(item)">
              {{ t("bookings.reserve") }}
            </v-btn>
          </template>
          <template #no-data>
            <span class="text-grey">{{ t("bookings.empty") }}</span>
          </template>
        </v-data-table>
      </v-window-item>

      <!-- TAB: Mis reservas -->
      <v-window-item value="mine">
        <v-alert v-if="myError" type="error" class="mb-3">{{ myError }}</v-alert>

        <v-data-table
          :headers="myHeaders"
          :items="myBookings"
          :loading="myLoading"
          density="compact"
        >
          <template #[`item.lesson_datetime`]="{ item }">
            {{ formatDate(item.lesson_datetime) }} {{ formatTime(item.lesson_datetime) }}
          </template>
          <template #[`item.status`]="{ item }">
            <v-chip :color="statusColor(item.status)" size="small">
              {{ t(`bookingStatus.${item.status}`) }}
            </v-chip>
          </template>
          <template #[`item.actions`]="{ item }">
            <v-btn
              v-if="item.status === 'RESERVADO'"
              size="small"
              color="error"
              variant="tonal"
              @click="confirmCancelBooking(item)"
            >
              {{ t("bookings.cancel") }}
            </v-btn>
          </template>
          <template #no-data>
            <span class="text-grey">{{ t("bookings.emptyMine") }}</span>
          </template>
        </v-data-table>
      </v-window-item>

      <!-- TAB: Gestión (staff) -->
      <v-window-item v-if="isStaff" value="manage">
        <v-select
          v-model="selectedManageLesson"
          :items="allLessons"
          item-title="label"
          item-value="id"
          :label="t('bookings.selectLesson')"
          density="compact"
          hide-details
          class="mb-4"
          style="max-width: 400px"
          clearable
        />

        <v-data-table
          v-if="selectedManageLesson"
          :headers="manageHeaders"
          :items="manageLessonBookings"
          :loading="manageLoading"
          density="compact"
        >
          <template #[`item.status`]="{ item }">
            <v-chip :color="statusColor(item.status)" size="small">
              {{ t(`bookingStatus.${item.status}`) }}
            </v-chip>
          </template>
          <template #[`item.actions`]="{ item }">
            <v-btn
              size="small"
              color="success"
              variant="tonal"
              class="mr-1"
              :loading="statusLoadingId === item.id"
              @click="setStatus(item, 'ASISTIO')"
            >
              {{ t("bookings.markAttended") }}
            </v-btn>
            <v-btn
              size="small"
              color="warning"
              variant="tonal"
              :loading="statusLoadingId === item.id"
              @click="setStatus(item, 'NO_ASISTIO')"
            >
              {{ t("bookings.markNotAttended") }}
            </v-btn>
          </template>
          <template #no-data>
            <span class="text-grey">{{ t("bookings.emptyMine") }}</span>
          </template>
        </v-data-table>
      </v-window-item>

    </v-window>

    <!-- Dialog: Reservar clase -->
    <v-dialog v-model="reserveDialog" max-width="480">
      <v-card>
        <v-card-title>{{ t("bookings.dialogTitle") }}</v-card-title>
        <v-card-text>
          <div v-if="reserveTarget" class="mb-4">
            <div><strong>{{ t("bookings.dialogDate") }}:</strong> {{ formatDate(reserveTarget.date_time) }} {{ formatTime(reserveTarget.date_time) }}</div>
            <div><strong>{{ t("bookings.dialogInstructor") }}:</strong> {{ reserveTarget.instructor_name }}</div>
            <div v-if="reserveTarget.track_name"><strong>{{ t("bookings.dialogTrack") }}:</strong> {{ reserveTarget.track_name }}</div>
            <div>
              <strong>{{ t("bookings.dialogSlots") }}:</strong>
              {{ reserveTarget.available_slots !== null ? reserveTarget.available_slots : t("bookings.unlimited") }}
            </div>
          </div>
          <v-text-field
            v-model="reserveForm.horse_request"
            :label="t('bookings.dialogHorseRequest')"
            density="compact"
            hide-details
            class="mb-3"
          />
          <v-textarea
            v-model="reserveForm.notes"
            :label="t('bookings.dialogNotes')"
            density="compact"
            hide-details
            rows="2"
          />
          <v-alert v-if="reserveError" type="error" class="mt-3">{{ reserveError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="reserveDialog = false">{{ t("bookings.dialogCancel") }}</v-btn>
          <v-btn color="primary" :loading="reserveLoading" @click="doReserve">
            {{ t("bookings.dialogConfirm") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog: Reserva masiva -->
    <v-dialog v-model="bulkDialog" max-width="480">
      <v-card>
        <v-card-title>{{ t("bookings.reserveSelected") }}</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="bulkForm.horse_request"
            :label="t('bookings.dialogHorseRequest')"
            density="compact"
            hide-details
            class="mb-3"
          />
          <v-textarea
            v-model="bulkForm.notes"
            :label="t('bookings.dialogNotes')"
            density="compact"
            hide-details
            rows="2"
          />
          <v-alert v-if="bulkError" type="error" class="mt-3">{{ bulkError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="bulkDialog = false">{{ t("bookings.dialogCancel") }}</v-btn>
          <v-btn color="primary" :loading="bulkLoading" @click="doBulkReserve">
            {{ t("bookings.dialogConfirm") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog: Confirmar cancelación -->
    <v-dialog v-model="cancelDialog" max-width="400">
      <v-card>
        <v-card-title>{{ t("bookings.cancel") }}</v-card-title>
        <v-card-text>{{ t("bookings.confirmCancel") }}</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="cancelDialog = false">{{ t("bookings.dialogCancel") }}</v-btn>
          <v-btn color="error" :loading="cancelLoading" @click="doCancel">
            {{ t("bookings.cancel") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "@/api/http";
import { userProfile } from "@/auth/profile";
import type { Booking, AvailableLesson, Lesson } from "@/types/api";

const { t } = useI18n();

const activeTab = ref("available");

const isStaff = computed(() =>
  ["stable_admin", "app_admin", "monitor", "assistant"].includes(userProfile.value?.role ?? "")
);

// ---------------------------------------------------------------------------
// Available lessons
// ---------------------------------------------------------------------------
const availableLoading = ref(false);
const availableError = ref("");
const availableLessons = ref<AvailableLesson[]>([]);
const selectedLessons = ref<number[]>([]);
const filterDate = ref("");

const availableHeaders = [
  { title: t("bookings.tableDate"), key: "date_time" },
  { title: t("bookings.tableTime"), key: "time" },
  { title: t("bookings.tableInstructor"), key: "instructor_name" },
  { title: t("bookings.tableTrack"), key: "track_name" },
  { title: t("bookings.tableSlots"), key: "available_slots" },
  { title: t("bookings.tableActions"), key: "actions", sortable: false },
];

const filteredAvailable = computed(() => {
  if (!filterDate.value) return availableLessons.value;
  return availableLessons.value.filter((l) => l.date_time.startsWith(filterDate.value));
});

async function loadAvailable() {
  availableLoading.value = true;
  availableError.value = "";
  try {
    const { data } = await http.get<AvailableLesson[]>("/api/v1/bookings/available");
    availableLessons.value = data;
  } catch {
    availableError.value = t("bookings.reserveError");
  } finally {
    availableLoading.value = false;
  }
}

// ---------------------------------------------------------------------------
// My bookings
// ---------------------------------------------------------------------------
const myLoading = ref(false);
const myError = ref("");
const myBookings = ref<Booking[]>([]);

const myHeaders = [
  { title: t("bookings.tableDate"), key: "lesson_datetime" },
  { title: t("bookings.tableStatus"), key: "status" },
  { title: t("bookings.tableHorseRequest"), key: "horse_request" },
  { title: t("bookings.tableActions"), key: "actions", sortable: false },
];

async function loadMyBookings() {
  if (isStaff.value) return;
  myLoading.value = true;
  myError.value = "";
  try {
    const { data } = await http.get<Booking[]>("/api/v1/bookings/mine");
    myBookings.value = data;
  } catch {
    myError.value = t("bookings.cancelError");
  } finally {
    myLoading.value = false;
  }
}

// ---------------------------------------------------------------------------
// Manage (staff)
// ---------------------------------------------------------------------------
const manageLoading = ref(false);
const selectedManageLesson = ref<number | null>(null);
const manageLessonBookings = ref<Booking[]>([]);
const allLessons = ref<{ id: number; label: string }[]>([]);
const statusLoadingId = ref<number | null>(null);

const manageHeaders = [
  { title: t("bookings.tableDate"), key: "lesson_datetime" },
  { title: "Alumno", key: "user_name" },
  { title: t("bookings.tableStatus"), key: "status" },
  { title: t("bookings.tableHorseRequest"), key: "horse_request" },
  { title: t("bookings.tableActions"), key: "actions", sortable: false },
];

async function loadAllLessons() {
  try {
    const { data } = await http.get<Lesson[]>("/api/v1/lessons/");
    allLessons.value = data.map((l) => ({
      id: l.id,
      label: `${formatDate(l.date_time)} ${formatTime(l.date_time)} — ${l.instructor_email}`,
    }));
  } catch {
    // silencioso
  }
}

async function loadManageLessonBookings(lessonId: number) {
  manageLoading.value = true;
  try {
    const { data } = await http.get<Booking[]>(`/api/v1/lessons/${lessonId}/bookings`);
    manageLessonBookings.value = data;
  } catch {
    manageLessonBookings.value = [];
  } finally {
    manageLoading.value = false;
  }
}

watch(selectedManageLesson, (id) => {
  if (id) loadManageLessonBookings(id);
  else manageLessonBookings.value = [];
});

async function setStatus(booking: Booking, status: string) {
  statusLoadingId.value = booking.id;
  try {
    await http.put(`/api/v1/bookings/${booking.id}/status`, { status });
    if (selectedManageLesson.value) loadManageLessonBookings(selectedManageLesson.value);
    showSnackbar(t("bookings.reserveSuccess"), "success");
  } catch {
    showSnackbar(t("bookings.reserveError"), "error");
  } finally {
    statusLoadingId.value = null;
  }
}

// ---------------------------------------------------------------------------
// Reserve dialog
// ---------------------------------------------------------------------------
const reserveDialog = ref(false);
const reserveLoading = ref(false);
const reserveError = ref("");
const reserveTarget = ref<AvailableLesson | null>(null);
const reserveForm = ref({ horse_request: "", notes: "" });

function openReserveDialog(lesson: AvailableLesson) {
  reserveTarget.value = lesson;
  reserveForm.value = { horse_request: "", notes: "" };
  reserveError.value = "";
  reserveDialog.value = true;
}

async function doReserve() {
  if (!reserveTarget.value) return;
  reserveLoading.value = true;
  reserveError.value = "";
  try {
    await http.post("/api/v1/bookings", {
      lesson_id: reserveTarget.value.id,
      horse_request: reserveForm.value.horse_request || null,
      notes: reserveForm.value.notes || null,
    });
    reserveDialog.value = false;
    showSnackbar(t("bookings.reserveSuccess"), "success");
    loadAvailable();
    loadMyBookings();
  } catch (e: any) {
    reserveError.value = e.response?.data?.detail ?? t("bookings.reserveError");
  } finally {
    reserveLoading.value = false;
  }
}

// ---------------------------------------------------------------------------
// Bulk reserve
// ---------------------------------------------------------------------------
const bulkDialog = ref(false);
const bulkLoading = ref(false);
const bulkError = ref("");
const bulkForm = ref({ horse_request: "", notes: "" });

function openBulkDialog() {
  bulkForm.value = { horse_request: "", notes: "" };
  bulkError.value = "";
  bulkDialog.value = true;
}

async function doBulkReserve() {
  bulkLoading.value = true;
  bulkError.value = "";
  try {
    const results: { lesson_id: number; success: boolean }[] = await http
      .post("/api/v1/bookings/bulk", {
        lesson_ids: selectedLessons.value,
        horse_request: bulkForm.value.horse_request || null,
        notes: bulkForm.value.notes || null,
      })
      .then((r) => r.data);
    const successCount = results.filter((r) => r.success).length;
    bulkDialog.value = false;
    selectedLessons.value = [];
    showSnackbar(
      successCount === results.length
        ? t("bookings.bulkReserveSuccess", { count: successCount })
        : t("bookings.bulkReservePartial", { success: successCount, total: results.length }),
      successCount > 0 ? "success" : "warning",
    );
    loadAvailable();
    loadMyBookings();
  } catch {
    bulkError.value = t("bookings.reserveError");
  } finally {
    bulkLoading.value = false;
  }
}

// ---------------------------------------------------------------------------
// Cancel booking
// ---------------------------------------------------------------------------
const cancelDialog = ref(false);
const cancelLoading = ref(false);
const cancelTarget = ref<Booking | null>(null);

function confirmCancelBooking(booking: Booking) {
  cancelTarget.value = booking;
  cancelDialog.value = true;
}

async function doCancel() {
  if (!cancelTarget.value) return;
  cancelLoading.value = true;
  try {
    await http.post(`/api/v1/bookings/${cancelTarget.value.id}/cancel`);
    cancelDialog.value = false;
    showSnackbar(t("bookings.cancelSuccess"), "success");
    loadMyBookings();
    loadAvailable();
  } catch {
    showSnackbar(t("bookings.cancelError"), "error");
  } finally {
    cancelLoading.value = false;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function statusColor(status: string) {
  switch (status) {
    case "RESERVADO": return "primary";
    case "CANCELADO": return "error";
    case "ASISTIO": return "success";
    case "NO_ASISTIO": return "warning";
    default: return "grey";
  }
}

function formatDate(dt: string) {
  return new Date(dt).toLocaleDateString();
}

function formatTime(dt: string) {
  return new Date(dt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const snackbar = ref({ show: false, message: "", color: "success" });
function showSnackbar(message: string, color = "success") {
  snackbar.value = { show: true, message, color };
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
onMounted(() => {
  loadAvailable();
  loadMyBookings();
  if (isStaff.value) loadAllLessons();
});
</script>
