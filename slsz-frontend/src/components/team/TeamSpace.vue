<template>
  <div class="team-space-page">
    <app-header />
    <div class="page-container">
      <div class="page-header-flex">
        <h2 class="page-title">组队空间</h2>
        <el-button @click="goBackToCompetitionSpace" :icon="ArrowLeft">返回竞赛空间</el-button>
      </div>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-input v-model="filters.teamName" placeholder="队伍名称" clearable class="filter-input" />
        <el-select v-model="filters.status" placeholder="状态" clearable class="filter-select">
          <el-option label="招募中" value="recruiting"></el-option>
          <el-option label="已锁定" value="locked"></el-option>
          <!-- 根据实际需要添加更多状态 -->
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="创建开始日期"
          end-placeholder="创建结束日期"
          class="filter-datepicker"
          value-format="YYYY-MM-DD"
        />
        <el-button type="primary" :icon="Search" @click="applyFilters">搜索</el-button>
        <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        <el-button type="warning" @click="openCreateTeamDialog" class="create-team-btn">创建队伍</el-button>
      </div>

      <!-- 队伍卡片列表 -->
      <div v-if="isLoading" class="loading-state">
        <el-icon class="is-loading" :size="26"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="teams.length > 0" class="team-grid">
        <el-card v-for="team in teams" :key="team.id" class="team-card" shadow="hover">
          <div class="team-card-content">
            <div class="team-info">
              <p><strong>队伍名称：</strong>{{ team.title }}</p>
              <p><strong>队长：</strong>{{ team.created_by }}</p>
              <p><strong>招募开始时间：</strong>{{ formatDate(team.created_at) }}</p>
              <p><strong>目前队伍人数：</strong>{{ team.current_number }}/{{ team.target_number || 'N/A' }}</p>
              <!-- 可以添加招募需求等信息 -->
              <p v-if="team.demand"><strong>需求：</strong>{{ team.demand }}</p>
            </div>
            <div class="team-actions">
              <el-button type="primary" text @click="openTeamDetails(team)" class="details-btn">查看详情</el-button>
              <el-button
                 v-if="canApply(team)"
                 type="danger"
                 @click="openApplyDialog(team)"
                 class="apply-btn"
              >申请</el-button>
               <el-tag v-else-if="isUserInTeam(team)" type="success" size="small">已加入</el-tag>
               <el-tag v-else-if="!team.is_recruiting" type="info" size="small">已停止招募</el-tag>
               <!-- 其他状态，例如已满员、已申请等 -->
            </div>
          </div>
        </el-card>
      </div>
      <div v-else class="empty-state">
        <el-empty description="暂无符合条件的队伍"></el-empty>
      </div>

       <!-- 分页 -->
      <div class="pagination" v-if="!isLoading && teams.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalTeams"
          @current-change="handlePageChange"
          layout="prev, pager, next, jumper"
          background
        />
      </div>

    </div>

    <!-- 创建队伍弹窗 -->
    <el-dialog v-model="createTeamDialogVisible" title="创建队伍" width="500px">
       <el-form :model="newTeamForm" label-width="80px">
         <el-form-item label="队伍名称" required>
           <el-input v-model="newTeamForm.teamName" placeholder="请输入队伍名称"></el-input>
         </el-form-item>
         <el-form-item label="期望人数" required>
           <el-input-number v-model="newTeamForm.targetNumber" :min="1" :max="100" placeholder="请输入期望人数"></el-input-number>
         </el-form-item>
         <el-form-item label="招募需求">
           <el-input
             v-model="newTeamForm.demand"
             type="textarea"
             placeholder="简单介绍一下队伍需求（可选）"
             :rows="3"
           ></el-input>
         </el-form-item>
       </el-form>
       <template #footer>
         <el-button @click="createTeamDialogVisible = false">取消</el-button>
         <el-button type="primary" @click="handleCreateTeam">确认创建</el-button>
       </template>
    </el-dialog>

     <!-- 申请加入队伍弹窗 -->
    <el-dialog v-model="applyDialogVisible" title="申请加入队伍" width="500px">
      <p>队伍名称：<strong>{{ applyingTeam?.title }}</strong></p>
      <el-input
        v-model="applyRequestDetail"
        type="textarea"
        placeholder="请输入申请理由或自我介绍（可选）"
        :rows="4"
        style="margin-top: 15px;"
      ></el-input>
      <template #footer>
        <el-button @click="applyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleApplyToTeam">提交申请</el-button>
      </template>
    </el-dialog>

    <!-- 队伍详情弹窗 (暂未实现) -->
    <!-- <el-dialog v-model="teamDetailsVisible" title="队伍详情"> ... </el-dialog> -->

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Search, Refresh, Loading, ArrowLeft } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import AppHeader from '../layout/AppHeader.vue';
import * as api from '../../utils/api';
import { userState } from '../../store/user'; // 用于判断用户是否已加入某队伍

const route = useRoute();
const router = useRouter();
const spaceId = route.params.spaceId; // 从路由获取竞赛空间ID

const filters = reactive({
  teamName: '',
  status: '', // recruiting, locked
  dateRange: [], // [startDate, endDate]
});

const teams = ref([]);
const isLoading = ref(false);
const currentPage = ref(1);
const pageSize = ref(9); // 每页显示9个卡片 (3x3)
const totalTeams = ref(0);

const createTeamDialogVisible = ref(false);
const newTeamForm = reactive({
  teamName: '',
  demand: '',
  targetNumber: 1
});

const applyDialogVisible = ref(false);
const applyingTeam = ref(null); // 当前申请的队伍信息
const applyRequestDetail = ref('');

// TODO: 完善日期格式化
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// 加载队伍列表
const loadTeams = async () => {
  isLoading.value = true;
  try {
    const apiFilters = {
      teamName: filters.teamName || '',
      // status: filters.status || undefined, // API 示例中没有 status 过滤
      created_at_start: filters.dateRange?.[0] || undefined,
      created_at_end: filters.dateRange?.[1] || undefined,
      // 添加分页参数，需要确认后端是否支持
      // page: currentPage.value,
      // pageSize: pageSize.value
    };
    // 根据 API 文档，listRecruitingTeams 接收 spaceId 和 filters
    console.log('API Filters:', apiFilters);
    const response = await api.listRecruitingTeams(spaceId, apiFilters);
    // **根据新示例调整**
    if (response && response.data) {
      teams.value = response.data; 
      // **返回包没有总数，需要前端分页或后端支持分页**
      // totalTeams.value = response.totalCount || response.data.length; 
      // 暂时基于当前返回的数据长度做客户端分页
      totalTeams.value = response.data.length; 
      // 如果后端确实不支持分页，需要在这里手动实现客户端分页
      // paginateTeams(); // 例如调用一个客户端分页函数
    } else {
       teams.value = [];
       totalTeams.value = 0;
    }
  } catch (error) {
    ElMessage.error('加载队伍列表失败: ' + (error.message || '未知错误'));
    teams.value = [];
    totalTeams.value = 0;
  } finally {
    isLoading.value = false;
  }
};

// 应用筛选
const applyFilters = () => {
  currentPage.value = 1; // 筛选后回到第一页
  loadTeams();
};

// 重置筛选
const resetFilters = () => {
  filters.teamName = '';
  filters.status = '';
  filters.dateRange = [];
  currentPage.value = 1;
  loadTeams();
};

// 处理分页
const handlePageChange = (page) => {
  currentPage.value = page;
  loadTeams(); // 重新加载当前页数据
};

// 打开创建队伍弹窗
const openCreateTeamDialog = () => {
  if (!userState.isLoggedIn) {
    ElMessage.warning('请先登录');
    // 可以考虑弹出登录框
    return;
  }
  newTeamForm.teamName = '';
  newTeamForm.demand = '';
  newTeamForm.targetNumber = 1;
  createTeamDialogVisible.value = true;
};

// 处理创建队伍
const handleCreateTeam = async () => {
  if (!newTeamForm.teamName.trim()) {
    ElMessage.warning('请输入队伍名称');
    return;
  }
  if (!newTeamForm.targetNumber || newTeamForm.targetNumber < 1) {
    ElMessage.warning('请输入有效的期望人数');
    return;
  }
  try {
    await api.createTeam(spaceId, {
      teamName: newTeamForm.teamName,
      demand: newTeamForm.demand,
      targetNumber: newTeamForm.targetNumber
    });
    ElMessage.success('队伍创建成功!');
    createTeamDialogVisible.value = false;
    loadTeams(); // 刷新列表
  } catch (error) {
     ElMessage.error('创建队伍失败: ' + (error.message || '未知错误'));
  }
};

// 打开申请加入弹窗
const openApplyDialog = (team) => {
   if (!userState.isLoggedIn) {
    ElMessage.warning('请先登录');
    return;
  }
  applyingTeam.value = team;
  applyRequestDetail.value = '';
  applyDialogVisible.value = true;
};

// 处理提交申请
const handleApplyToTeam = async () => {
  if (!applyingTeam.value || !applyingTeam.value.id) // 修改 ID 字段
  {
    ElMessage.error('请选择一个队伍');
    return;
  }
  try {
    await api.submitTeamRequest(applyingTeam.value.id, applyRequestDetail.value); // 修改 ID 字段
    ElMessage.success('申请已提交');
    applyDialogVisible.value = false;
    // 可以考虑更新按钮状态为"已申请"
    // 例如，添加一个本地状态来跟踪已申请的队伍
    // appliedTeams.value.add(applyingTeam.value.team_id);
  } catch (error) {
    ElMessage.error('提交申请失败: ' + (error.message || '未知错误'));
  }
};

// 打开队伍详情 (暂未实现)
const openTeamDetails = () => {
  ElMessage.info('查看队伍详情功能暂未开放');
  // router.push({ name: 'TeamDetails', params: { teamId: team.team_id } });
};

// 判断用户是否可以申请某个队伍
// TODO: 需要更完善的逻辑，例如判断是否已满员、是否已申请等
const canApply = (team) => {
  // 根据新示例调整：使用 is_recruiting 判断
  return userState.isLoggedIn && team.is_recruiting && !isUserInTeam(team) /*&& !hasApplied(team)*/ ;
};

// 判断用户是否在某个队伍中
// TODO: 需要获取用户加入的所有队伍信息进行判断
const isUserInTeam = () => {
   // 假设 userState.userInfo 中包含用户加入的队伍 ID 列表
   // return userState.userInfo?.teams?.some(userTeamId => userTeamId === team.id); // 修改 ID 字段
   return false; // 简化：默认未加入
};

// TODO: 判断用户是否已申请该队伍
// const hasApplied = (team) => {
//    return appliedTeams.value.has(team.team_id);
// }
// const appliedTeams = ref(new Set()); // 需要在 setup 中定义

// 新增：返回竞赛空间
const goBackToCompetitionSpace = () => {
  // router.push({ name: 'CompetitionSpace', params: { id: spaceId } }); // 或者直接返回上一页
  router.back();
};

onMounted(() => {
  if (!spaceId) {
    ElMessage.error('无效的竞赛空间ID');
    router.back(); // 返回上一页或首页
    return;
  }
  loadTeams(); // 页面加载时获取数据
});

</script>

<style scoped>
.team-space-page {
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-header-flex {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  color: #303133;
  margin-right: 20px;
  flex-grow: 1;
}

.filter-section {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 15px;
  padding: 15px;
  background-color: #f9fafc;
  border-radius: 6px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-input {
  width: 200px;
}

.filter-select {
  width: 150px;
}

.filter-datepicker {
  width: 240px;
}

.create-team-btn {
  margin-left: auto; /* 将创建按钮推到右侧 */
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.team-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.team-card-content {
  display: flex;
  flex-direction: column;
  height: 100%; /* 让卡片内容撑满 */
}

.team-info {
  flex-grow: 1; /* 信息区域占据更多空间 */
  margin-bottom: 15px;
}

.team-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}

.team-info p strong {
  color: #303133;
  margin-right: 5px;
}

.team-actions {
  margin-top: auto; /* 将按钮推到底部 */
  padding-top: 15px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: flex-end; /* 按钮靠右 */
  align-items: center;
  gap: 10px;
}

.details-btn {
  margin-right: auto; /* 查看详情靠左 */
  padding: 0; /* 移除文字按钮的默认内边距 */
  height: auto;
}

.loading-state,
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: #909399;
  gap: 8px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

/* 弹窗样式 */
:deep(.el-dialog__body) {
  padding-bottom: 10px; /* 减少底部内边距 */
}

</style>