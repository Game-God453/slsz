<template>
  <el-dialog
    v-model="visible"
    title="用户登录"
    width="400px"
    :before-close="handleClose"
    center
  >
    <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
      <el-form-item label="手机号码" prop="phone">
        <el-input 
          v-model="loginForm.phone" 
          placeholder="请输入手机号码" 
          maxlength="11"
        />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input 
          v-model="loginForm.password" 
          type="password" 
          placeholder="请输入密码" 
          show-password
        />
      </el-form-item>
    </el-form>
    <div class="login-actions">
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
    </div>
    <div class="register-link">
      还没有账号？<el-link type="primary" @click="goToRegister">立即注册</el-link>
    </div>
  </el-dialog>
</template>

<script>
import { userActions } from '../../store/user';

export default {
  name: 'LoginModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: false,
      loginForm: {
        phone: '',
        password: ''
      },
      rules: {
        phone: [
          { required: true, message: '请输入手机号码', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
        ]
      }
    };
  },
  computed: {
    visible: {
      get() {
        return this.show;
      },
      set(value) {
        this.$emit('update:show', value);
      }
    }
  },
  methods: {
    handleClose() {
      this.$refs.loginFormRef?.resetFields();
      this.visible = false;
    },
    async handleLogin() {
      if (!this.$refs.loginFormRef) return;
      
      await this.$refs.loginFormRef.validate(async (valid) => {
        if (valid) {
          try {
            this.loading = true;
            
            // 调用登录API
            const result = await userActions.login(
              this.loginForm.phone,
              this.loginForm.password
            );
            
            if (result.success) {
              this.$emit('login-success');
              this.$message.success(result.message);
              this.handleClose();
            } else {
              this.$message.error(result.message);
            }
          } catch (error) {
            console.error('登录失败:', error);
            this.$message.error('登录失败: ' + (error.message || '未知错误'));
          } finally {
            this.loading = false;
          }
        }
      });
    },
    goToRegister() {
      // 关闭登录弹窗，发出注册事件
      this.handleClose();
      this.$emit('go-register');
    }
  }
};
</script>

<style scoped>
.login-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.register-link {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}
</style> 