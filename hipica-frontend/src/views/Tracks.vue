<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("tracks.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="tracks"
      :search="search"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <template #top>
        <v-text-field
          v-model="search"
          :placeholder="t('tracks.search')"
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
          {{ t("tracks.empty") }}
        </v-alert>
      </template>

      <template #bottom>
        <div class="d-flex justify-space-between align-center ga-2 pa-2">
          <v-btn
            v-if="canManage"
            color="primary"
            variant="tonal"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            {{ t("tracks.addButton") }}
          </v-btn>
          <div v-else />

          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-file-excel"
              color="success"
              variant="tonal"
              :disabled="!tracks.length"
              :title="t('tracks.exportExcel')"
              @click="exportToExcel"
            />
            <v-btn
              icon="mdi-refresh"
              color="primary"
              variant="tonal"
              :loading="loading"
              :title="t('tracks.reload')"
              @click="load"
            />
          </div>
        </div>
      </template>
    </v-data-table>

    <!-- Diálogo crear / editar -->
    <v-dialog v-model="dialog" max-width="440" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingId ? t("tracks.dialog.titleEdit") : t("tracks.dialog.titleCreate") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-row dense>
            <v-col v-if="isAppAdmin" cols="12">
              <v-select
                v-model="form.stable_id"
                :label="t('tracks.dialog.stable')"
                :items="stables"
                item-title="name"
                item-value="id"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.name"
                :label="t('tracks.dialog.name')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-switch
                v-model="form.is_active"
                :label="t('tracks.table.active')"
                color="success"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-btn
            v-if="editingId && canManage"
            color="error"
            variant="text"
            :disabled="saving || deleting"
            @click="confirmDeleteDialog = true"
          >
            {{ t("tracks.dialog.delete") }}
          </v-btn>
          <v-spacer />
          <v-btn variant="text" :disabled="saving || deleting" @click="dialog = false">
            {{ t("tracks.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            :disabled="deleting"
            @click="save"
          >
            {{ t("tracks.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmación de eliminación -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("tracks.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("tracks.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("tracks.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteTrack">
            {{ t("tracks.dialog.delete") }}
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
import type { Track, Stable } from "../types/api";
import { canManage, isAppAdmin } from "../auth/profile";

const { t } = useI18n();
const tracks = ref<Track[]>([]);
const stables = ref<Stable[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editingId = ref<number | null>(null);
const confirmDeleteDialog = ref(false);
const form = ref({ name: "", is_active: true, stable_id: null as number | null });

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const headers = computed(() => [
  { title: t("tracks.table.id"),     key: "id",        sortable: true },
  { title: t("tracks.table.name"),   key: "name",      sortable: true },
  { title: t("tracks.table.active"), key: "is_active", sortable: true },
  { title: t("tracks.table.stable"), key: "stable_id", sortable: true },
]);

const filteredTracks = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return tracks.value;
  return tracks.value.filter((tr) => tr.name.toLowerCase().includes(q));
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const requests: Promise<any>[] = [http.get<Track[]>("/api/v1/tracks")];
    if (isAppAdmin.value) requests.push(http.get<Stable[]>("/api/v1/stables"));
    const [tracksRes, stablesRes] = await Promise.all(requests);
    tracks.value = tracksRes.data;
    if (stablesRes) stables.value = stablesRes.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("tracks.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Track }) {
  openEditDialog(row.item);
}

function openCreateDialog() {
  editingId.value = null;
  form.value = { name: "", is_active: true, stable_id: null };
  dialog.value = true;
}

function openEditDialog(track: Track) {
  editingId.value = track.id;
  form.value = { name: track.name, is_active: track.is_active, stable_id: track.stable_id };
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    const payload: Record<string, any> = { name: form.value.name };
    if (editingId.value) payload.is_active = form.value.is_active;
    if (isAppAdmin.value && form.value.stable_id) payload.stable_id = form.value.stable_id;

    if (editingId.value) {
      const res = await http.put<Track>(`/api/v1/tracks/${editingId.value}`, payload);
      const idx = tracks.value.findIndex((tr) => tr.id === editingId.value);
      if (idx !== -1) tracks.value[idx] = res.data;
    } else {
      const res = await http.post<Track>("/api/v1/tracks/", payload);
      tracks.value.push(res.data);
    }
    dialog.value = false;
    showSnackbar(t("tracks.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("tracks.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteTrack() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/tracks/${editingId.value}`);
    tracks.value = tracks.value.filter((tr) => tr.id !== editingId.value);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("tracks.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    showSnackbar(e?.response?.data?.detail || t("tracks.deleteError"), "error");
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
  const rows = filteredTracks.value.map((tr) => ({
    [t("tracks.table.id")]:     tr.id,
    [t("tracks.table.name")]:   tr.name,
    [t("tracks.table.active")]: tr.is_active ? "✓" : "✗",
    [t("tracks.table.stable")]: tr.stable_id,
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("tracks.title"));
  XLSX.writeFile(wb, `${t("tracks.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
