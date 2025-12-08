import { reactive } from 'vue';
import { login, logout, getUserInfo } from '../utils/api';

// 创建响应式状态对象
const userState = reactive({
  token: localStorage.getItem('token') || '',
  userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
  isLoggedIn: !!localStorage.getItem('token')
});

// 用户相关操作方法
const userActions = {
  // 登录
  async login(phone, password) {
    try {
      const response = await login(phone, password);
      if (response && response.data) {
        // response.data 包含JWT token
        userState.token = response.data;
        localStorage.setItem('token', response.data);
        
        // 获取用户信息
        await userActions.fetchUserInfo();
        return {
          success: true,
          message: response.message || '登录成功！'
        };
      }
      return {
        success: false,
        message: response.message || '登录失败，请检查账号密码'
      };
    } catch (error) {
      console.error('登录失败:', error);
      return {
        success: false,
        message: error.message || '登录失败，请稍后再试'
      };
    }
  },
  
  // 登出
  async logout() {
    try {
      if (userState.token) {
        await logout();
      }
      userActions.clearUserState();
      return true;
    } catch (error) {
      console.error('登出失败:', error);
      return false;
    }
  },
  
  // 获取用户信息
  async fetchUserInfo() {
    try {
      if (!userState.token) return false;
      
      const response = await getUserInfo();
      if (response && response.data) {
        userState.userInfo = response.data;
        userState.isLoggedIn = true;
        localStorage.setItem('userInfo', JSON.stringify(response.data));
        return true;
      }
      return false;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      return false;
    }
  },
  
  // 清除用户状态
  clearUserState() {
    userState.token = '';
    userState.userInfo = {};
    userState.isLoggedIn = false;
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
  },
  
  // 更新用户信息
  updateUserInfo(newUserInfo) {
    userState.userInfo = { ...userState.userInfo, ...newUserInfo };
    localStorage.setItem('userInfo', JSON.stringify(userState.userInfo));
  },
  
  // 设置模拟登录（开发测试用）
  setMockLogin(userData) {
    userState.token = userData.token;
    userState.userInfo = userData.userInfo;
    userState.isLoggedIn = true;
    localStorage.setItem('token', userData.token);
    localStorage.setItem('userInfo', JSON.stringify(userData.userInfo));
  }
};

export { userState, userActions }; 