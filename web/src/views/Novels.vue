<template>
  <div class="page-novels">
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-grid">
        <div class="filter-row-item">
          <span class="filter-label">书名/作者</span>
          <el-input v-model="keyword" placeholder="请输入" clearable @keyup.enter="fetchData" />
        </div>
        <div class="filter-row-item">
          <span class="filter-label">平台</span>
          <el-select v-model="platformId" placeholder="全部平台" clearable>
            <el-option v-for="p in platforms" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
        <div class="filter-row-item">
          <span class="filter-label">排序</span>
          <el-select v-model="sortBy">
            <el-option label="按排名" value="current_rank" />
            <el-option label="按评分" value="score" />
            <el-option label="按阅读" value="view_count" />
            <el-option label="按收藏" value="favorite_count" />
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
        <span class="card-title">小说列表</span>
      </template>
      <div class="table-wrapper">
        <el-table
          :data="novels"
          v-loading="loading"
          :header-cell-style="headerStyle"
        >
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
          <el-table-column prop="author" label="作者" width="130" show-overflow-tooltip />
          <el-table-column prop="platform_name" label="平台" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.platform_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="genre" label="类型" width="140" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'completed' ? 'success' : 'info'" size="small" effect="plain">
                {{ row.status || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="评分" width="70" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ row.score || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="current_rank" label="排名" width="70" align="center">
            <template #default="{ row }">
              <span class="cell-num">{{ row.current_rank || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center" fixed="right">
            <template #default="{ row }">
              <el-button text size="small" type="primary" @click="$router.push(`/novels/${row.id}`)">详情</el-button>
              <el-link v-if="row.url" :href="row.url" target="_blank" type="info" :underline="false" style="margin-left: 4px">
                <el-icon :size="14"><Link /></el-icon>
              </el-link>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-if="!loading && novels.length === 0" description="暂无数据" />
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
import { getNovels, getPlatforms } from '../api'

const novels = ref([])
const platforms = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')
const platformId = ref(null)
const sortBy = ref('current_rank')
const loading = ref(false)

const headerStyle = {
  background: 'rgb(242,243,245)',
  color: '#323335',
  fontWeight: '600',
  fontSize: '13px',
}

const resetFilter = () => {
  keyword.value = ''
  platformId.value = null
  sortBy.value = 'current_rank'
  page.value = 1
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, sort_by: sortBy.value }
    if (keyword.value) params.keyword = keyword.value
    if (platformId.value) params.platform_id = platformId.value
    const res = await getNovels(params)
    novels.value = res.items
    total.value = res.total
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
</style>
