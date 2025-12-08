<template>
  <div class="announcement-management">
    <div class="layout">
      <div class="sidebar-container">
        <SideBar />
      </div>
      <div class="main-container">
        <TopToolbar />
        <div class="content-container">
          <div class="category-container">
            <AnnouncementCategory @category-change="handleCategoryChange" />
          </div>
          <div class="list-container">
            <AnnouncementList ref="announcementList" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from '../layout/SideBar.vue';
import TopToolbar from '../layout/TopToolbar.vue';
import AnnouncementCategory from './AnnouncementCategory.vue';
import AnnouncementList from './AnnouncementList.vue';

export default {
  name: 'AnnouncementManagement',
  components: {
    SideBar,
    TopToolbar,
    AnnouncementCategory,
    AnnouncementList
  },
  methods: {
    handleCategoryChange(category) {
      // 可以在这里处理分类变更，例如过滤公告列表
      console.log('分类变更为:', category);
    }
  }
}
</script>

<style scoped>
.announcement-management {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.layout {
  display: flex;
  height: 100%;
}

.sidebar-container {
  width: 200px;
  height: 100%;
  flex-shrink: 0;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.category-container {
  width: 200px;
  flex-shrink: 0;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.list-container {
  flex: 1;
  overflow-y: auto;
}
</style>