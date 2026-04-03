<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("profile.title") }}</h2>

    <v-card max-width="480" variant="outlined">
      <!-- Avatar section -->
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

      <v-list lines="two">
        <v-list-item
          prepend-icon="mdi-email-outline"
          :title="t('profile.email')"
          :subtitle="userProfile?.email ?? '—'"
        />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-shield-account-outline"
          :title="t('profile.role')"
          :subtitle="roleLabel"
        />
        <v-divider v-if="userProfile?.stable_name || userProfile?.stable_id" />
        <v-list-item
          v-if="userProfile?.stable_name || userProfile?.stable_id"
          prepend-icon="mdi-home-outline"
          :title="t('profile.stable')"
          :subtitle="userProfile?.stable_name ?? String(userProfile?.stable_id)"
        />
      </v-list>

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
    <v-dialog v-model="dialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-4">{{ t("profile.dialog.title") }}</v-card-title>
        <v-divider />
        <v-card-text class="pa-4">
          <v-text-field
            v-model="form.email"
            :label="t('profile.dialog.email')"
            type="email"
            variant="outlined"
            density="compact"
            autofocus
          />
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
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { http } from "../api/http";
import { userProfile, fetchProfile } from "../auth/profile";
import type { UserProfile } from "../types/api";

const { t } = useI18n();

const dialog = ref(false);
const saving = ref(false);
const form = ref({ email: "" });

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

function openEditDialog() {
  form.value = { email: userProfile.value?.email ?? "" };
  dialog.value = true;
}

async function save() {
  saving.value = true;
  try {
    await http.put<UserProfile>("/api/v1/me/profile", { email: form.value.email });
    await fetchProfile();
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
