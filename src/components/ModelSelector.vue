<script setup>
defineProps({ models: Array })
</script>

<template>
  <div class="selector" v-if="models && models.length">
    <button
      v-for="m in models" :key="m.id"
      class="btn"
    >
      {{ m.id }}
    </button>
  </div>
</template>

<style scoped>
.selector { display: flex; gap: 6px; margin-bottom: 8px; }
.btn {
  flex: 1; background: #0E1223; color: #94A3B8;
  border: 1px solid transparent; border-radius: 5px;
  padding: 6px 8px; font-size: 9px; font-family: monospace;
  cursor: pointer; opacity: 0.6;
}
.btn:first-child { border-color: #059669; opacity: 1; color: #E2E8F0; }
.btn:hover { border-color: #059669; opacity: 0.8; }
</style>
