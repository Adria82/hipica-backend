<template>
  <div style="max-width: 420px; margin: 60px auto; font-family: system-ui;">
    <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
      <LanguageSelector />
    </div>

    <h2>{{ t("login.title") }}</h2>

    <form @submit.prevent="onSubmit" style="display: grid; gap: 12px;">
      <label>
        {{ t("login.email") }}
        <input v-model="email" type="email" required style="width: 100%; padding: 10px;" />
      </label>

      <label>
        {{ t("login.password") }}
        <input v-model="password" type="password" required style="width: 100%; padding: 10px;" />
      </label>

      <button :disabled="loading" style="padding: 10px;">
        {{ loading ? t("login.submitting") : t("login.submit") }}
      </button>

      <p v-if="error" style="color: #b00020;">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { setTokens } from "../auth/tokens";
import { getAppLocale } from "../i18n";
import type { TokenResponse } from "../types/api";
import LanguageSelector from "../components/LanguageSelector.vue";

const router = useRouter();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;
const { t } = useI18n();

const email = ref("abe@hipica.com");
const password = ref("qwerty");
const loading = ref(false);
const error = ref("");

async function onSubmit() {
  loading.value = true;
  error.value = "";

  try {
    const form = new URLSearchParams();
    form.append("username", email.value);
    form.append("password", password.value);

    const res = await axios.post<TokenResponse>(`${API_BASE_URL}/api/v1/auth/login`, form, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Language": getAppLocale(),
      },
    });

    setTokens(res.data);
    router.push({ name: "horses" });
  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("login.error");
  } finally {
    loading.value = false;
  }
}
</script>
