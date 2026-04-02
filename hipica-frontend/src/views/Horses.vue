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

      <!-- Columna box: null → "-" -->
      <template #[`item.box`]="{ item }">
        {{ item.box ?? "-" }}
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
          {{ t(`horses.levels.${lvl}`) }}
        </v-chip>
      </template>

      <!-- Sin resultados -->
      <template #no-results>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("horses.empty") }}
        </v-alert>
      </template>

      <!-- Sin datos -->
      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("horses.empty") }}
        </v-alert>
      </template>

      <!-- Botones de acción en el footer -->
      <template #bottom>
        <div class="d-flex justify-end ga-2 pa-2">
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
      </template>
    </v-data-table>

    <!-- Diálogo de edición -->
    <v-dialog v-model="dialog" max-width="520" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ t("horses.dialog.title") }}
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-row dense>
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
              <v-text-field
                v-model="form.box"
                :label="t('horses.table.box')"
                variant="outlined"
                density="compact"
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
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="saving"
            @click="dialog = false"
          >
            {{ t("horses.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            @click="save"
          >
            {{ t("horses.dialog.save") }}
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
import type { Horse } from "../types/api";

const { t } = useI18n();
const horses = ref<Horse[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

// Diálogo
const dialog = ref(false);
const saving = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ name: "", box: "", is_active: true, levels: [] as string[] });

// Snackbar
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const levelOptions = computed(() => [
  { title: t("horses.levels.principiante"), value: "principiante" },
  { title: t("horses.levels.iniciado"),     value: "iniciado" },
  { title: t("horses.levels.experto"),      value: "experto" },
]);

const headers = computed(() => [
  { title: t("horses.table.id"),     key: "id",        sortable: true  },
  { title: t("horses.table.name"),   key: "name",      sortable: true  },
  { title: t("horses.table.box"),    key: "box",       sortable: true  },
  { title: t("horses.table.levels"), key: "levels",    sortable: false },
  { title: t("horses.table.active"), key: "is_active", sortable: true  },
  { title: t("horses.table.stable"), key: "stable_id", sortable: true  },
]);

// Para export respetando el filtro de búsqueda
const filteredHorses = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return horses.value;
  return horses.value.filter(
    (h) =>
      h.name.toLowerCase().includes(q) ||
      (h.box ?? "").toString().toLowerCase().includes(q)
  );
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await http.get<Horse[]>("/api/v1/horses");
    horses.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("horses.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Horse }) {
  openDialog(row.item);
}

function openDialog(horse: Horse) {
  editingId.value = horse.id;
  form.value = {
    name:      horse.name,
    box:       horse.box ?? "",
    is_active: horse.is_active,
    levels:    [...horse.levels],
  };
  dialog.value = true;
}

async function save() {
  if (!editingId.value) return;
  saving.value = true;
  try {
    const res = await http.put<Horse>(`/api/v1/horses/${editingId.value}`, {
      name:      form.value.name,
      box:       form.value.box || null,
      is_active: form.value.is_active,
      levels:    form.value.levels,
    });
    // Actualizar el registro en la lista local sin recargar
    const idx = horses.value.findIndex((h) => h.id === editingId.value);
    if (idx !== -1) horses.value[idx] = res.data;
    dialog.value = false;
    showSnackbar(t("horses.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("horses.saveError"), "error");
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
  const rows = filteredHorses.value.map((h) => ({
    [t("horses.table.id")]:     h.id,
    [t("horses.table.name")]:   h.name,
    [t("horses.table.box")]:    h.box ?? "-",
    [t("horses.table.levels")]: h.levels.map((l) => t(`horses.levels.${l}`)).join(", "),
    [t("horses.table.active")]: h.is_active ? "✓" : "✗",
    [t("horses.table.stable")]: h.stable_id,
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("horses.title"));
  XLSX.writeFile(wb, `${t("horses.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
