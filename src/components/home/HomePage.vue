<template>
  <div class="home-page">
    <!-- 使用全局通用的顶部导航栏 -->
    <app-header 
      @search="handleSearch"
      @login-success="handleLoginSuccess"
      @logout-success="handleLogoutSuccess"
    />

    <!-- 添加导航菜单 -->
    <home-nav :active-page="'home'" />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <h2 class="section-title">热门赛事推送</h2>
      <div class="carousel-container">
        <el-carousel 
          ref="carousel" 
          :autoplay="true" 
          indicator-position="none"
          interval="5000"
          class="main-carousel"
          height="500px" 
          @change="handleCarouselChange"
        >
          <el-carousel-item v-for="(item, index) in carouselItems" :key="index">
            <div class="carousel-content">
              <div class="carousel-image">
                <img
                  :src="item.image"
                  :alt="item.title"
                  class="poster-image"
                  @click="goToCompetitionSpace(item.title)"
                />

              </div>
              <!-- <div class="carousel-info">
                <h3 class="carousel-title">{{ item.title }}</h3>
                <p class="carousel-description">{{ item.description }}</p>
                <el-button type="primary" size="small" @click="goToCompetitionSpace(item.spaceId)">查看详情</el-button>
              </div> -->
              <!-- 右侧文字导航 -->
              <div class="competition-nav-list">
                <div 
                  v-for="(navItem, navIndex) in carouselItems" 
                  :key="navIndex"
                  class="competition-nav-item"
                  :class="{ active: currentCarouselIndex === navIndex }"
                  @click="setCarouselIndex(navIndex)"
                >
                  {{ navItem.title }}
                </div>
              </div>
            </div>
            <!-- 底部数字导航 -->
            <div class="page-numbers">
              <div 
                v-for="pageIndex in carouselItems.length" 
                :key="pageIndex" 
                class="page-number" 
                :class="{ active: currentCarouselIndex === pageIndex - 1 }"
                @click="setCarouselIndex(pageIndex - 1)"
              >
                {{ pageIndex }}
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>

    <!-- 底部标签导航栏 -->
    <div class="tab-section">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="未读公告" name="unread">
          <el-badge is-dot class="tab-badge"></el-badge>
        </el-tab-pane>
        <el-tab-pane label="回复我的消息" name="pending">
          <el-badge is-dot class="tab-badge"></el-badge>
        </el-tab-pane>
      </el-tabs>

      <!-- 表格区域 -->
      <div class="table-container">
        <div v-if="activeTab === 'unread'">
          <div v-if="isLoadingAnnouncements" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="unreadAnnouncements.length > 0">
            <div v-for="(spaceData, index) in unreadAnnouncements" :key="index" class="space-announcements">
              <h4 class="space-title">{{ spaceData.space_title }}</h4>
              <div class="announcement-count">未读公告数: {{ spaceData.unread_count }}</div>
              <el-button 
                type="primary" 
                size="small" 
                @click="goToCompetitionSpaceID()"
              >查看详情</el-button>
            </div>
          </div>
          <div v-else class="empty-message">
            <el-empty description="暂无未读公告" />
          </div>
        </div>
        
        <div v-else-if="activeTab === 'pending'">
          <div v-if="isLoadingReplies" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="userReplies.length > 0">
            <el-table :data="userReplies" style="width: 100%">
              <el-table-column prop="space_title" label="竞赛空间" width="180" />
              <el-table-column prop="question_content" label="问题内容" />
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="viewReplyDetail(scope.row)"
                  >查看回复</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else class="empty-message">
            <el-empty description="暂无回复消息" />
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="footer">
      <div class="app-download">
        <span>计算机设计大赛</span>
      </div>
      <div class="friendly-links">
        <el-link type="info">关于我们</el-link>
        <el-link type="info">联系我们</el-link>
        <el-link type="info">帮助中心</el-link>
      </div>
      <div class="copyright">计算机设计大赛小组 版权所有</div>
    </div>
  </div>
</template>

<script>
import { userState } from "../../store/user";
import AppHeader from "../layout/AppHeader.vue";
import HomeNav from './HomeNav.vue';
import * as api from '../../utils/api';

export default {
  name: "HomePage",
  components: {
    AppHeader,
    HomeNav
  },
  data() {
    return {
      searchText: "",
      activeTab: "unread",
      tableData: [
        {
          time: "2023-10-15",
          name: "全国大学生计算机设计大赛",
          manager: "张教授",
          status: "进行中",
        },
        {
          time: "2023-10-20",
          name: "机械创新设计大赛",
          manager: "李教授",
          status: "报名中",
        },
        {
          time: "2023-11-01",
          name: "电子设计大赛",
          manager: "王教授",
          status: "未开始",
        },
        {
          time: "2023-11-15",
          name: "数学建模大赛",
          manager: "赵教授",
          status: "已结束",
        },
      ],
      notifications: [],
      unreadAnnouncements: [],
      userReplies: [],
      isLoadingAnnouncements: false,
      isLoadingReplies: false,
      carouselItems: [],
      isLoading: false,
      currentCarouselIndex: 0,
    };
  },
  methods: {
    handleCarouselChange(index) {
      this.currentCarouselIndex = index;
    },
    setCarouselIndex(index) {
      this.$refs.carousel.setActiveItem(index);
    },
    handleSearch(text) {
      this.searchText = text;
      // 实现搜索逻辑
    },
    handleLoginSuccess() {
      // 处理登录成功后的首页特定逻辑
      this.$message.success('欢迎回来！');
      this.fetchRecentCompetitions();
      this.fetchUnreadAnnouncements();
      this.fetchUserReplies();
      window.location.reload();
    },
    handleLogoutSuccess() {
      // 处理登出后的首页特定逻辑
      this.$message.info('已安全退出');
      // 清空数据
      this.unreadAnnouncements = [];
      this.userReplies = [];
      this.notifications = [];
    },
    
    // 获取未读公告
    async fetchUnreadAnnouncements() {
      if (!this.userState.isLoggedIn) return;
      
      try {
        this.isLoadingAnnouncements = true;
        const response = await api.getUnreadAnnouncements();
        console.log('获取未读公告数据:', response);
        if (response && response.data && response.data.length > 0) {
          //console.log('获取未读公告数据2:', response.data);
          this.unreadAnnouncements = response.data;
          
          // 处理未读公告数据，转换为通知列表格式
          const notificationItems = [];
          
          for (const spaceData of response.data) {
            if (spaceData.unread_count > 0) {
              notificationItems.push({
                title: `${spaceData.space_title} 有 ${spaceData.unread_count} 条未读公告`,
                spaceId: spaceData.space_id,
                type: 'announcement'
              });
            }
          }
          
          // 更新通知列表
          this.notifications = [...notificationItems];
        } else {
          this.unreadAnnouncements = [];
        }
      } catch (error) {
        console.error('获取未读公告失败:', error);
        this.$message.error('获取未读公告数据失败');
      } finally {
        this.isLoadingAnnouncements = false;
      }
    },
    
    // 获取回复我的消息
    async fetchUserReplies() {
      if (!this.userState.isLoggedIn) return;
      
      try {
        this.isLoadingReplies = true;
        // 使用discussion/listReplyToMe接口获取回复消息
        const response = await api.getRepliesToMe();
        
        if (response && response.data && response.data.replies && response.data.replies.length > 0) {
          this.userReplies = response.data.replies;
          
          // 处理回复消息数据，转换为通知列表格式
          const replyItems = this.userReplies.map(reply => ({
            title: `${reply.space_title}: ${reply.question_content}`,
            type: 'reply'
          }));
          
          // 更新通知列表，合并未读公告和回复消息
          this.notifications = [...this.notifications, ...replyItems];
        }
      } catch (error) {
        console.error('获取回复消息失败:', error);
      } finally {
        this.isLoadingReplies = false;
      }
    },
    // 获取最近10天内的热门竞赛
    async fetchRecentCompetitions() {
      try {
        this.isLoading = true;
        const response = await api.getRecentCompetitions();
        if (response && response.data && response.data.length > 0) {
          // 将API返回的数据转换为轮播图所需的格式
          this.carouselItems = response.data.map(item => ({
            id: item.id,
            image: item.poster_url || require("../../assets/laptop-icon.svg"), // 使用海报URL或默认图片
            title: item.title,
            description: item.description || `${this.getCategoryText(item.category)} - ${this.getLevelText(item.level)}`,
            spaceId: item.id
          }));
        } else {
          // 如果没有数据，使用默认图片
          this.carouselItems = [
            {
              image: require("../../assets/laptop-icon.svg"),
              title: "暂无近期竞赛",
              description: "请稍后查看或浏览竞赛分类页面了解更多竞赛信息。"
            }
          ];
        }
      } catch (error) {
        console.error('获取热门竞赛失败:', error);
        //this.$message.error('获取热门竞赛数据失败');
        // 出错时使用默认图片
        this.carouselItems = [
          {
            image: require("../../assets/laptop-icon.svg"),
            title: "数据加载失败",
            description: "请稍后再试或联系管理员。"
          }
        ];
      } finally {
        this.isLoading = false;
      }
    },
    // 获取竞赛类别文本
    getCategoryText(category) {
      const categoryMap = {
        'subject': '学科竞赛',
        'innovation': '创新创业',
        'entertainment': '素质拓展',
        'others': '其他'
      };
      return categoryMap[category] || category;
    },
    // 获取竞赛级别文本
    getLevelText(level) {
      const levelMap = {
        'school': '校级',
        'province': '省级',
        'national': '国家级'
      };
      return levelMap[level] || level;
    },
    
    // 查看回复详情
    viewReplyDetail(reply) {
      if (!reply || !reply.replies || reply.replies.length === 0) {
        this.$message.info('暂无回复内容');
        return;
      }
      
      // 构建回复内容显示
      const replyContent = reply.replies.map(item => {
        return `${item.from_user_username}: ${item.content} (${this.formatDateTime(item.created_at)})`;
      }).join('\n\n');
      
      // 使用Element Plus的MessageBox显示回复详情
      this.$msgbox({
        title: reply.question_content,
        message: replyContent,
        confirmButtonText: '关闭'
      });
    },
    
    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '';
      const date = new Date(dateTimeStr);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
    
// 跳转到竞赛空间
  goToCompetitionSpaceID() {
      // if (!spaceId) {
      //   this.$message.error('无效的竞赛空间ID');
      //   return;
      // }
      // this.$router.push(`/competition/space/${spaceId}`);
      //console.log('跳转到竞赛空间', title);
      this.$router.push('/notification');
    },

    // 跳转到竞赛空间
    goToCompetitionSpace(title) {
      // if (!spaceId) {
      //   this.$message.error('无效的竞赛空间ID');
      //   return;
      // }
      // this.$router.push(`/competition/space/${spaceId}`);
      console.log('跳转到竞赛空间', title);
      this.$router.push('/competition/category?search='+title).then(() => {
        window.location.reload(); 
      });
    }
  },
  setup() {
    return {
      userState
    };
  },
  mounted() {
    // 组件挂载时获取热门竞赛数据
    this.fetchRecentCompetitions();
    
    // 如果用户已登录，获取未读公告和回复消息
    if (this.userState.isLoggedIn) {
      this.fetchUnreadAnnouncements();
      this.fetchUserReplies();
    }
  }
};
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  padding: 15px;
  max-width: 1600px;
  margin: 0 auto;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.carousel-container {
  position: relative;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.main-carousel {
  width: 100%;
}

.carousel-content {
  display: flex;
  align-items: stretch; 
  height: 100%;
  position: relative;
}

.carousel-image {
  flex: 3;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  height: 450px;
  min-height: 450px;
}

.poster-image {
  width: 100%; 
  height: 80%;
  object-fit: cover;
}

.carousel-info {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.carousel-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.carousel-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 20px;
}

.page-numbers {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 5px;
}

.page-number {
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  cursor: pointer;
  border: 1px solid #409eff;
  border-radius: 50%;
  transition: all 0.3s;
  color: #409eff;
  background-color: rgba(255, 255, 255, 0.8);
}

.page-number.active {
  background-color: #409eff;
  color: #fff;
}

.competition-nav-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 450px;
  overflow-y: auto;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.competition-nav-item {
  cursor: pointer;
  padding: 8px 10px;
  border: 1px solid #409eff;
  border-radius: 4px;
  transition: all 0.3s;
  color: #409eff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background-color: rgba(255, 255, 255, 0.9);
}

.competition-nav-item.active {
  background-color: #409eff;
  color: #fff;
}

/* 底部标签导航栏样式 */
.tab-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.tab-badge {
  margin-top: -2px;
  margin-left: 5px;
}

.table-container {
  margin-top: 20px;
}

.notification-area {
  margin-top: 20px;
}

.notification-item {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.loading-container {
  padding: 20px;
}

.empty-message {
  padding: 20px;
  text-align: center;
}

.space-announcements {
  padding: 15px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.space-title {
  margin: 0 0 10px 0;
  color: #303133;
}

.announcement-count {
  margin-bottom: 10px;
  color: #606266;
}

/* 底部导航样式 */
.footer {
  margin-top: auto;
  padding: 20px;
  background-color: #303133;
  color: #fff;
  text-align: center;
}

.app-download,
.friendly-links {
  margin-bottom: 15px;
}

.friendly-links .el-link {
  margin: 0 10px;
}

.copyright {
  font-size: 12px;
  color: #909399;
}
</style>
