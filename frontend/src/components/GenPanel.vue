<template>
  <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
    <!-- 左：生成配置 + 渲染 prompt -->
    <n-grid-item :span="1">
      <n-card title="生成配置（手动桥接）" :bordered="true" size="small">
        <n-form label-placement="top" size="small">
          <n-form-item label="提示词模板">
            <n-select v-model:value="templateId" :options="templates.map(t => ({ label: t.name, value: t.id }))" />
          </n-form-item>
          <n-form-item label="本次生成指令">
            <n-input v-model:value="instruction" type="textarea" :rows="2"
              placeholder="如：从头生成前5集完整正文 / 续写第11-15集 / 重写第3集钩子" />
          </n-form-item>
          <n-form-item label="携带历史集数（保持连贯，token成本）">
            <n-select v-model:value="historyCount" :options="[
              { label: '不带历史', value: 0 }, { label: '前5集', value: 5 },
              { label: '前10集', value: 10 }, { label: '前20集', value: 20 }
            ]" />
          </n-form-item>
          <n-space justify="end">
            <n-button type="primary" :loading="rendering" @click="render">渲染 Prompt</n-button>
            <n-button secondary :disabled="!fullPrompt" @click="copyPrompt">一键复制</n-button>
          </n-space>
        </n-form>

        <n-divider style="margin: 12px 0" />
        <n-text depth="3" style="font-size: 12px">① 点渲染 → ② 复制 → ③ 粘贴到豆包桌面端生成 → ④ 把返回全文粘贴到右侧导入</n-text>
        <div v-if="fullPrompt" style="margin-top: 8px">
          <n-text style="font-size: 12px; color: #999">已渲染（约 {{ fullPrompt.length }} 字）</n-text>
          <pre style="white-space: pre-wrap; background: #f6f7f9; padding: 12px; border-radius: 6px; max-height: 480px; overflow: auto; font-size: 12px">{{ fullPrompt }}</pre>
        </div>
      </n-card>
    </n-grid-item>

    <!-- 右：导入 + 校验 -->
    <n-grid-item :span="1">
      <n-card title="导入 LLM 返回 & 校验" :bordered="true" size="small">
        <n-input v-model:value="rawText" type="textarea" placeholder="粘贴豆包返回的剧本文本，会自动解析分集、校验、存版本" :rows="14" />
        <n-space justify="end" style="margin-top: 10px">
          <n-button secondary @click="rawText = ''">清空</n-button>
          <n-button type="primary" :loading="importing" @click="doImport">导入并校验</n-button>
        </n-space>

        <template v-if="importResult">
          <n-divider style="margin: 12px 0" />
          <n-space align="center" size="small">
            <n-text strong>解析 {{ importResult.episode_count }} 集</n-text>
            <n-tag :type="scoreType" size="small">质量分 {{ importResult.report.score }}</n-tag>
            <n-text depth="3" style="font-size: 12px">{{ importResult.report.summary }}</n-text>
          </n-space>
          <n-alert v-if="importResult.report.issues.length === 0" type="success" :show-icon="false" style="margin-top: 8px">未发现硬伤，钩子与字数达标</n-alert>
          <n-list v-else bordered style="margin-top: 8px">
            <n-list-item v-for="(iss, i) in importResult.report.issues" :key="i" style="padding: 6px 10px">
              <n-space align="start" size="small">
                <n-tag size="tiny" :type="iss.severity === 'error' ? 'error' : 'warning'">{{ iss.severity }}</n-tag>
                <div style="font-size: 12px; line-height: 1.5">
                  <div>{{ iss.message }}</div>
                  <div v-if="iss.suggestion" style="color: #999">建议：{{ iss.suggestion }}</div>
                </div>
              </n-space>
            </n-list-item>
          </n-list>
        </template>
      </n-card>
    </n-grid-item>
  </n-grid>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { listTemplates, renderPrompt, importScript } from '../api'

const props = defineProps({ projectId: { type: String, required: true } })
const message = useMessage()

const templates = ref([])
const templateId = ref('submit_template')
const instruction = ref('')
const historyCount = ref(0)
const fullPrompt = ref('')
const rendering = ref(false)

const rawText = ref('')
const importing = ref(false)
const importResult = ref(null)

const scoreType = computed(() => {
  if (!importResult.value) return 'default'
  const s = importResult.value.report.score
  return s >= 90 ? 'success' : s >= 70 ? 'warning' : 'error'
})

async function loadTemplates() {
  templates.value = await listTemplates()
  if (templates.value.length && !templates.value.some(t => t.id === templateId.value)) {
    templateId.value = templates.value[0].id
  }
}

async function render() {
  rendering.value = true
  try {
    const r = await renderPrompt(props.projectId, { template_id: templateId.value, instruction: instruction.value, history_count: historyCount.value })
    fullPrompt.value = r.full_prompt
    message.success('Prompt 已渲染')
  } catch (e) {
    message.error(e.message)
  } finally {
    rendering.value = false
  }
}

async function copyPrompt() {
  await navigator.clipboard.writeText(fullPrompt.value)
  message.success('已复制，去豆包桌面端粘贴生成')
}

async function doImport() {
  if (!rawText.value.trim()) return message.warning('请先粘贴剧本文本')
  importing.value = true
  try {
    importResult.value = await importScript(props.projectId, rawText.value, '手动导入')
    message.success(`导入 ${importResult.value.episode_count} 集并已存版本`)
  } catch (e) {
    message.error(e.message)
  } finally {
    importing.value = false
  }
}

onMounted(loadTemplates)
</script>
