<template>
  <div class="announcement-list">
    <div class="filter-container">
      <div class="filter-item">
        <el-input
          v-model="searchTitle"
          placeholder="请输入"
          prefix-icon="el-icon-search"
          style="width: 200px"
          clearable
        />
      </div>
      <div class="filter-item">
        <el-select v-model="publishStatus" placeholder="请选择" style="width: 120px" clearable>
          <el-option label="已发布" value="已发布" />
          <el-option label="未发布" value="未发布" />
        </el-select>
      </div>
      <div class="filter-item">
        <el-select v-model="publisher" placeholder="请选择" style="width: 120px" clearable>
          <el-option label="张三江" value="张三江" />
          <el-option label="其他发布人" value="其他发布人" />
        </el-select>
      </div>
    </div>

    <el-table :data="filteredAnnouncements" style="width: 100%" border stripe>
      <el-table-column prop="id" label="序号" width="60" />
      <el-table-column prop="title" label="公告标题" min-width="150" />
      <el-table-column prop="publisher" label="发布人" width="100" />
      <el-table-column prop="scope" label="发布范围" width="120" />
      <el-table-column prop="type" label="发布类型" width="100" />
      <el-table-column prop="isPush" label="是否APP推送" width="120">
        <template #default="scope">
          <span>{{ scope.row.isPush ? '是' : '否' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="发布状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '已发布' ? 'success' : 'info'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="read" label="已读" width="80" />
      <el-table-column prop="unread" label="未读" width="80" />
      <el-table-column prop="publishTime" label="发布时间" width="160" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button type="text" size="small" @click="viewAnnouncement(scope.row)">查看</el-button>
          <el-button 
            v-if="scope.row.status === '未发布'"
            type="text" 
            size="small" 
            @click="editAnnouncement(scope.row)"
          >编辑</el-button>
          <el-button type="text" size="small" @click="deleteAnnouncement(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'AnnouncementList',
  data() {
    return {
      searchTitle: '',
      publishStatus: '',
      publisher: '',
      announcements: [
        {
          id: 1,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '全部用户',
          type: '定时发布',
          isPush: false,
          status: '未发布',
          read: 0,
          unread: 310,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 2,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '全部用户',
          type: '定时发布',
          isPush: false,
          status: '未发布',
          read: 0,
          unread: 310,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 3,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '全部用户',
          type: '定时发布',
          isPush: false,
          status: '未发布',
          read: 0,
          unread: 310,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 4,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '全部用户',
          type: '定时发布',
          isPush: false,
          status: '未发布',
          read: 0,
          unread: 310,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 5,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '全部用户',
          type: '定时发布',
          isPush: false,
          status: '未发布',
          read: 0,
          unread: 310,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 6,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '办公室成员',
          type: '即时发布',
          isPush: true,
          status: '已发布',
          read: 70,
          unread: 30,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 7,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '办公室成员',
          type: '即时发布',
          isPush: true,
          status: '已发布',
          read: 70,
          unread: 30,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 8,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '办公室成员',
          type: '即时发布',
          isPush: true,
          status: '已发布',
          read: 70,
          unread: 30,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 9,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '办公室成员',
          type: '即时发布',
          isPush: true,
          status: '已发布',
          read: 70,
          unread: 30,
          publishTime: '2022-02-02 12:23'
        },
        {
          id: 10,
          title: '公司春季运动会活动',
          publisher: '张三江',
          scope: '办公室成员',
          type: '即时发布',
          isPush: true,
          status: '已发布',
          read: 70,
          unread: 30,
          publishTime: '2022-02-02 12:23'
        }
      ]
    }
  },
  computed: {
    filteredAnnouncements() {
      let result = this.announcements;
      
      if (this.searchTitle) {
        result = result.filter(item => item.title.includes(this.searchTitle));
      }
      
      if (this.publishStatus) {
        result = result.filter(item => item.status === this.publishStatus);
      }
      
      if (this.publisher) {
        result = result.filter(item => item.publisher === this.publisher);
      }
      
      return result;
    }
  },
  methods: {
    viewAnnouncement(row) {
      this.$message.info(`查看公告：${row.title}`);
    },
    editAnnouncement(row) {
      this.$message.info(`编辑公告：${row.title}`);
    },
    deleteAnnouncement() {
      this.$confirm('确认删除该公告?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message.success('删除成功');
      }).catch(() => {
        this.$message.info('已取消删除');
      });
    }
  }
}
</script>

<style scoped>
.announcement-list {
  padding: 15px;
}

.filter-container {
  display: flex;
  margin-bottom: 20px;
}

.filter-item {
  margin-right: 15px;
}
</style>