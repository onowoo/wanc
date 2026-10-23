<template>
  <div style="max-width: 1100px; margin: 0 auto">
    <n-card size="small">
      <n-space justify="space-between" align="center">
        <n-space align="baseline" size="small">
          <n-h3 style="margin: 0">{{ project?.name || '加载中...' }}</n-h3>
          <n-tag size="small" :type="project?.purpose === 'submit' ? 'error' : 'info'">
            {{ project?.purpose === 'submit' ? '投稿版' : '漫剧草稿版' }}
          </n-tag>
          <n-text depth="3" style="font-size: 12px">题材：{{ project?.genre || '-' }} ｜ 赛道：{{ project?.track || '-' }}</n-text>
        </n-space>
        <n-space>
          <n-button size="small" secondary @click="editMeta = true">项目信息</n-button>
          <n-button size="small" @click="$router.push('/')">← 返回</n-button>
        </n-space>
      </n-space>
    </n-card>

    <n-card style="margin-top: 12px" :bordered="true" size="small">
      <n-tabs type="line" animated>
        <n-tab-pane name="char" tab="人设管理"><CharacterPanel :project-id="projectId" /></n-tab-pane>
        <n-tab-pane name="outline" tab="故事大纲"><OutlinePanel :project-id="projectId" /></n-tab-pane>
        <n-tab-pane name="gen" tab="剧本生成"><GenPanel :project-id="projectId" /></n-tab-pane>
        <n-tab-pane name="edit" tab="剧本编辑"><EpisodePanel :project-id="projectId" /></n-tab-pane>
        <n-tab-pane name="version" tab="版本管理"><VersionPanel :project-id="projectId" /></n-tab-pane>
        <n-tab-pane name="export" tab="导出"><ExportPanel :project-id="projectId" /></n-tab-pane>
      </n-tabs>
    </n-card>

    <n-modal v-model:show="editMeta" preset="card" title="项目信息" style="width: 480px">
      <n-form label-placement="left" label-width="80px">
        <n-form-item label="题材"><n-input v-model:value="form.genre" /></n-form-item>
        <n-form-item label="赛道"><n-input v-model:value="form.track" /></n-form-item>
        <n-form-item label="目标集数"><n-input-number v-model:value="form.target_episodes" :min="10" :max="200" style="width: 160px" /></n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="editMeta = false">取消</n-button>
          <n-button type="primary" @click="saveMeta">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { getProject, updateProject } from '../api'
import CharacterPanel from '../components/CharacterPanel.vue'
import OutlinePanel from '../components/OutlinePanel.vue'
import GenPanel from '../components/GenPanel.vue'
import EpisodePanel from '../components/EpisodePanel.vue'
import VersionPanel from '../components/VersionPanel.vue'
import ExportPanel from '../components/ExportPanel.vue'

const route = useRoute()
const message = useMessage()
const projectId = route.params.id
const project = ref(null)
const editMeta = ref(false)
const form = reactive({ genre: '', track: '', target_episodes: 40 })

async function load() {
  project.value = await getProject(projectId)
  form.genre = project.value.genre
  form.track = project.value.track
  form.target_episodes = project.value.target_episodes
}
async function saveMeta() {
  await updateProject(projectId, {
    name: project.value.name, genre: form.genre, track: form.track,
    target_episodes: form.target_episodes, purpose: project.value.purpose,
    template: project.value.template
  })
  message.success('已保存')
  editMeta.value = false
  load()
}

onMounted(load)
</script>
