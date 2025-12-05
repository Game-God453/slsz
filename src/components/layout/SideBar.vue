<template>
  <div class="sidebar">
    <div class="logo">
      <h2>赛链速组</h2>
    </div>
    <el-menu
      :default-active="activeIndex"
      class="sidebar-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      
      <el-menu-item index="/announcement">
        <el-icon><Bell /></el-icon>
        <span>公告管理</span>
      </el-menu-item>
      
      <el-menu-item index="3">
        <el-icon><Message /></el-icon>
        <span>消息管理</span>
      </el-menu-item>
      
      <!-- 设置菜单，使用 el-sub-menu 实现可折叠功能 -->
      <el-sub-menu index="4">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </template>
        <el-menu-item index="4-1">账号安全</el-menu-item>
        <el-menu-item index="4-2">员工管理</el-menu-item>
        <el-menu-item index="4-3">权限设置</el-menu-item>
        <el-menu-item index="4-4">系统配置</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script>
export default {
  name: 'SideBar',
  data() {
    return {
      activeIndex: this.$route.path
    }
  },
  watch: {
    $route(to) {
      this.activeIndex = to.path;
    }
  }
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.sidebar-menu {
  border-right: none;
}

/* 确保菜单项有足够的高度和内边距 */
.el-menu-item, .el-sub-menu__title {
  height: 50px;
  line-height: 50px;
}

/* 图标和文字的间距 */
.el-icon {
  margin-right: 10px;
}
</style>