<template>
  <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
    <n-grid-item :span="1">
      <n-card title="分集列表" :bordered="true" size="small">
        <template #header-extra>
          <n-button size="small" secondary @click="reload">刷新</n-button>
        </template>
        <n-empty v-if="episodes.length === 0" description="暂无分集，请到『生成』页导入" style="padding: 30px 0" />
        <n-list v-else bordered>
          <n-list-item v-for="ep in episodes" :key="ep.index" style="padding: 6px 10px">
            <n-space justify="space-between" align="center">
              <n-space size="small" align="center">
                <n-tag size="tiny" :type="ep.hook ? 'success' : 'error'">{{ ep.hook ? '有钩' : '无钩' }}</n-tag>
                <n-text strong style="font-size: 13px">第{{ ep.index }}集</n-text>
                <n-text depth="3" style="font-size: 12px">{{ ep.title || '未命名' }}</n-text>
                <n-text depth="3" style="font-size: 12px">{{ ep.word_count }}字</n-text>
              </n-space>
              <n-button size="tiny" secondary @click="openEpisode(ep)">编辑</n-button>
            </n-space>
          </n-list-item>
        </n-list>
      </n-card>
    </n-grid-item>

    <n-grid-item :span="1">
      <n-card :title="current ? `编辑：第${current.index}集` : '单集编辑'" :bordered="true" size="small">
        <template v-if="current">
          <n-form label-placement="top" size="small">
            <n-form-item label="本集标题">
              <n-input v-model:value="current.title" placeholder="如：归家" />
            </n-form-item>
            <n-form-item label="本集正文（格式：场景/动作/台词/【本集钩子】）">
              <n-input v-model:value="current.source_text" type="textarea" :rows="16" placeholder="【内/外｜场景｜日/夜】..." />
            </n-form-item>
            <n-space justify="end">
              <n-button type="primary" :loading="saving" @click="saveEpisode">保存本集</n-button>
            </n-space>
          </n-form>
        </template>
        <n-empty v-else description="在左侧选择一集进行编辑" />
      </n-card>
    </n-grid-item>
  </n-grid>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { getScript, updateEpisode } from '../api'

const props = defineProps({ projectId: { type: String, required: true } })
const message = useMessage()

const episodes = ref([])
const current = ref(null)
const saving = ref(false)

async function reload() {
  const r = await getScript(props.projectId)
  episodes.value = r.episodes
}
function openEpisode(ep) {
  current.value = { ...ep, source_text: ep.source_text || '' }
}
async function saveEpisode() {
  saving.value = true
  try {
    await updateEpisode(props.projectId, current.value.index, {
      title: current.value.title,
      source_text: current.value.source_text
    })
    message.success('已保存')
    reload()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>
