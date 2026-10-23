<template>
  <n-card title="版本管理" :bordered="true" size="small">
    <template #header-extra>
      <n-space>
        <n-input v-model:value="label" size="small" placeholder="备注，如：导入前5集" style="width: 180px" />
        <n-button size="small" secondary @click="saveSnapshot">存当前版本</n-button>
      </n-space>
    </template>
    <n-empty v-if="versions.length === 0" description="暂无版本快照" style="padding: 30px 0" />
    <n-data-table
      v-else
      :columns="columns"
      :data="versions"
      :bordered="false"
      size="small"
      :row-key="(row) => row.version"
      :pagination="false"
    />
    <n-divider style="margin: 12px 0" />
    <n-space align="center" size="small">
      <n-select v-model:value="diffA" :options="versionOptions" placeholder="版本 A" style="width: 200px" clearable />
      <n-text>对比</n-text>
      <n-select v-model:value="diffB" :options="versionOptions" placeholder="版本 B" style="width: 200px" clearable />
      <n-button size="small" secondary :disabled="!diffA || !diffB" @click="doDiff">Diff</n-button>
    </n-space>
    <pre v-if="diffText" style="white-space: pre-wrap; background: #f6f7f9; padding: 12px; border-radius: 6px; max-height: 360px; overflow: auto; font-size: 12px">{{ diffText }}</pre>
  </n-card>
</template>

<script setup>
import { computed, h, onMounted, ref } from 'vue'
import { NButton, NPopconfirm, useMessage } from 'naive-ui'
import { listVersions, createVersion, restoreVersion, diffVersions } from '../api'

const props = defineProps({ projectId: { type: String, required: true } })
const message = useMessage()

const versions = ref([])
const label = ref('')
const diffA = ref(null)
const diffB = ref(null)
const diffText = ref('')

const versionOptions = computed(() => versions.value.map(v => ({ label: `${v.version} ${v.label}`, value: v.version })))

const columns = [
  { title: '版本', key: 'version', width: 170 },
  { title: '备注', key: 'label' },
  {
    title: '操作', key: '_op', width: 150,
    render: (row) => h(NPopconfirm, {
      onPositiveClick: () => doRestore(row.version)
    }, {
      trigger: () => h(NButton, { size: 'tiny', type: 'warning', secondary: true }, () => '回滚'),
      default: () => '确认回滚到该版本？会先备份当前状态'
    })
  }
]

async function load() {
  versions.value = await listVersions(props.projectId)
}
async function saveSnapshot() {
  await createVersion(props.projectId, label.value || '手动快照')
  message.success('已存版本')
  label.value = ''
  load()
}
async function doRestore(version) {
  try {
    const r = await restoreVersion(props.projectId, version)
    message.success(`已回滚到 ${r.restored}（${r.episode_count} 集）`)
    load()
  } catch (e) {
    message.error(e.message)
  }
}
async function doDiff() {
  try {
    const r = await diffVersions(props.projectId, diffA.value, diffB.value)
    diffText.value = r.diff.join('\n') || '（两个版本正文一致）'
  } catch (e) {
    message.error(e.message)
  }
}

onMounted(load)
</script>
