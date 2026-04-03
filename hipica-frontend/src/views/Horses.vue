<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("horses.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="horses"
      :search="search"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <!-- Buscador encima de la tabla -->
      <template #top>
        <v-text-field
          v-model="search"
          :placeholder="t('horses.search')"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @click:clear="search = ''"
          hide-details
          class="ma-3"
        />
      </template>

      <!-- Columna box: muestra box_name o "-" -->
      <template #[`item.box_name`]="{ item }">
        {{ item.box_name ?? "-" }}
      </template>

      <!-- Columna activo: icono coloreado -->
      <template #[`item.is_active`]="{ item }">
        <v-icon :color="item.is_active ? 'success' : 'error'" size="20">
          {{ item.is_active ? "mdi-check-circle" : "mdi-close-circle" }}
        </v-icon>
      </template>

      <!-- Columna niveles: chips -->
      <template #[`item.levels`]="{ item }">
        <v-chip
          v-for="lvl in item.levels"
          :key="lvl"
          size="x-small"
          class="mr-1"
        >
          {{ lvl }}
        </v-chip>
      </template>

      <!-- Sin datos -->
      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("horses.empty") }}
        </v-alert>
      </template>

      <!-- Botones de acción en el footer -->
      <template #bottom>
        <div class="d-flex justify-space-between align-center ga-2 pa-2">
          <!-- Botón añadir (solo admin) -->
          <v-btn
            v-if="canManage"
            color="primary"
            variant="tonal"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            {{ t("horses.addButton") }}
          </v-btn>
          <div v-else />

          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-file-excel"
              color="success"
              variant="tonal"
              :disabled="!horses.length"
              :title="t('horses.exportExcel')"
              @click="exportToExcel"
            />
            <v-btn
              icon="mdi-refresh"
              color="primary"
              variant="tonal"
              :loading="loading"
              :title="t('horses.reload')"
              @click="load"
            />
          </div>
        </div>
      </template>
    </v-data-table>

    <!-- Diálogo de edición / creación -->
    <v-dialog v-model="dialog" max-width="520" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingId ? t("horses.dialog.titleEdit") : t("horses.dialog.titleCreate") }}
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-row dense>
            <v-col v-if="isAppAdmin" cols="12">
              <v-select
                v-model="form.stable_id"
                :label="t('horses.dialog.stable')"
                :items="stables"
                item-title="name"
                item-value="id"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.name"
                :label="t('horses.table.name')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="form.box_id"
                :label="t('horses.table.box')"
                :items="boxOptions"
                item-title="name"
                item-value="id"
                variant="outlined"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="form.levels"
                :label="t('horses.table.levels')"
                :items="levelOptions"
                variant="outlined"
                density="compact"
                multiple
                chips
                closable-chips
              />
            </v-col>
            <v-col cols="12">
              <v-switch
                v-model="form.is_active"
                :label="t('horses.table.active')"
                color="success"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <!-- Botón eliminar (solo al editar, solo admin) -->
          <v-btn
            v-if="editingId && canManage"
            color="error"
            variant="text"
            :disabled="saving || deleting"
            @click="confirmDeleteDialog = true"
          >
            {{ t("horses.dialog.delete") }}
          </v-btn>

          <v-spacer />
          <v-btn
            variant="text"
            :disabled="saving || deleting"
            @click="dialog = false"
          >
            {{ t("horses.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            :disabled="deleting"
            @click="save"
          >
            {{ t("horses.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de confirmación de eliminación -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("horses.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("horses.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("horses.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteHorse">
            {{ t("horses.dialog.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar de confirmación -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000" location="top">
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import * as XLSX from "xlsx";
import { http } from "../api/http";
import type { Horse, Box, Stable, Level } from "../types/api";
import { canManage, isAppAdmin } from "../auth/profile";

const { t } = useI18n();
const horses = ref<Horse[]>([]);
const boxes = ref<Box[]>([]);
const stables = ref<Stable[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

// Diálogo
const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ name: "", box_id: null as number | null, is_active: true, levels: [] as string[], stable_id: null as number | null });

// Confirmación de eliminación
const confirmDeleteDialog = ref(false);

// Snackbar
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const levels = ref<Level[]>([]);
const levelOptions = computed(() => levels.value.map((l) => ({ title: l.name, value: l.name })));

// Opciones de boxes activos para el select del diálogo
const boxOptions = computed(() =>
  boxes.value.filter((b) => b.is_active)
);

const headers = computed(() => [
  { title: t("horses.table.id"),     key: "id",        sortable: true  },
  { title: t("horses.table.name"),   key: "name",      sortable: true  },
  { title: t("horses.table.box"),    key: "box_name",  sortable: true  },
  { title: t("horses.table.levels"), key: "levels",    sortable: false },
  { title: t("horses.table.active"), key: "is_active", sortable: true  },
  { title: t("horses.table.stable"), key: "stable_name", sortable: true  },
]);

// Para export respetando el filtro de búsqueda
const filteredHorses = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return horses.value;
  return horses.value.filter(
    (h) =>
      h.name.toLowerCase().includes(q) ||
      (h.box_name ?? "").toLowerCase().includes(q)
  );
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const requests: Promise<any>[] = [
      http.get<Horse[]>("/api/v1/horses"),
      http.get<Box[]>("/api/v1/boxes"),
      http.get<Level[]>("/api/v1/levels"),
    ];
    if (isAppAdmin.value) requests.push(http.get<Stable[]>("/api/v1/stables"));
    const [horsesRes, boxesRes, levelsRes, stablesRes] = await Promise.all(requests);
    horses.value = horsesRes.data;
    boxes.value = boxesRes.data;
    levels.value = levelsRes.data;
    if (stablesRes) stables.value = stablesRes.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("horses.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Horse }) {
  openEditDialog(row.item);
}

function openCreateDialog() {
  editingId.value = null;
  form.value = { name: "", box_id: null, is_active: true, levels: [], stable_id: null };
  dialog.value = true;
}

function openEditDialog(horse: Horse) {
  editingId.value = horse.id;
  form.value = {
    name:      horse.name,
    box_id:    horse.box_id,
    is_active: horse.is_active,
    levels:    [...horse.levels],
    stable_id: horse.stable_id,
  };
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    const payload: Record<string, any> = {
      name:      form.value.name,
      box_id:    form.value.box_id ?? null,
      is_active: form.value.is_active,
      levels:    form.value.levels,
    };
    if (isAppAdmin.value && form.value.stable_id) {
      payload.stable_id = form.value.stable_id;
    }

    if (editingId.value) {
      const res = await http.put<Horse>(`/api/v1/horses/${editingId.value}`, payload);
      const idx = horses.value.findIndex((h) => h.id === editingId.value);
      if (idx !== -1) horses.value[idx] = res.data;
    } else {
      const res = await http.post<Horse>("/api/v1/horses/", payload);
      horses.value.push(res.data);
    }

    dialog.value = false;
    showSnackbar(t("horses.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("horses.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteHorse() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/horses/${editingId.value}`);
    horses.value = horses.value.filter((h) => h.id !== editingId.value);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("horses.dialog.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    showSnackbar(e?.response?.data?.detail || t("horses.dialog.deleteError"), "error");
  } finally {
    deleting.value = false;
  }
}

function showSnackbar(text: string, color: string) {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

function exportToExcel() {
  const rows = filteredHorses.value.map((h) => ({
    [t("horses.table.id")]:     h.id,
    [t("horses.table.name")]:   h.name,
    [t("horses.table.box")]:    h.box_name ?? "-",
    [t("horses.table.levels")]: h.levels.join(", "),
    [t("horses.table.active")]: h.is_active ? "✓" : "✗",
    [t("horses.table.stable")]: h.stable_name ?? h.stable_id,
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("horses.title"));
  XLSX.writeFile(wb, `${t("horses.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
