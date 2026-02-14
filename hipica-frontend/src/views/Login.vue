<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="hipica-card">
          <v-card-title class="d-flex align-center">
            <div>
              <h2 style="margin:0">{{ t("login.title") }}</h2>
            </div>
            <v-spacer />
            <LanguageSelector />
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="onSubmit">
              <v-text-field
                v-model="email"
                :label="t('login.email')"
                type="email"
                required
                autocomplete="username"
              />

              <v-text-field
                v-model="password"
                :label="t('login.password')"
                type="password"
                required
                autocomplete="current-password"
              />

              <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
                {{ error }}
              </v-alert>

              <v-card-actions>
                <v-spacer />
                <v-btn class="hipica" :loading="loading" type="submit">
                  {{ loading ? t("login.submitting") : t("login.submit") }}
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
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
