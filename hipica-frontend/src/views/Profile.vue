<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("profile.title") }}</h2>

    <v-card max-width="560" variant="outlined">
      <!-- Sección avatar -->
      <v-card-text class="d-flex flex-column align-center pa-6">
        <v-avatar size="96" class="mb-3" color="primary">
          <v-img v-if="userProfile?.avatar" :src="userProfile.avatar" cover />
          <v-icon v-else icon="mdi-account" size="56" color="white" />
        </v-avatar>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-camera"
          @click="triggerFileInput"
        >
          {{ t("profile.uploadPhoto") }}
        </v-btn>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="onFileChange"
        />
      </v-card-text>

      <v-divider />

      <!-- Datos básicos del usuario -->
      <v-list lines="two">
        <v-list-item
          prepend-icon="mdi-account-outline"
          :title="t('profile.name')"
          :subtitle="userProfile?.name ?? '—'"
        />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-badge-account-outline"
          :title="t('profile.apellidos')"
          :subtitle="userProfile?.apellidos ?? '—'"
        />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-email-outline"
          :title="t('profile.email')"
          :subtitle="userProfile?.email ?? '—'"
        />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-card-account-details-outline"
          :title="t('profile.dni')"
          :subtitle="userProfile?.dni ?? '-'"
        />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-phone-outline"
          :title="t('profile.phone')"
          :subtitle="userProfile?.phone ?? '—'"
        />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-shield-account-outline"
          :title="t('profile.role')"
          :subtitle="roleLabel"
        />
        <template v-if="userProfile?.stable_name || userProfile?.stable_id">
          <v-divider />
          <v-list-item
            prepend-icon="mdi-home-outline"
            :title="t('profile.stable')"
            :subtitle="userProfile?.stable_name ?? String(userProfile?.stable_id)"
          />
        </template>
      </v-list>

      <!-- Datos extendidos del perfil (si existen) -->
      <template v-if="hasExtendedProfile">
        <v-divider />
        <v-card-subtitle class="pa-4 font-weight-bold text-medium-emphasis">
          {{ t("profile.extendedTitle") }}
        </v-card-subtitle>

        <!-- Perfil cliente -->
        <template v-if="userProfile?.role === 'client' && clientProfile">
          <v-list lines="two">
            <v-list-item
              v-if="clientProfile.direccion"
              prepend-icon="mdi-map-marker-outline"
              :title="t('profile.fields.direccion')"
              :subtitle="clientProfile.direccion"
            />
            <v-divider v-if="clientProfile.direccion" />
            <v-list-item
              v-if="clientProfile.iban"
              prepend-icon="mdi-bank-outline"
              :title="t('profile.fields.iban')"
              :subtitle="clientProfile.iban"
            />
            <v-divider v-if="clientProfile.iban" />
            <v-list-item
              v-if="clientProfile.level_id"
              prepend-icon="mdi-podium"
              :title="t('profile.fields.level')"
              :subtitle="levelName(clientProfile.level_id)"
            />
            <v-divider v-if="clientProfile.level_id" />
            <v-list-item
              v-if="clientProfile.notes"
              prepend-icon="mdi-note-text-outline"
              :title="t('profile.fields.notes')"
              :subtitle="clientProfile.notes"
            />
          </v-list>
        </template>

        <!-- Perfil monitor/ayudante -->
        <template v-if="isMonitorRole && monitorProfile">
          <v-list lines="two">
            <v-list-item
              v-if="monitorProfile.especialidad"
              prepend-icon="mdi-medal-outline"
              :title="t('profile.fields.especialidad')"
              :subtitle="monitorProfile.especialidad"
            />
            <v-divider v-if="monitorProfile.especialidad" />
            <v-list-item
              v-if="monitorProfile.certificados"
              prepend-icon="mdi-certificate-outline"
              :title="t('profile.fields.certificados')"
              :subtitle="monitorProfile.certificados"
            />
            <v-divider v-if="monitorProfile.certificados" />
            <v-list-item
              v-if="monitorProfile.experiencia"
              prepend-icon="mdi-briefcase-outline"
              :title="t('profile.fields.experiencia')"
              :subtitle="monitorProfile.experiencia"
            />
            <v-divider v-if="monitorProfile.experiencia" />
            <v-list-item
              v-if="monitorProfile.disponibilidad"
              prepend-icon="mdi-calendar-clock"
              :title="t('profile.fields.disponibilidad')"
              :subtitle="monitorProfile.disponibilidad"
            />
            <v-divider v-if="monitorProfile.disponibilidad" />
            <v-list-item
              v-if="monitorProfile.iban"
              prepend-icon="mdi-bank-outline"
              :title="t('profile.fields.iban')"
              :subtitle="monitorProfile.iban"
            />
            <v-divider v-if="monitorProfile.iban" />
            <v-list-item
              v-if="monitorProfile.tarifa_hora != null"
              prepend-icon="mdi-currency-eur"
              :title="t('profile.fields.tarifa_hora')"
              :subtitle="String(monitorProfile.tarifa_hora)"
            />
            <v-divider v-if="monitorProfile.tarifa_hora != null" />
            <v-list-item
              v-if="monitorProfile.notas"
              prepend-icon="mdi-note-text-outline"
              :title="t('profile.fields.notas')"
              :subtitle="monitorProfile.notas"
            />
          </v-list>
        </template>
      </template>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="primary"
          variant="tonal"
          prepend-icon="mdi-pencil"
          @click="openEditDialog"
        >
          {{ t("profile.editButton") }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Diálogo editar perfil -->
    <v-dialog v-model="dialog" max-width="520" persistent scrollable>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("profile.dialog.title") }}</v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <!-- Campos básicos -->
          <v-text-field
            v-model="form.name"
            :label="t('profile.dialog.name')"
            variant="outlined"
            density="compact"
            class="mb-3"
            autofocus
          />
          <v-text-field
            v-model="form.apellidos"
            :label="t('profile.dialog.apellidos')"
            variant="outlined"
            density="compact"
            class="mb-3"
          />
          <v-text-field
            v-model="form.email"
            :label="t('profile.dialog.email')"
            type="email"
            variant="outlined"
            density="compact"
            class="mb-3"
          />
          <v-text-field
            v-model="form.dni"
            :label="t('profile.dialog.dni')"
            variant="outlined"
            density="compact"
            class="mb-3"
          />
          <v-text-field
            v-model="form.phone"
            :label="t('profile.dialog.phone')"
            variant="outlined"
            density="compact"
            class="mb-3"
          />

          <!-- Campos cliente -->
          <template v-if="userProfile?.role === 'client'">
            <v-divider class="mb-4" />
            <div class="text-subtitle-2 font-weight-bold mb-3 text-medium-emphasis">
              {{ t("profile.dialog.clientSection") }}
            </div>
            <v-text-field
              v-model="extForm.direccion"
              :label="t('profile.dialog.direccion')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-text-field
              v-model="extForm.iban"
              :label="t('profile.dialog.iban')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-select
              v-model="extForm.level_id"
              :label="t('profile.dialog.level')"
              :items="levelItems"
              item-title="label"
              item-value="id"
              variant="outlined"
              density="compact"
              clearable
              class="mb-3"
            />
            <v-textarea
              v-model="extForm.notes"
              :label="t('profile.dialog.notes')"
              variant="outlined"
              density="compact"
              rows="2"
              class="mb-3"
            />
          </template>

          <!-- Campos monitor/ayudante -->
          <template v-if="isMonitorRole">
            <v-divider class="mb-4" />
            <div class="text-subtitle-2 font-weight-bold mb-3 text-medium-emphasis">
              {{ t("profile.dialog.monitorSection") }}
            </div>
            <v-text-field
              v-model="monExtForm.especialidad"
              :label="t('profile.dialog.especialidad')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-text-field
              v-model="monExtForm.certificados"
              :label="t('profile.dialog.certificados')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-text-field
              v-model="monExtForm.experiencia"
              :label="t('profile.dialog.experiencia')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-text-field
              v-model="monExtForm.disponibilidad"
              :label="t('profile.dialog.disponibilidad')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-text-field
              v-model="monExtForm.iban"
              :label="t('profile.dialog.iban')"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-text-field
              v-model.number="monExtForm.tarifa_hora"
              :label="t('profile.dialog.tarifa_hora')"
              type="number"
              variant="outlined"
              density="compact"
              class="mb-3"
            />
            <v-textarea
              v-model="monExtForm.notas"
              :label="t('profile.dialog.notas')"
              variant="outlined"
              density="compact"
              rows="2"
              class="mb-3"
            />
          </template>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" :disabled="saving" @click="dialog = false">
            {{ t("profile.dialog.cancel") }}
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="save">
            {{ t("profile.dialog.save") }}
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
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "../api/http";
import { userProfile, fetchProfile } from "../auth/profile";
import type { UserProfile, ClientProfileData, MonitorProfileData, Level } from "../types/api";

const { t, locale } = useI18n();

const dialog = ref(false);
const saving = ref(false);

// Estado del perfil extendido cargado
const clientProfile = ref<ClientProfileData | null>(null);
const monitorProfile = ref<MonitorProfileData | null>(null);
const levels = ref<Level[]>([]);

// Formulario campos básicos
const form = ref({ name: "", apellidos: "", email: "", dni: "", phone: "" });

// Formulario campos extendidos cliente
const extForm = ref<ClientProfileData>({
  direccion: null,
  iban: null,
  notes: null,
  level_id: null,
});

// Formulario campos extendidos monitor/ayudante
const monExtForm = ref<MonitorProfileData>({
  especialidad: null,
  disponibilidad: null,
  certificados: null,
  experiencia: null,
  telefono: null,
  iban: null,
  notas: null,
  tarifa_hora: null,
});

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");
const fileInput = ref<HTMLInputElement | null>(null);

const roleLabel = computed(() => {
  const role = userProfile.value?.role;
  if (!role) return "—";
  const key = `profile.roles.${role}`;
  const translated = t(key);
  return translated !== key ? translated : role;
});

const isMonitorRole = computed(() =>
  userProfile.value?.role === "monitor" || userProfile.value?.role === "assistant"
);

const hasExtendedProfile = computed(() =>
  userProfile.value?.role === "client" || isMonitorRole.value
);

type LangKey = "es" | "ca" | "en";

function localizedName(names: { es: string; en: string; ca: string }): string {
  const lang = locale.value as LangKey;
  return names[lang] ?? names["es"];
}

const levelItems = computed(() =>
  levels.value.map((l) => ({
    id: l.id,
    label: localizedName(l.names),
  }))
);

function levelName(levelId: number): string {
  const l = levels.value.find((lv) => lv.id === levelId);
  return l ? localizedName(l.names) : String(levelId);
}

async function loadExtendedProfile() {
  if (!userProfile.value?.id) return;
  if (!hasExtendedProfile.value) return;

  try {
    const { data } = await http.get(`/api/v1/users/${userProfile.value.id}/profile`);
    if (userProfile.value.role === "client") {
      clientProfile.value = data as ClientProfileData;
    } else {
      monitorProfile.value = data as MonitorProfileData;
    }
  } catch {
    // Sin perfil extendido todavía
  }
}

async function loadLevels() {
  if (userProfile.value?.role !== "client") return;
  try {
    const { data } = await http.get<Level[]>("/api/v1/levels");
    levels.value = data;
  } catch {
    // Niveles no críticos
  }
}

onMounted(async () => {
  await loadExtendedProfile();
  await loadLevels();
});

function openEditDialog() {
  form.value = {
    name: userProfile.value?.name ?? "",
    apellidos: userProfile.value?.apellidos ?? "",
    email: userProfile.value?.email ?? "",
    dni: userProfile.value?.dni ?? "",
    phone: userProfile.value?.phone ?? "",
  };

  if (userProfile.value?.role === "client" && clientProfile.value) {
    extForm.value = { ...clientProfile.value };
  } else {
    extForm.value = { direccion: null, iban: null, notes: null, level_id: null };
  }

  if (isMonitorRole.value && monitorProfile.value) {
    monExtForm.value = { ...monitorProfile.value };
  } else {
    monExtForm.value = { especialidad: null, disponibilidad: null, certificados: null, experiencia: null, telefono: null, iban: null, notas: null, tarifa_hora: null };
  }

  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    // Guardar campos básicos del usuario
    await http.put<UserProfile>("/api/v1/me/profile", {
      name: form.value.name || undefined,
      apellidos: form.value.apellidos || undefined,
      email: form.value.email || undefined,
      dni: form.value.dni || undefined,
      phone: form.value.phone || undefined,
    });

    // Guardar perfil extendido si aplica
    if (userProfile.value?.id && hasExtendedProfile.value) {
      if (userProfile.value.role === "client") {
        await http.put(`/api/v1/users/${userProfile.value.id}/profile`, extForm.value);
      } else if (isMonitorRole.value) {
        await http.put(`/api/v1/users/${userProfile.value.id}/profile`, monExtForm.value);
      }
    }

    await fetchProfile();
    await loadExtendedProfile();
    dialog.value = false;
    showSnackbar(t("profile.saveSuccess"), "success");
  } catch (e: any) {
    showSnackbar(e?.response?.data?.detail || t("profile.saveError"), "error");
  } finally {
    saving.value = false;
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

function onFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const dataUrl = e.target?.result as string;
    try {
      await http.put<UserProfile>("/api/v1/me/profile", { avatar: dataUrl });
      await fetchProfile();
      showSnackbar(t("profile.saveSuccess"), "success");
    } catch {
      showSnackbar(t("profile.saveError"), "error");
    }
  };
  reader.readAsDataURL(file);
}

function showSnackbar(text: string, color: string) {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}
</script>

