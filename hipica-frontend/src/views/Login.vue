<template>
  <v-container class="login-container">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4" class="d-flex justify-center">
        
        <v-card class="mx-auto" width="420" elevation="3">
          <!-- Cabecera -->
          <v-card-title class="d-flex align-center">
            <h2 class="text-h5">{{ t("login.title") }}</h2>
            <v-spacer />
            <!-- Selector de idioma -->
            <language-selector />
          </v-card-title>

          <v-divider />

          <v-card-text>
            <v-form @submit.prevent="onSubmit">

              <!-- Email -->
              <v-text-field
                v-model="email"
                :label="t('login.email')"
                type="email"
                required
                autocomplete="username"
                prepend-inner-icon="mdi-account"
                variant="outlined"
              />

              <!-- Password -->
              <v-text-field
                v-model="password"
                :label="t('login.password')"
                type="password"
                required
                autocomplete="current-password"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
              />

              <!-- Error -->
              <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
                {{ error }}
              </v-alert>

              <!-- Submit -->
              <v-btn
                :loading="loading"
                type="submit"
                color="primary"
                block
                size="large"
              >
                {{ loading ? t("login.submitting") : t("login.submit") }}
              </v-btn>

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

import { setTokens } from "@/auth/tokens";
import { getAppLocale } from "@/i18n";
import type { TokenResponse } from "@/types/api";

import LanguageSelector from "@/components/LanguageSelector.vue";

/**
 * Hook de traducciones (NECESARIO para poder usar t() en el template)
 */
const { t } = useI18n();

const router = useRouter();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

/**
 * Estado del formulario
 */
const email = ref("abe@hipica.com");
const password = ref("qwerty");
const loading = ref(false);
const error = ref("");

/**
 * Envío del formulario de login.
 * Llama al backend (/api/v1/auth/login) usando formato OAuth2 (form-urlencoded).
 */
async function onSubmit() {
  loading.value = true;
  error.value = "";

  try {
    const form = new URLSearchParams();
    form.append("username", email.value);
    form.append("password", password.value);

    const res = await axios.post<TokenResponse>(
      `${API_BASE_URL}/api/v1/auth/login`,
      form,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Accept-Language": getAppLocale(),
        },
      }
    );

    // Guardar tokens en localStorage
    setTokens(res.data);

    // Redirigir a la app
    router.push({ name: "horses" });

  } catch (e: any) {
    error.value = e?.response?.data?.detail || t("login.error");
  } finally {
    loading.value = false;
  }
}
</script>
