<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("boxes.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="boxes"
      :search="search"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <!-- Buscador encima de la tabla -->
      <template #top>
        <v-text-field
          v-model="search"
          :placeholder="t('boxes.search')"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @click:clear="search = ''"
          hide-details
          class="ma-3"
        />
      </template>

      <!-- Columna activo: icono coloreado -->
      <template #[`item.is_active`]="{ item }">
        <v-icon :color="item.is_active ? 'success' : 'error'" size="20">
          {{ item.is_active ? "mdi-check-circle" : "mdi-close-circle" }}
        </v-icon>
      </template>

      <!-- Sin datos -->
      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("boxes.empty") }}
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
            {{ t("boxes.addButton") }}
          </v-btn>
          <div v-else />

          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-file-excel"
              color="success"
              variant="tonal"
              :disabled="!boxes.length"
              :title="t('boxes.exportExcel')"
              @click="exportToExcel"
            />
            <v-btn
              icon="mdi-refresh"
              color="primary"
              variant="tonal"
              :loading="loading"
              :title="t('boxes.reload')"
              @click="load"
            />
          </div>
        </div>
      </template>
    </v-data-table>

    <!-- Diálogo de edición / creación -->
    <v-dialog v-model="dialog" max-width="480" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingId ? t("boxes.dialog.titleEdit") : t("boxes.dialog.titleCreate") }}
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-row dense>
            <v-col v-if="isAppAdmin" cols="12">
              <v-select
                v-model="form.stable_id"
                :label="t('boxes.dialog.stable')"
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
                :label="t('boxes.table.name')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model.number="form.capacity"
                :label="t('boxes.table.capacity')"
                variant="outlined"
                density="compact"
                type="number"
                :min="1"
              />
            </v-col>
            <v-col cols="12">
              <v-switch
                v-model="form.is_active"
                :label="t('boxes.table.active')"
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
            {{ t("boxes.dialog.delete") }}
          </v-btn>

          <v-spacer />
          <v-btn
            variant="text"
            :disabled="saving || deleting"
            @click="dialog = false"
          >
            {{ t("boxes.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            :disabled="deleting"
            @click="save"
          >
            {{ t("boxes.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de confirmación de eliminación -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("boxes.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("boxes.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("boxes.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteBox">
            {{ t("boxes.dialog.delete") }}
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
import type { Box, Stable } from "../types/api";
import { canManage, isAppAdmin } from "../auth/profile";

const { t } = useI18n();
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
const form = ref({ name: "", capacity: 1, is_active: true, stable_id: null as number | null });

// Confirmación de eliminación
const confirmDeleteDialog = ref(false);

// Snackbar
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const headers = computed(() => [
  { title: t("boxes.table.id"),          key: "id",           sortable: true  },
  { title: t("boxes.table.name"),        key: "name",         sortable: true  },
  { title: t("boxes.table.capacity"),    key: "capacity",     sortable: true  },
  { title: t("boxes.table.horsesCount"), key: "horses_count", sortable: true  },
  { title: t("boxes.table.active"),      key: "is_active",    sortable: true  },
  { title: t("boxes.table.stable"),      key: "stable_name",  sortable: true  },
]);

// Para export respetando el filtro de búsqueda
const filteredBoxes = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return boxes.value;
  return boxes.value.filter((b) => b.name.toLowerCase().includes(q));
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const requests: Promise<any>[] = [http.get<Box[]>("/api/v1/boxes")];
    if (isAppAdmin.value) requests.push(http.get<Stable[]>("/api/v1/stables"));
    const [boxesRes, stablesRes] = await Promise.all(requests);
    boxes.value = boxesRes.data;
    if (stablesRes) stables.value = stablesRes.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("boxes.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Box }) {
  openEditDialog(row.item);
}

function openCreateDialog() {
  editingId.value = null;
  form.value = { name: "", capacity: 1, is_active: true, stable_id: null };
  dialog.value = true;
}

function openEditDialog(box: Box) {
  editingId.value = box.id;
  form.value = {
    name:      box.name,
    capacity:  box.capacity,
    is_active: box.is_active,
    stable_id: box.stable_id,
  };
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    const payload: Record<string, any> = {
      name:      form.value.name,
      capacity:  form.value.capacity,
      is_active: form.value.is_active,
    };
    if (isAppAdmin.value && form.value.stable_id) {
      payload.stable_id = form.value.stable_id;
    }

    if (editingId.value) {
      const res = await http.put<Box>(`/api/v1/boxes/${editingId.value}`, payload);
      const idx = boxes.value.findIndex((b) => b.id === editingId.value);
      if (idx !== -1) boxes.value[idx] = res.data;
    } else {
      const res = await http.post<Box>("/api/v1/boxes/", payload);
      boxes.value.push(res.data);
    }

    dialog.value = false;
    showSnackbar(t("boxes.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("boxes.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteBox() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/boxes/${editingId.value}`);
    boxes.value = boxes.value.filter((b) => b.id !== editingId.value);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("boxes.dialog.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    // El backend devuelve el mensaje con los nombres de caballos, lo mostramos directamente
    showSnackbar(e?.response?.data?.detail || t("boxes.dialog.deleteError"), "error");
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
  const rows = filteredBoxes.value.map((b) => ({
    [t("boxes.table.id")]:          b.id,
    [t("boxes.table.name")]:        b.name,
    [t("boxes.table.capacity")]:    b.capacity,
    [t("boxes.table.horsesCount")]: b.horses_count,
    [t("boxes.table.active")]:      b.is_active ? "✓" : "✗",
    [t("boxes.table.stable")]:      b.stable_name ?? b.stable_id,
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("boxes.title"));
  XLSX.writeFile(wb, `${t("boxes.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
