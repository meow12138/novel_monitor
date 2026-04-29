<template>
  <div class="page-tasks">
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-grid">
        <div class="filter-row-item">
          <span class="filter-label">状态</span>
          <el-select v-model="statusFilter" placeholder="全部状态" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="运行中" value="running" />
            <el-option label="等待中" value="pending" />
          </el-select>
        </div>
      </div>
      <div class="filter-actions">
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span class="card-title">抓取任务</span>
          <el-button size="small" @click="fetchData"><el-icon><Refresh /></el-icon>刷新</el-button>
        </div>
      </template>

      <div class="table-wrapper">
        <el-table
          :data="tasks"
          v-loading="loading"
          :header-cell-style="headerStyle"
        >
          <el-table-column prop="id" label="ID" width="60" align="center" />
          <el-table-column prop="platform_name" label="平台" width="140" />
          <el-table-column prop="task_type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.task_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="items_scraped" label="抓取数" width="80" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ row.items_scraped }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="started_at" label="开始时间" width="160">
            <template #default="{ row }">{{ formatTime(row.started_at) }}</template>
          </el-table-column>
          <el-table-column prop="finished_at" label="完成时间" width="160">
            <template #default="{ row }">{{ formatTime(row.finished_at) }}</template>
          </el-table-column>
          <el-table-column label="耗时" width="80" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ duration(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.error_message" style="color: var(--el-color-danger)">{{ row.error_message }}</span>
              <span v-else class="text-secondary">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-if="!loading && tasks.length === 0" description="暂无任务" />
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        :background="true"
        layout="prev, pager, next"
        @current-change="fetchData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTasks } from '../api'
import dayjs from 'dayjs'

const tasks = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const statusFilter = ref('')
const loading = ref(false)

const headerStyle = {
  background: 'rgb(242,243,245)',
  color: '#323335',
  fontWeight: '600',
  fontSize: '13px',
}

const statusMap = { success: 'success', failed: 'danger', running: 'warning', pending: 'info' }
const labelMap = { success: '成功', failed: '失败', running: '运行中', pending: '等待中' }
const statusType = (s) => statusMap[s] || 'info'
const statusLabel = (s) => labelMap[s] || s
const formatTime = (t) => (t ? dayjs(t).format('YYYY-MM-DD HH:mm:ss') : '-')

const duration = (row) => {
  if (!row.started_at || !row.finished_at) return '-'
  const ms = dayjs(row.finished_at).diff(dayjs(row.started_at))
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`
}

const resetFilter = () => {
  statusFilter.value = ''
  page.value = 1
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (statusFilter.value) params.status = statusFilter.value
    const res = await getTasks(params)
    tasks.value = res.items
    total.value = res.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
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

.text-secondary {
  color: var(--zw-text-secondary);
}
</style>
