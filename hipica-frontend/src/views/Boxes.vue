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
        <div class="d-flex justify-end ga-2 pa-2">
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
      </template>
    </v-data-table>

    <!-- Diálogo de edición -->
    <v-dialog v-model="dialog" max-width="480" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ t("boxes.dialog.title") }}
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-row dense>
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
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="saving"
            @click="dialog = false"
          >
            {{ t("boxes.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            @click="save"
          >
            {{ t("boxes.dialog.save") }}
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
import type { Box } from "../types/api";

const { t } = useI18n();
const boxes = ref<Box[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

// Diálogo
const dialog = ref(false);
const saving = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ name: "", capacity: 1, is_active: true });

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
  { title: t("boxes.table.stable"),      key: "stable_id",    sortable: true  },
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
    const res = await http.get<Box[]>("/api/v1/boxes");
    boxes.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("boxes.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Box }) {
  openDialog(row.item);
}

function openDialog(box: Box) {
  editingId.value = box.id;
  form.value = {
    name:      box.name,
    capacity:  box.capacity,
    is_active: box.is_active,
  };
  dialog.value = true;
}

async function save() {
  if (!editingId.value) return;
  saving.value = true;
  try {
    const res = await http.put<Box>(`/api/v1/boxes/${editingId.value}`, {
      name:      form.value.name,
      capacity:  form.value.capacity,
      is_active: form.value.is_active,
    });
    const idx = boxes.value.findIndex((b) => b.id === editingId.value);
    if (idx !== -1) boxes.value[idx] = res.data;
    dialog.value = false;
    showSnackbar(t("boxes.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("boxes.saveError"), "error");
  } finally {
    saving.value = false;
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
    [t("boxes.table.stable")]:      b.stable_id,
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("boxes.title"));
  XLSX.writeFile(wb, `${t("boxes.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
