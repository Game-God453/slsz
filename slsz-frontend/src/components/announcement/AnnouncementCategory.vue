<template>
  <div class="category-container">
    <div class="category-header">
      <h3>公告分类</h3>
      <el-button type="primary" size="small" @click="addCategory">增加分类</el-button>
    </div>
    <ul class="category-list">
      <li 
        v-for="(category, index) in categories" 
        :key="index"
        :class="{ active: category.name === activeCategory }"
        @click="selectCategory(category.name)"
      >
        {{ category.name }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'AnnouncementCategory',
  data() {
    return {
      categories: [
        { name: '全部' },
        { name: '竞赛公告' },
        { name: '申请通知' },
        { name: '队伍消息' },
        { name: 'BALABALA' },
        { name: 'BALABALA' }
      ],
      activeCategory: '竞赛公告'
    }
  },
  methods: {
    selectCategory(categoryName) {
      this.activeCategory = categoryName;
      this.$emit('category-change', categoryName);
    },
    addCategory() {
      // 实现添加分类的逻辑
      this.$message.info('增加分类功能待实现');
    }
  }
}
</script>

<style scoped>
.category-container {
  width: 200px;
  border-right: 1px solid #e0e0e0;
  padding: 10px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.category-header h3 {
  margin: 0;
  font-size: 16px;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-list li {
  padding: 10px 15px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 5px;
}

.category-list li.active {
  background-color: #e6f7ff;
  color: #1890ff;
}

.category-list li:hover {
  background-color: #f5f5f5;
}
</style>