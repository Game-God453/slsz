<template>
  <div class="my-teams-page">
    <AppHeader />
    
    <div class="page-content">
      <div class="page-header">
        <h1 class="page-title">我的队伍</h1>
        <div class="page-subtitle">管理您创建和参与的所有队伍</div>
        <!-- Add Back Button Here -->
        <el-button class="back-button" @click="goBack" circle>
          <el-icon><Back /></el-icon>
        </el-button>
      </div>
      
      <div class="teams-container">
        <!-- 左侧标签页 -->
        <div class="teams-tabs">
          <el-tabs v-model="activeTab" @tab-click="handleTabClick">
            <el-tab-pane label="我创建的队伍" name="created">
              <div v-if="isLoading" class="loading-state">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="createdTeams.length === 0" class="empty-state">
                <el-empty description="暂无创建的队伍" />
              </div>
              <div v-else class="team-list">
                <div 
                  v-for="team in createdTeams" 
                  :key="team.team_id"
                  class="team-item"
                  :class="{ 'active': selectedTeam && selectedTeam.team_id === team.team_id }"
                  @click="selectTeam(team)"
                >
                  <div class="team-item-content">
                    <div class="team-avatar">{{ team.teamName.charAt(0) }}</div>
                    <div class="team-info-container">
                      <div class="team-name">{{ team.teamName }}</div>
                      <div class="team-space">{{ team.space_title }}</div>
                    </div>
                    <div class="team-status">
                      <el-tag size="small" :type="team.is_recruiting ? 'success' : 'info'">
                        {{ team.is_recruiting ? '招募中' : '已锁定' }}
                      </el-tag>
                      <div class="team-members-count">
                        <el-icon><User /></el-icon> {{ team.members ? team.members.length : 0 }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="我参加的队伍" name="joined">
              <div v-if="isLoading" class="loading-state">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="joinedTeams.length === 0" class="empty-state">
                <el-empty description="暂无参加的队伍" />
              </div>
              <div v-else class="team-list">
                <div 
                  v-for="team in joinedTeams" 
                  :key="team.team_id"
                  class="team-item"
                  :class="{ 'active': selectedTeam && selectedTeam.team_id === team.team_id }"
                  @click="selectTeam(team)"
                >
                  <div class="team-item-content">
                    <div class="team-avatar">{{ team.teamName.charAt(0) }}</div>
                    <div class="team-info-container">
                      <div class="team-name">{{ team.teamName }}</div>
                      <div class="team-space">{{ team.space_title }}</div>
                    </div>
                    <div class="team-status">
                      <el-tag size="small" :type="team.is_recruiting ? 'success' : 'info'">
                        {{ team.is_recruiting ? '招募中' : '已锁定' }}
                      </el-tag>
                      <div class="team-members-count">
                        <el-icon><User /></el-icon> {{ team.members ? team.members.length : 0 }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- 右侧队伍详情 -->
        <div class="team-details">
          <div v-if="!selectedTeam" class="no-team-selected">
            <el-empty description="请选择一个队伍查看详情" />
          </div>
          <div v-else class="team-detail-content">
            <div class="team-header">
              <div class="team-title-section">
                <div v-if="selectedTeam.team_captain_avatar" class="team-avatar large">
                  <el-avatar :size="50" :src="selectedTeam.team_captain_avatar" alt="队长头像"></el-avatar>
                </div>
                <div v-else class="team-avatar large">{{ selectedTeam.teamName.charAt(0) }}</div>
                <div>
                  <h2>{{ selectedTeam.teamName }}</h2>
                  <div class="team-meta">
                    <el-tag 
                      :type="selectedTeam.is_recruiting ? 'success' : 'info'"
                      size="small"
                      effect="dark"
                    >
                      {{ selectedTeam.is_recruiting ? '招募中' : '已锁定' }}
                    </el-tag>
                    <span class="team-created-time">创建于 {{ formatDate(selectedTeam.created_at) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 队伍管理按钮 -->
              <div class="team-actions">
                <!-- 队长操作按钮 -->
                <template v-if="isTeamCaptain(selectedTeam)">
                  <el-button type="primary" @click="openUpdateTeamDialog">更新队伍信息</el-button>
                  <el-button 
                    :type="selectedTeam.is_recruiting ? 'warning' : 'success'" 
                    @click="toggleRecruitment"
                  >
                    {{ selectedTeam.is_recruiting ? '停止招募' : '开始招募' }}
                  </el-button>
                  <el-button 
                    :type="selectedTeam.is_locked ? 'success' : 'warning'" 
                    @click="toggleLock"
                  >
                    {{ selectedTeam.is_locked ? '解锁队伍' : '锁定队伍' }}
                  </el-button>
                  <el-button type="danger" @click="confirmDissolveTeam">解散队伍</el-button>
                </template>
                
                <!-- 普通队员操作按钮 -->
                <template v-else>
                  <el-button type="danger" @click="confirmLeaveTeam">离开队伍</el-button>
                </template>
              </div>
            </div>
            
            <div class="team-info-cards">
              <el-card class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>队伍信息</span>
                  </div>
                </template>
                <div class="info-content">
                  <p><el-icon><Trophy /></el-icon> <strong>竞赛空间：</strong>{{ selectedTeam.space_title }}</p>
                  <p v-if="selectedTeam.qq"><el-icon><ChatDotRound /></el-icon> <strong>QQ群：</strong>{{ selectedTeam.qq }}</p>
                  <p><el-icon><User /></el-icon> <strong>队长：</strong>{{ selectedTeam.team_captain_username }}</p>
                  <p v-if="selectedTeam.team_captain_qq"><el-icon><ChatDotRound /></el-icon> <strong>队长QQ：</strong>{{ selectedTeam.team_captain_qq }}</p>
                  <!-- <p v-else><el-icon><ChatDotRound /></el-icon> <strong>队长QQ：</strong><span class="text-muted">未设置</span></p> -->
                  <p><el-icon><UserFilled /></el-icon> <strong>成员数量：</strong>{{ selectedTeam.members ? selectedTeam.members.length : 0 }}人</p>
                </div>
              </el-card>
            </div>
            
            <div class="team-members">
              <h3><el-icon><UserFilled /></el-icon> 队伍成员</h3>
              <el-table :data="selectedTeam.members" style="width: 100%" :stripe="true" border>
                <el-table-column label="用户名" prop="user_username" />
                <el-table-column label="真实姓名" prop="realName" />
                <el-table-column label="学号" prop="studentId" />
                <el-table-column label="学院" prop="collegeName" />
                <el-table-column label="身份" width="100" align="center">
                  <template #default="scope">
                    <el-tag 
                      type="danger" 
                      effect="dark"
                      v-if="scope.row.user_username === selectedTeam.team_captain_username"
                    >
                      队长
                    </el-tag>
                    <el-tag v-else effect="plain">队员</el-tag>
                  </template>
                </el-table-column>
                <el-table-column v-if="isTeamCaptain(selectedTeam)" label="操作" width="120" align="center">
                  <template #default="scope">
                    <el-button 
                      v-if="scope.row.user_username !== selectedTeam.team_captain_username"
                      type="danger" 
                      size="small"
                      :loading="processingAction && removingMemberId === scope.row.space_user_id"
                      @click="confirmRemoveMember(scope.row.space_user_id, scope.row.user_username)"
                    >
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 更新队伍信息对话框 -->
  <el-dialog v-model="updateTeamDialogVisible" title="更新队伍信息" width="500px">
    <el-form :model="updateTeamForm" label-width="80px">
      <el-form-item label="队伍名称" required>
        <el-input v-model="updateTeamForm.teamName" placeholder="请输入队伍名称"></el-input>
      </el-form-item>
      <el-form-item label="招募需求">
        <el-input
          v-model="updateTeamForm.demand"
          type="textarea"
          placeholder="简单介绍一下队伍需求（可选）"
          :rows="3"
        ></el-input>
      </el-form-item>
      <el-form-item label="群聊qq">
        <el-input
          v-model="updateTeamForm.qq"
          type="textarea"
          placeholder="队伍群聊qq（可选）"
          :rows="1"
        ></el-input>
      </el-form-item>

      
    </el-form>
    <template #footer>
      <el-button @click="updateTeamDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="processingAction" @click="handleUpdateTeam">确认更新</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter
import { ElMessage, ElMessageBox } from 'element-plus';
import AppHeader from '../layout/AppHeader.vue';
import * as api from '../../utils/api';
import { User, UserFilled, Trophy, ChatDotRound, Back } from '@element-plus/icons-vue'; // Import Back icon
import { userState } from '../../store/user';

// Get router instance
const router = useRouter();

// Function to go back
const goBack = () => {
  router.back();
};

// 状态变量
const activeTab = ref('created');
const isLoading = ref(false);
const createdTeams = ref([]);
const joinedTeams = ref([]);
const selectedTeam = ref(null);
const updateTeamDialogVisible = ref(false);
const updateTeamForm = ref({
  teamName: '',
  demand: '',
  qq: '',
  targetNumber: ''
});
const processingAction = ref(false);
const removingMemberId = ref(null);

// 加载用户创建的队伍
const loadCreatedTeams = async () => {
  isLoading.value = true;
  try {
    const response = await api.getUserTeams(true);
    if (response && response.data) {
      createdTeams.value = response.data;
      // 如果当前没有选中的队伍，且有创建的队伍，则默认选中第一个
      if (!selectedTeam.value && createdTeams.value.length > 0) {
        selectedTeam.value = createdTeams.value[0];
      }
    } else {
      createdTeams.value = [];
    }
  } catch (error) {
    ElMessage.error('加载创建的队伍失败: ' + (error.message || '未知错误'));
    createdTeams.value = [];
  } finally {
    isLoading.value = false;
  }
};

// 加载用户参加的队伍
const loadJoinedTeams = async () => {
  isLoading.value = true;
  try {
    const response = await api.getUserTeams(false);
    if (response && response.data) {
      joinedTeams.value = response.data;
      // 如果当前没有选中的队伍，且有参加的队伍，则默认选中第一个
      if (!selectedTeam.value && joinedTeams.value.length > 0) {
        selectedTeam.value = joinedTeams.value[0];
      }
    } else {
      joinedTeams.value = [];
    }
  } catch (error) {
    ElMessage.error('加载参加的队伍失败: ' + (error.message || '未知错误'));
    joinedTeams.value = [];
  } finally {
    isLoading.value = false;
  }
};

// 处理标签页切换
const handleTabClick = (tab) => {
  if (tab.props.name === 'created') {
    if (createdTeams.value.length > 0) {
      selectedTeam.value = createdTeams.value[0];
    } else {
      selectedTeam.value = null;
    }
  } else {
    if (joinedTeams.value.length > 0) {
      selectedTeam.value = joinedTeams.value[0];
    } else {
      selectedTeam.value = null;
    }
  }
};

// 选择队伍
const selectTeam = (team) => {
  selectedTeam.value = team;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 判断当前用户是否是队长
const isTeamCaptain = (team) => {
  if (!team) return false;
  return team.team_captain_username === userState.userInfo?.username;
};

// 打开更新队伍对话框
const openUpdateTeamDialog = () => {
  if (!selectedTeam.value) return;
  updateTeamForm.value.teamName = selectedTeam.value.teamName;
  updateTeamForm.value.demand = selectedTeam.value.demand || '';
  updateTeamForm.value.qq = selectedTeam.value.qq || '';
  updateTeamForm.value.targetNumber = selectedTeam.value.targetNumber || '';
  updateTeamDialogVisible.value = true;
};

// 更新队伍信息
const handleUpdateTeam = async () => {
  if (!selectedTeam.value || !updateTeamForm.value.teamName.trim()) {
    ElMessage.warning('队伍名称不能为空');
    return;
  }
  
  processingAction.value = true;
  try {
    await api.updateTeam(selectedTeam.value.team_id, {
      teamName: updateTeamForm.value.teamName,
      demand: updateTeamForm.value.demand,
      qq: updateTeamForm.value.qq
    });
    ElMessage.success('队伍信息更新成功');
    updateTeamDialogVisible.value = false;
    
    // 更新本地数据
    selectedTeam.value.teamName = updateTeamForm.value.teamName;
    selectedTeam.value.demand = updateTeamForm.value.demand;
    selectedTeam.value.qq = updateTeamForm.value.qq;
    selectedTeam.value.targetNumber = updateTeamForm.value.targetNumber;
    // 刷新队伍列表
    if (activeTab.value === 'created') {
      loadCreatedTeams();
    } else {
      loadJoinedTeams();
    }
  } catch (error) {
    ElMessage.error('更新队伍信息失败: ' + (error.message || '未知错误'));
  } finally {
    processingAction.value = false;
  }
};

// 切换队伍招募状态
const toggleRecruitment = async () => {
  if (!selectedTeam.value) return;
  
  const newStatus = !selectedTeam.value.is_recruiting;
  const actionText = newStatus ? '开启' : '停止';
  
  try {
    processingAction.value = true;
    await api.setTeamRecruitment(selectedTeam.value.team_id, newStatus);
    ElMessage.success(`${actionText}招募成功`);
    selectedTeam.value.is_recruiting = newStatus;
    
    // 刷新队伍列表
    if (activeTab.value === 'created') {
      loadCreatedTeams();
    }
  } catch (error) {
    ElMessage.error(`${actionText}招募失败: ` + (error.message || '未知错误'));
  } finally {
    processingAction.value = false;
  }
};

// 切换队伍锁定状态
const toggleLock = async () => {
  if (!selectedTeam.value) return;
  
  const newStatus = !selectedTeam.value.is_locked;
  const actionText = newStatus ? '锁定' : '解锁';
  
  try {
    processingAction.value = true;
    await api.lockTeam(selectedTeam.value.team_id, newStatus);
    ElMessage.success(`${actionText}队伍成功`);
    selectedTeam.value.is_locked = newStatus;
    
    // 刷新队伍列表
    if (activeTab.value === 'created') {
      loadCreatedTeams();
    }
  } catch (error) {
    ElMessage.error(`${actionText}队伍失败: ` + (error.message || '未知错误'));
  } finally {
    processingAction.value = false;
  }
};

// 确认解散队伍
const confirmDissolveTeam = () => {
  if (!selectedTeam.value) return;
  
  ElMessageBox.confirm(
    '确定要解散该队伍吗？此操作不可恢复！',
    '解散队伍',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    dissolveTeam();
  }).catch(() => {
    // 用户取消操作
  });
};

// 解散队伍
const dissolveTeam = async () => {
  if (!selectedTeam.value) return;
  
  try {
    processingAction.value = true;
    await api.dissolveTeam(selectedTeam.value.team_id);
    ElMessage.success('队伍已解散');
    
    // 从列表中移除
    createdTeams.value = createdTeams.value.filter(team => team.team_id !== selectedTeam.value.team_id);
    selectedTeam.value = createdTeams.value.length > 0 ? createdTeams.value[0] : null;
  } catch (error) {
    ElMessage.error('解散队伍失败: ' + (error.message || '未知错误'));
  } finally {
    processingAction.value = false;
  }
};

// 确认移除队员
const confirmRemoveMember = (spaceUserId, memberName) => {
    //console.log('confirmRemoveMember', spaceUserId, memberName); // Add this log statement to check the spaceUserId and memberName values
  
    if (!selectedTeam.value) return;
  ElMessageBox.confirm(
    `确定要将 ${memberName} 移出队伍吗？`,
    '移除队员',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    removeMember(spaceUserId);
  }).catch(() => {
    // 用户取消操作
  });
};

// 移除队员
const removeMember = async (spaceUserId) => {
    //console.log('removeMember', spaceUserId); // Add this log statement to check the spaceUserId value
  if (!selectedTeam.value || !spaceUserId) return;
  
  try {
    processingAction.value = true;
    removingMemberId.value = spaceUserId;
    await api.removeTeamMember(selectedTeam.value.team_id, spaceUserId);
    ElMessage.success('队员已移除');
    
    // 从成员列表中移除
    selectedTeam.value.members = selectedTeam.value.members.filter(member => member.space_user_id !== spaceUserId);
  } catch (error) {
    ElMessage.error('移除队员失败: ' + (error.message || '未知错误'));
  } finally {
    processingAction.value = false;
    removingMemberId.value = null;
  }
};

// 确认离开队伍
const confirmLeaveTeam = () => {
  if (!selectedTeam.value) return;
  
  ElMessageBox.confirm(
    '确定要离开该队伍吗？',
    '离开队伍',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    leaveTeam();
  }).catch(() => {
    // 用户取消操作
  });
};

// 离开队伍
const leaveTeam = async () => {
  if (!selectedTeam.value) return;
  
  try {
    processingAction.value = true;
    await api.leaveTeam(selectedTeam.value.team_id);
    ElMessage.success('已离开队伍');
    
    // 从列表中移除
    joinedTeams.value = joinedTeams.value.filter(team => team.team_id !== selectedTeam.value.team_id);
    selectedTeam.value = joinedTeams.value.length > 0 ? joinedTeams.value[0] : null;
  } catch (error) {
    ElMessage.error('离开队伍失败: ' + (error.message || '未知错误'));
  } finally {
    processingAction.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  // 根据当前激活的标签页加载对应数据
  if (activeTab.value === 'created') {
    loadCreatedTeams();
  } else {
    loadJoinedTeams();
  }
});

// 使用watch监听标签页变化，加载对应数据
watch(activeTab, (newValue) => {
  if (newValue === 'created') {
    loadCreatedTeams();
  } else {
    loadJoinedTeams();
  }
});
</script>

<style scoped>
.my-teams-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  background-image: linear-gradient(to bottom, #f0f2f5, #ffffff);
}

.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
  position: relative; /* Add relative positioning for absolute child */
}

.page-title {
  font-size: 28px;
  margin-bottom: 8px;
  color: #303133;
  font-weight: 600;
}

.page-subtitle {
  color: #909399;
  font-size: 14px;
}

.back-button {
  position: absolute;
  top: 50%;
  right: 20px; /* Add some right padding */
  transform: translateY(-50%);
}

.teams-container {
  display: flex;
  gap: 25px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.teams-tabs {
  width: 320px;
  border-right: 1px solid #e4e7ed;
  padding: 20px 0;
  background-color: #fafafa;
}

.team-details {
  flex: 1;
  padding: 25px;
  background-color: #ffffff;
}

.team-list {
  max-height: 600px;
  overflow-y: auto;
  padding: 0 10px;
}

.team-item {
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.team-item-content {
  padding: 15px;
  display: flex;
  align-items: center;
}

.team-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.team-avatar.large {
  width: 60px;
  height: 60px;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

.team-info-container {
  flex: 1;
}

.team-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.team-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.2);
}

.team-name {
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.team-space {
  font-size: 12px;
  color: #909399;
}

.team-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.team-members-count {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.team-actions {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.team-title-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.team-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 5px;
}

.team-created-time {
  font-size: 12px;
  color: #909399;
}

.team-header {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.team-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.team-info-cards {
  margin-bottom: 25px;
}

.info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.info-content p {
  margin: 10px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-content .el-icon {
  color: #409eff;
}

.team-members {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.team-members h3 {
  margin-bottom: 15px;
  font-size: 18px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-state,
.empty-state,
.no-team-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  flex-direction: column;
  color: #909399;
  background-color: rgba(250, 250, 250, 0.5);
  border-radius: 8px;
  padding: 20px;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.03);
}

.empty-state .el-empty,
.no-team-selected .el-empty {
  margin-bottom: 15px;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .teams-container {
    flex-direction: column;
  }
  
  .teams-tabs {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .team-details {
    padding: 15px;
  }
  
  .page-content {
    padding: 15px;
  }
  
  .team-title-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .team-meta {
    justify-content: center;
    margin-top: 10px;
  }
  
  .team-avatar.large {
    margin-bottom: 10px;
  }
  
  .info-card {
    margin-bottom: 15px;
  }
  
  .team-members {
    padding: 15px 10px;
  }
}

@media screen and (max-width: 480px) {
  .team-item-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .team-avatar {
    margin-bottom: 10px;
  }
  
  .team-status {
    flex-direction: row;
    align-items: center;
    width: 100%;
    justify-content: space-between;
    margin-top: 10px;
  }
}

/* 过渡动画 */
.team-item {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.team-detail-content {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.el-table {
  transition: all 0.3s ease;
}

.el-table:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}
</style>