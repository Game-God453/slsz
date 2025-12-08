<template>
  <div class="competition-space">
    <!-- 顶部导航栏 -->
    <app-header 
      @search="handleSearch"
      @login-success="handleLoginSuccess"
      @logout-success="handleLogoutSuccess"
    />

    <!-- 页面头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <!-- 左侧竞赛空间标志 -->
        <div class="space-logo">
          <h2>竞赛空间</h2>
        </div>
        <!-- 右侧返回按钮 -->
        <div class="header-actions">
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        </div>
      </div>
    </div>

    <!-- 竞赛信息区域 -->
    <div class="competition-info">
      <div class="competition-banner" v-if="competitionInfo.poster">
        <el-image :src="competitionInfo.poster" fit="cover" class="competition-poster" />
      </div>
      <div class="info-header">
        <div class="info-left">
          <h1 class="competition-title">{{ competitionInfo.title }}</h1>
          <div class="competition-meta">
            <el-tag size="small" type="info">{{ getCategoryText(competitionInfo.category) }}</el-tag>
            <el-tag size="small" type="success">{{ getLevelText(competitionInfo.level) }}</el-tag>
            <span class="competition-date">
              {{ formatDate(competitionInfo.start_date) }} - {{ formatDate(competitionInfo.end_date) }}
            </span>
          </div>
        </div>
        <div class="info-right">
          <el-button type="primary" @click="openCompetitionFilesDialog">竞赛文件</el-button> <!-- Changed click handler -->
          <el-button type="info" @click="openAnnouncementDialog">竞赛公告</el-button>
          <el-button type="success" @click="goToTeamSpace">组队空间</el-button>
          <!-- 根据角色显示不同按钮 -->
          <el-button 
            v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'"
            type="danger"
            @click="openManageSpaceDialog"
          >
            管理竞赛空间
          </el-button>
          <!-- 新增：导出组队信息按钮，仅竞赛负责人可见 -->
          <el-button 
            v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'"
            type="danger"
            @click="handleExportTeamInfo"
          >
            导出组队信息
          </el-button>
          <el-button v-else @click="handleDownload('其他组队空间')">其他竞赛空间</el-button>
          <!-- 新增：更新个人信息按钮 -->
          <el-button v-if="userState.isLoggedIn" type="warning" @click="openUpdateUserInfoDialog">更新个人信息</el-button>
        </div>
      </div>
      <div class="competition-description">
        {{ competitionInfo.description }}
      </div>
    </div>

    <!-- 问答区域 -->
    <div class="discussion-section">
      <div class="discussion-header">
        <h2>问答区</h2>
      </div>

      <div class="discussion-container">
        <!-- 左侧问题列表 -->
        <div class="discussion-list">
          <div v-for="(question, index) in paginatedQuestions" :key="question.question_id || index" class="question-item" :class="{ 'active': selectedQuestion && selectedQuestion.question_id === question.question_id }" @click="selectQuestion(question)">
            <div class="question-user">
              <el-avatar :size="30" :src="question.author_avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="question-info">
                <div class="question-username">{{ question.author_username }}</div>
                <div class="question-time">{{ formatDate(question.created_at) }}</div>
              </div>
            </div>
            <div class="question-summary">{{ truncateText(question.content, 50) }}</div>
            <div class="question-actions">
              <el-button size="small" text type="primary" @click.stop="selectQuestion(question)">查看详情</el-button>
            </div>
          </div>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              @current-change="handlePageChange"
              layout="prev, pager, next"
              background
            />
          </div>
        </div>

        <!-- 右侧内容区 -->
        <div class="discussion-content">
          <!-- 查看问题详情 (非编辑状态) -->
          <div v-if="selectedQuestion && !isEditing" class="question-detail">
            <div class="detail-header">
              <div class="detail-user">
                <el-avatar :size="40" :src="selectedQuestion.author_avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <div class="detail-info">
                  <div class="detail-username">{{ selectedQuestion.author_username }}</div>
                  <div class="detail-time">{{ formatDate(selectedQuestion.created_at) }}</div>
                </div>
              </div>
              <div class="detail-actions">
                <el-button 
                  v-if="userState.isLoggedIn && userState.userInfo.username === selectedQuestion.author_username && !isEditing"
                  type="primary" 
                  size="small"
                  @click.stop="startEditQuestion(selectedQuestion)"
                  text
                  
                >
                  编辑
                </el-button>
                <el-button 
                  v-if="userState.isLoggedIn && userState.userInfo.username === selectedQuestion.author_username"
                  type="danger" 
                  size="small"
                  @click.stop="handleDeleteQuestion(selectedQuestion.question_id)"
                  text
                  
                >
                  删除问题
                </el-button>
                <el-button @click="clearSelectedQuestion">返回列表</el-button>
              </div>
            </div>
            <div class="detail-content">
              <p>{{ selectedQuestion.content }}</p>
            </div>
            <div v-if="selectedQuestion.question_images_urls && selectedQuestion.question_images_urls.length > 0" class="detail-images">
              <h4>相关图片:</h4>
              <el-image 
                v-for="(imgUrl, imgIndex) in selectedQuestion.question_images_urls" 
                :key="imgIndex" 
                :src="imgUrl"
                :preview-src-list="selectedQuestion.question_images_urls"
                :initial-index="imgIndex"
                fit="cover"
                style="width: 100px; height: 100px; margin-right: 10px; margin-bottom: 10px; border-radius: 4px;"
              />
            </div>
            
            <!-- 回复区域 -->
            <div class="replies-section">
              <h4>回复 ({{ selectedQuestion.replies?.length || 0 }})</h4>
              <!-- 回复列表 -->
              <div v-if="selectedQuestion.replies && selectedQuestion.replies.length > 0" class="replies-list">
                <div v-for="(reply, replyIndex) in selectedQuestion.replies" :key="reply.reply_id || replyIndex" class="reply-item">
                  <div class="reply-user">
                    <el-avatar :size="30" :src="reply.from_user_avatar">
                       <el-icon><User /></el-icon>
                    </el-avatar>
                  </div>
                  <div class="reply-content">
                    <div class="reply-meta">
                      <span class="reply-from-user">{{ reply.from_user }}</span>
                      <span class="reply-indicator"> 回复 </span>
                      <span class="reply-to-user">{{ reply.to_user }}</span>
                      <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                      <el-button 
                        v-if="userState.isLoggedIn && userState.userInfo.username === reply.from_user" 
                        type="danger" 
                        size="small" 
                        @click.stop="handleDeleteReply(reply.reply_id)" 
                        text
                        class="delete-reply-btn"
                      >
                        删除
                      </el-button>
                      <el-button 
                        v-if="userState.isLoggedIn" 
                        type="primary" 
                        size="small" 
                        @click.stop="replyToUser(reply.from_user, reply.from_space_user_id)" 
                        text
                        class="reply-btn"
                      >
                        回复
                      </el-button>
                    </div>
                    <p>{{ reply.content }}</p>
                     <!-- 回复图片展示 -->
                    <div v-if="reply.reply_images_urls && reply.reply_images_urls.length > 0" class="reply-images">
                      <el-image 
                        v-for="(imgUrl, imgIndex) in reply.reply_images_urls" 
                        :key="imgIndex" 
                        :src="imgUrl"
                        :preview-src-list="reply.reply_images_urls" 
                        :initial-index="imgIndex"
                        fit="cover"
                        style="width: 80px; height: 80px; margin-right: 8px; margin-top: 8px; border-radius: 4px; cursor: pointer;"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-reply">
                暂无回复，快来抢沙发吧~
              </div>

              <!-- 发表回复 -->
              <div class="reply-form">
                <!-- 回复目标提示 -->
                <div v-if="replyTarget" class="reply-target-info">
                  <span>回复给: <strong>{{ replyTarget.username }}</strong></span>
                  <el-button type="text" @click="clearReplyTarget">取消</el-button>
                </div>
                <el-input
                  v-model="newReply"
                  type="textarea"
                  :rows="3"
                  :placeholder="replyTarget ? `回复 ${replyTarget.username}...` : '发表你的回复...'" 
                  :autosize="{ minRows: 3, maxRows: 5 }"
                />
                 <!-- 回复图片上传 -->
                 <div class="upload-section reply-upload-section">
                   <el-upload
                     v-model:file-list="replyImages"
                     action="#"
                     list-type="picture-card"
                     :auto-upload="false"
                     :on-preview="handleReplyPictureCardPreview"
                     :on-remove="handleReplyRemove"
                     multiple
                   >
                     <el-icon><Plus /></el-icon>
                   </el-upload>
                 </div>
                 <div class="reply-actions">
                    <el-button type="primary" size="small" @click="submitReply">提交回复</el-button>
                 </div>
              </div>
            </div>
          </div>

          <!-- 编辑问题 或 默认提问 -->
          <div v-else>
            <!-- 提问/编辑表单 -->
            <div class="question-form">
              <h3>{{ isEditing ? '编辑问题' : '发表问题' }}</h3>
              <el-input
                v-model="newQuestion"
                type="textarea"
                :rows="4"
                :placeholder="isEditing ? '修改你的问题...' : '有什么想问的...'"
              />
              <!-- 图片上传 -->
              <div class="upload-section">
                <el-upload
                  v-model:file-list="uploadedImages"
                  action="#" 
                  list-type="picture-card"
                  :auto-upload="false"
                  :on-preview="handlePictureCardPreview"
                  :on-remove="handleRemove"
                  multiple
                >
                  <el-icon><Plus /></el-icon>
                </el-upload>
              </div>
              <div class="form-actions">
                <el-button v-if="isEditing" @click="cancelEditQuestion">取消编辑</el-button>
                <el-button type="primary" @click="isEditing ? handleUpdateQuestion() : submitQuestion()">
                  {{ isEditing ? '更新问题' : '提交问题' }}
                </el-button>
              </div>
            </div>

            <!-- 我的问题列表 (仅在非编辑状态下显示) -->
            <div v-if="!isEditing" class="my-questions">
              <h3>我的问题</h3>
              <div v-if="myQuestions.length > 0">
                <div v-for="(question, index) in myQuestions" :key="question.question_id || index" class="my-question-item" @click="selectQuestion(question)">
                  <div class="question-content">{{ truncateText(question.content, 100) }}</div>
                  <div class="question-time">{{ formatDate(question.created_at) }}</div>
                   <div class="question-actions">
                      <el-button size="small" text type="primary">查看详情</el-button>
                   </div>
                </div>
              </div>
              <div v-else class="empty-message">
                暂无提问记录
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <el-dialog v-model="dialogVisible">
      <img w-full :src="dialogImageUrl" alt="Preview Image" />
    </el-dialog>
    
    <!-- 其他竞赛空间弹窗 -->
    <el-dialog
      v-model="otherSpacesDialogVisible"
      title="我加入的其他竞赛空间"
      width="600px"
      :close-on-click-modal="true"
      :show-close="true"
    >
      <div class="space-dialog-content">
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
        <div v-else-if="loadingSpaces" class="space-empty">
          正在加载竞赛空间...
        </div>
        <div v-else class="space-empty">
          暂无加入的其他竞赛空间
        </div>
      </div>
    </el-dialog>

    <!-- 更新个人信息弹窗 -->
    <el-dialog v-model="updateUserInfoDialogVisible" title="更新在本竞赛空间的信息" width="500px">
      <el-form :model="updateUserInfoForm" label-width="80px">
        <el-form-item label="真实姓名">
          <el-input v-model="updateUserInfoForm.real_name" placeholder="请输入真实姓名"></el-input>
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="updateUserInfoForm.student_id" placeholder="请输入学号"></el-input>
        </el-form-item>
        <el-form-item label="学院">
          <el-input v-model="updateUserInfoForm.college_name" placeholder="请输入学院名称"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-input v-model="updateUserInfoForm.gender" placeholder="请输入性别"></el-input>
        </el-form-item>
        <el-form-item label="电话号">
          <el-input v-model="updateUserInfoForm.phone" placeholder="请输入电话号码"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="updateUserInfoForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="updateUserInfoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateSpaceUserInfo">确认更新</el-button>
      </template>
    </el-dialog>

    <!-- 管理竞赛空间弹窗 -->
    <el-dialog v-model="manageSpaceDialogVisible" title="管理竞赛空间" width="700px">
      <el-tabs v-model="activeManageTab">
        <!-- 更新竞赛信息 -->
        <el-tab-pane label="更新竞赛信息" name="update">
          <el-form :model="updateSpaceForm" label-width="100px">
            <el-form-item label="竞赛标题">
              <el-input v-model="updateSpaceForm.title" placeholder="请输入竞赛标题"></el-input>
            </el-form-item>
            <el-form-item label="竞赛描述">
              <el-input v-model="updateSpaceForm.description" type="textarea" :rows="4" placeholder="请输入竞赛描述"></el-input>
            </el-form-item>
            <el-form-item label="竞赛类别">
              <el-select v-model="updateSpaceForm.category" placeholder="请选择竞赛类别">
                <el-option label="学科竞赛" value="subject"></el-option>
                <el-option label="创新创业" value="innovation"></el-option>
                <el-option label="素质拓展" value="entertainment"></el-option>
                <el-option label="其他" value="others"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="竞赛级别">
              <el-select v-model="updateSpaceForm.level" placeholder="请选择竞赛级别">
                <el-option label="校级" value="school"></el-option>
                <el-option label="省级" value="province"></el-option>
                <el-option label="国家级" value="national"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期">
              <el-date-picker v-model="updateSpaceForm.start_date" type="date" placeholder="选择开始日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"></el-date-picker>
            </el-form-item>
            <el-form-item label="结束日期">
              <el-date-picker v-model="updateSpaceForm.end_date" type="date" placeholder="选择结束日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"></el-date-picker>
            </el-form-item>
            <el-form-item label="竞赛海报">
              <el-upload
                action="#"
                list-type="picture-card"
                :auto-upload="false"
                :limit="1"
                v-model:file-list="updateSpaceForm.posterFiles"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </el-form>
          <div class="dialog-footer">
            <el-button @click="manageSpaceDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleUpdateSpace">更新竞赛信息</el-button>
          </div>
        </el-tab-pane>
        
        <!-- 关闭竞赛空间 -->
        <el-tab-pane label="关闭竞赛空间" name="close">
          <div class="close-space-container">
            <el-alert
              title="警告：关闭竞赛空间后将无法恢复"
              type="warning"
              description="关闭后，所有用户将无法访问此竞赛空间，包括所有问答内容和组队信息。"
              show-icon
              :closable="false"
            ></el-alert>
            <div class="confirm-close-space">
              <p>请输入"确认关闭"以确认您的操作：</p>
              <el-input v-model="closeSpaceConfirmText" placeholder="请输入确认关闭"></el-input>
              <el-button 
                type="danger" 
                @click="handleCloseSpace"
                :disabled="closeSpaceConfirmText !== '确认关闭'"
              >关闭竞赛空间</el-button>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 管理成员 -->
        <el-tab-pane label="管理成员" name="members">
          <div class="space-members-container">
            <div v-if="loadingUsers" class="loading-container">
              <el-skeleton :rows="5" animated />
            </div>
            <div v-else>
              <!-- 使用虚拟列表替代普通表格，避免ResizeObserver循环错误 -->
              <div class="member-table-header">
                <div class="member-column" style="width: 120px">姓名</div>
                <div class="member-column" style="width: 120px">学号</div>
                <div class="member-column" style="flex: 1">学院</div>
                <div class="member-column" style="width: 80px">管理员</div>
                <div class="member-column" style="width: 120px">操作</div>
              </div>
              <div class="member-table-body">
                <div v-for="(member, index) in paginatedMembers" :key="index" class="member-row">
                  <div class="member-cell" style="width: 120px">{{ member.realName }}</div>
                  <div class="member-cell" style="width: 120px">{{ member.studentId }}</div>
                  <div class="member-cell" style="flex: 1">{{ member.collegeName }}</div>
                  <div class="member-cell" style="width: 80px">
                    <el-tag v-if="member.is_admin" type="success">是</el-tag>
                    <span v-else>否</span>
                  </div>
                  <div class="member-cell" style="width: 120px">
                    <el-button 
                      v-if="!member.is_admin"
                      type="danger" 
                      size="small" 
                      @click="handleRemoveSpaceMember(member)"
                    >移除</el-button>
                  </div>
                </div>
              </div>
              <div class="pagination">
                <el-pagination
                  v-model:current-page="memberCurrentPage"
                  :page-size="memberPageSize"
                  :total="memberTotal"
                  @current-change="handleMemberPageChange"
                  layout="prev, pager, next"
                  background
                />
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 新增：竞赛文件管理弹窗 -->
    <el-dialog v-model="competitionFilesDialogVisible" title="竞赛文件管理" width="600px">
      <!-- 文件上传区域 (仅管理员可见) -->
      <div v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'" class="competition-file-upload">
        <el-upload
          v-model:file-list="fileListForUpload"
          action="#" 
          :auto-upload="false"
          :limit="1" 
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          style="margin-right: 10px;"
        >
          <el-button type="primary" :icon="UploadFilled">选择文件</el-button>
        </el-upload>
        <el-button type="success" @click="handleUploadFile" :loading="loadingFiles">上传文件</el-button>
      </div>

      <!-- 文件列表区域 -->
      <div class="file-list-section">
        <h4>可用文件列表</h4>
        <div v-if="loadingFiles" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else-if="competitionFiles.length > 0">
          <el-table :data="competitionFiles" style="width: 100%">
                        <el-table-column label="文件名">
              <template #default="scope">
                {{ typeof scope.row.file_name === 'string' ? scope.row.file_name.split('/').pop() : scope.row.file_name }}
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="upload_time" label="上传时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.upload_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button size="small" type="primary" :icon="Download" @click="handleDownloadFile(scope.row)">下载</el-button>
                <el-button 
                  v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'"
                  size="small" 
                  type="danger" 
                  :icon="Delete" 
                  @click="handleDeleteFile(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="empty-message">
          暂无竞赛文件
        </div>
      </div>

      <template #footer>
        <el-button @click="competitionFilesDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 竞赛公告管理对话框 -->
    <el-dialog v-model="announcementDialogVisible" :title="userState.isLoggedIn && userState.userInfo.role === 'competition_admin' ? '竞赛公告管理' : '竞赛公告'" width="600px">
      <!-- 公告列表 -->
      <div class="announcement-list">
        <div v-if="loadingAnnouncements" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else-if="announcements.length > 0">
          <el-table :data="announcements" style="width: 100%">
            <el-table-column prop="announcement_title" label="标题" />
            <el-table-column prop="created_at" label="发布时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewAnnouncement(scope.row)">查看</el-button>
                <el-button 
                  v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'"
                  size="small" 
                  type="warning" 
                  @click="editAnnouncement(scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'"
                  size="small" 
                  type="danger" 
                  @click="confirmDeleteAnnouncement(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="empty-message">
          暂无公告
        </div>
      </div>

      <!-- 管理员可见的创建公告按钮 -->
      <div v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'" class="announcement-actions">
        <el-button type="primary" @click="openCreateAnnouncementForm">创建新公告</el-button>
      </div>

      <!-- 公告详情查看 -->
      <div v-if="selectedAnnouncement && !isEditingAnnouncement" class="announcement-detail">
        <h3>{{ selectedAnnouncement.announcement_title }}</h3>
        <div class="announcement-meta">
          <span>发布时间: {{ formatDate(selectedAnnouncement.created_at) }}</span>
          <span v-if="selectedAnnouncement.updated_at !== selectedAnnouncement.created_at">
            更新时间: {{ formatDate(selectedAnnouncement.updated_at) }}
          </span>
        </div>
        <div class="announcement-content">
          <p>{{ selectedAnnouncement.announcement_content }}</p>
        </div>
        <div class="announcement-actions">
          <el-button @click="selectedAnnouncement = null">返回列表</el-button>
          <el-button 
            v-if="userState.isLoggedIn && userState.userInfo.role === 'competition_admin'"
            type="warning" 
            @click="editAnnouncement(selectedAnnouncement)"
          >
            编辑
          </el-button>
        </div>
      </div>

      <!-- 创建/编辑公告表单 -->
      <div v-if="isEditingAnnouncement" class="announcement-form">
        <h3>{{ editingAnnouncementId ? '编辑公告' : '创建公告' }}</h3>
        <el-form :model="announcementForm" label-width="80px">
          <el-form-item label="标题" required>
            <el-input v-model="announcementForm.title" placeholder="请输入公告标题"></el-input>
          </el-form-item>
          <el-form-item label="内容" required>
            <el-input 
              v-model="announcementForm.content" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入公告内容"
            ></el-input>
          </el-form-item>
        </el-form>
        <div class="form-actions">
          <el-button @click="cancelEditAnnouncement">取消</el-button>
          <el-button type="primary" @click="submitAnnouncement" :loading="submittingAnnouncement">
            {{ editingAnnouncementId ? '更新' : '发布' }}
          </el-button>
        </div>
      </div>

      <template #footer v-if="!selectedAnnouncement && !isEditingAnnouncement">
        <el-button @click="announcementDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script>
import { ref, onMounted, computed, reactive } from 'vue'; // Import reactive and watch
import { useRoute } from 'vue-router';
import { User, Plus } from '@element-plus/icons-vue'; // Import necessary icons
import { ElMessageBox, ElMessage } from 'element-plus';
import { userState } from '../../store/user';
import AppHeader from '../layout/AppHeader.vue';
import * as api from '../../utils/api';

// Helper function to create download link
function createDownloadLink(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export default {
  name: 'CompetitionSpace',
  components: {
    AppHeader,
    User,
    Plus,
    // Download, // Register icons
    // Delete,
    // UploadFilled
  },
  setup() {
    const route = useRoute();
    const spaceId = route.params.id;
    
    const competitionInfo = ref({});
    const allQuestions = ref([]);
    const newQuestion = ref('');
    const currentPage = ref(1);
    const pageSize = ref(10);
    const total = ref(0);
    const selectedQuestion = ref(null);
    const uploadedImages = ref([]);
    const dialogVisible = ref(false);
    const dialogImageUrl = ref('');
    // 新增：回复目标
    //const replyTarget = ref(null); // {username: '用户名', userId: '用户ID'}
    const newReply = ref('');
    const replyImages = ref([]);
    const isEditing = ref(false);

    // 更新个人信息对话框状态
    const updateUserInfoDialogVisible = ref(false);
    const updateUserInfoForm = reactive({
      real_name: '',
      student_id: '',
      college_name: ''
    });
    
    // 管理竞赛空间对话框状态
    const manageSpaceDialogVisible = ref(false);
    const activeManageTab = ref('update');
    
    // 更新竞赛信息表单
    const updateSpaceForm = reactive({
      title: '',
      description: '',
      category: '',
      level: '',
      start_date: '',
      end_date: '',
      posterFiles: []
    });
    
    // 关闭竞赛空间确认
    const closeSpaceConfirmText = ref('');
    
    // 竞赛空间成员管理
    const spaceMembers = ref([]);
    const memberCurrentPage = ref(1);
    const memberPageSize = ref(10);
    const memberTotal = ref(0);
    const loadingUsers = ref(false);

    // 其他竞赛空间弹窗相关
    const otherSpacesDialogVisible = ref(false);
    const userSpaces = ref([]);
    const loadingSpaces = ref(false);
    
    // 新增：竞赛文件管理弹窗状态
    const competitionFilesDialogVisible = ref(false);
    const competitionFiles = ref([]);
    const loadingFiles = ref(false);
    const fileToUpload = ref(null); // 用于存储待上传的文件对象
    const fileListForUpload = ref([]); // 用于 el-upload 的 v-model
    
    // 公告管理相关
    const announcementDialogVisible = ref(false);
    const announcements = ref([]);
    const loadingAnnouncements = ref(false);
    const selectedAnnouncement = ref(null);
    const isEditingAnnouncement = ref(false);
    const editingAnnouncementId = ref(null);
    const announcementForm = reactive({
      title: '',
      content: ''
    });
    const submittingAnnouncement = ref(false);

    // 新增：竞赛文件管理 - 打开对话框并加载文件列表
    const openCompetitionFilesDialog = async () => {
      competitionFilesDialogVisible.value = true;
      fileToUpload.value = null; // 重置上传状态
      fileListForUpload.value = []; // 重置 el-upload 列表
      await loadCompetitionFiles();
    };
    
    // 打开公告对话框
    const openAnnouncementDialog = async () => {
      announcementDialogVisible.value = true;
      selectedAnnouncement.value = null;
      isEditingAnnouncement.value = false;
      await loadAnnouncements();
    };

    // 加载竞赛空间的公告
    const loadAnnouncements = async () => {
      if (!spaceId) return;
      loadingAnnouncements.value = true;
      try {
        const response = await api.getSpaceAnnouncements();
        if (response && response.data) {
          // 处理新的API响应格式
          const spaceData = response.data.find(item => {
            // 查找当前竞赛空间的公告
            return item.announcements && item.announcements.length > 0;
          });
          
          if (spaceData && spaceData.announcements) {
            announcements.value = spaceData.announcements;
          } else {
            announcements.value = [];
          }
        } else {
          announcements.value = [];
        }
      } catch (error) {
        console.error('获取公告失败:', error);
        ElMessage.error('获取公告列表失败');
        announcements.value = [];
      } finally {
        loadingAnnouncements.value = false;
      }
    };

    // 查看公告详情
    const viewAnnouncement = (announcement) => {
      // 直接使用传入的公告对象，无需再次请求
      selectedAnnouncement.value = announcement;
    };
    
    // 确认删除公告
    const confirmDeleteAnnouncement = (announcement) => {
      ElMessageBox.confirm(
        '确定要删除这条公告吗？此操作不可恢复。',
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(async () => {
          try {
            await api.deleteAnnouncement(announcement.announcement_id);
            ElMessage.success('公告删除成功');
            // 重新加载公告列表
            await loadAnnouncements();
          } catch (error) {
            console.error('删除公告失败:', error);
            ElMessage.error('删除公告失败');
          }
        })
        .catch(() => {
          // 用户取消删除
        });
    };

    // 打开创建公告表单
    const openCreateAnnouncementForm = () => {
      isEditingAnnouncement.value = true;
      editingAnnouncementId.value = null;
      announcementForm.title = '';
      announcementForm.content = '';
      selectedAnnouncement.value = null;
    };

    // 编辑公告
    const editAnnouncement = (announcement) => {
      isEditingAnnouncement.value = true;
      editingAnnouncementId.value = announcement.announcement_id;
      announcementForm.title = announcement.announcement_title;
      announcementForm.content = announcement.announcement_content;
    };

    // 取消编辑公告
    const cancelEditAnnouncement = () => {
      isEditingAnnouncement.value = false;
      editingAnnouncementId.value = null;
    };

    // 提交公告（创建或更新）
    const submitAnnouncement = async () => {
      if (!announcementForm.title.trim() || !announcementForm.content.trim()) {
        ElMessage.warning('标题和内容不能为空');
        return;
      }

      submittingAnnouncement.value = true;
      try {
        if (editingAnnouncementId.value) {
          // 更新公告
          await api.updateAnnouncement({
            announcement_id: editingAnnouncementId.value,
            title: announcementForm.title,
            content: announcementForm.content
          });
          ElMessage.success('公告更新成功');
        } else {
          // 创建公告
          await api.createAnnouncement({
            space_id: spaceId,
            title: announcementForm.title,
            content: announcementForm.content
          });
          ElMessage.success('公告发布成功');
        }
        // 重新加载公告列表
        await loadAnnouncements();
        // 重置表单状态
        isEditingAnnouncement.value = false;
        editingAnnouncementId.value = null;
      } catch (error) {
        console.error('提交公告失败:', error);
        ElMessage.error(editingAnnouncementId.value ? '更新公告失败' : '发布公告失败');
      } finally {
        submittingAnnouncement.value = false;
      }
    };

    // // 确认删除公告
    // const confirmDeleteAnnouncement = (announcement) => {
    //   ElMessageBox.confirm(
    //     '确定要删除这条公告吗？此操作不可恢复。',
    //     '删除确认',
    //     {
    //       confirmButtonText: '确定',
    //       cancelButtonText: '取消',
    //       type: 'warning'
    //     }
    //   ).then(async () => {
    //     try {
    //       await api.deleteAnnouncement(announcement.announcement_id);
    //       ElMessage.success('公告已删除');
    //       await loadAnnouncements();
    //       if (selectedAnnouncement.value && selectedAnnouncement.value.announcement_id === announcement.announcement_id) {
    //         selectedAnnouncement.value = null;
    //       }
    //     } catch (error) {
    //       console.error('删除公告失败:', error);
    //       ElMessage.error('删除公告失败');
    //     }
    //   }).catch(() => {
    //     // 用户取消删除
    //   });
    // };

    // 新增：处理导出组队信息
    const handleExportTeamInfo = async () => {
      try {
        // 显示导出选项对话框
        await ElMessageBox.confirm(
          '请确认要导出的信息内容',
          '导出组队信息',
          {
            confirmButtonText: '确认导出',
            cancelButtonText: '取消',
            type: 'info',
            showInput: false,
            customClass: 'export-dialog',
            beforeClose: (action, instance, done) => {
              if (action === 'confirm') {
                instance.confirmButtonLoading = true;
                instance.confirmButtonText = '导出中...'
                setTimeout(() => {
                  done();
                  setTimeout(() => {
                    instance.confirmButtonLoading = false;
                  }, 300);
                }, 1000);
              } else {
                done();
              }
            }
          }
        );

        // 设置导出选项
        const options = {
          include_team_name: true,
          include_real_name: true,
          include_gender: true,
          include_student_id: true,
          include_college_name: true,
          include_phone_number: false,
          include_email: true
        };

        ElMessage.info('正在导出组队信息，请稍候...');
        const response = await api.exportTeamInfo(spaceId, options);
        
        // 创建下载链接并触发下载
        const filename = `组队信息_${competitionInfo.value.title}_${new Date().toISOString().split('T')[0]}.xlsx`;
        createDownloadLink(response, filename);
        
        ElMessage.success('组队信息导出成功');
      } catch (error) {
        console.error('导出组队信息失败:', error);
        ElMessage.error('导出组队信息失败');
      }
    };

    // 加载竞赛文件列表
    const loadCompetitionFiles = async () => {
      if (!spaceId) return;
      loadingFiles.value = true;
      try {
        const response = await api.listCompetitionFiles(spaceId);
        if (response && response.data) {
          // 确保每个文件对象都有必要的属性
          competitionFiles.value = response.data.map(file => ({
            file_id: file.file_id,
            file_name: file.file_name,
            description: file.description || '无描述',
            upload_time: file.upload_time || new Date().toISOString(),
            // 保留其他可能的属性
            ...file
          }));
          console.log('加载的文件列表:', competitionFiles.value);
        } else {
          ElMessage.error((response && response.message) || '加载文件列表失败');
          competitionFiles.value = [];
        }
      } catch (error) {
        console.error('加载文件列表失败:', error);
        ElMessage.error('加载文件列表失败');
        competitionFiles.value = [];
      } finally {
        loadingFiles.value = false;
      }
    };

    // 新增：处理文件选择变化 (el-upload)
    const handleFileChange = (uploadFile, uploadFiles) => {
      // 限制只能上传一个文件，新的替换旧的
      if (uploadFiles.length > 1) {
        // 仅保留最新选择的文件
        fileListForUpload.value = [uploadFiles[uploadFiles.length - 1]];
      } else {
        fileListForUpload.value = uploadFiles;
      }
      fileToUpload.value = fileListForUpload.value.length > 0 ? fileListForUpload.value[0].raw : null;
    };

    // 新增：处理文件移除 (el-upload)
    const handleFileRemove = (uploadFile, uploadFiles) => {
      fileListForUpload.value = uploadFiles;
      fileToUpload.value = null;
    };

    // 新增：执行文件上传
    const handleUploadFile = async () => {
      if (!fileToUpload.value) {
        ElMessage.warning('请先选择要上传的文件');
        return;
      }
      loadingFiles.value = true; // 可以使用独立的上传加载状态
      try {
        const response = await api.uploadCompetitionFile(spaceId, fileToUpload.value);
        if (response) {
          ElMessage.success('文件上传成功');
          fileToUpload.value = null;
          fileListForUpload.value = []; // 清空 el-upload 列表
          await loadCompetitionFiles(); // 重新加载列表
        } else {
          ElMessage.error(response.message || '文件上传失败');
        }
      } catch (error) {
        console.error('文件上传失败:', error);
        ElMessage.error('文件上传失败');
      } finally {
        loadingFiles.value = false;
      }
    };

    // 新增：处理文件下载
    const handleDownloadFile = async (file) => {
      try {
        ElMessage.info(`开始下载文件: ${file.file_name}`);
        const response = await api.downloadCompetitionFile(file.file_id);
        // response 是 Blob 对象
        createDownloadLink(response, file.file_name);
        // 下载成功通常不需要显式提示，浏览器会处理
      } catch (error) {
        console.error('下载文件失败:', error);
        ElMessage.error(`下载文件 ${file.file_name} 失败`);
      }
    };

    // 新增：处理文件删除 (仅管理员)
    const handleDeleteFile = async (file) => {
      try {
        await ElMessageBox.confirm(`确定要删除文件 "${file.file_name}" 吗？`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        });
        const response = await api.deleteCompetitionFile(file.file_id);
        if (response.code === 200) {
          ElMessage.success('文件删除成功');
          await loadCompetitionFiles(); // 重新加载列表
        } else {
          ElMessage.error(response.message || '删除失败');
        }
      } catch (error) {
        if (error !== 'cancel') { // 忽略用户取消操作
          console.error('删除文件失败:', error);
          ElMessage.error('删除文件失败');
        }
      }
    };

    // 加载竞赛空间信息
    const loadCompetitionInfo = async () => {
      try {
        const response = await api.getSpaceInfo(spaceId);
        if (response && response.data) {
          competitionInfo.value = response.data;
        }
      } catch (error) {
        console.error('获取竞赛空间信息失败:', error);
      }
    };

    // 加载问答区内容
    const loadDiscussions = async () => {
      try {
        const response = await api.getDiscussions(spaceId);
        if (response) {
          allQuestions.value = response.map((q, index) => ({ ...q, question_id: q.question_id || `temp_${index}` }));
          total.value = allQuestions.value.length;
        } else {
          allQuestions.value = [];
          total.value = 0;
        }
      } catch (error) {
        console.error('获取问答区内容失败:', error);
        allQuestions.value = [];
        total.value = 0;
      }
    };

    // 计算当前页显示的问题
    const paginatedQuestions = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return allQuestions.value.slice(start, end);
    });
    
    // 计算当前页显示的成员
    const paginatedMembers = computed(() => {
      const start = (memberCurrentPage.value - 1) * memberPageSize.value;
      const end = start + memberPageSize.value;
      return spaceMembers.value.slice(start, end);
    });

    // 计算当前用户的问题
    const myQuestions = computed(() => {
      if (!userState.isLoggedIn) return [];
      return allQuestions.value.filter(q => 
        q.author_username === userState.userInfo.username
      );
    });

    // 选择问题时，如果正在编辑，则取消编辑
    const selectQuestion = (question) => {
      if (isEditing.value) {
        // 可能需要提示用户是否放弃编辑
        isEditing.value = false;
      }
      selectedQuestion.value = question;
    };

    // 清除选中的问题，返回列表视图
    const clearSelectedQuestion = () => {
      selectedQuestion.value = null;
    };

    // 处理图片预览
    const handlePictureCardPreview = (file) => {
      dialogImageUrl.value = file.url;
      dialogVisible.value = true;
    };

    // 处理图片移除
    const handleRemove = (file, fileList) => {
      uploadedImages.value = fileList;
    };

    // 截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      return text.length > maxLength 
        ? text.substring(0, maxLength) + '...' 
        : text;
    };

    // 处理回复图片预览
    const handleReplyPictureCardPreview = (file) => {
      dialogImageUrl.value = file.url;
      dialogVisible.value = true;
    };

    // 处理回复图片移除
    const handleReplyRemove = (file, fileList) => {
      replyImages.value = fileList;
    };

    onMounted(() => {
      loadCompetitionInfo();
      loadDiscussions();
    });

    return {
      userState,
      competitionInfo,
      allQuestions,
      paginatedQuestions,
      myQuestions,
      newQuestion,
      currentPage,
      pageSize,
      total,
      spaceId,
      selectedQuestion,
      selectQuestion,
      clearSelectedQuestion,
      truncateText,
      uploadedImages,
      dialogVisible,
      dialogImageUrl,
      newReply,
      replyImages,
      handlePictureCardPreview,
      handleRemove,
      handleReplyPictureCardPreview,
      handleReplyRemove,
      isEditing,
      // 更新个人信息相关
      updateUserInfoDialogVisible,
      updateUserInfoForm,
      // 管理竞赛空间相关
      manageSpaceDialogVisible,
      activeManageTab,
      updateSpaceForm,
      closeSpaceConfirmText,
      spaceMembers,
      memberCurrentPage,
      memberPageSize,
      memberTotal,
      paginatedMembers,
      loadingUsers,
      // 新增：竞赛文件管理弹窗状态
      competitionFilesDialogVisible,
      competitionFiles,
      loadingFiles,
      fileToUpload,
      fileListForUpload,
      openCompetitionFilesDialog, // Expose method to open dialog
      // 新增：暴露文件管理方法
      loadCompetitionFiles,
      handleFileChange,
      handleFileRemove,
      handleUploadFile,
      handleDownloadFile,
      handleDeleteFile,
      // 其他竞赛空间相关
      otherSpacesDialogVisible,
      userSpaces,
      loadingSpaces,
      
      // 公告相关
      announcementDialogVisible,
      announcements,
      loadingAnnouncements,
      selectedAnnouncement,
      isEditingAnnouncement,
      editingAnnouncementId,
      announcementForm,
      submittingAnnouncement,
      openAnnouncementDialog,
      loadAnnouncements,
      viewAnnouncement,
      openCreateAnnouncementForm,
      editAnnouncement,
      cancelEditAnnouncement,
      submitAnnouncement,
      confirmDeleteAnnouncement,
      
      // 新增：导出组队信息
      handleExportTeamInfo
    };
  },
  methods: {
    goBack() {
      this.$router.back();
    },
    
    handleSearch() {
      // 实现搜索逻辑
    },

    handleLoginSuccess() {
      this.$message.success('登录成功');
    },

    handleLogoutSuccess() {
      this.$message.info('已退出登录');
    },

    handleDownload(type) {
      if (type === '竞赛公告') {
        this.openAnnouncementDialog();
      } else if (type === '其他组队空间') {
        this.openOtherSpacesDialog();
      } else {
        this.$message.info(`正在下载${type}...`);
      }
    },
    
    // 打开其他竞赛空间弹窗
    openOtherSpacesDialog() {
      if (!userState.isLoggedIn) {
        this.$message.warning('请先登录');
        return;
      }
      this.otherSpacesDialogVisible = true;
      this.loadUserSpaces();
    },
    
    // 加载用户加入的竞赛空间
    async loadUserSpaces() {
      if (!userState.isLoggedIn || this.loadingSpaces) return;
      
      try {
        this.loadingSpaces = true;
        const response = await api.listUserSpaces();
        if (response && response.data) {
          const spaces = Array.isArray(response.data) ? response.data : [];
          // 过滤掉当前竞赛空间
          this.userSpaces = spaces.filter(space => space.id !== parseInt(this.spaceId));
        }
      } catch (error) {
        console.error('获取用户竞赛空间失败:', error);
        this.$message.error('获取竞赛空间列表失败');
      } finally {
        this.loadingSpaces = false;
      }
    },
    
    // 跳转到选择的竞赛空间
    goToSpace(spaceId) {
      this.$router.push(`/competition/space/${spaceId}`).then(() => {
        window.location.reload(); // 导航完成后刷新页面
      });
      this.otherSpacesDialogVisible = false;
    },

    // 新增：跳转到组队空间页面
    goToTeamSpace() {
      this.$router.push({ name: 'TeamSpace', params: { spaceId: this.spaceId } });
    },

    // 打开更新个人信息对话框
    async openUpdateUserInfoDialog() {
      if (!this.spaceId) {
        this.$message.error('无法获取竞赛空间ID');
        return;
      }
      try {
        console.log('Attempting to fetch user info for space:', this.spaceId);
        const response = await api.getSpaceUserInfo(this.spaceId);
        if (response && response.data) {
          const userInfo = response.data;
          this.updateUserInfoForm.real_name = userInfo.realName || '';
          this.updateUserInfoForm.student_id = userInfo.studentId || '';
          this.updateUserInfoForm.college_name = userInfo.collegeName || '';
          this.updateUserInfoForm.gender = userInfo.gender || '';
          this.updateUserInfoForm.phone = userInfo.phone || ''; // API 返回的是 phone
          this.updateUserInfoForm.email = userInfo.email || '';
          // 头像处理比较复杂，暂时只显示URL，不提供上传
          this.updateUserInfoForm.avatar = userInfo.avatar || ''; 
        } else {
          // 如果获取失败或没有数据，清空表单
          this.updateUserInfoForm.real_name = '';
          this.updateUserInfoForm.student_id = '';
          this.updateUserInfoForm.college_name = '';
          this.updateUserInfoForm.gender = '';
          this.updateUserInfoForm.phone = '';
          this.updateUserInfoForm.email = '';
          this.updateUserInfoForm.avatar = '';
          this.$message.warning('未能获取到您在此空间的个人信息，请手动填写');
        }
      } catch (error) {
        console.error('获取空间用户信息失败:', error);
        this.$message.error('获取空间用户信息失败');
        // 出错时也清空表单
        this.updateUserInfoForm.real_name = '';
        this.updateUserInfoForm.student_id = '';
        this.updateUserInfoForm.college_name = '';
        this.updateUserInfoForm.gender = '';
        this.updateUserInfoForm.phone = '';
        this.updateUserInfoForm.email = '';
        this.updateUserInfoForm.avatar = '';
      }
      this.updateUserInfoDialogVisible = true;
    },
    
    // 提交空间内用户信息更新
    async handleUpdateSpaceUserInfo() {
      if (!this.spaceId) {
        this.$message.error('无法获取竞赛空间ID');
        return;
      }
      try {
        // 注意：API 函数需要的是 real_name, student_id 等，但发送时是 realName, studentId
        // api.js 中的 updateSpaceUserInfo 函数已处理此转换
        const response = await api.updateSpaceUserInfo(this.spaceId, this.updateUserInfoForm);
        if (response) { // 假设成功消息是 '更新成功'
          this.$message.success('个人信息更新成功');
          this.updateUserInfoDialogVisible = false;
          // 可选：如果更新的信息影响页面显示，可能需要重新获取数据
        } else {
          this.$message.error(response.message || '更新失败');
        }
      } catch (error) {
        console.error('更新空间用户信息失败:', error);
        this.$message.error('更新空间用户信息失败');
      }
    },

    // 打开管理竞赛空间对话框
    openManageSpaceDialog() {
      // 初始化更新竞赛信息表单
      this.updateSpaceForm.title = this.competitionInfo.title || '';
      this.updateSpaceForm.description = this.competitionInfo.description || '';
      this.updateSpaceForm.category = this.competitionInfo.category || '';
      this.updateSpaceForm.level = this.competitionInfo.level || '';
      this.updateSpaceForm.start_date = this.competitionInfo.start_date || '';
      this.updateSpaceForm.end_date = this.competitionInfo.end_date || '';
      this.updateSpaceForm.posterFiles = [];
      
      // 重置关闭竞赛空间确认文本
      this.closeSpaceConfirmText = '';
      
      // 加载竞赛空间成员
      this.loadSpaceMembers();
      
      // 显示对话框
      this.manageSpaceDialogVisible = true;
      this.activeManageTab = 'update';
    },
    
    // 加载竞赛空间成员
    async loadSpaceMembers() {
      this.loadingUsers = true;
      try {
        const response = await api.getSpaceMembers(this.spaceId);
        if (response && response.data) {
          // 使用延迟加载策略，避免ResizeObserver循环错误
          setTimeout(() => {
            this.spaceMembers = response.data;
            this.memberTotal = this.spaceMembers.length;
            this.loadingUsers = false;
          }, 100);
        } else {
          this.spaceMembers = [];
          this.memberTotal = 0;
          this.loadingUsers = false;
        }
      } catch (error) {
        console.error('获取竞赛空间成员失败:', error);
        ElMessage.error('获取竞赛空间成员失败');
        this.spaceMembers = [];
        this.memberTotal = 0;
        this.loadingUsers = false;
      }
    },
    
    // 处理成员分页变化
    handleMemberPageChange(page) {
      this.memberCurrentPage = page;
    },
    
    // 更新竞赛空间信息
    async handleUpdateSpace() {
      try {
        const formData = new FormData();
        formData.append('space_id', this.spaceId);
        formData.append('title', this.updateSpaceForm.title);
        formData.append('description', this.updateSpaceForm.description);
        formData.append('category', this.updateSpaceForm.category);
        formData.append('level', this.updateSpaceForm.level);
        formData.append('start_date', this.updateSpaceForm.start_date);
        formData.append('end_date', this.updateSpaceForm.end_date);
        //console.log(formData)
        // 如果有上传新海报
        if (this.updateSpaceForm.posterFiles.length > 0) {
          formData.append('poster', this.updateSpaceForm.posterFiles[0].raw);
        }
        
        const response = await api.updateSpace(formData);
        if (response) {
          ElMessage.success('竞赛空间信息更新成功');
          this.manageSpaceDialogVisible = false;
          // 重新加载竞赛信息
          //this.loadCompetitionInfo();
          window.location.reload();
        } else {
          ElMessage.error(response.message || '更新失败');
        }
      } catch (error) {
        console.error('更新竞赛空间信息失败:', error);
        //ElMessage.error('更新竞赛空间信息失败,请检查输入');
      }
    },
    
    // 关闭竞赛空间
    async handleCloseSpace() {
      try {
        const response = await api.closeSpace(this.spaceId);
        this.$router.push('/competition/category').then(() => {
            window.location.reload(); // 导航完成后刷新页面
          });
        if (response) {
          ElMessage.success('竞赛空间已关闭');
          
          this.manageSpaceDialogVisible = false;
          // 返回上一页
        } else {
          ElMessage.error(response.message || '关闭失败');
        }
      } catch (error) {
        console.error('关闭竞赛空间失败:', error);
        ElMessage.error('关闭竞赛空间失败');
      }
    },
    
    // 移除竞赛空间成员
    async handleRemoveSpaceMember(member) {
      try {
        await ElMessageBox.confirm('确定要移除该成员吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        const response = await api.removeSpaceMember(this.spaceId, member.space_user_id);
        if (response ) {
          ElMessage.success('成员已移除');
          // 重新加载成员列表
          this.loadSpaceMembers();
        } else {
          ElMessage.error(response.message || '移除失败');
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('移除竞赛空间成员失败:', error);
          ElMessage.error('移除竞赛空间成员失败');
        }
      }
    },

    // 新增：处理更新空间内个人信息
    // async handleUpdateSpaceUserInfo() {
    //   if (!this.spaceId) {
    //     this.$message.error('无法获取竞赛空间ID');
    //     return;
    //   }
    //   // 简单校验，至少填一项
    //   if (!this.updateUserInfoForm.real_name && !this.updateUserInfoForm.student_id && !this.updateUserInfoForm.college_name) {
    //     this.$message.warning('请至少填写一项需要更新的信息');
    //     return;
    //   }

    //   try {
    //     const response = await api.updateSpaceUserInfo(this.spaceId, this.updateUserInfoForm);
    //     if (response) { // 假设成功的响应码是 200
    //       this.$message.success(response.message || '用户信息更新成功');
    //       this.updateUserInfoDialogVisible = false;
    //       // 可能需要重新加载某些依赖此信息的数据
    //     } else {
    //       this.$message.error(response.message || '更新失败');
    //     }
    //   } catch (error) {
    //     console.error('更新空间用户信息失败:', error);
    //     this.$message.error(error.message || '更新用户信息时发生错误');
    //   }
    // },

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
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },

    async submitQuestion() {
      if (!this.newQuestion.trim()) {
        this.$message.warning('请输入问题内容');
        return;
      }

      if (!userState.isLoggedIn) {
        this.$message.warning('请先登录');
        return;
      }

      // 准备提交的数据
      const submissionData = {
        content: this.newQuestion,
        images: this.uploadedImages.map(file => file.raw) // 获取原始文件对象
      };

      try {
        const response = await api.submitDiscussion(this.spaceId, submissionData);
        
        if (response && response.message) {
          this.$message.success(response.message || '问题发表成功');
          this.newQuestion = '';
          this.uploadedImages = []; // 清空已上传图片列表
          this.loadDiscussions();
        } else {
          this.$message.warning('提交成功，但未收到预期的响应');
          this.newQuestion = '';
          this.uploadedImages = [];
          this.loadDiscussions();
        }
      } catch (error) {
        console.error('发表问题失败:', error);
        this.$message.error(error.message || '发表问题失败');
      }
    },

    handlePageChange(page) {
      this.currentPage = page;
    },

    // 加载问答区内容
    async loadDiscussions() {
      try {
        const response = await api.getDiscussions(this.spaceId);
        window.location.reload();
        if (response && response.data) {
          this.allQuestions = response.data;
          this.total = response.data.length;
          window.location.reload();
        }
      } catch (error) {
        console.error('获取问答区内容失败:', error);
      }
    },

    async submitReply() {
      if (!this.selectedQuestion || !this.selectedQuestion.question_id) {
        this.$message.error('未选中任何问题');
        return;
      }
      if (!this.newReply.trim()) {
        this.$message.warning('请输入回复内容');
        return;
      }
      if (!userState.isLoggedIn) {
        this.$message.warning('请先登录');
        return;
      }

      // console.log(this.selectedQuestion)
      // console.log(this.replyTarget.userId)
      // 确定回复对象：如果有指定回复目标则使用目标ID，否则默认回复楼主
      const toUserId = this.replyTarget ? this.replyTarget.userId : this.selectedQuestion.author_space_user_id;
      
      const replyData = {
        question_id: this.selectedQuestion.question_id,
        content: this.newReply,
        to_user_id: toUserId, 
        images: this.replyImages.map(file => file.raw) // 获取原始文件对象
      };

      //console.log(replyData)
      // 检查 to_user_id 是否存在
      if (!replyData.to_user_id) {
        console.error('无法获取回复对象ID (to_user_id)', this.replyTarget || this.selectedQuestion);
        this.$message.error('无法提交回复：无法获取回复对象ID');
        return;
      }

      try {
        const response = await api.submitReply(replyData);
        if (response && response.message) {
          this.$message.success(response.message || '回复成功');
          this.newReply = '';
          this.replyImages = []; // 清空已上传图片列表
          this.clearReplyTarget(); // 清空回复目标
          this.loadDiscussions(); 
        } else {
           this.$message.warning('提交成功，但未收到预期响应');
           this.newReply = '';
           this.replyImages = []; // 清空已上传图片列表
           this.clearReplyTarget(); // 清空回复目标
           this.loadDiscussions();
        }
      } catch (error) {
         console.error('提交回复失败:', error);
         this.$message.error(error.message || '提交回复失败');
      }
    },

    // 删除问题
    async handleDeleteQuestion(questionId) {
      if (!questionId) return;
      
      try {
        await ElMessageBox.confirm(
          '确定要删除这个问题及其所有回复吗？此操作不可撤销。',
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
          }
        );
        
        // 用户确认删除
        await api.deleteQuestion(questionId);
        ElMessage.success('问题已删除');
        
        // 刷新问答区
        this.clearSelectedQuestion(); // 返回列表视图
        this.loadDiscussions();
        
      } catch (error) {
        if (error !== 'cancel') { // 捕获非取消操作的错误
          console.error('删除问题失败:', error);
          ElMessage.error(error.message || '删除问题失败');
        }
      }
    },

    // 设置回复目标用户
    replyToUser(username, userId) {
      this.replyTarget = {
        username: username,
        userId: userId
      };
      // 聚焦到回复框
      this.$nextTick(() => {
        const replyTextarea = document.querySelector('.reply-form .el-textarea__inner');
        if (replyTextarea) {
          replyTextarea.focus();
        }
      });
    },
    
    // 清除回复目标
    clearReplyTarget() {
      this.replyTarget = null;
    },
    
    // 删除回复
    async handleDeleteReply(replyId) {
       if (!replyId) return;
      
      try {
        await ElMessageBox.confirm(
          '确定要删除这条回复吗？此操作不可撤销。',
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
          }
        );
        
        // 用户确认删除
        await api.deleteReply(replyId);
        ElMessage.success('回复已删除');
        
        // 刷新当前问题的回复列表 (或者整个问答区)
        // 简单起见，重新加载整个问答区
        this.loadDiscussions(); 
        // 如果希望只更新当前问题，需要更复杂的逻辑
        // 例如，从 selectedQuestion.replies 中移除对应项
        // this.selectedQuestion.replies = this.selectedQuestion.replies.filter(r => r.reply_id !== replyId);

      } catch (error) {
        if (error !== 'cancel') { // 捕获非取消操作的错误
          console.error('删除回复失败:', error);
          ElMessage.error(error.message || '删除回复失败');
        }
      }
    },

    // 新增：开始编辑问题
    startEditQuestion(question) {
      if (!question) return;
      // this.selectQuestion(question); // 不再需要，因为点击编辑时 question 已经是 selectedQuestion
      this.isEditing = true;
      this.newQuestion = question.content; // 填充表单
      // 注意：不清空 uploadedImages，让用户看到之前的图片，但需要提示用户重新上传以覆盖
      // 或者清空让用户必须重新上传
      this.uploadedImages = []; // 决定清空，让用户重新上传
      this.$message.info('请重新上传图片以更新，否则图片将被清空。');
    },

    // 新增：取消编辑
    cancelEditQuestion() {
      this.isEditing = false;
      this.newQuestion = ''; // 清空表单
      this.uploadedImages = [];
      // selectedQuestion 保持不变，用户仍在查看该问题详情
      // 如果希望取消后返回列表，则调用 this.clearSelectedQuestion();
    },

    // 新增：处理更新问题
    async handleUpdateQuestion() {
      if (!this.selectedQuestion || !this.selectedQuestion.question_id) {
        ElMessage.error('错误：未选中要编辑的问题');
        return;
      }
      if (!this.newQuestion.trim()) {
        ElMessage.warning('请输入问题内容');
        return;
      }

      const updatedData = {
        content: this.newQuestion,
        // API 会覆盖图片，所以传递当前上传列表中的文件
        images: this.uploadedImages.map(file => file.raw) 
      };

      try {
        const response = await api.updateQuestion(this.selectedQuestion.question_id, updatedData);
        if (response && response.message) {
          ElMessage.success(response.message || '问题更新成功');
          // 更新成功，退出编辑状态，并刷新数据
          this.isEditing = false;
          this.newQuestion = '';
          this.uploadedImages = [];
          // 重新加载讨论以查看更新
          // 同时需要更新 selectedQuestion 的内容，或者直接清空返回列表
          const updatedQuestionId = this.selectedQuestion.question_id;
          this.selectedQuestion = null; // 先清空
          await this.loadDiscussions(); // 加载新数据
          // 尝试重新选中更新后的问题（如果还在当前页）
          const reloadedQuestion = this.allQuestions.find(q => q.question_id === updatedQuestionId);
          if(reloadedQuestion) {
             this.selectedQuestion = reloadedQuestion;
          } else {
             // 如果问题不在当前页了（不太可能发生），或加载失败，就返回列表
             this.clearSelectedQuestion();
          }
          
        } else {
          ElMessage.warning('更新成功，但未收到预期响应');
           // 可能也需要刷新数据
          this.loadDiscussions();
        }
      } catch (error) {
        console.error('更新问题失败:', error);
        ElMessage.error(error.message || '更新问题失败');
      }
    }
  }
};
</script>

<style scoped>
.competition-space {
  width: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.competition-info {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.competition-banner {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.competition-poster {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.info-left {
  flex: 1;
  min-width: 300px;
}

.info-right {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.competition-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.competition-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.competition-date {
  color: #606266;
  font-size: 14px;
}

.competition-description {
  line-height: 1.6;
  color: #606266;
  white-space: pre-line;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.discussion-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

@media (max-width: 768px) {
  .info-header {
    flex-direction: column;
  }
  
  .info-right {
    margin-top: 15px;
    width: 100%;
  }
  
  .competition-poster {
    height: 200px;
  }
}
</style>

<style scoped>
.competition-space {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;
  z-index: 1;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 999;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.space-logo {
  display: flex;
  align-items: center;
}

.space-logo h2 {
  font-size: 20px;
  color: #303133;
  margin: 0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
}

.competition-info {
  position: relative;
  z-index: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.info-left {
  flex: 1;
}

.competition-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.competition-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.competition-date {
  color: #909399;
  font-size: 14px;
}

.info-right {
  display: flex;
  gap: 10px;
}

.competition-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-top: 20px;
}

/* 问答区样式 */
.discussion-section {
  padding: 20px;
  max-width: 1200px;
  margin: 20px auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.discussion-header {
  margin-bottom: 20px;
}

.discussion-container {
  display: flex;
  gap: 20px;
}

.discussion-list {
  flex: 1;
  border-right: 1px solid #ebeef5;
  padding-right: 20px;
}

.discussion-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-item {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.question-item:hover, .question-item.active {
  background-color: #f5f7fa;
}

.question-user {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.question-info {
  margin-left: 10px;
}

.question-username {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.question-time {
  font-size: 12px;
  color: #909399;
}

.question-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 5px;
}

.question-actions {
  text-align: right;
}

/* 问题详情区域样式 */
.question-detail {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-user {
  display: flex;
  align-items: center;
}

.detail-info {
  margin-left: 12px;
}

.detail-username {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.detail-time {
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}

.detail-content p {
  font-size: 14px;
  color: #303133;
  line-height: 1.7;
  margin-bottom: 15px;
  white-space: pre-wrap;
}

.detail-images h4 {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.question-form {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.question-form h3 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.my-questions {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.my-questions h3 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

/* 图片上传区域样式 */
.upload-section {
  margin-top: 15px;
}

:deep(.el-upload--picture-card) {
  width: 80px;
  height: 80px;
  line-height: 90px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 80px;
  height: 80px;
}

.my-question-item {
  padding: 12px;
  background-color: #fff;
  border-radius: 4px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.my-question-item:last-child {
  margin-bottom: 0;
}

.question-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  margin-bottom: 8px;
}

.empty-message {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

/* 移除原有的 comments-section 相关样式 */
.comments-section {
  display: none;
}

/* 回复区域样式 */
.replies-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9fafc;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.replies-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.replies-list {
  margin-bottom: 20px;
}

/* 修改：回复项布局 */
.reply-item {
  display: flex; /* 使用 Flex 布局 */
  padding: 12px 0;
  border-bottom: 1px dashed #e4e7ed;
  align-items: flex-start; /* 顶部对齐 */
}

.reply-item:last-child {
  border-bottom: none;
}

/* 修改：回复用户头像区域 */
.reply-user {
  /* display: flex; */ /* 不再需要内嵌 flex */
  /* align-items: flex-start; */
  /* width: 150px; */ /* 移除固定宽度 */
  margin-right: 12px; /* 调整头像与内容的间距 */
  flex-shrink: 0; /* 防止头像被压缩 */
}

.reply-info {
  /* 样式移到 .reply-meta */
  display: none; 
}

.reply-username {
  /* 样式移到 .reply-meta */
  display: none; 
}

/* .reply-time 的 float: right 已在 .reply-meta 中处理 */

.reply-content {
  flex: 1; /* 占据剩余空间 */
}

/* .reply-content p 的样式移到 .reply-text p */
/* .reply-content p {
  display: none; 
} */ /* 移除 display: none */

/* 修改：直接给 .reply-content p 应用样式 */
.reply-content p {
  margin: 0 0 8px 0; /* 增加底部间距 */
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap; /* 保留换行 */
}

.empty-reply {
  text-align: center;
  color: #c0c4cc;
  padding: 15px 0;
  font-size: 13px;
}

/* 回复元信息样式 */
.reply-meta {
  margin-bottom: 8px;
  font-size: 13px;
  color: #909399;
  display: flex; /* 使用 flex 布局对齐元信息 */
  align-items: center;
  flex-wrap: wrap; /* 允许换行 */
}

.reply-from-user,
.reply-to-user {
  font-weight: 500;
  color: #409eff;
  cursor: pointer; /* 可选：如果想添加用户点击功能 */
}

.reply-indicator {
  margin: 0 4px;
}

.reply-time {
  /* float: right; */ /* 移除 float */
  margin-left: auto; /* 将时间推到右侧 */
  font-size: 11px;
  align-self: flex-start; /* 保持时间在顶部 */
}

/* 新增：删除回复按钮样式 */
.delete-reply-btn {
  margin-left: 8px; /* 与时间戳保持间距 */
}

/* 回复文本样式 */
.reply-text p {
  margin: 0 0 8px 0;  
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap; 
}

/* 回复图片区域样式 */
.reply-images {
  /* margin-top: 8px; */ /* 移除，间距由 reply-text p 控制 */
}

.reply-form {
  margin-top: 15px;
}

/* 新增：回复上传区域的特定样式 */
.reply-upload-section {
  margin-top: 10px; /* 调整与输入框的间距 */
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}
/* 成员管理表格样式 */
.loading-container {
  padding: 20px;
}

.member-table-header {
  display: flex;
  background-color: #f5f7fa;
  padding: 12px 0;
  font-weight: bold;
  border-bottom: 1px solid #ebeef5;
}

.member-table-body {
  max-height: 400px;
  overflow-y: auto;
}

.member-row {
  display: flex;
  border-bottom: 1px solid #ebeef5;
  transition: background-color 0.3s;
}

.member-row:hover {
  background-color: #f5f7fa;
}

.member-column, .member-cell {
  padding: 12px 10px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 公告管理样式 */
.announcement-list {
  margin-bottom: 20px;
}

.announcement-detail {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-top: 20px;
}

.announcement-meta {
  color: #909399;
  font-size: 13px;
  margin-bottom: 15px;
  display: flex;
  gap: 15px;
}

.announcement-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.announcement-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.announcement-form {
  margin-top: 20px;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}



.member-cell {
  display: flex;
  align-items: center;
}

.competition-file-upload {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.file-list-section h4 {
  margin-bottom: 10px;
}

.empty-message {
  text-align: center;
  color: #909399;
  margin-top: 20px;
}

/* 其他竞赛空间弹窗样式 */
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
</style>