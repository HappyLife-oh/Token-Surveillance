<script setup>
import { ref } from 'vue'

const emit = defineEmits(['confirm'])
const key = ref('')

function submit() {
  if (key.value.trim()) emit('confirm', key.value.trim())
}
</script>

<template>
  <div class="overlay">
    <div class="dialog">
      <div class="icon">⬡</div>
      <h2>Token Surveillance</h2>
      <p>输入你的 DeepSeek API Key 开始监控用量</p>
      <div class="input-group">
        <input
          v-model="key"
          type="password"
          placeholder="sk-..."
          @keyup.enter="submit"
        />
      </div>
      <button class="confirm-btn" :disabled="!key.trim()" @click="submit">
        确认
      </button>
      <p class="hint">Key 仅保存在本地，不会上传</p>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: #020617;
}
.dialog {
  background: #0E1223; border: 1px solid #1E293B; border-radius: 12px;
  padding: 32px; width: 300px; text-align: center;
}
.icon { font-size: 32px; color: #22C55E; margin-bottom: 8px; }
h2 { color: #F1F5F9; font-size: 16px; margin: 0 0 8px; font-weight: 700; }
p { color: #94A3B8; font-size: 12px; margin: 0 0 20px; }
.input-group { margin-bottom: 16px; }
input {
  width: 100%; box-sizing: border-box;
  background: #020617; border: 1px solid #334155; border-radius: 6px;
  padding: 10px 12px; color: #E2E8F0; font-size: 13px;
  outline: none; font-family: monospace;
}
input:focus { border-color: #059669; }
.confirm-btn {
  background: #059669; color: white; border: none; border-radius: 6px;
  padding: 10px 32px; font-size: 13px; cursor: pointer; width: 100%;
}
.confirm-btn:disabled { opacity: 0.3; cursor: default; }
.hint { color: #475569; font-size: 10px; margin-top: 16px; margin-bottom: 0; }
</style>
