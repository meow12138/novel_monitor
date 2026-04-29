import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '仪表盘', icon: 'DataAnalysis' },
  },
  {
    path: '/ranking',
    name: 'Ranking',
    component: () => import('../views/Ranking.vue'),
    meta: { title: '排行榜', icon: 'Trophy' },
  },
  {
    path: '/novels',
    name: 'Novels',
    component: () => import('../views/Novels.vue'),
    meta: { title: '小说管理', icon: 'Reading' },
  },
  {
    path: '/novels/:id',
    name: 'NovelDetail',
    component: () => import('../views/NovelDetail.vue'),
    meta: { title: '小说详情', hidden: true },
  },
  {
    path: '/platforms',
    name: 'Platforms',
    component: () => import('../views/Platforms.vue'),
    meta: { title: '平台管理', icon: 'Platform' },
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/Tasks.vue'),
    meta: { title: '抓取任务', icon: 'Download' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
