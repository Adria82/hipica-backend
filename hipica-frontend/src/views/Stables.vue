<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("stables.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="stables"
      :search="search"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <template #top>
        <v-text-field
          v-model="search"
          :placeholder="t('stables.search')"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @click:clear="search = ''"
          hide-details
          class="ma-3"
        />
      </template>

      <template #[`item.is_active`]="{ item }">
        <v-icon :color="item.is_active ? 'success' : 'error'" size="20">
          {{ item.is_active ? "mdi-check-circle" : "mdi-close-circle" }}
        </v-icon>
      </template>

      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("stables.empty") }}
        </v-alert>
      </template>

      <template #bottom>
        <div class="d-flex justify-space-between align-center ga-2 pa-2">
          <v-btn
            color="primary"
            variant="tonal"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            {{ t("stables.addButton") }}
          </v-btn>
          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-file-excel"
              color="success"
              variant="tonal"
              :disabled="!stables.length"
              :title="t('stables.exportExcel')"
              @click="exportToExcel"
            />
            <v-btn
              icon="mdi-refresh"
              color="primary"
              variant="tonal"
              :loading="loading"
              :title="t('stables.reload')"
              @click="load"
            />
          </div>
        </div>
      </template>
    </v-data-table>

    <!-- Diálogo crear / editar -->
    <v-dialog v-model="dialog" max-width="480" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingId ? t("stables.dialog.titleEdit") : t("stables.dialog.titleCreate") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-row dense>
            <v-col cols="12">
              <v-text-field
                v-model="form.name"
                :label="t('stables.dialog.name')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.location"
                :label="t('stables.dialog.location')"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-switch
                v-model="form.is_active"
                :label="t('stables.dialog.active')"
                color="success"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-btn
            v-if="editingId"
            color="error"
            variant="text"
            :disabled="saving || deleting"
            @click="confirmDeleteDialog = true"
          >
            {{ t("stables.dialog.delete") }}
          </v-btn>
          <v-spacer />
          <v-btn variant="text" :disabled="saving || deleting" @click="dialog = false">
            {{ t("stables.dialog.cancel") }}
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" :disabled="deleting" @click="save">
            {{ t("stables.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmación de eliminación -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("stables.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("stables.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("stables.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteStable">
            {{ t("stables.dialog.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
import type { Stable } from "../types/api";

const { t } = useI18n();
const stables = ref<Stable[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ name: "", location: "", is_active: true });

const confirmDeleteDialog = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const headers = computed(() => [
  { title: t("stables.table.id"),       key: "id",        sortable: true },
  { title: t("stables.table.name"),     key: "name",      sortable: true },
  { title: t("stables.table.location"), key: "location",  sortable: true },
  { title: t("stables.table.active"),   key: "is_active", sortable: true },
]);

const filteredStables = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return stables.value;
  return stables.value.filter((s) => s.name.toLowerCase().includes(q));
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await http.get<Stable[]>("/api/v1/stables");
    stables.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("stables.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Stable }) {
  editingId.value = row.item.id;
  form.value = { name: row.item.name, location: row.item.location, is_active: row.item.is_active };
  dialog.value = true;
}

function openCreateDialog() {
  editingId.value = null;
  form.value = { name: "", location: "", is_active: true };
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    if (editingId.value) {
      const res = await http.patch<Stable>(`/api/v1/stables/${editingId.value}`, {
        name: form.value.name,
        location: form.value.location,
        is_active: form.value.is_active,
      });
      const idx = stables.value.findIndex((s) => s.id === editingId.value);
      if (idx !== -1) stables.value[idx] = res.data;
    } else {
      const res = await http.post<Stable>("/api/v1/stables/", {
        name: form.value.name,
        location: form.value.location,
        is_active: form.value.is_active,
      });
      stables.value.push(res.data);
    }
    dialog.value = false;
    showSnackbar(t("stables.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("stables.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteStable() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/stables/${editingId.value}`);
    stables.value = stables.value.filter((s) => s.id !== editingId.value);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("stables.dialog.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    showSnackbar(e?.response?.data?.detail || t("stables.dialog.deleteError"), "error");
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
  const rows = filteredStables.value.map((s) => ({
    [t("stables.table.id")]:       s.id,
    [t("stables.table.name")]:     s.name,
    [t("stables.table.location")]: s.location,
    [t("stables.table.active")]:   s.is_active ? "✓" : "✗",
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("stables.title"));
  XLSX.writeFile(wb, `${t("stables.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
