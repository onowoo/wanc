import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err?.response?.data?.detail || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

// 项目
export const listProjects = () => http.get('/projects')
export const createProject = (data) => http.post('/projects', data)
export const getProject = (id) => http.get(`/projects/${id}`)
export const updateProject = (id, data) => http.put(`/projects/${id}`, data)
export const deleteProject = (id) => http.delete(`/projects/${id}`)
export const getOutline = (id) => http.get(`/projects/${id}/outline`)
export const putOutline = (id, data) => http.put(`/projects/${id}/outline`, data)

// 人物
export const listCharacters = (id) => http.get(`/projects/${id}/characters`)
export const addCharacter = (id, data) => http.post(`/projects/${id}/characters`, data)
export const updateCharacter = (id, cid, data) => http.put(`/projects/${id}/characters/${cid}`, data)
export const deleteCharacter = (id, cid) => http.delete(`/projects/${id}/characters/${cid}`)
export const renderSnapshot = (id) => http.get(`/projects/${id}/characters/snapshot`)

// 提示词
export const listTemplates = () => http.get('/prompts/templates')
export const renderPrompt = (id, data) => http.post(`/prompts/render/${id}`, data)

// 剧本
export const getScript = (id) => http.get(`/projects/${id}/scripts`)
export const importScript = (id, rawText, label) => http.post(`/projects/${id}/scripts/import`, { raw_text: rawText, label })
export const validateScript = (id) => http.post(`/projects/${id}/scripts/validate`)
export const updateEpisode = (id, index, data) => http.put(`/projects/${id}/scripts/episode/${index}`, data)
export const listVersions = (id) => http.get(`/projects/${id}/scripts/versions`)
export const createVersion = (id, label) => http.post(`/projects/${id}/scripts/versions`, { label })
export const restoreVersion = (id, version) => http.post(`/projects/${id}/scripts/versions/${version}/restore`)
export const diffVersions = (id, a, b) => http.get(`/projects/${id}/scripts/versions/${a}/diff/${b}`)

// 导出
export const exportMarkdown = (id) => http.get(`/projects/${id}/export/markdown`)
export const exportMarkdownRaw = (id) => http.get(`/projects/${id}/export/markdown/raw`)
export const exportJson = (id) => http.get(`/projects/${id}/export/json`)

export default http
