<template>
  <el-dialog
    v-model="visible"
    title="用户注册"
    width="500px"
    :before-close="handleClose"
    center
  >
    <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="100px">
      <el-form-item label="手机号码" prop="phone">
        <el-input 
          v-model="registerForm.phone" 
          placeholder="请输入手机号码" 
          maxlength="11"
        />
      </el-form-item>
      <el-form-item label="昵称" prop="username">
        <el-input 
          v-model="registerForm.username" 
          placeholder="请输入昵称" 
        />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input 
          v-model="registerForm.password" 
          type="password" 
          placeholder="请输入密码" 
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm_password">
        <el-input 
          v-model="registerForm.confirm_password" 
          type="password" 
          placeholder="请再次输入密码" 
          show-password
        />
      </el-form-item>
      <el-form-item label="所在学校" prop="school_id">
        <el-select 
          v-model="registerForm.school_id" 
          placeholder="请选择学校"
          filterable
          :loading="loadingSchools"
        >
          <el-option
            v-for="item in schoolOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <div class="register-actions">
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleRegister" :loading="loading">注册</el-button>
    </div>
    <div class="login-link">
      已有账号？<el-link type="primary" @click="goToLogin">返回登录</el-link>
    </div>
  </el-dialog>
</template>

<script>
import { getSchoolList, register } from '../../utils/api';

export default {
  name: 'RegisterModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    // 密码一致性验证
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    };
    
    return {
      loading: false,
      loadingSchools: false,
      registerForm: {
        phone: '',
        password: '',
        confirm_password: '',
        username: '',
        school_id: null
      },
      schoolOptions: [],
      rules: {
        phone: [
          { required: true, message: '请输入手机号码', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        username: [
          { required: true, message: '请输入昵称', trigger: 'blur' },
          { min: 2, max: 20, message: '昵称长度在2到20个字符之间', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validatePass, trigger: 'blur' }
        ],
        school_id: [
          { required: true, message: '请选择学校', trigger: 'change' }
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
      this.$refs.registerFormRef?.resetFields();
      this.visible = false;
    },
    goToLogin() {
      this.handleClose();
      this.$emit('go-login');
    },
    async fetchSchools() {
      if (this.schoolOptions.length > 0) return;
      
      try {
        this.loadingSchools = true;
        const response = await getSchoolList();
        if (response && response.data) {
          this.schoolOptions = response.data.map(school => ({
            label: school.name,
            value: school.id
          }));
        }
      } catch (error) {
        console.error('获取学校列表失败:', error);
        this.$message.error('获取学校列表失败，请稍后再试');
      } finally {
        this.loadingSchools = false;
      }
    },
    async handleRegister() {
      if (!this.$refs.registerFormRef) return;
      
      await this.$refs.registerFormRef.validate(async (valid) => {
        if (valid) {
          this.loading = true;
          try {
            const response = await register(this.registerForm);
            
            if (response && response.data) {
              this.$message.success(response.message || '注册成功，请登录');
              this.handleClose();
              this.$emit('register-success');
            }
          } catch (error) {
            console.error('注册失败:', error);
            const errorMsg = error.message || '注册失败，请稍后再试';
            this.$message.error(errorMsg);
          } finally {
            this.loading = false;
          }
        }
      });
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.fetchSchools();
      }
    }
  }
};
</script>

<style scoped>
.register-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.login-link {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}
</style> 