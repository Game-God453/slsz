<template>
  <div class="competition-category">
    <!-- 添加顶部导航栏 -->
    <app-header
      activePage="competition"
      @search="handleSearch"
      @login-success="handleLoginSuccess"
      @logout-success="handleLogoutSuccess"
    />
    
    <div class="main-content">
      <div class="filter-section">
        <div class="filter-item title-row">
          <h2 class="section-title">竞赛分类</h2>
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        </div>
        <div class="filter-item">
          <span class="label">竞赛名称：</span>
          <el-input v-model="filters.name" placeholder="请输入竞赛名称" class="input-box"></el-input>
        </div>
        <div class="filter-item">
          <span class="label">级别：</span>
          <el-select v-model="filters.level" placeholder="请选择" class="input-box">
            <el-option label="全部" value=""></el-option>
            <el-option label="校级" value="school"></el-option>
            <el-option label="省级" value="province"></el-option>
            <el-option label="国家级" value="national"></el-option>
          </el-select>
        </div>
        <div class="filter-item">
          <span class="label">类型：</span>
          <el-select v-model="filters.category" placeholder="请选择" class="input-box">
            <el-option label="全部" value=""></el-option>
            <el-option label="学科竞赛" value="subject"></el-option>
            <el-option label="创新创业" value="innovation"></el-option>
            <el-option label="素质拓展" value="entertainment"></el-option>
            <el-option label="其他" value="others"></el-option>
          </el-select>
        </div>
        <div class="filter-item">
          <span class="label">日期范围：</span>
          <el-date-picker
            v-model="startDate"
            type="date"
            placeholder="开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-picker"
          ></el-date-picker>
          <el-date-picker
            v-model="endDate"
            type="date"
            placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-picker"
            :disabled="!startDate"
          ></el-date-picker>
        </div>
        <div class="filter-item">
          <el-button type="primary" @click="searchCompetitions">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>

      <!-- 用户已加入的竞赛空间部分 -->
      <div v-if="userState.isLoggedIn && userJoinedSpaces.length > 0" class="user-joined-spaces">
        <h2 class="section-title">我加入的竞赛空间</h2>
        <div class="competition-grid">
          <div v-for="competition in userJoinedSpaces" :key="competition.id" class="competition-card">
            <div class="competition-card-inner">
              <div class="competition-img">
                <img :src="competition.poster" alt="竞赛海报" />
              </div>
              <div class="competition-details">
                <h3 class="competition-title">{{ competition.title }}</h3>
                <p class="competition-description">{{ competition.description }}</p>
                <div class="competition-meta">
                  <el-tag size="small" type="info">{{ competition.category }}</el-tag>
                  <el-tag size="small" type="success">{{ competition.level }}</el-tag>
                </div>
                <div class="competition-time">
                  {{ formatDate(competition.start_date) }} - {{ formatDate(competition.end_date) }}
                </div>
                <div class="competition-actions">
                  <el-button size="small" type="primary" @click="viewDetail(competition)">
                    查看详情
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 竞赛列表部分 -->
      <div class="competition-grid">
        <el-row :gutter="20">
          <el-col :span="8" v-for="(competition, index) in competitions" :key="index" class="grid-item">
            <el-card class="competition-card">
              <div class="card-content">
                <div class="card-image">
                  <img :src="competition.poster || require('../../assets/laptop-icon.svg')" alt="竞赛海报" />
                </div>
                <div class="card-info">
                  <h3 class="competition-title">{{ competition.title }}</h3>
                  <div class="competition-details">
                    <p>
                      <span class="label">开始时间：</span>
                      <span>{{ formatDate(competition.start_date) }}</span>
                    </p>
                    <p>
                      <span class="label">结束时间：</span>
                      <span>{{ formatDate(competition.end_date) }}</span>
                    </p>
                    <p>
                      <span class="label">级别：</span>
                      <span>{{ getLevelText(competition.level) }}</span>
                    </p>
                  </div>
                  <div class="card-actions">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="submitApplication(competition.id)"
                      :disabled="!userState.isLoggedIn"
                    >
                      {{ userState.isLoggedIn ? '申请加入' : '请先登录' }}
                    </el-button>
                    <el-button 
                      type="info" 
                      size="small" 
                      @click="viewCompetitionDetail(competition)"
                    >
                      查看详情
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="totalCompetitions"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </div>

    <!-- 申请加入对话框 -->
    <el-dialog
      v-model="dialogFormVisible"
      title="申请加入竞赛"
      width="500px"
    >
      <el-form :model="applicationForm" :rules="applicationRules" ref="applicationFormRef" label-width="100px">
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="applicationForm.real_name" placeholder="请输入真实姓名"></el-input>
        </el-form-item>
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="applicationForm.student_id" placeholder="请输入学号"></el-input>
        </el-form-item>
        <el-form-item label="学院" prop="college_name">
          <el-input v-model="applicationForm.college_name" placeholder="请输入学院名称"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogFormVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmApplication" :loading="submitting">提交申请</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 竞赛详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="竞赛详情"
      width="600px"
    >
      <div class="competition-detail" v-if="selectedCompetition">
        <div class="detail-header">
          <div class="detail-image">
            <img :src="selectedCompetition.poster || require('../../assets/laptop-icon.svg')" alt="竞赛海报" />
          </div>
          <div class="detail-info">
            <h2 class="detail-title">{{ selectedCompetition.title }}</h2>
            <div class="detail-meta">
              <p><span class="label">级别：</span>{{ getLevelText(selectedCompetition.level) }}</p>
              <p><span class="label">类型：</span>{{ getCategoryText(selectedCompetition.category) }}</p>
              <p><span class="label">开始时间：</span>{{ formatDate(selectedCompetition.start_date) }}</p>
              <p><span class="label">结束时间：</span>{{ formatDate(selectedCompetition.end_date) }}</p>
              <p><span class="label">状态：</span>{{ selectedCompetition.is_active ? '进行中' : '已结束' }}</p>
            </div>
          </div>
        </div>
        <div class="detail-description">
          <h3>竞赛描述</h3>
          <p>{{ selectedCompetition.description }}</p>
        </div>
        <div class="detail-actions">
          <el-button 
            type="primary" 
            @click="submitApplication(selectedCompetition.id)"
            :disabled="!userState.isLoggedIn"
          >
            {{ userState.isLoggedIn ? '申请加入' : '请先登录' }}
          </el-button>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import * as api from '../../utils/api';
import { userState } from '../../store/user';
import AppHeader from "../layout/AppHeader.vue";

export default {
  name: "CompetitionCategory",
  components: {
    AppHeader
  },
  data() {
    return {
      searchText: "",
      totalCompetitions: 0,
      pageSize: 9,
      currentPage: 1,
      competitions: [],
      userJoinedSpaces: [],
      filters: {
        name: "",
        level: "",
        category: "",
        is_active: true
      },
      startDate: null,
      endDate: null,
      dialogFormVisible: false,
      submitting: false,
      selectedCompetitionId: null,
      applicationForm: {
        real_name: "",
        student_id: "",
        college_name: ""
      },
      applicationRules: {
        real_name: [
          { required: true, message: '请输入真实姓名', trigger: 'blur' }
        ],
        student_id: [
          { required: true, message: '请输入学号', trigger: 'blur' }
        ],
        college_name: [
          { required: true, message: '请输入学院名称', trigger: 'blur' }
        ]
      },
      detailDialogVisible: false,
      selectedCompetition: null,
      loading: false,
    };
  },
  computed: {
    userState() {
      return userState;
    }
  },
  mounted() {
    this.loadCompetitions();
    if (userState.isLoggedIn) {
      this.loadUserSpaces();
    }
  },
  watch: {
    // 监听用户登录状态变化
    'userState.isLoggedIn': function(newVal) {
      if (newVal) {
        // 用户登录状态变为已登录，加载用户已加入的竞赛空间
        this.loadUserSpaces();
      } else {
        // 用户登出，清空用户已加入的竞赛空间
        this.userJoinedSpaces = [];
      }
    },
    '$route.query.search'(newVal) {
      this.filters.name = newVal || ''
    }
  },
  created() {
    // 初始化时设置值
    this.filters.name = this.$route.query.search || ''
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '未设置';
      // 处理ISO格式的日期字符串（包含时间部分）
      const date = new Date(dateString);
      // 检查日期是否有效
      if (isNaN(date.getTime())) return '日期无效';
      // 返回格式化的日期 (YYYY-MM-DD)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    
    getLevelText(level) {
      const levelMap = {
        'school': '校级',
        'province': '省级',
        'national': '国家级'
      };
      return levelMap[level] || '未知';
    },
    
    getCategoryText(category) {
      const categoryMap = {
        'subject': '学科竞赛',
        'innovation': '创新创业',
        'entertainment': '素质拓展',
        'others': '其他'
      };
      return categoryMap[category] || '未知';
    },
    
    async loadCompetitions() {
      try {
        // 准备参数
        const params = { ...this.filters };
        
        // 处理竞赛名称搜索
        if (this.searchText) {
          params.name = this.searchText;
        }
        
        // 处理日期范围
        if (this.startDate) {
          params.date_start = this.startDate;
          if (this.endDate) {
            params.date_end = this.endDate;
          }
        }
        
        // 调用API获取竞赛列表
        const response = await api.listSpaces(params);
        
        // API返回格式: { data: [...], message: "成功获取竞赛空间列表" }
        if (response && response.data && Array.isArray(response.data)) {
          this.competitions = response.data.map(item => ({
            id: item.id,
            title: item.title,
            description: item.description,
            category: item.category,
            level: item.level,
            start_date: item.start_date,
            end_date: item.end_date,
            poster: item.poster_url || require("../../assets/laptop-icon.svg"),
            is_active: item.is_active
          }));
          this.totalCompetitions = this.competitions.length;
        } else {
          // 如果API调用失败或数据为空，使用模拟数据（用于开发测试）
          this.competitions = this.getMockCompetitions();
          this.totalCompetitions = this.competitions.length;
          console.warn('使用模拟数据', response?.message);
        }
      } catch (error) {
        console.error("加载竞赛列表失败:", error);
        this.$message.error("加载竞赛列表失败，使用模拟数据");
        // 使用模拟数据作为备用
        this.competitions = this.getMockCompetitions();
        this.totalCompetitions = this.competitions.length;
      }
    },
    
    searchCompetitions() {
      this.currentPage = 1;
      this.loadCompetitions();
    },
    
    resetFilters() {
      this.filters = {
        name: "",
        level: "",
        category: "",
        is_active: true
      };
      this.dateRange = null;
      this.searchText = "";
      this.loadCompetitions();
    },
    
    handlePageChange(page) {
      this.currentPage = page;
      this.loadCompetitions();
    },
    
    submitApplication(competitionId) {
      if (!userState.isLoggedIn) {
        this.$message.error("请先登录才能参加竞赛！");
        return;
      }

      // 弹出对话框收集用户报名信息
      this.selectedCompetitionId = competitionId;
      this.dialogFormVisible = true;
    },

    async confirmApplication() {
      this.submitting = true;
      try {
        // 验证表单
        if (!this.applicationForm.real_name || !this.applicationForm.student_id || !this.applicationForm.college_name) {
          this.$message.error("请填写所有必填项！");
          this.submitting = false;
          return;
        }

        // 准备申请数据
        const requestData = {
          space_id: this.selectedCompetitionId,
          real_name: this.applicationForm.real_name,
          student_id: this.applicationForm.student_id,
          college_name: this.applicationForm.college_name
        };

        // 调用API提交申请
        const response = await api.submitSpaceRequest(requestData);
        
        // 检查API响应 { message: "申请提交成功" }
        if (response && (response.message || response.data)) {
          this.$message.success(response.message || "申请已提交成功，请等待审核！");
          this.dialogFormVisible = false;
          // 重置表单
          this.applicationForm = {
            real_name: '',
            student_id: '',
            college_name: ''
          };
          
          // 获取申请反馈（如果有）
          this.checkApplicationFeedback();
        } else {
          this.$message.error(response?.message || "提交申请失败，请稍后重试");
        }
      } catch (error) {
        console.error("提交申请失败:", error);
        this.$message.error("提交申请失败，请稍后重试");
      } finally {
        this.submitting = false;
      }
    },

    async checkApplicationFeedback() {
      try {
        const response = await api.getSpaceRequestFeedback();
        if (response && response.data && Array.isArray(response.data)) {
          // 处理反馈信息
          const pendingApplications = response.data.filter(item => item.status === 'pending');
          if (pendingApplications.length > 0) {
            this.$message.info(`您有${pendingApplications.length}个竞赛申请正在审核中`);
          }
          
          const approvedApplications = response.data.filter(item => item.status === 'approved');
          if (approvedApplications.length > 0) {
            this.$message.success(`您有${approvedApplications.length}个竞赛申请已被批准`);
          }
          
          const rejectedApplications = response.data.filter(item => item.status === 'rejected');
          if (rejectedApplications.length > 0) {
            this.$message.warning(`您有${rejectedApplications.length}个竞赛申请被拒绝`);
          }
        }
      } catch (error) {
        console.error("获取申请反馈失败:", error);
      }
    },
    
    viewCompetitionDetail(competition) {
      this.selectedCompetition = competition;
      this.detailDialogVisible = true;
    },
    
    goBack() {
      this.$router.go(-1);
    },
    
    handleAvatarClick() {
      if (!userState.isLoggedIn) {
        this.$message.warning("请先登录");
      }
    },
    
    async handleLogout() {
      try {
        await userState.logout();
        this.$message.success("退出登录成功");
        this.showUserProfile = false;
      } catch (error) {
        console.error("退出登录失败", error);
        this.$message.error("退出登录失败");
      }
    },
    
    // 模拟数据
    getMockCompetitions() {
      return [
        {
          id: "comp1",
          title: "全国大学生计算机设计大赛",
          description: "计算机设计大赛是展示学生计算机应用能力和创新思维的重要平台。",
          category: "subject",
          level: "national",
          start_date: "2025-04-18T00:00:00",
          end_date: "2025-05-18T00:00:00",
          poster_url: null,
          is_active: true
        },
        {
          id: "comp2",
          title: "机械创新设计大赛",
          description: "机械创新设计大赛是展示机械设计创新和实践能力的重要赛事。",
          category: "innovation",
          level: "province",
          start_date: "2023-09-01T00:00:00",
          end_date: "2023-10-31T00:00:00",
          poster_url: null,
          is_active: true
        },
        {
          id: "comp3",
          title: "电子设计大赛",
          description: "电子设计大赛是电子设计领域的重要赛事，展示电子设计创新和实践能力。",
          category: "subject",
          level: "national",
          start_date: "2023-11-01T00:00:00",
          end_date: "2023-12-15T00:00:00",
          poster_url: null,
          is_active: true
        }
      ];
    },

    handleSearch(text) {
      this.searchText = text;
      this.searchCompetitions();
    },
    
    handleLoginSuccess() {
      // 登录成功后的处理
      this.$message.success('登录成功');
      // 登录成功后加载用户已加入的竞赛空间
      this.loadUserSpaces();
    },
    
    handleLogoutSuccess() {
      // 登出成功后的处理
      this.$message.success('退出登录成功');
      // 登出后清空用户已加入的竞赛空间
      this.userJoinedSpaces = [];
    },

    async loadUserSpaces() {
      if (!userState.isLoggedIn) return;
      
      try {
        this.loading = true;
        // 调用API获取用户已加入的竞赛空间
        const response = await api.listUserSpaces();
        if (response && response.data && response.data.code === 0) {
          this.userJoinedSpaces = response.data.data || [];
        }
      } catch (error) {
        console.error('获取用户已加入的竞赛空间失败:', error);
        this.$message.error('获取用户已加入的竞赛空间失败');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.competition-category {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  padding-top: 20px;
}

.filter-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

.filter-item:first-child {
  display: flex;
  align-items: center;
  width: 100%;
  justify-content: space-between;
}

.filter-item:first-child::before {
  content: none;
}

.filter-item:last-child {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

.filter-item {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.label {
  margin-right: 10px;
  white-space: nowrap;
  color: #606266;
}

.input-box {
  width: 180px;
}

.date-picker {
  width: 350px;
}

.competition-grid {
  margin-bottom: 30px;
}

.grid-item {
  margin-bottom: 20px;
}

.competition-card {
  height: 100%;
  transition: all 0.3s;
}

.competition-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  flex-direction: column;
}

.card-image {
  height: 160px;
  overflow: hidden;
  margin-bottom: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.competition-title {
  font-size: 16px;
  color: #303133;
  margin-top: 0;
  margin-bottom: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.competition-details {
  flex: 1;
  margin-bottom: 15px;
}

.competition-details p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.card-actions {
  display: flex;
  justify-content: space-between;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.filter-item.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 10px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

/* 竞赛详情样式 */
.competition-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  margin-bottom: 20px;
}

.detail-image {
  width: 200px;
  height: 200px;
  overflow: hidden;
  margin-right: 20px;
  border-radius: 4px;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-info {
  flex: 1;
}

.detail-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 15px 0;
}

.detail-meta {
  color: #606266;
}

.detail-meta p {
  margin: 8px 0;
  font-size: 14px;
}

.detail-description {
  margin-bottom: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.detail-description h3 {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 10px 0;
}

.detail-description p {
  color: #606266;
  line-height: 1.5;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

/* 用户已加入的竞赛空间部分 */
.user-joined-spaces {
  margin-bottom: 30px;
}

.competition-card {
  margin-bottom: 20px;
}

.competition-card-inner {
  display: flex;
}

.competition-img {
  width: 200px;
  height: 120px;
  overflow: hidden;
  margin-right: 20px;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.competition-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.competition-details {
  flex: 1;
}

.competition-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-top: 0;
  margin-bottom: 10px;
}

.competition-description {
  color: #606266;
  margin-bottom: 10px;
}

.competition-meta {
  margin-bottom: 10px;
}

.competition-time {
  color: #606266;
}

.competition-actions {
  margin-top: 10px;
}
</style>