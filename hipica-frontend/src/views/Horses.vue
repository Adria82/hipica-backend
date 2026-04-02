<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("horses.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <!-- Buscador -->
    <v-text-field
      v-model="search"
      :placeholder="t('horses.search')"
      prepend-inner-icon="mdi-magnify"
      variant="outlined"
      density="compact"
      clearable
      @click:clear="search = ''"
      hide-details
      class="mb-4"
    />

    <!-- Tabla -->
    <v-table v-if="filteredHorses.length || loading" hover>
      <thead>
        <tr>
          <th>{{ t("horses.table.id") }}</th>
          <th>{{ t("horses.table.name") }}</th>
          <th>{{ t("horses.table.box") }}</th>
          <th>{{ t("horses.table.active") }}</th>
          <th>{{ t("horses.table.stable") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="5" class="text-center py-6">
            <v-progress-circular indeterminate color="primary" size="28" />
          </td>
        </tr>
        <tr v-else v-for="h in filteredHorses" :key="h.id">
          <td>{{ h.id }}</td>
          <td>{{ h.name }}</td>
          <td>{{ h.box ?? "-" }}</td>
          <td>
            <v-icon :color="h.is_active ? 'success' : 'error'" size="20">
              {{ h.is_active ? "mdi-check-circle" : "mdi-close-circle" }}
            </v-icon>
          </td>
          <td>{{ h.stable_id }}</td>
        </tr>
      </tbody>
    </v-table>

    <v-alert v-else-if="!loading" type="warning" variant="tonal" class="mt-4">
      {{ t("horses.empty") }}
    </v-alert>

    <!-- Acciones bajo la tabla -->
    <div class="d-flex justify-end ga-2 mt-4">
      <v-btn
        icon="mdi-file-excel"
        color="success"
        variant="tonal"
        :disabled="!filteredHorses.length"
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
    [t("horses.table.id")]: h.id,
    [t("horses.table.name")]: h.name,
    [t("horses.table.box")]: h.box ?? "-",
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
