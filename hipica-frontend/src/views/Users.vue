<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("users.title") }}</h2>

    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="users"
      :search="search"
      :loading="loading"
      hover
      @click:row="onRowClick"
    >
      <!-- Buscador -->
      <template #top>
        <v-text-field
          v-model="search"
          :placeholder="t('users.search')"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @click:clear="search = ''"
          hide-details
          class="ma-3"
        />
      </template>

      <!-- Columna rol: chip con color -->
      <template #[`item.role`]="{ item }">
        <v-chip :color="roleColor(item.role)" size="small" variant="tonal">
          {{ t(`users.roles.${item.role}`) }}
        </v-chip>
      </template>

      <!-- Columna hípica -->
      <template #[`item.stable_id`]="{ item }">
        {{ stableName(item.stable_id) }}
      </template>

      <!-- Columna activo -->
      <template #[`item.is_active`]="{ item }">
        <v-icon :color="item.is_active ? 'success' : 'error'" size="20">
          {{ item.is_active ? "mdi-check-circle" : "mdi-close-circle" }}
        </v-icon>
      </template>

      <!-- Sin datos -->
      <template #no-data>
        <v-alert type="warning" variant="tonal" class="ma-4">
          {{ t("users.empty") }}
        </v-alert>
      </template>

      <!-- Footer con acciones -->
      <template #bottom>
        <div class="d-flex justify-space-between align-center ga-2 pa-2">
          <v-btn
            v-if="canManage"
            color="primary"
            variant="tonal"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            {{ t("users.addButton") }}
          </v-btn>
          <div v-else />

          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-file-excel"
              color="success"
              variant="tonal"
              :disabled="!users.length"
              :title="t('users.exportExcel')"
              @click="exportToExcel"
            />
            <v-btn
              icon="mdi-refresh"
              color="primary"
              variant="tonal"
              :loading="loading"
              :title="t('users.reload')"
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
          {{ editingId ? t("users.dialog.titleEdit") : t("users.dialog.titleCreate") }}
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-row dense>
            <!-- Hípica — solo app_admin -->
            <v-col v-if="isAppAdmin" cols="12">
              <v-select
                v-model="form.stable_id"
                :label="t('users.dialog.stable')"
                :items="stables"
                item-title="name"
                item-value="id"
                variant="outlined"
                density="compact"
                clearable
              />
            </v-col>

            <!-- Nombre -->
            <v-col cols="12">
              <v-text-field
                v-model="form.name"
                :label="t('users.dialog.name')"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>

            <!-- Email -->
            <v-col cols="12">
              <v-text-field
                v-model="form.email"
                :label="t('users.dialog.email')"
                type="email"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>

            <!-- Password — solo en creación -->
            <v-col v-if="!editingId" cols="12">
              <v-text-field
                v-model="form.password"
                :label="t('users.dialog.password')"
                type="password"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>

            <!-- Rol -->
            <v-col cols="12">
              <v-select
                v-model="form.role"
                :label="t('users.dialog.role')"
                :items="availableRoles"
                item-title="title"
                item-value="value"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>

            <!-- Activo -->
            <v-col cols="12">
              <v-switch
                v-model="form.is_active"
                :label="t('users.dialog.active')"
                color="success"
                hide-details
              />
            </v-col>

            <!-- Sección datos adicionales — visible siempre que el rol tenga perfil -->
            <template v-if="['client','monitor','assistant'].includes(form.role)">
              <v-col cols="12">
                <v-divider class="mt-2 mb-3" />
                <div class="text-caption text-medium-emphasis mb-2">{{ t("users.dialog.profileSection") }}</div>
              </v-col>

              <!-- Teléfono -->
              <v-col cols="12">
                <v-text-field
                  v-model="form.phone"
                  :label="t('users.dialog.phone')"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <!-- Campos client -->
              <template v-if="form.role === 'client'">
                <v-col cols="12">
                  <v-text-field
                    v-model="clientProfile.apellidos"
                    :label="t('users.dialog.clientProfile.apellidos')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="clientProfile.direccion"
                    :label="t('users.dialog.clientProfile.direccion')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="clientProfile.iban"
                    :label="t('users.dialog.clientProfile.iban')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <!-- Nivel de equitación -->
                <v-col cols="6">
                  <v-select
                    v-model="clientProfile.level_id"
                    :label="t('users.dialog.clientProfile.level')"
                    :items="levelOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    density="compact"
                    clearable
                  />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="clientProfile.notes"
                    :label="t('users.dialog.clientProfile.notes')"
                    variant="outlined"
                    density="compact"
                    rows="2"
                    auto-grow
                  />
                </v-col>
              </template>

              <!-- Campos monitor / assistant -->
              <template v-if="['monitor','assistant'].includes(form.role)">
                <v-col cols="12">
                  <v-text-field
                    v-model="monitorProfile.especialidad"
                    :label="t('users.dialog.monitorProfile.especialidad')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="monitorProfile.certificados"
                    :label="t('users.dialog.monitorProfile.certificados')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="monitorProfile.experiencia"
                    :label="t('users.dialog.monitorProfile.experiencia')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="monitorProfile.iban"
                    :label="t('users.dialog.monitorProfile.iban')"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="monitorProfile.tarifa_hora"
                    :label="t('users.dialog.monitorProfile.tarifa_hora')"
                    type="number"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="monitorProfile.notas"
                    :label="t('users.dialog.monitorProfile.notas')"
                    variant="outlined"
                    density="compact"
                    rows="2"
                    auto-grow
                  />
                </v-col>

                <!-- Constructor de horario semanal -->
                <v-col cols="12">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <div class="text-caption text-medium-emphasis">{{ t("users.dialog.monitorProfile.schedule") }}</div>
                    <v-btn size="x-small" variant="tonal" color="primary" prepend-icon="mdi-plus" @click="addScheduleDay">
                      {{ t("users.dialog.monitorProfile.addDay") }}
                    </v-btn>
                  </div>
                  <div v-for="(dayEntry, di) in schedule" :key="di" class="mb-3 pa-2 rounded" style="border:1px solid rgba(0,0,0,0.12)">
                    <div class="d-flex align-center gap-2 mb-2">
                      <v-select
                        v-model="dayEntry.day"
                        :items="weekdayOptions"
                        item-title="label"
                        item-value="value"
                        density="compact"
                        variant="outlined"
                        hide-details
                        :label="t('users.dialog.monitorProfile.selectDay')"
                        style="max-width:180px"
                      />
                      <v-spacer />
                      <v-btn icon="mdi-delete-outline" size="x-small" color="error" variant="text" @click="removeScheduleDay(di)" />
                    </div>
                    <div v-for="(slot, si) in dayEntry.slots" :key="si" class="d-flex align-center gap-2 mb-1">
                      <v-text-field
                        v-model="slot.from"
                        :label="t('users.dialog.monitorProfile.from')"
                        type="time"
                        density="compact"
                        variant="outlined"
                        hide-details
                        style="max-width:130px"
                      />
                      <v-text-field
                        v-model="slot.to"
                        :label="t('users.dialog.monitorProfile.to')"
                        type="time"
                        density="compact"
                        variant="outlined"
                        hide-details
                        style="max-width:130px"
                      />
                      <v-btn icon="mdi-close" size="x-small" color="error" variant="text" @click="removeScheduleSlot(di, si)" />
                    </div>
                    <v-btn size="x-small" variant="text" color="primary" prepend-icon="mdi-plus" class="mt-1" @click="addScheduleSlot(di)">
                      {{ t("users.dialog.monitorProfile.addSlot") }}
                    </v-btn>
                  </div>
                </v-col>
              </template>
            </template>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <!-- Eliminar — solo app_admin al editar -->
          <v-btn
            v-if="editingId && isAppAdmin"
            color="error"
            variant="text"
            :disabled="saving || deleting"
            @click="confirmDeleteDialog = true"
          >
            {{ t("users.dialog.delete") }}
          </v-btn>

          <v-spacer />

          <!-- Cambiar contraseña — solo app_admin al editar -->
          <v-btn
            v-if="editingId && isAppAdmin"
            color="warning"
            variant="text"
            :disabled="saving || deleting"
            @click="openChangePasswordDialog"
          >
            {{ t("users.dialog.changePassword") }}
          </v-btn>

          <v-btn variant="text" :disabled="saving || deleting" @click="dialog = false">
            {{ t("users.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            :disabled="deleting"
            @click="save"
          >
            {{ t("users.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo cambiar contraseña -->
    <v-dialog v-model="changePasswordDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("users.dialog.changePasswordTitle") }}</v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-row dense>
            <v-col cols="12">
              <v-text-field
                v-model="changePasswordForm.password"
                :label="t('users.dialog.newPassword')"
                type="password"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="changePasswordForm.confirm"
                :label="t('users.dialog.confirmPassword')"
                type="password"
                variant="outlined"
                density="compact"
                :error-messages="changePasswordForm.confirm && changePasswordForm.password !== changePasswordForm.confirm ? t('users.dialog.passwordMismatch') : ''"
                required
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="changingPassword" @click="changePasswordDialog = false">
            {{ t("users.dialog.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="changingPassword"
            :disabled="!changePasswordForm.password || changePasswordForm.password !== changePasswordForm.confirm"
            @click="changePassword"
          >
            {{ t("users.dialog.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo confirmación eliminación -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("users.dialog.delete") }}</v-card-title>
        <v-card-text class="pa-4">{{ t("users.dialog.confirmDelete") }}</v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="deleting" @click="confirmDeleteDialog = false">
            {{ t("users.dialog.cancel") }}
          </v-btn>
          <v-btn color="error" variant="flat" :loading="deleting" @click="deleteUser">
            {{ t("users.dialog.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
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
import type { UserRead, Stable, ClientProfile, MonitorProfile } from "../types/api";
import { canManage, isAppAdmin } from "../auth/profile";

// --- Tipos para el horario del monitor ---
interface TimeSlot { from: string; to: string }
interface DayScheduleEntry { day: string; slots: TimeSlot[] }
const WEEKDAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"] as const;

const { t, locale } = useI18n();

const users = ref<UserRead[]>([]);
const stables = ref<Stable[]>([]);
const levels = ref<{ id: number; names: Record<string, string> }[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");

// Diálogo
const dialog = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editingId = ref<number | null>(null);
const form = ref({
  name: "",
  email: "",
  password: "",
  role: "client",
  phone: null as string | null,
  stable_id: null as number | null,
  is_active: true,
});

const clientProfile = ref<ClientProfile & { level_id?: number | null }>({ apellidos: null, direccion: null, iban: null, notes: null, level_id: null });
const monitorProfile = ref<MonitorProfile>({ especialidad: null, disponibilidad: null, certificados: null, experiencia: null, telefono: null, iban: null, notas: null, tarifa_hora: null });
const schedule = ref<DayScheduleEntry[]>([]);

// Confirmación de eliminación
const confirmDeleteDialog = ref(false);

// Cambiar contraseña
const changePasswordDialog = ref(false);
const changingPassword = ref(false);
const changePasswordForm = ref({ password: "", confirm: "" });

// Snackbar
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

// Roles disponibles según el rol del usuario actual
const availableRoles = computed(() => {
  const all = [
    { title: t("users.roles.app_admin"),    value: "app_admin"    },
    { title: t("users.roles.stable_admin"), value: "stable_admin" },
    { title: t("users.roles.monitor"),      value: "monitor"      },
    { title: t("users.roles.assistant"),    value: "assistant"    },
    { title: t("users.roles.client"),       value: "client"       },
  ];
  if (isAppAdmin.value) return all;
  // stable_admin puede asignar monitor, assistant o client
  return all.filter((r) => ["monitor", "assistant", "client"].includes(r.value));
});

const headers = computed(() => [
  { title: t("users.table.id"),     key: "id",        sortable: true  },
  { title: t("users.table.name"),   key: "name",      sortable: true  },
  { title: t("users.table.email"),  key: "email",     sortable: true  },
  { title: t("users.table.role"),   key: "role",      sortable: true  },
  { title: t("users.table.stable"), key: "stable_id", sortable: false },
  { title: t("users.table.active"), key: "is_active", sortable: true  },
]);

// Opciones de nivel para el selector del perfil cliente
const levelOptions = computed(() =>
  levels.value.map((l) => ({
    value: l.id,
    title: l.names[locale.value as "es"|"ca"|"en"] || l.names["es"] || String(l.id),
  }))
);

// Opciones de días de la semana para el selector del horario monitor
const weekdayOptions = computed(() =>
  WEEKDAYS.map((d) => ({ value: d, label: t(`users.days.${d}`) }))
);

// Mapa id → nombre de hípica para la columna de tabla
const stableMap = computed(() => {
  const map: Record<number, string> = {};
  for (const s of stables.value) map[s.id] = s.name;
  return map;
});

function stableName(stableId: number | null): string {
  if (stableId == null) return "-";
  return stableMap.value[stableId] ?? String(stableId);
}

function roleColor(role: string): string {
  const colors: Record<string, string> = {
    app_admin:    "error",
    stable_admin: "warning",
    monitor:      "info",
    client:       "success",
  };
  return colors[role] ?? "default";
}

// Para export respetando el filtro de búsqueda
const filteredUsers = computed(() => {
  const q = (search.value ?? "").trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter(
    (u) =>
      u.name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q)
  );
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const requests: Promise<any>[] = [
      http.get<UserRead[]>("/api/v1/users"),
      http.get("/api/v1/levels"),
    ];
    if (isAppAdmin.value) requests.push(http.get<Stable[]>("/api/v1/stables"));
    const [usersRes, levelsRes, stablesRes] = await Promise.all(requests);
    users.value = usersRes.data;
    levels.value = levelsRes.data;
    if (stablesRes) stables.value = stablesRes.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("users.error");
  } finally {
    loading.value = false;
  }
}

function onRowClick(_event: Event, row: { item: UserRead }) {
  if (canManage.value) openEditDialog(row.item);
}

function openCreateDialog() {
  editingId.value = null;
  form.value = { name: "", email: "", password: "", role: "client", phone: null, stable_id: null, is_active: true };
  clientProfile.value = { apellidos: null, direccion: null, iban: null, notes: null, level_id: null };
  monitorProfile.value = { especialidad: null, disponibilidad: null, certificados: null, experiencia: null, telefono: null, iban: null, notas: null, tarifa_hora: null };
  schedule.value = [];
  dialog.value = true;
}

async function openEditDialog(user: UserRead) {
  editingId.value = user.id;
  form.value = {
    name:      user.name,
    email:     user.email,
    password:  "",
    role:      user.role,
    phone:     user.phone,
    stable_id: user.stable_id,
    is_active: user.is_active,
  };
  clientProfile.value = { apellidos: null, direccion: null, iban: null, notes: null, level_id: null };
  monitorProfile.value = { especialidad: null, disponibilidad: null, certificados: null, experiencia: null, telefono: null, iban: null, notas: null, tarifa_hora: null };
  schedule.value = [];
  if (["client", "monitor", "assistant"].includes(user.role)) {
    try {
      const res = await http.get(`/api/v1/users/${user.id}/profile`);
      if (res.data) {
        if (user.role === "client") {
          clientProfile.value = { ...clientProfile.value, ...res.data };
        } else {
          const { disponibilidad, ...rest } = res.data;
          monitorProfile.value = { ...monitorProfile.value, ...rest };
          // Deserializar horario guardado como JSON en disponibilidad
          if (disponibilidad) {
            try { schedule.value = JSON.parse(disponibilidad); } catch { schedule.value = []; }
          }
        }
      }
    } catch { /* perfil vacío — no bloquear apertura del diálogo */ }
  }
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    if (editingId.value) {
      // PUT — sin password
      const payload: Record<string, any> = {
        name:      form.value.name,
        email:     form.value.email,
        role:      form.value.role,
        phone:     form.value.phone ?? null,
        is_active: form.value.is_active,
      };
      if (isAppAdmin.value) payload.stable_id = form.value.stable_id ?? null;

      const res = await http.put<UserRead>(`/api/v1/users/${editingId.value}`, payload);
      const idx = users.value.findIndex((u) => u.id === editingId.value);
      if (idx !== -1) users.value[idx] = res.data;

      // Guardar perfil extendido si corresponde
      if (form.value.role === "client") {
        await http.put(`/api/v1/users/${editingId.value}/profile`, clientProfile.value);
      } else if (["monitor", "assistant"].includes(form.value.role)) {
        const profilePayload = {
          ...monitorProfile.value,
          disponibilidad: schedule.value.length ? JSON.stringify(schedule.value) : null,
        };
        await http.put(`/api/v1/users/${editingId.value}/profile`, profilePayload);
      }
    } else {
      // POST — incluye password
      const payload: Record<string, any> = {
        name:      form.value.name,
        email:     form.value.email,
        password:  form.value.password,
        role:      form.value.role,
        phone:     form.value.phone ?? null,
        is_active: form.value.is_active,
      };
      if (isAppAdmin.value && form.value.stable_id) {
        payload.stable_id = form.value.stable_id;
      }

      const res = await http.post<UserRead>("/api/v1/users/", payload);
      users.value.push(res.data);
      // Guardar perfil del nuevo usuario si aplica
      if (form.value.role === "client") {
        await http.put(`/api/v1/users/${res.data.id}/profile`, clientProfile.value).catch(() => {});
      } else if (["monitor", "assistant"].includes(form.value.role)) {
        const profilePayload = { ...monitorProfile.value, disponibilidad: schedule.value.length ? JSON.stringify(schedule.value) : null };
        await http.put(`/api/v1/users/${res.data.id}/profile`, profilePayload).catch(() => {});
      }
    }

    dialog.value = false;
    showSnackbar(t("users.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("users.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteUser() {
  if (!editingId.value) return;
  deleting.value = true;
  try {
    await http.delete(`/api/v1/users/${editingId.value}`);
    users.value = users.value.filter((u) => u.id !== editingId.value);
    confirmDeleteDialog.value = false;
    dialog.value = false;
    showSnackbar(t("users.dialog.deleteSuccess"), "success");
  } catch (e: any) {
    confirmDeleteDialog.value = false;
    showSnackbar(e?.response?.data?.detail || t("users.dialog.deleteError"), "error");
  } finally {
    deleting.value = false;
  }
}

function showSnackbar(text: string, color: string) {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

// --- Horario semanal del monitor ---
function addScheduleDay() {
  schedule.value.push({ day: "monday", slots: [{ from: "09:00", to: "13:00" }] });
}
function removeScheduleDay(di: number) {
  schedule.value.splice(di, 1);
}
function addScheduleSlot(di: number) {
  schedule.value[di].slots.push({ from: "09:00", to: "13:00" });
}
function removeScheduleSlot(di: number, si: number) {
  schedule.value[di].slots.splice(si, 1);
}

// --- Cambiar contraseña ---
function openChangePasswordDialog() {
  changePasswordForm.value = { password: "", confirm: "" };
  changePasswordDialog.value = true;
}

async function changePassword() {
  if (!editingId.value || changePasswordForm.value.password !== changePasswordForm.value.confirm) return;
  changingPassword.value = true;
  try {
    await http.put(`/api/v1/users/${editingId.value}/password`, { password: changePasswordForm.value.password });
    changePasswordDialog.value = false;
    showSnackbar(t("users.dialog.passwordChanged"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("users.saveError"), "error");
  } finally {
    changingPassword.value = false;
  }
}

function exportToExcel() {
  const rows = filteredUsers.value.map((u) => ({
    [t("users.table.id")]:     u.id,
    [t("users.table.name")]:   u.name,
    [t("users.table.email")]:  u.email,
    [t("users.table.role")]:   t(`users.roles.${u.role}`),
    [t("users.table.stable")]: stableName(u.stable_id),
    [t("users.table.active")]: u.is_active ? "✓" : "✗",
  }));
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, t("users.title"));
  XLSX.writeFile(wb, `${t("users.title").toLowerCase()}.xlsx`);
}

onMounted(load);
</script>
