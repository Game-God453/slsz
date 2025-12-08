<template>
  <div class="user-profile-page">
    <div class="page-header">
      <div class="back-button" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>返回首页
      </div>
      <h2>个人中心</h2>
    </div>

    <div class="profile-content">
      <div class="section user-info-section">
        <h3 class="section-title">个人信息</h3>
        <div class="user-info-container">
          <div class="avatar-container">
            <el-avatar :size="120" class="user-avatar">
              <el-icon v-if="!userForm.avatar"><User /></el-icon>
              <img v-else :src="userForm.avatar" alt="头像" />
            </el-avatar>
            <el-button class="upload-button" type="primary" size="small" @click="handleAvatarUpload">
              更换头像
            </el-button>
            <input
              type="file"
              ref="avatarInput"
              style="display: none"
              accept="image/*"
              @change="onAvatarFileChange"
            />
          </div>
          <div class="form-container">
            <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
              <el-form-item label="昵称" prop="username">
                <el-input v-model="userForm.username" placeholder="请输入昵称"></el-input>
              </el-form-item>
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="userForm.phone" disabled></el-input>
                <div class="help-text">手机号不可修改</div>
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="userForm.email" placeholder="请输入邮箱"></el-input>
              </el-form-item>
              <el-form-item label="学校" prop="school">
                <el-input v-model="userForm.school" disabled></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveUserInfo" :loading="saving">修改用户信息</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>

      <div class="section account-info-section">
        <h3 class="section-title">账户安全</h3>
        <div class="account-info-container">
          <!-- Add Notification Settings Button -->
          <div class="setting-item" style="margin-bottom: 20px;">
            <h4>通知设置</h4>
            <p>管理您希望收到的通知类型。</p>
            <el-button type="primary" @click="openNotificationDialog">设置通知</el-button>
          </div>
          
          <div class="danger-zone">
            <h4>危险操作</h4>
            <p>注销账号后，您的所有数据将被删除，且无法恢复</p>
            <el-button type="danger" @click="showDeleteConfirm">注销账号</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认注销对话框 -->
    <el-dialog
      v-model="deleteAccountDialogVisible"
      title="注销账号确认"
      width="400px"
    >
      <div class="delete-account-dialog">
        <p>注销账号将删除所有与您账号相关的数据，此操作不可恢复。</p>
        <p>确认要注销您的账号吗？</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteAccountDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteAccount" :loading="deletingAccount">确认注销</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Notification Settings Dialog -->
    <el-dialog
      v-model="notificationDialogVisible"
      title="通知设置"
      width="500px"
    >
      <el-form label-width="150px">
        <el-form-item label="团队申请/邀请处理">
          <el-switch v-model="notificationSettings.team_handel_notify" />
        </el-form-item>
        <el-form-item label="空间动态更新">
          <el-switch v-model="notificationSettings.space_handel_notify" />
        </el-form-item>
        <el-form-item label="竞赛公告发布">
          <el-switch v-model="notificationSettings.announcement_notify" />
        </el-form-item>
        <el-form-item label="问答回复提醒">
          <el-switch v-model="notificationSettings.reply_notify" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="notificationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveNotificationSettings" :loading="savingNotifications">保存设置</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ArrowLeft, User } from '@element-plus/icons-vue';
import { reactive } from 'vue'; // Import reactive
import { userState, userActions } from '../../store/user';
import { updateUserInfo, deleteAccount, setNotificationSettings } from '../../utils/api'; // Import setNotificationSettings and potentially getUserInfo if needed

export default {
  name: 'UserProfile',
  components: {
    ArrowLeft,
    User
  },
  data() {
    return {
      saving: false,
      deletingAccount: false,
      deleteAccountDialogVisible: false,
      notificationDialogVisible: false, // Add state for notification dialog
      savingNotifications: false, // Add state for saving notifications
      
      userForm: {
        avatar: '',
        username: '',
        phone: '',
        email: '',
        school: ''
      },
      // Add reactive state for notification settings
      notificationSettings: reactive({
        team_handel_notify: false,
        space_handel_notify: false,
        announcement_notify: false,
        reply_notify: false
      }),
      
      userRules: {
        username: [
          { required: true, message: '请输入昵称', trigger: 'blur' },
          { min: 2, max: 20, message: '昵称长度在2到20个字符之间', trigger: 'blur' }
        ],
        email: [
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      }
    };
  },
  created() {
    this.loadUserInfo();
  },
  mounted() {
    // 确保用户信息是最新的，重新从服务器获取
    if (userState.isLoggedIn) {
      userActions.fetchUserInfo().then(() => {
        this.loadUserInfo();
      });
    }
  },
  methods: {
    goBack() {
      this.$router.push('/');
    },
    
    async loadUserInfo() { // Make async if we need to await fetch
      if (userState.isLoggedIn) {
        // Ensure latest info is fetched if not already loaded
        if (!userState.userInfo?.username) { 
          await userActions.fetchUserInfo(); // Wait for fetch to complete
        }
        
        if (userState.userInfo) {
          // Load user info
          this.userForm.avatar = userState.userInfo.avatar || '';
          this.userForm.username = userState.userInfo.username || '';
          this.userForm.phone = userState.userInfo.phone || '';
          this.userForm.email = userState.userInfo.email || '';
          this.userForm.school = userState.userInfo.school || '';
          
          // Load notification settings - Assuming they are part of userInfo
          // Adjust the property names if they differ in the actual API response
          if (userState.userInfo.notificationSettings) { // Check if settings exist
             this.notificationSettings.team_handel_notify = userState.userInfo.notificationSettings.team_handel_notify ?? false;
             this.notificationSettings.space_handel_notify = userState.userInfo.notificationSettings.space_handel_notify ?? false;
             this.notificationSettings.announcement_notify = userState.userInfo.notificationSettings.announcement_notify ?? false;
             this.notificationSettings.reply_notify = userState.userInfo.notificationSettings.reply_notify ?? false;
          } else {
            // Optionally fetch settings separately if not included in userInfo
            // console.warn('Notification settings not found in userInfo');
            // You might need a separate API call here like: 
            // const settingsResponse = await getNotificationSettings();
            // if (settingsResponse && settingsResponse.data) { ... load settings ... }
          }
        }
      } else {
        this.$message.warning('请先登录');
        this.$router.push('/');
      }
    },
    
    handleAvatarUpload() {
      this.$refs.avatarInput.click();
    },
    
    onAvatarFileChange(e) {
      const file = e.target.files[0];
      if (!file) return;
      
      // 这里可以添加文件类型和大小验证
      if (!file.type.match('image.*')) {
        this.$message.error('请上传图片文件');
        return;
      }
      
      // 创建本地预览
      const reader = new FileReader();
      reader.onload = (event) => {
        this.userForm.avatar = event.target.result;
      };
      reader.readAsDataURL(file);
    },
    
    async saveUserInfo() {
      if (!this.$refs.userFormRef) return;
      
      try {
        await this.$refs.userFormRef.validate();
        this.saving = true;
        
        // 准备用户数据
        const userData = {
          username: this.userForm.username,
          email: this.userForm.email,
          avatar: this.userForm.avatar
        };
        
        // 调用更新用户信息API
        const response = await updateUserInfo(userData);
        
        if (response) {
          // 更新本地状态
          userActions.updateUserInfo({
            username: this.userForm.username,
            email: this.userForm.email,
            avatar: this.userForm.avatar
          });
          
          // 重新获取用户信息以确保头像URL是最新的
          await userActions.fetchUserInfo();
          // 重新加载表单
          this.loadUserInfo();
          
          this.$message({
            message: '用户信息更新成功',
            type: 'success'
          });
        } else {
          this.$message.error(response?.message || '更新失败');
        }
      } catch (error) {
        console.error('保存用户信息失败:', error);
        this.$message.error('保存用户信息失败: ' + (error.message || '未知错误'));
      } finally {
        this.saving = false;
      }
    },
    
    // Method to open notification settings dialog
    openNotificationDialog() {
      // Optionally re-fetch settings here if they can change elsewhere
      this.loadUserInfo(); // Reload to ensure settings are current
      this.notificationDialogVisible = true;
    },

    // Method to save notification settings
    async saveNotificationSettings() {
      this.savingNotifications = true;
      try {
        const response = await setNotificationSettings(this.notificationSettings);
        if (response) {
          this.$message.success('通知设置已更新');
          // Optionally update local user state if needed
           userActions.updateUserInfo({
            // Update local user state if notification settings are stored there
             notificationSettings: { ...this.notificationSettings }
           });
          this.notificationDialogVisible = false;
        } else {
          this.$message.error(response?.message || '更新通知设置失败');
        }
      } catch (error) {
        console.error('保存通知设置失败:', error);
        this.$message.error('保存通知设置失败: ' + (error.message || '未知错误'));
      } finally {
        this.savingNotifications = false;
      }
    },
    
    showDeleteConfirm() {
      this.deleteAccountDialogVisible = true;
    },
    
    async deleteAccount() {
      this.deletingAccount = true;
      
      try {
        // 调用注销账号API
        const response = await deleteAccount();
        
        if (response) {
          //console.log('response', response);
          userActions.clearUserState();
          // 注销成功后清除用户状态并重定向到首页
          //await userActions.logout(); // 调用logout确保完全退出登录
          this.$message.success('账号已注销');
          this.deleteAccountDialogVisible = false;
          
          this.$router.push('/');
        } else {
          this.$message.error(response?.message || '注销失败');
        }
      } catch (error) {
        console.error('账号注销失败:', error);
        this.$message.error('账号注销失败: ' + (error.message || '未知错误'));
      } finally {
        this.deletingAccount = false;
      }
    }
  }
};
</script>

<style scoped>
.user-profile-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 20px;
  color: #409eff;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.section-title {
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.user-info-container {
  display: flex;
  gap: 30px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  border: 2px solid #ebeef5;
}

.form-container {
  flex: 1;
}

.account-info-container {
  max-width: 500px;
}

.help-text {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

.danger-zone {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f56c6c;
}

.danger-zone h4 {
  color: #f56c6c;
  margin-top: 0;
}

.delete-account-dialog p {
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .user-info-container {
    flex-direction: column;
  }
}
</style>