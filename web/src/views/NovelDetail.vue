<template>
  <div v-if="novel" class="novel-detail">
    <el-page-header @back="$router.back()" :title="'返回'">
      <template #content>
        <span class="page-header-title">{{ novel.title }}</span>
      </template>
    </el-page-header>

    <el-row :gutter="16" style="margin-top: 16px">
      <!-- 左侧信息 -->
      <el-col :xl="6" :lg="8" :md="24">
        <el-card shadow="never">
          <el-image
            v-if="novel.cover_url"
            :src="novel.cover_url"
            fit="cover"
            style="width: 100%; border-radius: 8px; margin-bottom: 16px"
          />
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">作者</span>
              <span>{{ novel.author || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">平台</span>
              <el-tag size="small" effect="plain">{{ novel.platform_name }}</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">类型</span>
              <span>{{ novel.genre || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态</span>
              <el-tag :type="novel.status === 'completed' ? 'success' : 'info'" size="small" effect="plain">
                {{ novel.status || '-' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">语言</span>
              <span>{{ novel.language || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">付费</span>
              <el-tag :type="novel.is_paid ? 'warning' : 'success'" size="small" effect="plain">
                {{ novel.is_paid ? '是' : '否' }}
              </el-tag>
            </div>
            <div v-if="novel.url" style="margin-top: 8px">
              <el-link :href="novel.url" target="_blank" type="primary">查看原文</el-link>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧内容 -->
      <el-col :xl="18" :lg="16" :md="24">
        <!-- 数据指标 -->
        <el-card shadow="never">
          <el-row :gutter="16">
            <el-col :span="6" v-for="item in kpiItems" :key="item.label" class="kpi-col">
              <div class="kpi-label">{{ item.label }}</div>
              <div class="kpi-value" :class="item.highlight ? 'highlight' : ''">{{ item.value }}</div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 简介 -->
        <el-card shadow="never" style="margin-top: 16px">
          <template #header><span class="card-title">简介</span></template>
          <p class="desc-text">{{ novel.description || '暂无简介' }}</p>
        </el-card>

        <!-- 数据趋势 -->
        <el-card v-if="novel.snapshots && novel.snapshots.length" shadow="never" style="margin-top: 16px">
          <template #header><span class="card-title">数据趋势</span></template>
          <v-chart :option="chartOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getNovel } from '../api'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import dayjs from 'dayjs'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const route = useRoute()
const novel = ref(null)

const formatNum = (n) => {
  if (!n) return '-'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

const kpiItems = computed(() => {
  if (!novel.value) return []
  const n = novel.value
  return [
    { label: '当前排名', value: n.current_rank || '-', highlight: true },
    { label: '评分', value: n.score || '-' },
    { label: '评分人数', value: formatNum(n.rating_count) },
    { label: '评论数', value: formatNum(n.review_count) },
    { label: '阅读量', value: formatNum(n.view_count) },
    { label: '收藏数', value: formatNum(n.favorite_count) },
    { label: '字数', value: formatNum(n.word_count) },
    { label: '章节数', value: n.chapter_count || '-' },
  ]
})

const chartOption = computed(() => {
  if (!novel.value?.snapshots?.length) return {}
  const snaps = novel.value.snapshots
  const times = snaps.map((s) => dayjs(s.snapshot_time).format('MM-DD HH:mm'))

  const series = []
  const primary = '#00bf8a'
  const info = '#1677ff'
  const warning = '#ff7d00'

  if (snaps.some((s) => s.rank)) {
    series.push({ name: '排名', type: 'line', data: snaps.map((s) => s.rank), yAxisIndex: 0, smooth: true, itemStyle: { color: primary }, lineStyle: { color: primary } })
  }
  if (snaps.some((s) => s.view_count)) {
    series.push({ name: '阅读量', type: 'line', data: snaps.map((s) => s.view_count), yAxisIndex: 1, smooth: true, itemStyle: { color: info }, lineStyle: { color: info } })
  }
  if (snaps.some((s) => s.favorite_count)) {
    series.push({ name: '收藏', type: 'line', data: snaps.map((s) => s.favorite_count), yAxisIndex: 1, smooth: true, itemStyle: { color: warning }, lineStyle: { color: warning } })
  }

  return {
    tooltip: { trigger: 'axis' },
    legend: { data: series.map((s) => s.name), textStyle: { color: '#86909c', fontSize: 12 } },
    grid: { left: 60, right: 60, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: times, axisLine: { lineStyle: { color: '#e5e6eb' } }, axisLabel: { color: '#86909c', fontSize: 12 } },
    yAxis: [
      { type: 'value', name: '排名', inverse: true, min: 1, axisLine: { show: false }, splitLine: { lineStyle: { color: '#f2f3f5' } }, axisLabel: { color: '#86909c' } },
      { type: 'value', name: '数量', axisLine: { show: false }, splitLine: { show: false }, axisLabel: { color: '#86909c' } },
    ],
    series,
  }
})

onMounted(async () => {
  try {
    novel.value = await getNovel(route.params.id)
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.page-header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--zw-text);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--zw-text);
}

.info-label {
  color: var(--zw-text-secondary);
  flex-shrink: 0;
}

.kpi-col {
  text-align: center;
  padding: 12px 0;
}

.kpi-label {
  font-size: 13px;
  color: var(--zw-text-secondary);
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--zw-text);
  font-variant-numeric: tabular-nums;
}

.kpi-value.highlight {
  color: var(--zw-primary);
  font-size: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--zw-text);
}

.desc-text {
  line-height: 1.8;
  color: var(--zw-text);
  font-size: 14px;
}
</style>
