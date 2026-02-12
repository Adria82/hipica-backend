<template>
  <div style="max-width: 420px; margin: 60px auto; font-family: system-ui;">
    <h2>Login</h2>

    <form @submit.prevent="onSubmit" style="display: grid; gap: 12px;">
      <label>
        Email
        <input v-model="email" type="email" required style="width: 100%; padding: 10px;" />
      </label>

      <label>
        Contraseña
        <input v-model="password" type="password" required style="width: 100%; padding: 10px;" />
      </label>

      <button :disabled="loading" style="padding: 10px;">
        {{ loading ? "Entrando..." : "Entrar" }}
      </button>

      <p v-if="error" style="color: #b00020;">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { setTokens } from "../auth/tokens";
import type { TokenResponse } from "../types/api";

const router = useRouter();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

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
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    setTokens(res.data);
    router.push({ name: "horses" });
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "No se pudo iniciar sesión";
  } finally {
    loading.value = false;
  }
}
</script>
