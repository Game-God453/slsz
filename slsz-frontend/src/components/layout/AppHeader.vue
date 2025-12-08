<template>
  <div class="header">
    <!-- <div class="header-left" @click="goToPage('/')" style="cursor: pointer;">
      <h1 class="title">赛链速组</h1>
      <div class="subtitle">我的竞赛圈子</div>
    </div> -->
    <div class="logo-container" @click="goToPage('/')" style="cursor: pointer;">
      <img src="../../assets/logo.png" alt="赛链速组" class="logo-image" />
    </div>
    <div class="header-center">
      <div class="search-box">
        <el-input
          placeholder="输入竞赛名称查询"
          v-model="searchText"
          class="search-input"
        ></el-input>
        <el-button class="search-button" type="success" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
    </div>
    <div class="header-right">
      <el-badge :value="unreadAnnouncementsCount" class="notification-badge">
        <el-button circle @click="goToPage('/notification')">
          <el-icon><Bell /></el-icon>
        </el-button>
      </el-badge>
      <div class="user-profile-container" @mouseenter="showUserProfile = true" @mouseleave="showUserProfile = false">
        <el-avatar :size="40" class="user-avatar" @click="handleAvatarClick">
          <el-icon v-if="!userState.isLoggedIn || !userState.userInfo.avatar"><User /></el-icon>
          <img v-else :src="userState.userInfo.avatar + '?t=' + new Date().getTime()" alt="avatar" />
        </el-avatar>
        <span v-if="userState.isLoggedIn" class="user-name">{{ userState.userInfo.username || '用户' }}</span>
        <div v-if="userState.isLoggedIn" class="user-level">
          <el-icon><Trophy /></el-icon>
        </div>
        
        <transition name="profile-expand">
          <div v-show="showUserProfile && userState.isLoggedIn" class="user-profile-card">
            <div class="profile-header">
              <el-avatar :size="60" class="profile-avatar">
                <el-icon v-if="!userState.isLoggedIn || !userState.userInfo.avatar"><User /></el-icon>
                <img v-else :src="userState.userInfo.avatar + '?t=' + new Date().getTime()" alt="avatar" />
              </el-avatar>
              <div class="profile-info">
                <div class="profile-name">{{ userState.userInfo.username || '用户' }}</div>
                <div class="profile-level">
                  <el-icon><Trophy /></el-icon>
                  <span>Lv.6</span>
                </div>
              </div>
            </div>
            <div class="profile-stats">
              <div class="stat-item">
                <div class="stat-value">{{ userState.userInfo.space_count || 0 }}</div>
                <div class="stat-label">参加竞赛空间数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userState.userInfo.team_count || 0 }}</div>
                <div class="stat-label">参加团队数</div>
              </div>
            </div>
            <div class="profile-actions">
              <el-button size="small" type="primary" @click="goToPage('/profile')">个人中心</el-button>
              <el-button size="small" @click="goToPage('/my-teams')">我的队伍</el-button>
              <el-button size="small" type="danger" @click="handleLogout">退出登录</el-button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>

  <!-- 登录模态框 -->
  <login-modal
    v-model:show="showLoginModal"
    @login-success="handleLoginSuccess"
    @go-register="handleGoRegister"
  />

  <!-- 注册模态框 -->
  <register-modal
    v-model:show="showRegisterModal"
    @register-success="handleRegisterSuccess"
    @go-login="handleGoLogin"
  />

  <!-- 未登录公告弹窗 -->
  <el-dialog
    v-model="showAnnouncementDialog"
    title="网站使用指南"
    width="500px"
    :close-on-click-modal="false"
    :show-close="true"
  >
    <div class="announcement-content">
      <h3 class="instruction-title">使用说明</h3>
      <p class="instruction-text">由于学校间竞赛数据隔离，所以网站未登录前不会获取任何有效数据，请使用下面的账户信息进行登录。</p>
      
      <h3 class="account-title">用户账号信息</h3>
      <p style="display: inline;">由于本网站服务于3类用户：普通学生、竞赛负责人、学校超级管理员，故不同账号登录的功能有所不同，为方便体验，我们预先创建了3个账号，具体如下：</p>
      <p style="display: inline; color: red;">（点击右上角头像登录）</p>
      <div class="account-info">
        <h4>①普通学生（请使用网址：<a href="http://47.121.203.184:8080" target="_blank" class="link-url">http://47.121.203.184:8080</a> 登录，即本网址）</h4>
        <p>手机号码：13000000000</p>
        <p>密码：123456</p>
      </div>
      <div class="account-info">
        <h4>②竞赛负责人（请使用网址：<a href="http://47.121.203.184:8080" target="_blank" class="link-url">http://47.121.203.184:8080</a> 登录，即本网址）</h4>
        <p>手机号码：14000000000</p>
        <p>密码：123456</p>
      </div>
      <div class="account-info">
        <h4>③学校超级管理员（请使用网址：<a href="http://116.62.208.67:8000/admin" target="_blank" class="link-url">http://116.62.208.67:8000/admin</a> 登录）</h4>
        <p>phone：15000000000</p>
        <p>password：123456</p>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="closeAnnouncementDialog">我知道了</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { Bell, User, Trophy, Search } from "@element-plus/icons-vue";
import { userState, userActions } from "../../store/user";
import LoginModal from "../login/LoginModal.vue";
import RegisterModal from "../login/RegisterModal.vue";
import * as api from '../../utils/api';


export default {
  name: "AppHeader",
  components: {
    Bell,
    User,
    Trophy,
    Search,
    LoginModal,
    RegisterModal
  },
  data() {
    return {
      searchText: "",
      showUserProfile: false,
      showLoginModal: false,
      showRegisterModal: false,
      unreadAnnouncementsCount: 0,
      showAnnouncementDialog: false,
    };
  },
  methods: {
    checkLoginStatus() {
      // 检查用户是否已登录，如果未登录则显示公告
      if (!userState.isLoggedIn) {
        // 检查本地存储中是否已经关闭过公告
        const hasClosedAnnouncement = localStorage.getItem('hasClosedAnnouncement');
        if (!hasClosedAnnouncement) {
          this.showAnnouncementDialog = true;
        }
      }
    },
    
    closeAnnouncementDialog() {
      this.showAnnouncementDialog = false;
      // 在本地存储中记录已关闭公告，避免重复显示
      //localStorage.setItem('hasClosedAnnouncement', 'true');
    },
    
    handleSearch() {
      this.$router.push('/competition/category?search='+this.searchText).then(() => {
      window.location.reload(); // 导航完成后刷新页面
    });
    },
    goToPage(path) {
      this.$router.push(path);
    },
    handleAvatarClick() {
      if (!userState.isLoggedIn) {
        this.showLoginModal = true;
      }
    },
    handleLoginSuccess() {
      this.showUserProfile = true;
      this.$emit('login-success');
    },
    handleGoRegister() {
      this.showLoginModal = false;
      this.showRegisterModal = true;
    },
    handleGoLogin() {
      this.showRegisterModal = false;
      this.showLoginModal = true;
    },
    handleRegisterSuccess() {
      this.$message.success('注册成功，请登录');
      this.handleGoLogin();
    },
    async handleLogout() {
      try {
        await userActions.logout();
        this.$message.success('退出登录成功');
        this.showUserProfile = false;
        this.$emit('logout-success');
        this.$router.push(`/`).then(() => {
          window.location.reload(); // 导航完成后刷新页面
        });
      } catch (error) {
        console.error('退出登录失败', error);
        this.$message.error('退出登录失败');
      }
    },
    // 获取未读公告
    async fetchUnreadAnnouncementsCounts() {
        if (!this.userState.isLoggedIn) return;
        
        try {
          const response = await api.getUnreadAnnouncements();
          // console.log('获取未读公告数成功', response.data);
          // this.unreadAnnouncementsCount = response.data.length;
          this.unreadAnnouncements = response.data;
          
          // 处理未读公告数据，转换为通知列表格式
          //const notificationItems = [];
          
          for (const spaceData of response.data) {
            if (spaceData.unread_count > 0) {
              this.unreadAnnouncementsCount = this.unreadAnnouncementsCount+spaceData.unread_count;
            }
          }
          return this.unreadAnnouncementsCount;
        } catch (error) {
          console.error('获取未读公告数失败', error);
        } 
    },
    async updateUnreadCount() {
      this.unreadAnnouncementsCount = await this.fetchUnreadAnnouncementsCounts();
    }
  },
  setup() {
    return {
      userState
    };
  },
  mounted() {
    this.updateUnreadCount();
    this.checkLoginStatus();
  },
  watch: {
    'userState.isLoggedIn': function() {
      this.updateUnreadCount();
    }
  }
};
</script>

<style scoped>
.announcement-content {
  font-size: 14px;
  line-height: 1.5;
}

.instruction-title, .account-title {
  margin: 0 0 10px 0;
  color: #409EFF;
  font-size: 16px;
  font-weight: bold;
}

.instruction-text {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #ecf5ff;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
}

.account-info {
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.account-info h4 {
  margin: 0 0 8px 0;
  color: #409EFF;
}

.account-info p {
  margin: 5px 0;
}

.link-url {
  color: #409EFF;
  text-decoration: none;
  transition: all 0.3s;
}

.link-url:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.dialog-footer {
  text-align: center;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1000;
}

.header-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.title {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #606266;
}

.logo-container {
  margin: 0 20px;
}

.logo-image {
  height: 50px;
  width: auto;
  object-fit: contain;
}

.header-center {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin: 0 20px;
}

.search-box {
  display: flex;
  align-items: center;
  width: 100%;
  align-self: center;
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 4px 0 0 4px;
}

.search-button {
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  padding: 0 15px;
  height: 32px;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.notification-badge {
  margin-right: 10px;
}

.user-profile-container {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-avatar {
  margin-right: 5px;
}

.user-name {
  font-size: 14px;
  color: #303133;
  margin-right: 5px;
}

.user-level {
  color: #e6a23c;
}

.user-profile-card {
  position: absolute;
  top: 50px;
  right: 0;
  width: 280px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 100;
  padding: 16px;
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.profile-avatar {
  margin-right: 12px;
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.profile-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.profile-level {
  display: flex;
  align-items: center;
  color: #e6a23c;
  font-size: 12px;
}

.profile-level .el-icon {
  margin-right: 4px;
}

.profile-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 10px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.profile-actions {
  display: flex;
  justify-content: space-between;
}

/* 展开动画效果 */
.profile-expand-enter-active,
.profile-expand-leave-active {
  transition: all 0.3s ease;
  transform-origin: top right;
}

.profile-expand-enter-from,
.profile-expand-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>