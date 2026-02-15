<template>
  <v-app>
    <!-- Barra superior -->
    <v-app-bar color="primary">
      <v-app-bar-title>Hípica</v-app-bar-title>

      <v-spacer />

      <!-- aquí luego pondremos usuario/logout -->
      <language-selector />
    </v-app-bar>

    <!-- Aquí irán vistas hijas -->
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import LanguageSelector from "@/components/LanguageSelector.vue";
</script>
