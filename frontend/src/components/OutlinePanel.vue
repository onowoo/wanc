<template>
  <n-card title="故事大纲" :bordered="true" size="small">
    <n-form label-placement="top" size="small">
      <n-form-item label="一句话卖点（≤30字）">
        <n-input v-model:value="pitch" placeholder="主角困境 + 底牌 + 期待" maxlength="30" show-count />
      </n-form-item>
      <n-form-item label="故事梗概（150-250字）">
        <n-input v-model:value="synopsis" type="textarea" :rows="4" placeholder="开局绝境 → 金手指/转机 → 对抗主线 → 中期反转 → 结局" />
      </n-form-item>
      <n-form-item label="分集大纲（重点标注节奏节点）">
        <n-data-table
          :columns="columns"
          :data="outline"
          :bordered="false"
          size="small"
          :row-key="(row) => row.index"
        />
      </n-form-item>
      <n-space justify="end">
        <n-button secondary @click="addRow">+ 加一集大纲</n-button>
        <n-button type="primary" :loading="saving" @click="save">保存大纲</n-button>
      </n-space>
    </n-form>
  </n-card>
</template>

<script setup>
import { h, onMounted, ref } from 'vue'
import { NInput, NSelect, NButton, useMessage } from 'naive-ui'
import { getOutline, putOutline } from '../api'

const props = defineProps({ projectId: { type: String, required: true } })
const message = useMessage()

const pitch = ref('')
const synopsis = ref('')
const outline = ref([])
const saving = ref(false)

const nodeOptions = [
  { label: '普通推进', value: '' },
  { label: '开局绝境', value: '开局绝境' },
  { label: '小打脸', value: '小打脸' },
  { label: '中型反转', value: '中型反转' },
  { label: '马甲曝光', value: '马甲曝光' },
  { label: '大反转', value: '大反转' },
  { label: '终极摊牌', value: '终极摊牌' }
]

const columns = [
  { title: '集数', width: 70, key: 'index', render: (row) => row.index },
  {
    title: '本集大纲', key: 'summary',
    render: (row) => h(NInput, {
      value: row.summary, size: 'small',
      onUpdateValue: (v) => (row.summary = v)
    })
  },
  {
    title: '节奏节点', key: 'node_type', width: 150,
    render: (row) => h(NSelect, {
      value: row.node_type, size: 'small', options: nodeOptions,
      onUpdateValue: (v) => (row.node_type = v)
    })
  },
  {
    title: '', key: '_del', width: 50,
    render: (row) => h(NButton, {
      size: 'tiny', text: true, type: 'error', onClick: () => removeRow(row.index)
    }, () => '删')
  }
]

function addRow() {
  const max = outline.value.length ? Math.max(...outline.value.map(r => r.index)) : 0
  outline.value.push({ index: max + 1, summary: '', node_type: '' })
}
function removeRow(index) {
  outline.value = outline.value.filter(r => r.index !== index)
}

async function load() {
  const d = await getOutline(props.projectId)
  pitch.value = d.pitch || ''
  synopsis.value = d.synopsis || ''
  outline.value = (d.outline || []).map(o => ({ ...o }))
}

async function save() {
  saving.value = true
  try {
    await putOutline(props.projectId, { pitch: pitch.value, synopsis: synopsis.value, outline: outline.value })
    message.success('大纲已保存')
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
