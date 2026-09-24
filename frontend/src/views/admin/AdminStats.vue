<template>
  <div class="stats-page">
    <div class="page-header">
      <h2 class="page-title">数据统计</h2>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-item">
        <label class="filter-label">时间范围</label>
        <select v-model="dateRange" class="filter-select" @change="fetchData">
          <option value="7d">近7天</option>
          <option value="30d">近30天</option>
          <option value="90d">近90天</option>
        </select>
      </div>
      <div class="filter-item">
        <label class="filter-label">孩子</label>
        <select v-model="childId" class="filter-select" @change="fetchData">
          <option value="">全部孩子</option>
          <option v-for="child in children" :key="child.id" :value="child.id">
            {{ child.nickname }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-box">
      <span class="loading-spinner"></span>
      <span>加载中...</span>
    </div>

    <template v-else>
      <!-- Metric cards -->
      <div class="metric-cards">
        <div class="metric-card accent-blue">
          <div class="metric-icon">💰</div>
          <div class="metric-body">
            <div class="metric-label">积分发放量</div>
            <div class="metric-value">{{ overview.totalPointsIssued ?? 0 }}</div>
          </div>
        </div>
        <div class="metric-card accent-pink">
          <div class="metric-icon">🎁</div>
          <div class="metric-body">
            <div class="metric-label">兑换次数</div>
            <div class="metric-value">{{ overview.totalRedeemCount ?? 0 }}</div>
          </div>
        </div>
        <div class="metric-card accent-green">
          <div class="metric-icon">✅</div>
          <div class="metric-body">
            <div class="metric-label">完成率</div>
            <div class="metric-value">{{ completionRate }}%</div>
          </div>
        </div>
        <div class="metric-card accent-purple">
          <div class="metric-icon">👶</div>
          <div class="metric-body">
            <div class="metric-label">活跃孩子数</div>
            <div class="metric-value">{{ overview.activeChildCount ?? 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Trend chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">积分趋势</h3>
          <div class="chart-legend">
            <span class="legend-item"><span class="legend-dot blue"></span>发放积分</span>
            <span class="legend-item"><span class="legend-dot pink"></span>兑换积分</span>
          </div>
        </div>
        <div v-if="trend.length" class="chart-body">
          <div class="chart-bars">
            <div v-for="item in trend" :key="item.date" class="bar-group">
              <div class="bar-pair">
                <div
                  class="bar bar-issued"
                  :style="{ height: barHeight(item.pointsIssued) + 'px' }"
                  :title="`发放 ${item.pointsIssued}`"
                ></div>
                <div
                  class="bar bar-redeemed"
                  :style="{ height: barHeight(item.pointsRedeemed) + 'px' }"
                  :title="`兑换 ${item.pointsRedeemed}`"
                ></div>
              </div>
              <div class="bar-label">{{ formatDate(item.date) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="chart-empty">暂无趋势数据</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getChildren, getStatsOverview, getStatsTrend } from '../../api/admin'

const CHART_HEIGHT = 200

const loading = ref(false)
const dateRange = ref('7d')
const childId = ref('')
const children = ref([])

const overview = reactive({
  totalPointsIssued: 0,
  totalRedeemCount: 0,
  taskCompletionRate: 0,
  activeChildCount: 0,
})
const trend = ref([])

const completionRate = computed(() => {
  const r = overview.taskCompletionRate ?? 0
  const pct = r <= 1 ? r * 100 : r
  return Math.round(pct)
})

const maxVal = computed(() => {
  let m = 0
  for (const item of trend.value) {
    if (item.pointsIssued > m) m = item.pointsIssued
    if (item.pointsRedeemed > m) m = item.pointsRedeemed
  }
  return m || 1
})

function barHeight(val) {
  return Math.max(2, ((val || 0) / maxVal.value) * CHART_HEIGHT)
}

function formatDate(dateStr) {
  const parts = String(dateStr).split('-')
  if (parts.length >= 2) {
    return `${parts[parts.length - 2]}-${parts[parts.length - 1]}`
  }
  return dateStr
}

function buildParams() {
  const params = { dateRange: dateRange.value }
  if (childId.value) params.childId = childId.value
  return params
}

async function fetchChildren() {
  try {
    const res = await getChildren()
    children.value = res.data || []
  } catch (e) {
    children.value = []
  }
}

async function fetchData() {
  loading.value = true
  try {
    const [ovRes, trRes] = await Promise.all([
      getStatsOverview(buildParams()),
      getStatsTrend(buildParams()),
    ])
    Object.assign(overview, ovRes.data)
    trend.value = trRes.data.trend || []
  } catch (e) {
    // keep last state / empty
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchChildren()
  await fetchData()
})
</script>

<style scoped>
.stats-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
}

.filter-bar {
  display: flex;
  gap: 20px;
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.filter-select {
  height: 36px;
  padding: 0 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  min-width: 140px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-select:focus {
  border-color: #6366f1;
}

.loading-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 60px 0;
  color: #94a3b8;
  font-size: 15px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.metric-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric-card {
  background: #fff;
  border-radius: 12px;
  padding: 22px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  border-top: 3px solid transparent;
}

.metric-card.accent-blue {
  border-top-color: #3b82f6;
}
.metric-card.accent-pink {
  border-top-color: #ec4899;
}
.metric-card.accent-green {
  border-top-color: #10b981;
}
.metric-card.accent-purple {
  border-top-color: #8b5cf6;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
}

.accent-blue .metric-icon {
  background: #dbeafe;
}
.accent-pink .metric-icon {
  background: #fce7f3;
}
.accent-green .metric-icon {
  background: #d1fae5;
}
.accent-purple .metric-icon {
  background: #ede9fe;
}

.metric-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.chart-legend {
  display: flex;
  gap: 18px;
  font-size: 13px;
  color: #64748b;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.legend-dot.blue {
  background: #3b82f6;
}

.legend-dot.pink {
  background: #ec4899;
}

.chart-body {
  overflow-x: auto;
  padding-bottom: 4px;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 240px;
  min-width: 100%;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 48px;
}

.bar-pair {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 200px;
}

.bar {
  width: 16px;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
  min-height: 2px;
}

.bar-issued {
  background: linear-gradient(180deg, #60a5fa, #3b82f6);
}

.bar-redeemed {
  background: linear-gradient(180deg, #f472b6, #ec4899);
}

.bar-label {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
}

.chart-empty {
  text-align: center;
  padding: 60px 0;
  color: #94a3b8;
  font-size: 15px;
}

@media (max-width: 900px) {
  .metric-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .metric-cards {
    grid-template-columns: 1fr;
  }
}
</style>
