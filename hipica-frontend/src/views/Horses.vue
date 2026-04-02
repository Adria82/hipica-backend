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

      <!-- Sin resultados (búsqueda sin coincidencias) -->
      <template #no-results>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("horses.empty") }}
        </v-alert>
      </template>

      <!-- Sin datos (lista vacía) -->
      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("horses.empty") }}
        </v-alert>
      </template>

      <!-- Botones de acción en el footer, a la derecha -->
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

const headers = computed(() => [
  { title: t("horses.table.id"),     key: "id",        sortable: true },
  { title: t("horses.table.name"),   key: "name",      sortable: true },
  { title: t("horses.table.box"),    key: "box",       sortable: true },
  { title: t("horses.table.active"), key: "is_active", sortable: true },
  { title: t("horses.table.stable"), key: "stable_id", sortable: true },
]);

// Usada solo para el export (respeta el filtro de búsqueda)
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

function exportToExcel() {
  const rows = filteredHorses.value.map((h) => ({
    [t("horses.table.id")]:     h.id,
    [t("horses.table.name")]:   h.name,
    [t("horses.table.box")]:    h.box ?? "-",
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
