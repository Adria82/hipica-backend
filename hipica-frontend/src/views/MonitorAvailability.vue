<template>
  <v-container fluid>
    <div class="d-flex align-center mb-4">
      <h2 class="text-h5 flex-grow-1">{{ t("availability.title") }}</h2>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
        {{ t("availability.addButton") }}
      </v-btn>
    </div>

    <v-alert v-if="error" type="error" class="mb-3">{{ error }}</v-alert>

    <v-data-table
      :headers="headers"
      :items="availabilities"
      :loading="loading"
      density="compact"
    >
      <template #[`item.type`]="{ item }">
        {{ item.is_recurring ? t("availability.recurring") : t("availability.specific") }}
      </template>
      <template #[`item.day`]="{ item }">
        <span v-if="item.is_recurring && item.day_of_week !== null">
          {{ dayName(item.day_of_week) }}
        </span>
        <span v-else-if="item.specific_date">{{ item.specific_date }}</span>
      </template>
      <template #[`item.is_active`]="{ item }">
        <v-icon :color="item.is_active ? 'success' : 'error'">
          {{ item.is_active ? "mdi-check-circle" : "mdi-close-circle" }}
        </v-icon>
      </template>
      <template #[`item.actions`]="{ item }">
        <v-btn icon size="small" variant="text" @click="openEditDialog(item)">
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
        <v-btn icon size="small" variant="text" color="error" @click="confirmDelete(item)">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </template>
      <template #no-data>
        <span class="text-grey">{{ t("availability.empty") }}</span>
      </template>
    </v-data-table>

    <!-- Dialog crear/editar -->
    <v-dialog v-model="dialog" max-width="480">
      <v-card>
        <v-card-title>
          {{ editTarget ? t("availability.dialogTitleEdit") : t("availability.dialogTitleCreate") }}
        </v-card-title>
        <v-card-text>
          <v-switch
            v-model="form.is_recurring"
            :label="t('availability.isRecurring')"
            color="primary"
            class="mb-2"
          />
          <v-select
            v-if="form.is_recurring"
            v-model="form.day_of_week"
            :items="dayItems"
            item-title="label"
            item-value="value"
            :label="t('availability.dayOfWeek')"
            density="compact"
            hide-details
            class="mb-3"
          />
          <v-text-field
            v-else
            v-model="form.specific_date"
            type="date"
            :label="t('availability.specificDate')"
            density="compact"
            hide-details
            class="mb-3"
          />
          <v-text-field
            v-model="form.start_time"
            type="time"
            :label="t('availability.startTime')"
            density="compact"
            hide-details
            class="mb-3"
          />
          <v-text-field
            v-model="form.end_time"
            type="time"
            :label="t('availability.endTime')"
            density="compact"
            hide-details
          />
          <v-alert v-if="saveError" type="error" class="mt-3">{{ saveError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialog = false">{{ t("availability.cancel") }}</v-btn>
          <v-btn color="primary" :loading="saving" @click="doSave">
            {{ t("availability.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog confirmar eliminación -->
    <v-dialog v-model="deleteDialog" max-width="380">
      <v-card>
        <v-card-text>{{ t("availability.confirmDelete") }}</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">{{ t("availability.cancel") }}</v-btn>
          <v-btn color="error" :loading="deleting" @click="doDelete">
            {{ t("availability.deleteSuccess") }}
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
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "@/api/http";
import type { MonitorAvailability } from "@/types/api";

const { t } = useI18n();

const loading = ref(false);
const error = ref("");
const availabilities = ref<MonitorAvailability[]>([]);

const headers = [
  { title: t("availability.tableType"), key: "type" },
  { title: t("availability.tableDay"), key: "day" },
  { title: t("availability.tableFrom"), key: "start_time" },
  { title: t("availability.tableTo"), key: "end_time" },
  { title: t("availability.tableActive"), key: "is_active" },
  { title: t("availability.tableActions"), key: "actions", sortable: false },
];

const dayItems = [0, 1, 2, 3, 4, 5, 6].map((v) => ({ value: v, label: dayName(v) }));

function dayName(dow: number): string {
  const days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
  return days[dow] ?? String(dow);
}

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await http.get<MonitorAvailability[]>("/api/v1/monitor-availability");
    availabilities.value = data;
  } catch {
    error.value = t("availability.error");
  } finally {
    loading.value = false;
  }
}

// ---------------------------------------------------------------------------
// Dialog crear / editar
// ---------------------------------------------------------------------------
const dialog = ref(false);
const saving = ref(false);
const saveError = ref("");
const editTarget = ref<MonitorAvailability | null>(null);

const form = ref({
  is_recurring: true,
  day_of_week: 0 as number | null,
  specific_date: "" as string,
  start_time: "09:00",
  end_time: "11:00",
});

function openCreateDialog() {
  editTarget.value = null;
  form.value = { is_recurring: true, day_of_week: 0, specific_date: "", start_time: "09:00", end_time: "11:00" };
  saveError.value = "";
  dialog.value = true;
}

function openEditDialog(item: MonitorAvailability) {
  editTarget.value = item;
  form.value = {
    is_recurring: item.is_recurring,
    day_of_week: item.day_of_week,
    specific_date: item.specific_date ?? "",
    start_time: item.start_time,
    end_time: item.end_time,
  };
  saveError.value = "";
  dialog.value = true;
}

async function doSave() {
  saving.value = true;
  saveError.value = "";
  const payload = {
    user_id: 0,
    is_recurring: form.value.is_recurring,
    day_of_week: form.value.is_recurring ? form.value.day_of_week : null,
    specific_date: !form.value.is_recurring ? (form.value.specific_date || null) : null,
    start_time: form.value.start_time,
    end_time: form.value.end_time,
  };
  try {
    if (editTarget.value) {
      await http.put(`/api/v1/monitor-availability/${editTarget.value.id}`, payload);
    } else {
      await http.post("/api/v1/monitor-availability", payload);
    }
    dialog.value = false;
    showSnackbar(t("availability.saveSuccess"), "success");
    loadData();
  } catch {
    saveError.value = t("availability.saveError");
  } finally {
    saving.value = false;
  }
}

// ---------------------------------------------------------------------------
// Delete
// ---------------------------------------------------------------------------
const deleteDialog = ref(false);
const deleting = ref(false);
const deleteTarget = ref<MonitorAvailability | null>(null);

function confirmDelete(item: MonitorAvailability) {
  deleteTarget.value = item;
  deleteDialog.value = true;
}

async function doDelete() {
  if (!deleteTarget.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/monitor-availability/${deleteTarget.value.id}`);
    deleteDialog.value = false;
    showSnackbar(t("availability.deleteSuccess"), "success");
    loadData();
  } catch {
    showSnackbar(t("availability.deleteError"), "error");
  } finally {
    deleting.value = false;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const snackbar = ref({ show: false, message: "", color: "success" });
function showSnackbar(message: string, color = "success") {
  snackbar.value = { show: true, message, color };
}

onMounted(loadData);
</script>
