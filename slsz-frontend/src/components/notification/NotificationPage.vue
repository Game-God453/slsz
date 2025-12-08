<template>
  <div class="notification-page">
    <div class="notification-header">
      <div class="back-button" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>返回首页
      </div>
      <div class="header-search">
        <div class="search-item">
          <span class="label">公告标题：</span>
          <el-input v-model="searchTitle" placeholder="请输入" class="input-box"></el-input>
        </div>
        <div class="search-item">
          <span class="label">状态：</span>
          <el-select v-model="statusFilter" placeholder="请选择" class="input-box">
            <el-option label="全部" value=""></el-option>
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="已通过" value="approved"></el-option>
            <el-option label="已拒绝" value="rejected"></el-option>
            <el-option label="未读" value="unread"></el-option>
            <el-option label="已读" value="read"></el-option>
          </el-select>
        </div>
        <div class="search-item">
          <span class="label">发布时间：</span>
          <el-date-picker v-model="publishDate" type="date" placeholder="请选择"></el-date-picker>
        </div>
      </div>
    </div>

    <div class="notification-content">
      <div class="sidebar">
        <div class="category-title">消息分类</div>
        <div class="category-list">
          <div 
            class="category-item" 
            :class="{ active: activeCategory === 'all' }"
            @click="setCategory('all')"
          >
            全部
          </div>
          <div 
            class="category-item" 
            :class="{ active: activeCategory === 'competition' }"
            @click="setCategory('competition')"
          >
            竞赛公告
          </div>
          <div 
            class="category-item" 
            :class="{ active: activeCategory === 'space' }"
            @click="setCategory('space')"
          >
            竞赛空间申请反馈
          </div>
          <div 
            class="category-item" 
            :class="{ active: activeCategory === 'team' }"
            @click="setCategory('team')"
          >
            队伍申请反馈
          </div>
          <div 
            class="category-item" 
            :class="{ active: activeCategory === 'handle_team' }" 
            @click="setCategory('handle_team')"
          >
            处理队伍申请
          </div>
          <div 
            class="category-item" 
            :class="{ active: activeCategory === 'handle_space' }" 
            @click="setCategory('handle_space')"
            v-if="userState.userInfo.role === 'competition_admin'"
          >
            处理竞赛空间申请
          </div>
        </div>
      </div>

      <div class="notification-table">
        <div class="table-title">通知列表</div>
        <el-table :data="filteredNotifications" style="width: 100%" v-loading="isLoading[activeCategory] || isLoading.all">
          <el-table-column label="标题/内容">
            <template #default="scope">
              <div v-if="scope.row.type === 'space_request'">
                您申请加入 <strong>{{ scope.row.space_title }}</strong> 的请求
              </div>
              <div v-else-if="scope.row.type === 'team_request'">
                您申请加入队伍 <strong>{{ scope.row.team_title || '未知队伍' }}</strong> 的请求
              </div>
              <div v-else-if="scope.row.type === 'handle_team_request'">
                 用户 <strong>{{ scope.row.user_username || '未知用户' }}</strong> 申请加入队伍 <strong>{{ scope.row.team_title || '未知队伍' }}</strong>
                 <div v-if="scope.row.request_detail" style="font-size: 12px; color: #606266; margin-top: 4px;">
                   申请详情: {{ scope.row.request_detail }}
                 </div>
              </div>
              <div v-else-if="scope.row.type === 'handle_space_request'">
                 用户 <strong>{{ scope.row.realName || '未知用户' }}</strong> 申请加入竞赛空间 <strong>{{ scope.row.space_title || '未知竞赛空间' }}</strong>
                 <div style="font-size: 12px; color: #606266; margin-top: 4px;">
                   学号: {{ scope.row.studentId || '无' }} | 学院: {{ scope.row.collegeName || '无' }}
                 </div>
              </div>
              <div v-else-if="scope.row.type === 'competition'">
                {{ scope.row.title }} (来自: {{ scope.row.competition || '未知竞赛' }})
              </div>
              <div v-else> {{ scope.row.title || '无标题' }} </div>
              <div v-if="scope.row.status === 'rejected' && scope.row.rejection_reason" style="color: #f56c6c; font-size: 12px; margin-top: 4px;">
                拒绝理由: {{ scope.row.rejection_reason }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <span 
                :class="{
                  'status-approved': scope.row.status === 'approved',
                  'status-rejected': scope.row.status === 'rejected',
                  'status-pending': scope.row.status === 'pending',
                  'status-read': scope.row.status === 'read',
                  'status-unread': scope.row.status === 'unread'
                }"
              >
                {{ 
                  scope.row.status === 'approved' ? '已通过' :
                  scope.row.status === 'rejected' ? '已拒绝' :
                  scope.row.status === 'pending' ? '待处理' :
                  scope.row.status === 'read' ? '已读' :
                  scope.row.status === 'unread' ? '未读' :
                  scope.row.status
                }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="180">
             <template #default="scope">
                {{ formatDate(scope.row.requested_at || scope.row.publishTime || scope.row.created_at) }}
             </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="scope">
              
              <el-button type="primary" link @click="markAsRead(scope.row)" v-if="scope.row.status === 'unread'">标记已读</el-button>
              <template v-if="scope.row.type === 'handle_team_request' && scope.row.status === 'pending'">
                <el-button type="success" link @click="handleTeamRequest(scope.row, 'approve')">批准</el-button>
                <el-button type="warning" link @click="handleTeamRequest(scope.row, 'reject')">拒绝</el-button>
                <!-- <el-button type="danger" link @click="deleteNotification(scope.row)">删除</el-button> -->
              </template>
              <template v-if="scope.row.type === 'handle_space_request' && scope.row.status === 'pending'">
                <el-button type="primary" link @click="viewNotification(scope.row)">查看</el-button>
                <el-button type="success" link @click="handleSpaceRequest(scope.row, 'approve')">批准</el-button>
                <el-button type="warning" link @click="handleSpaceRequest(scope.row, 'reject')">拒绝</el-button>
                <!-- <el-button type="danger" link @click="deleteNotification(scope.row)">删除</el-button> -->
              </template>
              <template v-if="scope.row.type === 'competition'">
                <el-button type="primary" link @click="viewNotification(scope.row)">查看</el-button>
              </template>
              
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft } from '@element-plus/icons-vue'; // 导入图标
import * as api from '../../utils/api';
import { userState } from '../../store/user'; // 可能需要用于判断操作权限
// 引入 Element Plus 消息提示
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();

// 筛选条件
const searchTitle = ref('');
const statusFilter = ref(''); // 'approved', 'rejected', 'pending' (或根据 API 返回调整)
const publishDate = ref(''); // 日期筛选可能需要调整，API 返回的是 requested_at
const activeCategory = ref('all'); // 'all', 'competition', 'space', 'team', 'handle_team'

// 存储不同类型的通知
const competitionAnnouncements = ref([]); // 待实现 API
const spaceRequestsFeedback = ref([]);
const teamRequestsFeedback = ref([]);
const receivedTeamRequests = ref([]); // 新增：存储收到的队伍申请
const receivedSpaceRequests = ref([]); // 新增：存储收到的竞赛空间申请
const isLoading = ref({ // 分类加载状态
  competition: false,
  space: false,
  team: false,
  handle_team: false, // 新增加载状态
  handle_space: false, // 新增加载状态
  all: computed(() => isLoading.value.competition || isLoading.value.space || isLoading.value.team || isLoading.value.handle_team || isLoading.value.handle_space) // 计算总加载状态
});

// --- API 调用 --- 
const fetchSpaceRequestFeedback = async () => {
  if (!userState.isLoggedIn) return; // 假设需要登录才能查看
  isLoading.value.space = true;
  try {
    const response = await api.getSpaceRequestFeedback();
    if (response && response.data) {
      // 给每个反馈添加一个唯一的 id，方便表格处理
      spaceRequestsFeedback.value = response.data.map((item, index) => ({
        ...item,
        // 使用 smr_id 作为唯一 ID，如果存在的话，否则使用索引
        id: item.smr_id || `space_${index}`,
        type: 'space_request' // 添加类型标识
      }));
    } else {
      spaceRequestsFeedback.value = [];
    }
  } catch (error) {
    console.error('获取空间申请反馈失败:', error);
    // ElMessage.error('获取空间申请反馈失败: ' + (error.message || '未知错误'));
    spaceRequestsFeedback.value = [];
  } finally {
    isLoading.value.space = false;
  }
};

const fetchTeamRequestsFeedback = async () => {
  if (!userState.isLoggedIn) return;
  isLoading.value.team = true;
  try {
    const response = await api.getTeamRequestFeedback(); // 调用新 API
    if (response && response.data) {
      teamRequestsFeedback.value = response.data.map((item, index) => ({
        ...item,
        // 使用 req_id 作为唯一 ID
        id: item.req_id || `team_${index}`,
        type: 'team_request' // 添加类型标识
      }));
    } else {
      teamRequestsFeedback.value = [];
    }
  } catch (error) {
    console.error('获取队伍申请反馈失败:', error);
    // ElMessage.error('获取队伍申请反馈失败: ' + (error.message || '未知错误'));
    teamRequestsFeedback.value = [];
  } finally {
    isLoading.value.team = false;
  }
};

// 新增：获取收到的队伍申请
const fetchReceivedTeamRequests = async () => {
  if (!userState.isLoggedIn) return; // 假设需要登录
  isLoading.value.handle_team = true;
  try {
    // 调用 listTeamRequests API，可以传入筛选条件，例如只看 pending
    const response = await api.listTeamRequests({ }); // 默认获取待处理的
    if (response && response.data) {
      receivedTeamRequests.value = response.data.map((item, index) => ({
        ...item,
        id: item.req_id || `handle_team_${index}`,
        type: 'handle_team_request' // 添加类型标识
      }));
    } else {
      receivedTeamRequests.value = [];
    }
  } catch (error) {
    console.error('获取收到的队伍申请失败:', error);
    // ElMessage.error('获取收到的队伍申请失败: ' + (error.message || '未知错误'));
    receivedTeamRequests.value = [];
  } finally {
    isLoading.value.handle_team = false;
  }
};

// 新增：获取收到的竞赛空间申请
const fetchReceivedSpaceRequests = async () => {
  if (!userState.isLoggedIn || userState.userInfo.role !== 'competition_admin') return; // 只有竞赛负责人可以查看
  isLoading.value.handle_space = true;
  try {
    // 调用 listSpaceRequests API，可以传入筛选条件
    const response = await api.listSpaceRequests({ }); // 默认获取所有的
    if (response && response.data) {
      receivedSpaceRequests.value = response.data.map((item, index) => ({
        ...item,
        id: item.req_id || `handle_space_${index}`,
        type: 'handle_space_request' // 添加类型标识
      }));
    } else {
      receivedSpaceRequests.value = [];
    }
  } catch (error) {
    console.error('获取收到的竞赛空间申请失败:', error);
    receivedSpaceRequests.value = [];
  } finally {
    isLoading.value.handle_space = false;
  }
};

// 获取未读竞赛公告
const fetchCompetitionAnnouncements = async () => {
  if (!userState.isLoggedIn) return;
  isLoading.value.competition = true;
  try {
    const response = await api.getUnreadAnnouncements();
    if (response && response.data && response.data.length > 0) {
      // 处理未读公告数据，将每个空间的未读公告转换为通知项
      const announcements = [];
      
      response.data.forEach(spaceData => {
        // 为每个未读公告ID创建一个通知项
        if (spaceData.unread_announcement_ids && spaceData.unread_announcement_ids.length > 0) {
          spaceData.unread_announcement_ids.forEach((announcementId) => {
            announcements.push({
              id: announcementId,
              title: `来自 ${spaceData.space_title} 的未读公告`,
              competition: spaceData.space_title,
              space_id: spaceData.space_id,
              status: 'unread',
              type: 'competition',
              created_at: new Date().toISOString() // 由于API没有返回时间，使用当前时间
            });
          });
        }
      });
      
      competitionAnnouncements.value = announcements;
    } else {
      competitionAnnouncements.value = [];
    }
  } catch (error) {
    console.error('获取未读公告失败:', error);
    competitionAnnouncements.value = [];
  } finally {
    isLoading.value.competition = false;
  }
};

// --- 计算属性：合并和筛选通知 --- 
const allNotifications = computed(() => {
  // 合并所有类型的通知
  return [
    ...competitionAnnouncements.value, 
    ...spaceRequestsFeedback.value, 
    ...teamRequestsFeedback.value,
    ...receivedTeamRequests.value, // 合并新数据
    ...receivedSpaceRequests.value // 合并竞赛空间申请数据
  ];
});

const filteredNotifications = computed(() => {
  let sourceData = [];
  // 1. 根据分类选择数据源
  switch (activeCategory.value) {
    case 'space': // 注意：之前 category-item 的 key 是 'space'
      sourceData = spaceRequestsFeedback.value;
      break;
    case 'team': // 注意：之前 category-item 的 key 是 'team'
      sourceData = teamRequestsFeedback.value;
      break;
    case 'handle_team': // 新增 case
      sourceData = receivedTeamRequests.value;
      break;
    case 'handle_space': // 新增 case
      sourceData = receivedSpaceRequests.value;
      break;
    case 'competition':
      sourceData = competitionAnnouncements.value;
      break;
    default: // 'all'
      sourceData = allNotifications.value;
  }

  // 2. 应用通用筛选
  let filtered = [...sourceData];

  // 根据标题筛选 (需要确定标题字段)
  if (searchTitle.value) {
    const searchTerm = searchTitle.value.toLowerCase();
    filtered = filtered.filter(item => {
      let title = '';
      if (item.type === 'space_request') {
        title = item.space_title;
      } else if (item.type === 'team_request') {
        title = item.team_title;
      } else if (item.type === 'handle_team_request') {
        // 搜索申请人用户名或队伍名
        title = `${item.user_username || ''} ${item.team_title || ''}`;
      } else if (item.type === 'competition') {
        title = item.title;
      } else {
        title = item.title; // 默认或未知类型
      }
      return title?.toLowerCase().includes(searchTerm);
    });
  }

  // 根据状态筛选
  if (statusFilter.value) {
     // 状态字段和值可能需要根据不同类型调整
     // API 返回的状态值是 'approved', 'rejected', 'pending' 等
     // 下拉框的 value 也是这些值，可以直接比较
     filtered = filtered.filter(item => item.status === statusFilter.value);
  }

  // 根据日期筛选 (使用 requested_at 或 publishTime)
  if (publishDate.value) {
    try {
      const selectedDateStr = new Date(publishDate.value).toLocaleDateString();
      filtered = filtered.filter(item => {
        // 尝试使用 requested_at 或 publishTime 或 created_at
        const itemDateStr = item.requested_at || item.publishTime || item.created_at;
        if (!itemDateStr) return false;
        return new Date(itemDateStr).toLocaleDateString() === selectedDateStr;
      });
    } catch (e) {
       console.error('日期筛选错误:', e);
    }
  }

  return filtered;
});

// --- 方法 --- 
const goBack = () => {
  router.push('/');
};

const setCategory = (category) => {
  activeCategory.value = category;
  // 重置筛选条件可能更好
  searchTitle.value = '';
  statusFilter.value = '';
  publishDate.value = '';
  
  // 如果是查看"处理队伍申请"，默认筛选 pending
  if (category === 'handle_team') {
      statusFilter.value = 'pending';
      // 如果 fetchReceivedTeamRequests 已经筛选了 pending，这里可能重复
      // 或者调整 fetchReceivedTeamRequests 不预先筛选，让前端筛选
  } else {
      statusFilter.value = '';
  }
  
  // 如果数据未加载，则加载
  if (category === 'handle_team' && receivedTeamRequests.value.length === 0 && !isLoading.value.handle_team) {
      fetchReceivedTeamRequests();
  }
  // 如果是竞赛空间申请且数据未加载，则加载
  if (category === 'handle_space' && receivedSpaceRequests.value.length === 0 && !isLoading.value.handle_space) {
      fetchReceivedSpaceRequests();
  }
  // ... 其他类型的按需加载逻辑 ...
};

// 处理通知查看、标记已读和删除的方法
const viewNotification = async (row) => {
  console.log('查看通知:', row);
  
  // 如果是竞赛公告类型且状态为未读，自动标记为已读
  if (row.type === 'competition' && row.status === 'unread') {
    await markAsRead(row);
  }
  
  // 如果是竞赛公告，获取详细内容
  if (row.type === 'competition') {
    try {
      const response = await api.getAnnouncementById(row.id);
      if (response && response.data) {
        // 可以使用Element Plus的对话框显示公告详情
        ElMessageBox.alert(
          response.data.announcement_content,
          response.data.announcement_title,
          {
            confirmButtonText: '关闭',
            dangerouslyUseHTMLString: false
          }
        );
      }
    } catch (error) {
      console.error('获取公告详情失败:', error);
      ElMessage.error('获取公告详情失败');
    }
  }
  // 其他类型的通知处理逻辑...
};

const markAsRead = async (row) => {
  if (row.type === 'competition' && row.status === 'unread') {
    try {
      await api.markAnnouncementAsRead(row.id);
      // 更新本地状态
      row.status = 'read';
      ElMessage.success('已标记为已读');
      
      // 刷新公告列表
      fetchCompetitionAnnouncements();
    } catch (error) {
      console.error('标记公告已读失败:', error);
      ElMessage.error('标记已读失败');
    }
  }
  // 其他类型的通知标记已读逻辑...
};

// const deleteNotification = (row) => {
//   console.log('删除通知:', row);
//   // 目前API中没有删除通知的接口，可以在前端临时移除
//   if (row.type === 'competition') {
//     competitionAnnouncements.value = competitionAnnouncements.value.filter(item => item.id !== row.id);
//   }
//   // 其他类型的通知删除逻辑...
// };

// 处理队伍申请的方法
const handleTeamRequest = async (row, action) => {
  console.log(`处理队伍申请: ID=${row.req_id}, Action=${action}`);
  try {
    let rejectionReason = '';
    if (action === 'reject') {
      // 可以添加弹窗让用户输入拒绝理由
      rejectionReason = window.prompt('请输入拒绝理由（可选）：');
    }
    
    await api.handleTeamRequest(row.req_id, action, rejectionReason);
    // 成功后刷新数据
    fetchReceivedTeamRequests();
    alert(action === 'approve' ? '已批准申请' : '已拒绝申请');
  } catch (error) {
    console.error('处理队伍申请失败:', error);
    alert('处理失败: ' + (error.message || '未知错误'));
  }
};

// 处理竞赛空间申请的方法
const handleSpaceRequest = async (row, action) => {
  console.log(`处理竞赛空间申请: ID=${row.req_id}, Action=${action}`);
  try {
    let rejectionReason = '';
    if (action === 'reject') {
      // 可以添加弹窗让用户输入拒绝理由
      rejectionReason = window.prompt('请输入拒绝理由（可选）：');
    }
    
    await api.handleSpaceRequest(row.req_id, action, rejectionReason);
    // 成功后刷新数据
    fetchReceivedSpaceRequests();
    alert(action === 'approve' ? '已批准申请' : '已拒绝申请');
  } catch (error) {
    console.error('处理竞赛空间申请失败:', error);
    alert('处理失败: ' + (error.message || '未知错误'));
  }
};

// 日期格式化函数
const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
      const date = new Date(dateString);
      return date.toLocaleString(); // 使用更详细的格式
  } catch (e) {
      return '日期无效';
  }
};

// --- 生命周期钩子 --- 
onMounted(() => {
  fetchSpaceRequestFeedback();
  fetchTeamRequestsFeedback(); // 调用获取队伍申请反馈的函数
  fetchCompetitionAnnouncements(); // 调用获取未读公告的函数
  // 如果默认显示 'all' 或者 'handle_team'，则需要加载
  if (activeCategory.value === 'all' || activeCategory.value === 'handle_team') {
    fetchReceivedTeamRequests(); 
  }
  // 如果是竞赛负责人，加载竞赛空间申请
  if (userState.userInfo.role === 'competition_admin' && 
      (activeCategory.value === 'all' || activeCategory.value === 'handle_space')) {
    fetchReceivedSpaceRequests();
  }
});

</script>

<style scoped>
.notification-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.notification-header {
  background-color: #fff;
  padding: 15px 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.back-button {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-bottom: 15px;
  color: #303133;
  font-weight: bold;
}

.back-button .el-icon {
  margin-right: 5px;
}

.header-search {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.search-item {
  display: flex;
  align-items: center;
}

.label {
  margin-right: 10px;
  white-space: nowrap;
}

.input-box {
  width: 200px;
}

.notification-content {
  display: flex;
  gap: 20px;
}

.sidebar {
  width: 200px;
  background-color: #fff;
  border-radius: 4px;
  padding: 15px 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  align-self: flex-start;
}

.category-title {
  font-weight: bold;
  padding: 0 15px 15px;
  border-bottom: 1px solid #e0e0e0;
}

.category-list {
  margin-top: 10px;
}

.category-item {
  padding: 12px 15px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-item:hover {
  background-color: #f5f7fa;
}

.category-item.active {
  background-color: #409eff;
  color: #fff;
}

.notification-table {
  flex: 1;
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.table-title {
  font-weight: bold;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.status-unread {
  color: #f56c6c;
  font-weight: bold;
}

.status-read {
  color: #67c23a;
}

/* 调整状态下拉框选项 */
.el-select-dropdown__item {
  padding: 0 20px;
}

/* 状态样式 */
.status-pending {
  color: #e6a23c; /* Warning */
}
.status-approved {
  color: #67c23a; /* Success */
}
.status-rejected {
  color: #f56c6c; /* Danger */
}
.status-unread {
  color: #f56c6c; /* Danger - 保持和之前一致或调整 */
  font-weight: bold;
}
.status-read {
  color: #909399; /* Info - 或用 Success */
}
</style>