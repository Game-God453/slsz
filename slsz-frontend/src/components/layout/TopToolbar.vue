<template>
  <div class="toolbar">
    <div class="tab-container">
      <div class="tab-item" :class="{ active: activeTab === 'message' }" @click="activeTab = 'message'">
        消息设置
      </div>
      <div class="tab-item" :class="{ active: activeTab === 'announcement' }" @click="activeTab = 'announcement'">
        公告消息
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopToolbar',
  data() {
    return {
      activeTab: 'announcement'
    }
  }
}
</script>

<style scoped>
.toolbar {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.tab-container {
  display: flex;
}

.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
  margin-right: 10px;
  background-color: #fff;
}

.tab-item.active {
  background-color: #409EFF;
  color: white;
}
</style>