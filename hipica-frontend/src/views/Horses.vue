<template>
  <div style="max-width: 900px; margin: 40px auto; font-family: system-ui;">
    <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
      <LanguageSelector />
    </div>

    <div style="display:flex; justify-content: space-between; align-items:center;">
      <h2>{{ t("horses.title") }}</h2>
      <button @click="logout" style="padding: 8px 10px;">{{ t("horses.logout") }}</button>
    </div>

    <button @click="load" :disabled="loading" style="padding: 10px; margin: 10px 0;">
      {{ loading ? t("horses.loading") : t("horses.reload") }}
    </button>

    <p v-if="error" style="color:#b00020;">{{ error }}</p>

    <table v-if="horses.length" border="1" cellpadding="8" cellspacing="0" style="width:100%;">
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
        <tr v-for="h in horses" :key="h.id">
          <td>{{ h.id }}</td>
          <td>{{ h.name }}</td>
          <td>{{ h.box ?? "-" }}</td>
          <td>{{ h.is_active }}</td>
          <td>{{ h.stable_id }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else-if="!loading">{{ t("horses.empty") }}</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { http } from "../api/http";
import { clearTokens } from "../auth/tokens";
import type { Horse } from "../types/api";
import LanguageSelector from "../components/LanguageSelector.vue";

const router = useRouter();
const { t } = useI18n();
const horses = ref<Horse[]>([]);
const loading = ref(false);
const error = ref("");

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

function logout() {
  clearTokens();
  router.push({ name: "login" });
}

onMounted(load);
</script>
