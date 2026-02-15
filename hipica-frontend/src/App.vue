<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>Hípica</v-app-bar-title>
      <v-spacer></v-spacer>
      <language-selector />
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import LanguageSelector from "./components/LanguageSelector.vue";
</script>