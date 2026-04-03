<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("clients.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="clients"
      :search="search"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <template #top>
        <v-text-field
          v-model="search"
          :placeholder="t('clients.search')"
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

      <template #[`item.email`]="{ item }">
        {{ item.email ?? "-" }}
      </template>

      <template #[`item.phone`]="{ item }">
        {{ item.phone ?? "-" }}
      </template>

      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("clients.empty") }}
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
            {{ t("clients.addButton") }}
          </v-btn>
          <div v-else />
          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-file-excel"
              color="success"
              variant="tonal"
              :disabled="!clients.length"
              :title="t('clients.exportExcel')"
              @click="exportToExcel"
            />
            <v-btn
              icon="mdi-refresh"
              color="primary"
              variant="tonal"
              :loading="loading"
              :title="t('clients.reload')"
              @click="load"
            />
          </div>
        </div>
      </template>
    </v-data-table>

    <!-- Diálogo crear / editar -->
    <v-dialog v-model="dialog" max-width="520" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">
          {{ editingId ? t("clients.dialog.titleEdit") : t("clients.dialog.titleCreate") }}
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-row dense>
            <v-col v-if="isAppAdmin" cols="12">
              <v-select
                v-model="form.stable_id"
                :label="t('clients.dialog.stable')"
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
                :label="t('clients.dialog.name')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.email"
                :label="t('clients.dialog.email')"
                variant="outlined"
                density="compact"
                type="email"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.phone"
                :label="t('clients.dialog.phone')"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-switch
                v-model="form.is_active"
                :label="t('clients.dialog.active')"
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
            {{ t("clients.dialog.delete") }}
          </v-btn>
          <v-spacer />
          <v-btn variant="text" :disabled="saving || deleting" @click="dialog = false">
            {{ t("clients.dialog.cancel") }}
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" :disabled="deleting" @click="save">
            {{ t("clients.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmación de eliminación -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("clients.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("clients.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("clients.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteClient">
            {{ t("clients.dialog.delete") }}
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
import type { Client, Stable } from "../types/api";
import { canManage, isAppAdmin } from "../auth/profile";

const { t } = useI18n();
const clients = ref<Client[]>([]);
const stables = ref<Stable[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ name: "", email: "", phone: "", is_active: true, stable_id: null as number | null });

const confirmDeleteDialog = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const headers = computed(() => [
  { title: t("clients.table.id"),     key: "id",        sortable: true },
  { title: t("clients.table.name"),   key: "name",      sortable: true },
  { title: t("clients.table.email"),  key: "email",     sortable: true },
  { title: t("clients.table.phone"),  key: "phone",     sortable: false },
  { title: t("clients.table.active"), key: "is_active", sortable: true },
  { title: t("clients.table.stable"), key: "stable_name", sortable: true },
]);

const filteredClients = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return clients.value;
  return clients.value.filter(
    (c) =>
      c.name.toLowerCase().includes(q) ||
      (c.email ?? "").toLowerCase().includes(q)
  );
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const requests: Promise<any>[] = [http.get<Client[]>("/api/v1/clients")];
    if (isAppAdmin.value) requests.push(http.get<Stable[]>("/api/v1/stables"));
    const [clientsRes, stablesRes] = await Promise.all(requests);
    clients.value = clientsRes.data;
    if (stablesRes) stables.value = stablesRes.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("clients.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: Client }) {
  editingId.value = row.item.id;
  form.value = {
    name:      row.item.name,
    email:     row.item.email ?? "",
    phone:     row.item.phone ?? "",
    is_active: row.item.is_active,
    stable_id: row.item.stable_id,
  };
  dialog.value = true;
}

function openCreateDialog() {
  editingId.value = null;
  form.value = { name: "", email: "", phone: "", is_active: true, stable_id: null };
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    const payload: Record<string, any> = {
      name:      form.value.name,
      email:     form.value.email || null,
      phone:     form.value.phone || null,
      is_active: form.value.is_active,
    };
    if (isAppAdmin.value && form.value.stable_id) payload.stable_id = form.value.stable_id;

    if (editingId.value) {
      const res = await http.put<Client>(`/api/v1/clients/${editingId.value}`, payload);
      const idx = clients.value.findIndex((c) => c.id === editingId.value);
      if (idx !== -1) clients.value[idx] = res.data;
    } else {
      const res = await http.post<Client>("/api/v1/clients/", payload);
      clients.value.push(res.data);
    }
    dialog.value = false;
    showSnackbar(t("clients.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("clients.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteClient() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/clients/${editingId.value}`);
    clients.value = clients.value.filter((c) => c.id !== editingId.value);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("clients.dialog.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    showSnackbar(e?.response?.data?.detail || t("clients.dialog.deleteError"), "error");
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
  const rows = filteredClients.value.map((c) => ({
    [t("clients.table.id")]:     c.id,
    [t("clients.table.name")]:   c.name,
    [t("clients.table.email")]:  c.email ?? "-",
    [t("clients.table.phone")]:  c.phone ?? "-",
    [t("clients.table.active")]: c.is_active ? "✓" : "✗",
    [t("clients.table.stable")]: c.stable_name ?? c.stable_id,
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("clients.title"));
  XLSX.writeFile(wb, `${t("clients.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
