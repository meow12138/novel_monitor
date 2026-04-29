<template>
  <div class="page-ranking">
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-grid">
        <div class="filter-row-item">
          <span class="filter-label">平台</span>
          <el-select v-model="platformId" placeholder="全部平台" clearable @change="fetchData">
            <el-option v-for="p in platforms" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
        <div class="filter-row-item">
          <span class="filter-label">榜单</span>
          <el-select v-model="rankType" @change="fetchData">
            <el-option label="热门榜" value="hot" />
            <el-option label="趋势榜" value="trending" />
            <el-option label="新书榜" value="new" />
            <el-option label="完结榜" value="completed" />
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
        <span class="card-title">排行榜</span>
      </template>
      <div class="table-wrapper">
        <el-table
          :data="novels"
          v-loading="loading"
          :header-cell-style="headerStyle"
        >
          <el-table-column label="排名" width="70" align="center">
            <template #default="{ row }">
              <span :class="['rank-badge', row.current_rank <= 3 ? 'top3' : '']">{{ row.current_rank }}</span>
            </template>
          </el-table-column>
          <el-table-column label="封面" width="70" align="center">
            <template #default="{ row }">
              <el-image v-if="row.cover_url" :src="row.cover_url" fit="cover" class="cover-img" />
            </template>
          </el-table-column>
          <el-table-column prop="title" label="书名" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <el-link :underline="false" type="primary" @click="$router.push(`/novels/${row.id}`)">{{ row.title }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="author" label="作者" width="140" show-overflow-tooltip />
          <el-table-column prop="platform_name" label="平台" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.platform_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="genre" label="类型" width="150" show-overflow-tooltip />
          <el-table-column prop="score" label="评分" width="80" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ row.score || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="view_count" label="阅读量" width="100" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ formatNum(row.view_count) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="favorite_count" label="收藏" width="90" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ formatNum(row.favorite_count) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-if="!loading && novels.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRanking, getPlatforms } from '../api'

const novels = ref([])
const platforms = ref([])
const platformId = ref(null)
const rankType = ref('hot')
const loading = ref(false)

const headerStyle = {
  background: 'rgb(242,243,245)',
  color: '#323335',
  fontWeight: '600',
  fontSize: '13px',
}

const formatNum = (n) => {
  if (!n) return '-'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

const resetFilter = () => {
  platformId.value = null
  rankType.value = 'hot'
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { rank_type: rankType.value, limit: 100 }
    if (platformId.value) params.platform_id = platformId.value
    novels.value = await getRanking(params)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  platforms.value = await getPlatforms()
  await fetchData()
})
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--zw-text);
}

.cover-img {
  width: 40px;
  height: 56px;
  border-radius: 4px;
}

.rank-badge {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--zw-text-secondary);
  background: rgb(242, 243, 245);
}

.rank-badge.top3 {
  background: var(--zw-primary-bg);
  color: var(--zw-primary);
}
</style>
