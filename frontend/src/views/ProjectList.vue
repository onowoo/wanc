<template>
  <div style="max-width: 960px; margin: 0 auto">
    <n-card>
      <n-space justify="space-between" align="center">
        <n-h3 style="margin: 0">短剧剧本项目</n-h3>
        <n-button type="primary" @click="showCreate = true">新建项目</n-button>
      </n-space>

      <n-empty v-if="projects.length === 0" description="还没有剧本项目，点击右上角新建" style="padding: 40px 0" />

      <n-list v-else bordered>
        <n-list-item v-for="p in projects" :key="p.id">
          <template #prefix>
            <n-avatar round :style="{ background: p.purpose === 'submit' ? '#e64646' : '#2f6fed' }">
              {{ p.purpose === 'submit' ? '投' : '漫' }}
            </n-avatar>
          </template>
          <n-space vertical size="small">
            <n-space align="baseline" size="small">
              <router-link :to="`/project/${p.id}`" style="font-weight: 600; font-size: 16px; color: #222; text-decoration: none">
                {{ p.name }}
              </router-link>
              <n-tag size="small" :type="p.purpose === 'submit' ? 'error' : 'info'">
                {{ p.purpose === 'submit' ? '投稿版' : '漫剧草稿版' }}
              </n-tag>
              <n-text depth="3" style="font-size: 12px">{{ p.track || '未设赛道' }}</n-text>
            </n-space>
            <n-text depth="3" style="font-size: 12px">
              题材：{{ p.genre || '-' }} ｜ 目标 {{ p.target_episodes }} 集 ｜ 更新：{{ p.updated_at }}
            </n-text>
          </n-space>
          <template #suffix>
            <n-space>
              <n-button size="small" @click="openProject(p.id)">打开</n-button>
              <n-popconfirm @positive-click="removeProject(p.id)">
                <template #trigger><n-button size="small" type="error" secondary>删除</n-button></template>
                确认删除该项目？其下所有剧本、人设、版本将一并删除。
              </n-popconfirm>
            </n-space>
          </template>
        </n-list-item>
      </n-list>
    </n-card>

    <n-modal v-model:show="showCreate" preset="card" title="新建剧本项目" style="width: 520px">
      <n-form label-placement="left" label-width="90px">
        <n-form-item label="项目名称" required>
          <n-input v-model:value="form.name" placeholder="如：重生千金复仇记" />
        </n-form-item>
        <n-form-item label="用途">
          <n-radio-group v-model:value="form.purpose">
            <n-radio value="submit">投稿版（编剧投稿）</n-radio>
            <n-radio value="draft">漫剧草稿版（AI漫剧）</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="题材">
          <n-input v-model:value="form.genre" placeholder="如：女频逆袭" />
        </n-form-item>
        <n-form-item label="赛道">
          <n-input v-model:value="form.track" placeholder="如：真假千金 / 男频神医" />
        </n-form-item>
        <n-form-item label="目标集数">
          <n-input-number v-model:value="form.target_episodes" :min="10" :max="200" style="width: 160px" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="doCreate">创建</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { listProjects, createProject, deleteProject } from '../api'

const router = useRouter()
const message = useMessage()
const projects = ref([])
const showCreate = ref(false)
const creating = ref(false)
const form = reactive({ name: '', purpose: 'submit', genre: '', track: '', target_episodes: 40 })

async function load() {
  projects.value = await listProjects()
}

async function doCreate() {
  if (!form.name.trim()) return message.warning('请填写项目名称')
  creating.value = true
  try {
    const p = await createProject(form)
    message.success('项目已创建')
    showCreate.value = false
    form.name = ''
    router.push(`/project/${p.id}`)
  } catch (e) {
    message.error(e.message)
  } finally {
    creating.value = false
  }
}

async function removeProject(id) {
  try {
    await deleteProject(id)
    message.success('已删除')
    load()
  } catch (e) {
    message.error(e.message)
  }
}

function openProject(id) {
  router.push(`/project/${id}`)
}

onMounted(load)
</script>
