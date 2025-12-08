import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 使用代理路径
  timeout: 10000
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从本地存储获取token并添加到请求头
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = token;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    if (error.response) {
      // 处理错误响应
      const { status, data } = error.response;
      if (status === 401) {
        // 未授权，可能是token过期
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        // 可以在这里添加重定向到登录页面的逻辑
      }
      return Promise.reject(data || error);
    }
    return Promise.reject(error);
  }
);

// 用户登录
export const login = (phone, password) => {
  const formData = new FormData();
  formData.append('phone', phone);
  formData.append('password', password);
  return api.post('/account/login', formData);
};

// 用户注册
export const register = (userData) => {
  return api.post('/account/register', userData);
};

// 用户登出
export const logout = () => {
  return api.post('/account/logout');
};

// 获取用户信息
export const getUserInfo = () => {
  return api.get('/account/userInfo');
};

// 更新用户信息
export const updateUserInfo = (userData) => {
  const formData = new FormData();
  
  // 处理用户数据字段
  if (userData.username) formData.append('username', userData.username);
  if (userData.email) formData.append('email', userData.email);
  
  // 如果有头像并且是文件对象，则直接添加到formData
  if (userData.avatar && userData.avatar instanceof File) {
    formData.append('avatar', userData.avatar);
    return api.post('/account/userUpdate', formData);
  } 
  // 如果是Base64格式的图片，先转换为Blob再添加
  else if (userData.avatar && userData.avatar.startsWith('data:')) {
    return new Promise((resolve, reject) => {
      fetch(userData.avatar)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'avatar.jpg', { type: 'image/jpeg' });
          formData.append('avatar', file);
          // 在文件添加到formData后再发送请求
          api.post('/account/userUpdate', formData)
            .then(response => resolve(response))
            .catch(error => reject(error));
        })
        .catch(error => reject(error));
    });
  }
  // 如果是URL格式的头像地址，不需要上传，直接跳过
  else if (userData.avatar && (userData.avatar.startsWith('http://') || userData.avatar.startsWith('https://'))) {
    // 其他信息有更新时才发送请求
    if (userData.username || userData.email) {
      return api.post('/account/userUpdate', formData);
    }
    // 没有任何更新时返回成功
    return Promise.resolve({ code: 200, message: '无更新内容' });
  }
  
  // 没有头像则直接发送其他数据
  return api.post('/account/userUpdate', formData);
};

// 注销账号
export const deleteAccount = () => {
  return api.delete('/account/close');
};

// 设置通知
export const setNotificationSettings = (settings) => {
  // API期望接收一个原始JSON对象
  return api.post('/account/chooseToNotify', settings);
};

// 获取学校列表
export const getSchoolList = () => {
  return api.get('/account/school');
};

// 竞赛空间相关API

// 获取筛选后的竞赛空间列表
export const listSpaces = (filters) => {
  return api.post('/space/listSpaces', filters);
};

// 获取最近10天内的热门竞赛
//但是为了展示效果，暂时不使用
export const getRecentCompetitions = () => {
  // 计算当前日期和10天后的日期
  //const today = new Date();
  // const tenDaysLater = new Date();
  // tenDaysLater.setDate(today.getDate() + 10);
  
  // 格式化日期为YYYY-MM-DD
  // const formatDate = (date) => {
  //   const year = date.getFullYear();
  //   const month = String(date.getMonth() + 1).padStart(2, '0');
  //   const day = String(date.getDate()).padStart(2, '0');
  //   return `${year}-${month}-${day}`;
  // };
  
  // 构建筛选条件
  const filters = {
    name: "",
    is_active: true
    // date_start: formatDate(today),
    // date_end: formatDate(tenDaysLater)
  };
  
  return listSpaces(filters);
};

// 获取用户加入的所有竞赛空间
export const listUserSpaces = () => {
  return api.get('/space/listUserSpaces');
};

// 提交加入竞赛空间的申请
export const submitSpaceRequest = (requestData) => {
  const formData = new FormData();
  
  if (requestData.space_id) formData.append('space_id', requestData.space_id);
  if (requestData.real_name) formData.append('real_name', requestData.real_name);
  if (requestData.student_id) formData.append('student_id', requestData.student_id);
  if (requestData.college_name) formData.append('college_name', requestData.college_name);
  
  return api.post('/approval/submitSpaceRequest', formData);
};

// 获取竞赛空间申请的处理结果
export const getSpaceRequestFeedback = () => {
  return api.get('/approval/spaceRequestFeedback');
};

// 获取用户收到的组队申请处理结果
export const getTeamRequestFeedback = () => {
  return api.get('/approval/teamRequestFeedback');
};

// 获取别人对自己的所有回复
export const getRepliesToMe = () => {
  return api.get('/discussion/listReplyToMe');
};

// 获取所有待处理的组队申请 (供队长/管理员使用)
export const listTeamRequests = (filters = {}) => {
  // 根据 Postman 接口文档，使用 POST 方法，filters 可选
  return api.post('/approval/listTeamRequest', filters);
};

// 获取所有竞赛空间的加入申请 (供竞赛负责人使用)
export const listSpaceRequests = (filters = {}) => {
  // 根据 Postman 接口文档，使用 POST 方法，filters 可选
  return api.post('/approval/listSpaceRequest', filters);
};

// 处理竞赛空间申请
export const handleSpaceRequest = (reqId, action, rejectionReason = '') => {
  const formData = new FormData();
  formData.append('smr_id', reqId);
  formData.append('action', action); // 'approve' 或 'reject'
  
  // 如果是拒绝，可以添加拒绝理由
  if (action === 'reject' && rejectionReason) {
    formData.append('rejection_reason', rejectionReason);
  }
  
  return api.post('/approval/handleSpaceRequest', formData);
};

// 处理组队申请
export const handleTeamRequest = (tmrId, action, rejectionReason = '') => {
  const formData = new FormData();
  formData.append('tmr_id', tmrId);
  formData.append('action', action); // 'approve' 或 'reject'
  
  // 如果是拒绝，可以添加拒绝理由
  if (action === 'reject' && rejectionReason) {
    formData.append('rejection_reason', rejectionReason);
  }
  
  return api.post('/approval/handleTeamRequest', formData);
};

// 获取竞赛空间的问答区内容
export async function getDiscussions(spaceId) {
  const url = `/discussion/listAll/${spaceId}`;
  try {
    const response = await api.get(url);
    // 根据 axios 拦截器，这里直接返回 data 部分
    return response.data; 
  } catch (error) {
    console.error('获取竞赛空间问答区内容失败:', error);
    throw error;
  }
}


// 提交竞赛空间问题
export async function submitDiscussion(spaceId, data) {
  const formData = new FormData();
  
  // 添加竞赛空间ID
  formData.append('space_id', spaceId);
  
  // 添加问题内容
  if (data.content) formData.append('content', data.content);
  
  // 如果有图片，添加图片
  // 注意：Postman 示例中 images 是一个数组，但通常 formdata 中同名文件需要分别 append
  if (data.images && Array.isArray(data.images)) {
    data.images.forEach((imageFile) => {
      if (imageFile instanceof File) {
        formData.append('images', imageFile);
      }
    });
  }
  
  try {
    // 使用修正后的 URL 和 FormData
    const response = await api.post('/discussion/createQuestion', formData);
    // 拦截器会处理 .data，这里直接返回响应体
    return response; 
  } catch (error) {
    console.error('提交问题失败:', error);
    throw error;
  }
}


// 提交问题回复
export async function submitReply(data) {
  if (!data || !data.question_id || !data.content || !data.to_user_id) {
    console.error('提交回复参数不完整:', data);
    throw new Error('提交回复时缺少必需参数 (question_id, content, to_user_id)');
  }
  
  const formData = new FormData();
  
  // 添加必需参数
  formData.append('question_id', data.question_id);
  formData.append('content', data.content);
  formData.append('to_space_user_id', data.to_user_id); // 必须传递
  
  // 添加可选图片
  if (data.images && Array.isArray(data.images)) {
    data.images.forEach((imageFile) => {
      if (imageFile instanceof File) {
        formData.append('images', imageFile);
      }
    });
  }

  try {
    const response = await api.post('/discussion/createReply', formData);
    return response; // 返回拦截器处理后的响应
  } catch (error) {
    console.error('提交回复失败:', error);
    throw error;
  }
}

// 获取竞赛空间内用户信息
export async function getSpaceUserInfo(spaceId) {
  if (!spaceId) {
    throw new Error('获取空间用户信息时缺少 spaceId');
  }
  try {
    // 注意：API 路径通常是 /space/getUserInfo/{spaceId}
    // 但根据 Postman 集合，它可能是 /space/getUserInfo?space_id={spaceId} 或其他形式
    // 这里假设是路径参数形式，如果后端不同，需要调整
    const response = await api.get(`/space/getUserInfo/${spaceId}`);
    return response; // 拦截器已处理 .data
  } catch (error) {
    console.error('获取空间用户信息失败:', error);
    throw error;
  }
}

// 更新用户在特定竞赛空间的信息
export async function updateSpaceUserInfo(spaceId, userData) {
  if (!spaceId) {
    throw new Error('更新空间用户信息时缺少 spaceId');
  }
  const formData = new FormData();
  formData.append('space_id', spaceId);

  // 添加需要更新的用户信息 (根据 Postman 更新)
  if (userData.real_name !== undefined) formData.append('realName', userData.real_name); // Postman 使用 realName
  if (userData.student_id !== undefined) formData.append('studentId', userData.student_id); // Postman 使用 studentId
  if (userData.college_name !== undefined) formData.append('collegeName', userData.college_name); // Postman 使用 collegeName
  if (userData.gender !== undefined) formData.append('gender', userData.gender); // 新增：性别
  if (userData.phone !== undefined) formData.append('phoneNumber', userData.phone); // 新增：电话, Postman 使用 phoneNumber
  if (userData.email !== undefined) formData.append('email', userData.email); // 新增：邮箱

  // 检查是否有实际数据需要更新 (除了 space_id)
  let hasUpdates = false;
  for (const key of formData.keys()) {
    if (key !== 'space_id') {
      hasUpdates = true;
      break;
    }
  }

  if (!hasUpdates) {
    console.warn('没有提供需要更新的用户信息');
    return Promise.resolve({ code: 200, message: '无信息更新' });
  }

  try {
    const response = await api.post('/space/updateUser', formData);
    return response;
  } catch (error) {
    console.error('更新空间用户信息失败:', error);
    throw error;
  }
}

// 删除问题
export async function deleteQuestion(questionId) {
  // if (!questionId) {
  //   throw new Error('删除问题时缺少必需的 questionId');
  // }
  try {
    const response = await api.delete(`/discussion/deleteQuestion/${questionId}`);
    return response; 
  } catch (error) {
    console.error('删除问题失败:', error);
    throw error;
  }
}



// 删除回复
export async function deleteReply(replyId) {
  if (!replyId) {
    throw new Error('删除回复时缺少必需的 replyId');
  }
  try {
    const response = await api.delete(`/discussion/deleteReply/${replyId}`);
    return response; 
  } catch (error) {
    console.error('删除回复失败:', error);
    throw error;
  }
}



// 更新问题
export async function updateQuestion(questionId, data) {
  if (!questionId) {
    throw new Error('更新问题时缺少必需的 questionId');
  }
  
  const formData = new FormData();
  formData.append('question_id', questionId);
  
  // 添加问题内容 (可选更新)
  if (data.content !== undefined) formData.append('content', data.content);
  
  // 添加图片 (可选更新，会覆盖原有图片)
  if (data.images && Array.isArray(data.images)) {
    data.images.forEach((imageFile) => {
      if (imageFile instanceof File) {
        formData.append('images', imageFile);
      }
    });
  }
  // 如果用户想清空图片，可以传递一个空的 images 数组，这里会append 0 个文件

  try {
    const response = await api.post('/discussion/updateQuestion', formData);
    return response; 
  } catch (error) {
    console.error('更新问题失败:', error);
    throw error;
  }
}



// -- 队伍相关 API --

// 列出正在招募的队伍 (带筛选)
export async function listRecruitingTeams(spaceId, filters = {}) {
  // API 文档显示 filters 在 body 中，但实际通常 GET/POST 参数不同
  // Postman 是 POST，所以我们用 POST
  // 需要确认后端实际接收方式，这里按 Postman 实现
  const payload = {
    space_id: spaceId,
    ...filters // 合并筛选条件
  };
  //console.log(payload);
  // 移除空值过滤器，以允许后端使用默认值
  //Object.keys(payload).forEach(key => payload[key] === undefined || payload[key] === '' || payload[key] === null ? delete payload[key] : {});

  try {
    // 假设 API listRecruiting 需要 space_id, 即使 filters 里也有
    // 如果后端设计为 space_id 只在 filters 里，则移除第一个参数
    const response = await api.post('/team/listRecruiting', payload); 
    return response; // 假设返回 { data: [], message: '' }
  } catch (error) {
    console.error('获取招募队伍列表失败:', error);
    throw error;
  }
}



// 创建队伍
export async function createTeam(spaceId, teamData) {
  if (!spaceId || !teamData || !teamData.teamName) {
    throw new Error('创建队伍时缺少必需参数 (spaceId, teamName)');
  }
  const payload = {
    space_id: spaceId,
    teamName: teamData.teamName,
    demand: teamData.demand || '', // demand 是可选的
    targetNumber: teamData.targetNumber || 1 // 添加期望人数参数
  };
  try {
    const response = await api.post('/team/create', payload);
    return response;
  } catch (error) {
    console.error('创建队伍失败:', error);
    throw error;
  }
}



// 获取用户的队伍列表
export async function getUserTeams(created = false) {
  try {
    const url = created ? '/team/getUserTeams?created=1' : '/team/getUserTeams';
    const response = await api.get(url);
    return response;
  } catch (error) {
    console.error('获取用户队伍列表失败:', error);
    throw error;
  }
}



// 提交组队申请
export async function submitTeamRequest(teamId, requestDetail) {
   if (!teamId) {
    throw new Error('提交组队申请时缺少 teamId');
  }
  const formData = new FormData();
  formData.append('team_id', teamId);
  formData.append('request_detail', requestDetail || ''); // 申请详情可选
  console.log(formData);
  try {
    const response = await api.post('/approval/submitTeamRequest', formData);
    return response;
  } catch (error) {
    console.error('提交组队申请失败:', error);
    throw error;
  }
}



// 更新队伍信息
export async function updateTeam(teamId, teamData) {
  if (!teamId) {
    throw new Error('更新队伍信息时缺少 teamId');
  }
  const formData = new FormData();
  formData.append('team_id', teamId);
  
  if (teamData.teamName) formData.append('teamName', teamData.teamName);
  if (teamData.demand !== undefined) formData.append('demand', teamData.demand);
  //if (teamData.targetNumber!== undefined) formData.append('targetNumber', teamData.targetNumber);
  if (teamData.qq !== undefined) formData.append('qq', teamData.qq);
  
  try {
    const response = await api.post('/team/updateTeam', formData);
    return response;
  } catch (error) {
    console.error('更新队伍信息失败:', error);
    throw error;
  }
}



// 解散队伍
export async function dissolveTeam(teamId) {
  if (!teamId) {
    throw new Error('解散队伍时缺少 teamId');
  }
  try {
    const response = await api.delete(`/team/dissolve/${teamId}`);
    return response;
  } catch (error) {
    console.error('解散队伍失败:', error);
    throw error;
  }
}



// 移除队员
export async function removeTeamMember(teamId, spaceUserId) {
  if (!teamId || !spaceUserId) {
    throw new Error('移除队员时缺少必要参数');
  }
  const formData = new FormData();
  formData.append('team_id', teamId);
  formData.append('target_space_user_id', spaceUserId);
  
  try {
    const response = await api.post('/team/remove', formData);
    return response;
  } catch (error) {
    console.error('移除队员失败:', error);
    throw error;
  }
}



// 离开队伍
export async function leaveTeam(teamId) {
  if (!teamId) {
    throw new Error('离开队伍时缺少 teamId');
  }
  try {
    const response = await api.post(`/team/leave/${teamId}`);
    return response;
  } catch (error) {
    console.error('离开队伍失败:', error);
    throw error;
  }
}



// 锁定/解锁队伍
export async function lockTeam(teamId, isLocked) {
  if (!teamId) {
    throw new Error('锁定/解锁队伍时缺少 teamId');
  }
  try {
    const response = await api.post('/team/lock', {
      team_id: teamId,
      lock: isLocked
    });
    return response;
  } catch (error) {
    console.error('锁定/解锁队伍失败:', error);
    throw error;
  }
}



// 设置队伍招募状态
export async function setTeamRecruitment(teamId, isRecruiting) {
  if (!teamId) {
    throw new Error('设置队伍招募状态时缺少 teamId');
  }
  try {
    const response = await api.post('/team/recruit', {
      team_id: teamId,
      recruit: isRecruiting
    });
    return response;
  } catch (error) {
    console.error('设置队伍招募状态失败:', error);
    throw error;
  }
}



// 创建竞赛空间
export const createSpace = (formData) => {
  // 确保formData是FormData类型
  if (!(formData instanceof FormData)) {
    throw new Error('创建竞赛空间参数必须是FormData类型');
  }
  
  try {
    return api.post('/space/create', formData);
  } catch (error) {
    console.error('创建竞赛空间失败:', error);
    throw error;
  }
}


// 获取竞赛空间信息
export const getSpaceInfo = (spaceId) => {
  if (!spaceId) {
    throw new Error('获取竞赛空间信息时缺少必需的 spaceId');
  }
  try {
    return api.get(`/space/getSpaceInfo/${spaceId}`);
  } catch (error) {
    console.error('获取竞赛空间信息失败:', error);
    throw error;
  }
}

// 获取竞赛空间成员列表
export const getSpaceMembers = (spaceId) => {
  if (!spaceId) {
    throw new Error('获取竞赛空间成员列表时缺少必需的 spaceId');
  }
  try {
    return api.get(`/space/listSpaceUsers/${spaceId}`);
  } catch (error) {
    console.error('获取竞赛空间成员列表失败:', error);
    throw error;
  }
}

// 更新竞赛空间信息
export const updateSpace = (formData) => {
  if (!(formData instanceof FormData)) {
    throw new Error('更新竞赛空间信息参数必须是FormData类型');
  }
  
  if (!formData.get('space_id')) {
    throw new Error('更新竞赛空间信息时缺少必需的 space_id');
  }
  
  try {
    return api.post('/space/updateSpace', formData);
  } catch (error) {
    console.error('更新竞赛空间信息失败:', error);
    throw error;
  }
}

export const closeSpace = (spaceId) => {
  try {
    return api.post(`/space/close/${spaceId}`);
  } catch (error) {
    console.error('更新竞赛空间信息失败:', error);
    throw error;
  }
}

// 移除竞赛空间成员
export const removeSpaceMember = (spaceId, spaceUserId) => {
  if (!spaceId || !spaceUserId) {
    throw new Error('移除竞赛空间成员时缺少必需参数 (spaceId, spaceUserId)'); 
  }
  
  const formData = new FormData();
  formData.append('space_id', spaceId);
  formData.append('target_user_id', spaceUserId);
  
  try {
    return api.post('/space/removeUser', formData);
  } catch (error) {
    console.error('移除竞赛空间成员失败:', error);
    throw error;
  }
};


// 获取竞赛空间文件列表 (假设端点)
export const listCompetitionFiles = (spaceId) => {
  if (!spaceId) {
    throw new Error('获取竞赛空间文件列表时缺少必需的 spaceId');
  }
  try {
    // 假设后端提供了一个按 spaceId 列出文件的端点
    return api.get(`/files/get/${spaceId}`); 
  } catch (error) {
    console.error('获取竞赛空间文件列表失败:', error);
    throw error;
  }
};

// 上传竞赛空间文件 (使用 Postman 中的端点，但需确认是否需要 spaceId)
export const uploadCompetitionFile = (spaceId, file) => {
  if (!spaceId || !file) {
    throw new Error('上传文件时缺少必需参数 (spaceId, file)');
  }
  const formData = new FormData();
  formData.append('space_id', spaceId); // 假设需要 space_id
  formData.append('file', file); // Postman 中 key 是 'file'

  try {
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  } catch (error) {
    console.error('上传竞赛空间文件失败:', error);
    throw error;
  }
};

// 下载竞赛空间文件 (使用 Postman 中的端点)
export const downloadCompetitionFile = (fileId) => {
  if (!fileId) {
    throw new Error('下载文件时缺少必需的 fileId');
  }
  try {
    // 注意：下载通常需要设置 responseType 为 'blob' 或 'arraybuffer'
    // 并且需要手动处理下载链接的创建
    // 这里仅返回 Axios Promise，具体处理在组件中进行
    return api.get(`/files/download/${fileId}`, {
      responseType: 'blob' // 重要：设置响应类型以便处理文件下载
    });
  } catch (error) {
    console.error('下载竞赛空间文件失败:', error);
    throw error;
  }
};

// 删除竞赛空间文件 (假设端点，仅管理员)
export const deleteCompetitionFile = (fileId) => {
  if (!fileId) {
    throw new Error('删除文件时缺少必需的 fileId');
  }
  try {
    // 假设后端提供了一个删除文件的端点
    return api.delete(`/files/delete/${fileId}`); 
  } catch (error) {
    console.error('删除竞赛空间文件失败:', error);
    throw error;
  }
};

// 公告相关API

// 创建公告
export const createAnnouncement = (data) => {
  if (!data || !data.space_id || !data.title || !data.content) {
    throw new Error('创建公告时缺少必需参数 (space_id, title, content)');
  }
  try {
    return api.post('/announcement/create', data);
  } catch (error) {
    console.error('创建公告失败:', error);
    throw error;
  }
};

// 更新公告
export const updateAnnouncement = (data) => {
  if (!data || !data.announcement_id || !data.title || !data.content) {
    throw new Error('更新公告时缺少必需参数 (announcement_id, title, content)');
  }
  try {
    return api.put('/announcement/update', data);
  } catch (error) {
    console.error('更新公告失败:', error);
    throw error;
  }
};

// 删除公告
export const deleteAnnouncement = (announcementId) => {
  if (!announcementId) {
    throw new Error('删除公告时缺少必需的 announcementId');
  }
  try {
    return api.delete(`/announcement/delete/${announcementId}`);
  } catch (error) {
    console.error('删除公告失败:', error);
    throw error;
  }
};

// 通过ID获取公告详情
export const getAnnouncementById = (announcementId) => {
  if (!announcementId) {
    throw new Error('获取公告详情时缺少必需的 announcementId');
  }
  try {
    return api.get(`/announcement/getById/${announcementId}`);
  } catch (error) {
    console.error('获取公告详情失败:', error);
    throw error;
  }
};

// 获取竞赛空间的所有公告
export const getSpaceAnnouncements = () => {
  try {
    return api.get('/announcement/getAll');
  } catch (error) {
    console.error('获取竞赛空间公告失败:', error);
    throw error;
  }
};

// 获取未读公告
export const getUnreadAnnouncements = () => {
  try {
    return api.get('/announcement/getUnread');
  } catch (error) {
    console.error('获取未读公告失败:', error);
    throw error;
  }
};

// 标记公告为已读
export const markAnnouncementAsRead = (announcementId) => {
  if (!announcementId) {
    throw new Error('标记公告已读时缺少必需的 announcementId');
  }
  try {
    return api.post(`/announcement/markRead/${announcementId}`);
  } catch (error) {
    console.error('标记公告已读失败:', error);
    throw error;
  }
};


export default api;

// 创建一个全局配置，用于处理ResizeObserver错误
const originalConsoleError = console.error;
console.error = function(message) {
  if (message && message.toString().includes('ResizeObserver loop')) {
    // 忽略ResizeObserver循环错误
    return;
  }
  originalConsoleError.apply(console, arguments);
};


// 导出竞赛空间的组队信息
export const exportTeamInfo = (spaceId, options = {}) => {
  if (!spaceId) {
    throw new Error('导出组队信息时缺少必需的 spaceId');
  }
  try {
    // 设置响应类型为blob以处理文件下载
    return api.post(`/files/export/${spaceId}`, options, {
      responseType: 'blob' // 重要：设置响应类型以便处理文件下载
    });
  } catch (error) {
    console.error('导出组队信息失败:', error);
    throw error;
  }
};