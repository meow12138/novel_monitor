<template>
  <div class="page-platforms">
    <!-- 操作栏 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">平台管理</span>
          <el-button type="primary" @click="runAllScrape" :loading="runAllLoading">
            <el-icon><Download /></el-icon>一键抓取全部
          </el-button>
        </div>
      </template>

      <div class="table-wrapper">
        <el-table
          :data="platforms"
          v-loading="loading"
          :header-cell-style="headerStyle"
        >
          <el-table-column prop="name" label="平台名称" width="160" />
          <el-table-column prop="code" label="编码" width="120" />
          <el-table-column prop="website" label="网址" min-width="240">
            <template #default="{ row }">
              <el-link :href="row.website" target="_blank" type="primary" :underline="false">{{ row.website }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="region" label="地区" width="80" align="center" />
          <el-table-column prop="category" label="分类" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="categoryType(row.category)" effect="plain">{{ categoryLabel(row.category) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="novel_count" label="小说数" width="80" align="right">
            <template #default="{ row }">
              <span class="cell-num">{{ row.novel_count }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="togglePlatform(row)" />
            </template>
          </el-table-column>
          <el-table-column label="爬虫" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.scraper_class ? 'success' : 'info'" size="small" effect="plain">
                {{ row.scraper_class ? '已实现' : '待开发' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" align="center" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="doScrape(row)" :disabled="!row.enabled || !row.scraper_class">
                抓取
              </el-button>
              <el-button text size="small" @click="$router.push({ path: '/novels', query: { platform_id: row.id } })">
                小说
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-if="!loading && platforms.length === 0" description="暂无平台" />
    </el-card>

    <!-- 平台说明 -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <span class="card-title">平台说明</span>
      </template>
      <div class="table-wrapper">
        <el-table :data="platforms" :header-cell-style="headerStyle">
          <el-table-column prop="name" label="平台" width="160" />
          <el-table-column prop="description" label="说明" min-width="300" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPlatforms, updatePlatform, runScrape, runScrapeAll } from '../api'
import { ElMessage } from 'element-plus'

const platforms = ref([])
const loading = ref(false)
const runAllLoading = ref(false)

const headerStyle = {
  background: 'rgb(242,243,245)',
  color: '#323335',
  fontWeight: '600',
  fontSize: '13px',
}

const categoryMap = {
  cn_overseas: { label: '中国出海', type: 'danger' },
  us_native: { label: '欧美本土', type: '' },
  jp: { label: '日本', type: 'warning' },
  kr: { label: '韩国', type: 'success' },
  ebook: { label: '电子书', type: 'info' },
  social: { label: '社交媒体', type: '' },
}
const categoryLabel = (c) => categoryMap[c]?.label || c || '-'
const categoryType = (c) => categoryMap[c]?.type || 'info'

const togglePlatform = async (row) => {
  try {
    await updatePlatform(row.id, { enabled: row.enabled })
    ElMessage.success(`${row.name} 已${row.enabled ? '启用' : '停用'}`)
  } catch (e) {
    row.enabled = !row.enabled
  }
}

const doScrape = async (row) => {
  try {
    await runScrape(row.id)
    ElMessage.success(`${row.name} 抓取任务已启动`)
  } catch (e) {
    ElMessage.error('启动失败')
  }
}

const runAllScrape = async () => {
  runAllLoading.value = true
  try {
    const res = await runScrapeAll()
    ElMessage.success(res.message || '全部抓取任务已启动')
  } catch (e) {
    ElMessage.error('启动失败')
  } finally {
    runAllLoading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    platforms.value = await getPlatforms()
  } finally {
    loading.value = false
  }
})
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
</style>
