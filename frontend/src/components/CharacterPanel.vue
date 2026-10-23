<template>
  <n-grid :cols="2" :x-gap="16">
    <!-- 左：人物列表 -->
    <n-grid-item>
      <n-card title="人物设定" :bordered="true" size="small">
        <template #header-extra>
          <n-button size="small" type="primary" @click="openNew">+ 新增人物</n-button>
        </template>
        <n-empty v-if="chars.length === 0" description="还没有人物，点右上角新增" style="padding: 20px 0" />
        <n-list v-else bordered>
          <n-list-item v-for="c in chars" :key="c.cid" style="padding: 8px 12px">
            <n-space justify="space-between" align="center">
              <n-space align="center" size="small">
                <n-tag :type="roleTag(c.role_type)" size="small">{{ roleLabel(c.role_type) }}</n-tag>
                <span style="font-weight: 600">{{ c.name }}</span>
                <n-text depth="3" style="font-size: 12px">{{ c.cid }}</n-text>
              </n-space>
              <n-space size="small">
                <n-button size="tiny" secondary @click="openEdit(c)">编辑</n-button>
                <n-button size="tiny" type="error" secondary @click="remove(c.cid)">删</n-button>
              </n-space>
            </n-space>
          </n-list-item>
        </n-list>
        <n-divider style="margin: 10px 0" />
        <n-button block secondary @click="showSnapshot = true">预览人设快照（注入 LLM 文本）</n-button>
      </n-card>
    </n-grid-item>

    <!-- 右：编辑表单 -->
    <n-grid-item>
      <n-card :title="editing ? `编辑：${form.name || ''}` : '新增人物'" :bordered="true" size="small">
        <n-form label-placement="top" size="small">
          <n-form-item label="姓名" required>
            <n-input v-model:value="form.name" placeholder="角色名" />
          </n-form-item>
          <n-form-item label="角色类型">
            <n-select v-model:value="form.role_type" :options="roleOptions" />
          </n-form-item>
          <n-form-item label="核心欲望">
            <n-input v-model:value="form.core_desire" placeholder="他/她最想得到/证明什么" type="textarea" :rows="2" />
          </n-form-item>
          <n-form-item label="核心弱点">
            <n-input v-model:value="form.core_weakness" placeholder="致命的性格弱点" type="textarea" :rows="2" />
          </n-form-item>
          <n-form-item label="性格标签">
            <n-dynamic-tags v-model:value="form.personality_tags" />
          </n-form-item>
          <n-form-item label="说话风格">
            <n-input v-model:value="form.speech_style" placeholder="短句克制 / 表面柔弱话里带刺..." />
          </n-form-item>
          <n-form-item label="禁止行为（人设红线）">
            <n-dynamic-tags v-model:value="form.forbidden_behavior" />
          </n-form-item>
          <n-form-item label="固定外貌描述">
            <n-input v-model:value="form.appearance_desc" placeholder="漫剧绘图/投稿用，全程统一" type="textarea" :rows="2" />
          </n-form-item>
          <n-space justify="end" style="margin-top: 8px">
            <n-button v-if="editing" @click="resetForm">取消</n-button>
            <n-button type="primary" :loading="saving" @click="save">保存</n-button>
          </n-space>
        </n-form>
      </n-card>
    </n-grid-item>
  </n-grid>

  <n-modal v-model:show="showSnapshot" preset="card" title="人设快照（渲染后注入提示词）" style="width: 640px">
    <pre style="white-space: pre-wrap; background: #f6f7f9; padding: 14px; border-radius: 6px; font-size: 13px">{{ snapshot }}</pre>
    <template #footer>
      <n-button type="primary" @click="copySnapshot">复制</n-button>
    </template>
  </n-modal>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { listCharacters, addCharacter, updateCharacter, deleteCharacter, renderSnapshot } from '../api'

const props = defineProps({ projectId: { type: String, required: true } })
const message = useMessage()

const chars = ref([])
const editing = ref(false)
const editingCid = ref(null)
const saving = ref(false)
const showSnapshot = ref(false)
const snapshot = ref('')

const emptyForm = () => ({
  name: '', role_type: 'tool', core_desire: '', core_weakness: '',
  personality_tags: [], speech_style: '', forbidden_behavior: [],
  appearance_desc: '', relations: {}
})
const form = reactive(emptyForm())

const roleOptions = [
  { label: '主角', value: 'protagonist' },
  { label: '反派', value: 'antagonist' },
  { label: '盟友/靠山', value: 'ally' },
  { label: '工具人/配角', value: 'tool' }
]
const roleLabel = (v) => roleOptions.find(o => o.value === v)?.label || v
const roleTag = (v) => ({ protagonist: 'error', antagonist: 'warning', ally: 'success', tool: 'default' }[v] || 'default')

async function load() {
  chars.value = await listCharacters(props.projectId)
}
function openNew() {
  editing.value = false
  editingCid.value = null
  Object.assign(form, emptyForm())
}
function openEdit(c) {
  editing.value = true
  editingCid.value = c.cid
  Object.assign(form, {
    name: c.name, role_type: c.role_type, core_desire: c.core_desire,
    core_weakness: c.core_weakness, personality_tags: [...c.personality_tags],
    speech_style: c.speech_style, forbidden_behavior: [...c.forbidden_behavior],
    appearance_desc: c.appearance_desc, relations: { ...c.relations }
  })
}
function resetForm() { openNew() }

async function save() {
  if (!form.name.trim()) return message.warning('请填写姓名')
  saving.value = true
  try {
    if (editing.value) {
      await updateCharacter(props.projectId, editingCid.value, form)
      message.success('已更新')
    } else {
      await addCharacter(props.projectId, form)
      message.success('已新增')
    }
    openNew()
    load()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}

async function remove(cid) {
  try {
    await deleteCharacter(props.projectId, cid)
    message.success('已删除')
    load()
  } catch (e) {
    message.error(e.message)
  }
}

async function loadSnapshot() {
  const r = await renderSnapshot(props.projectId)
  snapshot.value = r.snapshot
  showSnapshot.value = true
}
async function copySnapshot() {
  await navigator.clipboard.writeText(snapshot.value)
  message.success('已复制')
}

onMounted(load)
</script>
