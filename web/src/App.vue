<template>
  <div class="app-layout">
    <!-- Sider -->
    <aside class="sider" :class="{ collapsed: isCollapsed, 'mobile-open': mobileOpen }">
      <div class="logo">
        <div class="logo-icon"><el-icon :size="20" color="#00BF8A"><Reading /></el-icon></div>
        <span v-show="!isCollapsed || mobileOpen" class="logo-text">Novel Monitor</span>
      </div>

      <el-menu
        :default-active="$route.path"
        :collapse="isCollapsed && !mobileOpen"
        :collapse-transition="false"
        :unique-opened="true"
        router
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item :index="route.path">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <template #title>{{ route.meta.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>

      <div class="collapse-btn" @click="mobileOpen ? (mobileOpen = false) : (isCollapsed = !isCollapsed)">
        <span v-if="!isCollapsed && !mobileOpen" class="collapse-icon">≡</span>
        <el-icon v-else-if="isCollapsed && !mobileOpen" :size="16"><Expand /></el-icon>
        <el-icon v-else :size="16"><Close /></el-icon>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div v-if="mobileOpen" class="mobile-overlay" @click="mobileOpen = false" />

    <!-- Main -->
    <div class="main-wrapper" :class="{ collapsed: isCollapsed }">
      <header class="app-header">
        <el-icon class="hamburger" :size="20" @click="mobileOpen = true"><Operation /></el-icon>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="header-right">
          <el-tag type="success" effect="plain" size="small">v1.0</el-tag>
        </div>
      </header>

      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import router from './router'

const route = useRoute()
const isCollapsed = ref(false)
const mobileOpen = ref(false)

const menuRoutes = computed(() =>
  router.options.routes.filter((r) => r.meta && !r.meta.hidden && r.meta.icon)
)

const currentTitle = computed(() => route.meta?.title || '')
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}

/* ---- Sider ---- */
.sider {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--zw-sider-width);
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid var(--zw-border);
  display: flex;
  flex-direction: column;
  z-index: 200;
  transition: width 0.3s, transform 0.3s;
  overflow: hidden;
}
.sider.collapsed {
  width: var(--zw-sider-collapsed-width);
}

/* Logo */
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-shrink: 0;
  padding: 0 16px;
}
.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e6f9f3;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--zw-text);
  white-space: nowrap;
}

/* Menu */
:deep(.el-menu) {
  flex: 1;
  border-right: none !important;
  background: transparent;
  overflow-y: auto;
}
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 46px;
  line-height: 46px;
  border-radius: 4px;
  margin: 2px 8px;
  width: calc(100% - 16px);
  color: #4e5969 !important;
  font-size: 14px;
  transition: background-color 0.15s, color 0.15s;
}
:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: rgba(0, 0, 0, 0.04) !important;
  color: var(--zw-text) !important;
}
:deep(.el-menu-item.is-active) {
  background-color: var(--zw-primary-bg) !important;
  color: var(--zw-primary) !important;
  font-weight: 600;
}
:deep(.el-menu-item.is-active::after) {
  display: none !important;
}

/* Collapse btn */
.collapse-btn {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 16px;
  background: #f7f8fa;
  border-top: 1px solid var(--zw-border);
  cursor: pointer;
  color: var(--zw-text-secondary);
  flex-shrink: 0;
}
.collapse-btn:hover {
  color: var(--zw-primary);
}
.collapse-icon {
  font-size: 18px;
  line-height: 1;
  font-weight: 400;
  letter-spacing: -1px;
}

/* Collapsed state */
.sider.collapsed .logo {
  padding: 0;
}
.sider.collapsed :deep(.el-menu-item),
.sider.collapsed :deep(.el-sub-menu__title) {
  margin: 2px 0;
  width: 100%;
  padding: 0 !important;
  justify-content: center;
}

/* ---- Main wrapper ---- */
.main-wrapper {
  margin-left: var(--zw-sider-width);
  transition: margin-left 0.3s;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main-wrapper.collapsed {
  margin-left: var(--zw-sider-collapsed-width);
}

.app-header {
  height: var(--zw-header-height);
  background: #ffffff;
  border-bottom: 1px solid var(--zw-border);
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 0 var(--zw-gap);
  gap: 12px;
  flex-shrink: 0;
}
.hamburger {
  display: none;
  cursor: pointer;
  color: var(--zw-text-secondary);
}
.header-right {
  margin-left: auto;
}

.app-content {
  flex: 1;
  padding: var(--zw-gap);
  overflow-y: auto;
  background: var(--zw-bg);
}

/* ---- Mobile overlay ---- */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 199;
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .sider {
    transform: translateX(-100%);
  }
  .sider.mobile-open {
    transform: translateX(0);
    width: var(--zw-sider-width);
  }
  .main-wrapper,
  .main-wrapper.collapsed {
    margin-left: 0;
  }
  .hamburger {
    display: block;
  }
}
</style>
