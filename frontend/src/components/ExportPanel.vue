<template>
  <n-card title="导出" :bordered="true" size="small">
    <n-space>
      <n-button type="primary" :loading="loadingMd" @click="doExportMd">生成 Markdown 投稿包</n-button>
      <n-button secondary :loading="loadingJson" @click="doExportJson">导出结构化 JSON</n-button>
    </n-space>

    <template v-if="markdownContent">
      <n-divider style="margin: 14px 0" />
      <n-alert v-if="exportedPath" type="success" :show-icon="false">
        已生成文件：{{ exportedPath }}
      </n-alert>
      <n-divider style="margin: 12px 0" />
      <n-text strong>Markdown 预览</n-text>
      <n-collapse style="margin-top: 8px">
        <n-collapse-item title="点击展开预览 / 复制全文">
          <pre style="white-space: pre-wrap; background: #f6f7f9; padding: 14px; border-radius: 6px; font-size: 12px; max-height: 480px; overflow: auto">{{ markdownContent }}</pre>
        </n-collapse-item>
      </n-collapse>
      <n-button size="small" secondary style="margin-top: 8px" @click="copyMd">复制 Markdown 全文</n-button>
    </template>

    <template v-if="jsonText">
      <n-divider style="margin: 14px 0" />
      <n-text strong>JSON 预览</n-text>
      <pre style="white-space: pre-wrap; background: #f6f7f9; padding: 14px; border-radius: 6px; font-size: 12px; max-height: 480px; overflow: auto">{{ jsonText }}</pre>
    </template>
  </n-card>
</template>

<script setup>
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import { exportMarkdown, exportJson } from '../api'

const props = defineProps({ projectId: { type: String, required: true } })
const message = useMessage()

const loadingMd = ref(false)
const loadingJson = ref(false)
const markdownContent = ref('')
const exportedPath = ref('')
const jsonText = ref('')

async function doExportMd() {
  loadingMd.value = true
  try {
    const r = await exportMarkdown(props.projectId)
    markdownContent.value = r.content
    exportedPath.value = r.path
    jsonText.value = ''
    message.success('投稿包已生成')
  } catch (e) {
    message.error(e.message)
  } finally {
    loadingMd.value = false
  }
}

async function doExportJson() {
  loadingJson.value = true
  try {
    const r = await exportJson(props.projectId)
    jsonText.value = JSON.stringify(r, null, 2)
    message.success('JSON 已导出')
  } catch (e) {
    message.error(e.message)
  } finally {
    loadingJson.value = false
  }
}

async function copyMd() {
  await navigator.clipboard.writeText(markdownContent.value)
  message.success('已复制')
}
</script>
