<template>
  <div class="nav-container">
    <div class="nav-menu-custom">
      <div 
        class="nav-item" 
        :class="{ active: activePage === 'home' }"
        @click="goToPage('/')"
      >首页</div>
      <div 
        class="nav-item" 
        :class="{ active: activePage === 'competition' }"
        @click="goToPage('/competition/category')"
      >竞赛分类</div>
      <div 
        class="nav-item" 
        :class="{ active: activePage === 'team' }"
        @click="handleSpaceClick"
      >
        竞赛空间
      </div>
      <!-- <div 
        class="nav-item" 
        :class="{ active: activePage === 'announcement' }"
        @click="goToPage('/announcement')"
      >赛事公告</div> -->
    </div>
  </div>

  <!-- 竞赛空间弹窗 -->
  <el-dialog
    v-model="showSpaceDialog"
    title="我加入的竞赛空间"
    width="600px"
    :close-on-click-modal="true"
    :show-close="true"
  >
    <div class="space-dialog-content">
      <!-- 管理员创建竞赛空间按钮 -->
      <div v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'" class="create-space-section">
        <el-button type="primary" @click="showCreateSpaceForm = true">创建新竞赛空间</el-button>
      </div>
      
      <div v-if="userState.isLoggedIn && userSpaces.length > 0" class="space-list">
        <div 
          v-for="space in userSpaces" 
          :key="space.id" 
          class="space-item" 
          @click="goToSpace(space.id)"
        >
          <div class="space-item-title">{{ space.title }}</div>
          <div class="space-item-desc">{{ space.description }}</div>
          <div class="space-item-meta">
            <el-tag size="small" type="info">{{ getCategoryText(space.category) }}</el-tag>
            <el-tag size="small" type="success">{{ getLevelText(space.level) }}</el-tag>
            <span class="space-date">{{ formatDate(space.start_date) }} - {{ formatDate(space.end_date) }}</span>
          </div>
        </div>
      </div>
      <div v-else-if="!userState.isLoggedIn" class="space-empty">
        请先登录查看竞赛空间
      </div>
      <div v-else class="space-empty">
        暂无加入的竞赛空间
      </div>
    </div>
  </el-dialog>
  
  <!-- 创建竞赛空间表单弹窗 -->
  <el-dialog
    v-model="showCreateSpaceForm"
    title="创建新竞赛空间"
    width="600px"
    :close-on-click-modal="false"
    :show-close="true"
  >
    <el-form :model="createSpaceForm" :rules="createSpaceRules" ref="createSpaceFormRef" label-width="100px">
      <el-form-item label="竞赛名称" prop="title">
        <el-input v-model="createSpaceForm.title" placeholder="请输入竞赛名称"></el-input>
      </el-form-item>
      <el-form-item label="竞赛描述" prop="description">
        <el-input v-model="createSpaceForm.description" type="textarea" :rows="3" placeholder="请输入竞赛描述"></el-input>
      </el-form-item>
      <el-form-item label="竞赛类别" prop="category">
        <el-select v-model="createSpaceForm.category" placeholder="请选择竞赛类别">
          <el-option label="学科竞赛" value="subject"></el-option>
          <el-option label="创新创业" value="innovation"></el-option>
          <el-option label="素质拓展" value="entertainment"></el-option>
          <el-option label="其他" value="others"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="竞赛级别" prop="level">
        <el-select v-model="createSpaceForm.level" placeholder="请选择竞赛级别">
          <el-option label="校级" value="school"></el-option>
          <el-option label="省级" value="province"></el-option>
          <el-option label="国家级" value="national"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker v-model="createSpaceForm.start_date" type="date" placeholder="选择开始日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"></el-date-picker>
      </el-form-item>
      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker v-model="createSpaceForm.end_date" type="date" placeholder="选择结束日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"></el-date-picker>
      </el-form-item>
      <el-form-item label="竞赛海报" prop="poster">
        <el-upload
          class="avatar-uploader"
          action="#"
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          :on-change="handlePosterChange"
          :on-exceed="handleExceed"
          :before-upload="beforePosterUpload"
        >
          <img v-if="posterUrl" :src="posterUrl" class="avatar" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCreateSpaceForm = false">取消</el-button>
      <el-button type="primary" @click="submitCreateSpace" :loading="submitting">创建</el-button>
    </template>
  </el-dialog>
</template>

<script>
import { userState } from '../../store/user';
import * as api from '../../utils/api';
import { Plus } from '@element-plus/icons-vue';

export default {
  name: 'HomeNav',
  components: {
    Plus
  },
  props: {
    activePage: {
      type: String,
      default: 'home'
    }
  },
  data() {
    return {
      showSpaceDialog: false,
      userSpaces: [],
      loading: false,
      showCreateSpaceForm: false,
      submitting: false,
      posterUrl: '',
      posterFile: null,
      createSpaceForm: {
        title: '',
        description: '',
        category: 'subject',
        level: 'school',
        start_date: '',
        end_date: '',
        poster: null
      },
      createSpaceRules: {
        title: [{ required: true, message: '请输入竞赛名称', trigger: 'blur' }],
        description: [{ required: true, message: '请输入竞赛描述', trigger: 'blur' }],
        category: [{ required: true, message: '请选择竞赛类别', trigger: 'change' }],
        level: [{ required: true, message: '请选择竞赛级别', trigger: 'change' }],
        start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
        end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
        poster: [{ required: false, message: '请上传竞赛海报', trigger: 'change' }]
      }
    };
  },
  methods: {
    goToPage(path) {
      this.$router.push(path);
    },
    
    handleSpaceClick() {
      if (!userState.isLoggedIn) {
        this.$message.warning('请先登录');
        return;
      }
      this.showSpaceDialog = true;
      this.loadUserSpaces();
    },
    
    async loadUserSpaces() {
      if (!userState.isLoggedIn || this.loading) return;
      
      try {
        this.loading = true;
        const response = await api.listUserSpaces();
        console.log('用户空间数据:', response);
        if (response && response.data) {
          const spaces = Array.isArray(response.data) ? response.data : [];
          console.log('处理后的空间数据:', spaces);
          this.userSpaces = spaces;
        }
      } catch (error) {
        console.error('获取用户竞赛空间失败:', error);
        this.$message.error('获取竞赛空间列表失败');
      } finally {
        this.loading = false;
      }
    },

    goToSpace(spaceId) {
      this.$router.push(`/competition/space/${spaceId}`);
      this.showSpaceDialog = false;
    },

    getCategoryText(category) {
      const categoryMap = {
        'subject': '学科竞赛',
        'innovation': '创新创业',
        'entertainment': '素质拓展',
        'others': '其他'
      };
      return categoryMap[category] || category;
    },
    
    getLevelText(level) {
      const levelMap = {
        'school': '校级',
        'province': '省级',
        'national': '国家级'
      };
      return levelMap[level] || level;
    },

    formatDate(dateString) {
      if (!dateString) return '未设置';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '日期无效';
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    
    // 海报上传相关方法
    handlePosterChange(file) {
      this.posterFile = file.raw;
      this.posterUrl = URL.createObjectURL(file.raw);
      this.createSpaceForm.poster = file.raw;
    },
    
    handleExceed() {
      this.$message.warning('只能上传一张海报图片');
    },
    
    beforePosterUpload(file) {
      const isImage = file.type.startsWith('image/');
      const isLt2M = file.size / 1024 / 1024 < 2;

      if (!isImage) {
        this.$message.error('上传海报只能是图片格式!');
      }
      if (!isLt2M) {
        this.$message.error('上传海报图片大小不能超过 2MB!');
      }
      return isImage && isLt2M;
    },
    
    // 提交创建竞赛空间
    async submitCreateSpace() {
      this.$refs.createSpaceFormRef.validate(async (valid) => {
        if (valid) {
          try {
            this.submitting = true;
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('title', this.createSpaceForm.title);
            formData.append('description', this.createSpaceForm.description);
            formData.append('category', this.createSpaceForm.category);
            formData.append('level', this.createSpaceForm.level);
            formData.append('start_date', this.createSpaceForm.start_date);
            formData.append('end_date', this.createSpaceForm.end_date);
            
            // 添加海报文件
            if (this.posterFile) {
              formData.append('poster', this.posterFile);
            }
            
            // 调用创建竞赛空间API
            const response = await api.createSpace(formData);
            
            if (response && response.data) {
              this.$message.success('竞赛空间创建成功');
              this.showCreateSpaceForm = false;
              this.resetCreateForm();
              // 刷新竞赛空间列表
              this.loadUserSpaces();
            } else {
              this.$message.error(response.message || '创建失败，请稍后再试');
            }
          } catch (error) {
            console.error('创建竞赛空间失败:', error);
            this.$message.error(error.message || '创建失败，请稍后再试');
          } finally {
            this.submitting = false;
          }
        } else {
          return false;
        }
      });
    },
    
    // 重置创建表单
    resetCreateForm() {
      this.createSpaceForm = {
        title: '',
        description: '',
        category: 'subject',
        level: 'school',
        start_date: '',
        end_date: '',
        poster: null
      };
      this.posterUrl = '';
      this.posterFile = null;
      if (this.$refs.createSpaceFormRef) {
        this.$refs.createSpaceFormRef.resetFields();
      }
    }
  },
  watch: {
    'userState.isLoggedIn': {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.loadUserSpaces();
        } else {
          this.userSpaces = [];
        }
      }
    },
    showCreateSpaceForm(newVal) {
      if (!newVal) {
        this.resetCreateForm();
      }
    }
  },
  setup() {
    return {
      userState
    };
  }
};
</script>

<style scoped>
.nav-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.nav-menu-custom {
  display: flex;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px;
}

.nav-item {
  position: relative;
  padding: 0 30px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  color: #303133;
  border-radius: 4px;
}

.nav-item.active {
  background-color: #4169e1;
  color: white;
}

.nav-item:hover:not(.active) {
  color: #409eff;
  background-color: #f5f7fa;
}

.space-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.space-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.space-item {
  padding: 16px;
  border-radius: 8px;
  background-color: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s;
}

.space-item:hover {
  background-color: #ecf5ff;
  transform: translateY(-2px);
}

.space-item-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.space-item-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.4;
}

.space-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.space-date {
  color: #909399;
  font-size: 13px;
}

.space-empty {
  padding: 32px;
  text-align: center;
  color: #909399;
  font-size: 14px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__header) {
  margin-right: 0;
  padding: 20px;
  border-bottom: 1px solid #dcdfe6;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 500;
}

/* 创建竞赛空间按钮样式 */
.create-space-section {
  margin-bottom: 20px;
  text-align: right;
}

/* 海报上传样式 */
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}
</style>