<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon" style="background: var(--zw-primary-bg)">
            <el-icon :size="24" color="var(--zw-primary)"><Reading /></el-icon>
          </div>
          <div>
            <div class="stat-value">{{ stats.total_novels }}</div>
            <div class="stat-label">小说总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon" style="background: #e8f7ff">
            <el-icon :size="24" color="#1677ff"><Monitor /></el-icon>
          </div>
          <div>
            <div class="stat-value">{{ stats.total_platforms }}</div>
            <div class="stat-label">平台总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon :size="24" color="#ff7d00"><Connection /></el-icon>
          </div>
          <div>
            <div class="stat-value">{{ stats.active_platforms }}</div>
            <div class="stat-label">已启用平台</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xl="6" :lg="6" :md="12" :sm="12" :xs="24">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon" style="background: #fef0f0">
            <el-icon :size="24" color="#f53f3f"><Download /></el-icon>
          </div>
          <div>
            <div class="stat-value">{{ stats.today_scraped }}</div>
            <div class="stat-label">今日抓取</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 热门小说 -->
      <el-col :xl="14" :lg="14" :md="24">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">热门小说 TOP 10</span>
              <el-button text type="primary" size="small" @click="$router.push('/ranking')">查看排行榜</el-button>
            </div>
          </template>
          <div class="table-wrapper">
            <el-table :data="stats.top_novels" :header-cell-style="headerStyle">
              <el-table-column label="#" width="50" align="center">
                <template #default="{ $index }">
                  <span :class="['rank-badge', $index < 3 ? 'top3' : '']">{{ $index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="书名" min-width="180" show-overflow-tooltip />
              <el-table-column prop="author" label="作者" width="120" show-overflow-tooltip />
              <el-table-column prop="platform_name" label="平台" width="110" align="center">
                <template #default="{ row }">
                  <el-tag size="small" effect="plain">{{ row.platform_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="评分" width="70" align="right">
                <template #default="{ row }">
                  <span class="cell-num">{{ row.score || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="current_rank" label="排名" width="70" align="center">
                <template #default="{ row }">
                  <span class="cell-num">{{ row.current_rank }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-if="stats.top_novels.length === 0" description="暂无数据" />
        </el-card>
      </el-col>

      <!-- 最近任务 -->
      <el-col :xl="10" :lg="10" :md="24">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近抓取任务</span>
              <el-button text type="primary" size="small" @click="$router.push('/tasks')">全部任务</el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="task in stats.recent_tasks"
              :key="task.id"
              :type="taskStatusType(task.status)"
              :timestamp="formatTime(task.created_at)"
              placement="top"
            >
              <div class="task-item">
                <span class="task-platform">{{ task.platform_name }}</span>
                <el-tag :type="taskStatusType(task.status)" size="small" effect="plain">{{ statusLabel(task.status) }}</el-tag>
                <span v-if="task.items_scraped" class="task-count">{{ task.items_scraped }} 条</span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="stats.recent_tasks.length === 0" description="暂无任务" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '../api'
import dayjs from 'dayjs'

const stats = ref({
  total_novels: 0,
  total_platforms: 0,
  active_platforms: 0,
  today_scraped: 0,
  recent_tasks: [],
  top_novels: [],
})

const headerStyle = {
  background: 'rgb(242,243,245)',
  color: '#323335',
  fontWeight: '600',
  fontSize: '13px',
}

const statusMap = { success: 'success', failed: 'danger', running: 'warning', pending: 'info' }
const labelMap = { success: '成功', failed: '失败', running: '运行中', pending: '等待中' }
const taskStatusType = (s) => statusMap[s] || 'info'
const statusLabel = (s) => labelMap[s] || s
const formatTime = (t) => (t ? dayjs(t).format('MM-DD HH:mm') : '')

onMounted(async () => {
  try {
    stats.value = await getDashboard()
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--zw-gap);
}

.stat-row {
  margin-bottom: 0 !important;
}

.stat-card .el-card__body {
  display: flex;
  align-items: center;
  gap: var(--zw-gap);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--zw-text);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 13px;
  color: var(--zw-text-secondary);
  margin-top: 2px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--zw-text);
}

.rank-badge {
  display: inline-block;
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--zw-text-secondary);
  background: rgb(242, 243, 245);
}

.rank-badge.top3 {
  background: var(--zw-primary-bg);
  color: var(--zw-primary);
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-platform {
  font-weight: 500;
  font-size: 13px;
  color: var(--zw-text);
}

.task-count {
  font-size: 12px;
  color: var(--zw-text-secondary);
}
</style>
