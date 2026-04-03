<template>
  <v-container>
    <h2 class="text-h5 mb-4">{{ t("profile.title") }}</h2>

    <v-card max-width="480" variant="outlined">
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
        <v-divider v-if="userProfile?.stable_id" />
        <v-list-item
          v-if="userProfile?.stable_id"
          prepend-icon="mdi-home-outline"
          :title="t('profile.stable')"
          :subtitle="String(userProfile.stable_id)"
        />
      </v-list>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { userProfile } from "../auth/profile";

const { t } = useI18n();

const roleLabel = computed(() => {
  const role = userProfile.value?.role;
  if (!role) return "—";
  const key = `profile.roles.${role}`;
  const translated = t(key);
  return translated !== key ? translated : role;
});
</script>
