import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'projects', component: () => import('../views/ProjectList.vue') },
  { path: '/project/:id', name: 'workspace', component: () => import('../views/ProjectWorkspace.vue') }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
