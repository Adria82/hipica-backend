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
      <template #[`item.names`]="{ item }">
        {{ localeName(item) }}
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

    <!-- Diálogo crear / editar -->
    <v-dialog v-model="dialog" max-width="420" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingId ? t("levels.dialog.titleEdit") : t("levels.dialog.titleCreate") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-row dense>
            <v-col cols="12">
              <v-text-field
                v-model="form.es"
                :label="t('levels.dialog.nameEs')"
                variant="outlined"
                density="compact"
                autofocus
                required
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.en"
                :label="t('levels.dialog.nameEn')"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.ca"
                :label="t('levels.dialog.nameCa')"
                variant="outlined"
                density="compact"
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
            :loading="deleting"
            @click="confirmDelete"
          >
            {{ t("levels.dialog.delete") }}
          </v-btn>
          <v-spacer />
          <v-btn variant="text" :disabled="saving || deleting" @click="dialog = false">
            {{ t("levels.dialog.cancel") }}
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="save">
            {{ t("levels.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo confirmar eliminar -->
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

const { t, locale } = useI18n();
const levels = ref<Level[]>([]);
const loading = ref(false);
const error = ref("");

const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ es: "", en: "", ca: "" });

const confirmDeleteDialog = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const headers = computed(() => [
  { title: t("levels.table.id"),   key: "id",    sortable: true },
  { title: t("levels.table.name"), key: "names", sortable: false },
]);

function localeName(level: Level): string {
  console.log("[Levels] item:", JSON.stringify(level));
  if (!level?.names) return `??${level?.id}`;
  const lang = locale.value;
  if (lang === "es") return level.names.es || level.names.ca || level.names.en || "";
  if (lang === "en") return level.names.en || level.names.es || level.names.ca || "";
  return level.names.ca || level.names.es || level.names.en || "";
}

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
  editingId.value = null;
  form.value = { es: "", en: "", ca: "" };
  dialog.value = true;
}

function onRowClick(_event: Event, row: { item: Level }) {
  editingId.value = row.item.id;
  form.value = {
    es: row.item.names.es ?? "",
    en: row.item.names.en ?? "",
    ca: row.item.names.ca ?? "",
  };
  dialog.value = true;
}

function confirmDelete() {
  dialog.value = false;
  confirmDeleteDialog.value = true;
}

async function save() {
  saving.value = true;
  const payload = { names: { es: form.value.es, en: form.value.en, ca: form.value.ca } };
  try {
    if (editingId.value) {
      const res = await http.put<Level>(`/api/v1/levels/${editingId.value}`, payload);
      const idx = levels.value.findIndex((l) => l.id === editingId.value);
      if (idx !== -1) levels.value[idx] = res.data;
      dialog.value = false;
      showSnackbar(t("levels.saveSuccessEdit"), "success");
    } else {
      const res = await http.post<Level>("/api/v1/levels/", payload);
      levels.value.push(res.data);
      dialog.value = false;
      showSnackbar(t("levels.saveSuccess"), "success");
    }
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("levels.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteLevel() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/levels/${editingId.value}`);
    levels.value = levels.value.filter((l) => l.id !== editingId.value);
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
