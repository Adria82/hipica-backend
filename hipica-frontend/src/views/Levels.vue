<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("levels.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="levels"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <template #[`item.name`]="{ item }">
        {{ t(`levels.names.${item.name}`) }}
      </template>

      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("levels.empty") }}
        </v-alert>
      </template>

      <template #bottom>
        <div class="d-flex justify-space-between align-center pa-2">
          <v-btn
            color="primary"
            variant="tonal"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            {{ t("levels.addButton") }}
          </v-btn>
          <v-btn
            icon="mdi-refresh"
            color="primary"
            variant="tonal"
            :loading="loading"
            @click="load"
          />
        </div>
      </template>
    </v-data-table>

    <!-- Diálogo crear -->
    <v-dialog v-model="dialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ t("levels.dialog.titleCreate") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-select
            v-model="form.name"
            :label="t('levels.dialog.name')"
            :items="levelOptions"
            variant="outlined"
            density="compact"
            required
          />
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="saving" @click="dialog = false">
            {{ t("levels.dialog.cancel") }}
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="save">
            {{ t("levels.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo confirmar eliminar (al hacer click en fila) -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("levels.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("levels.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("levels.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteLevel">
            {{ t("levels.dialog.delete") }}
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
import { http } from "../api/http";
import type { Level } from "../types/api";

const { t } = useI18n();
const levels = ref<Level[]>([]);
const loading = ref(false);
const error = ref("");

const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const deletingId = ref<number | null>(null);
const form = ref({ name: "" });

const confirmDeleteDialog = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const ALL_LEVELS = ["principiante", "iniciado", "experto"];

const levelOptions = computed(() =>
  ALL_LEVELS
    .filter((l) => !levels.value.some((existing) => existing.name === l))
    .map((l) => ({ title: t(`levels.names.${l}`), value: l }))
);

const headers = computed(() => [
  { title: t("levels.table.id"),   key: "id",   sortable: true },
  { title: t("levels.table.name"), key: "name", sortable: true },
]);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await http.get<Level[]>("/api/v1/levels");
    levels.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("levels.error");
  } finally {
    loading.value = false;
  }
}

function openCreateDialog() {
  form.value = { name: "" };
  dialog.value = true;
}

function onRowClick(_event: Event, row: { item: Level }) {
  deletingId.value = row.item.id;
  confirmDeleteDialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    const res = await http.post<Level>("/api/v1/levels/", { name: form.value.name });
    levels.value.push(res.data);
    dialog.value = false;
    showSnackbar(t("levels.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("levels.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteLevel() {
  if (!deletingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/levels/${deletingId.value}`);
    levels.value = levels.value.filter((l) => l.id !== deletingId.value);
    confirmDeleteDialog.value = false;
    showSnackbar(t("levels.dialog.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    showSnackbar(e?.response?.data?.detail || t("levels.dialog.deleteError"), "error");
  } finally {
    deleting.value = false;
  }
}

function showSnackbar(text: string, color: string) {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

onMounted(load);
</script>
