<template>
  <el-card class="search-card" shadow="hover">
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户">
          <el-select
            v-model="searchForm.userId"
            placeholder="请选择用户"
            clearable
            filterable
            style="width: 200px"
            :loading="userListLoading"
            @keyup.enter="handleSearch"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="`${user.username} (ID: ${user.id})`"
              :value="user.id"
            >
              <div class="user-option">
                <span>{{ user.username }}</span>
                <el-text type="info" size="small" style="margin-left: 8px">
                  ID: {{ user.id }}
                </el-text>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="挑战模式">
          <el-select
            v-model="searchForm.mode"
            placeholder="请选择模式"
            clearable
            style="width: 150px"
          >
            <el-option label="随机挑战" value="random" />
            <el-option label="题库挑战" value="questionSet" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="进行中" :value="0" />
            <el-option label="已完成" :value="1" />
            <el-option label="已放弃" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            查询
          </el-button>
          <el-button :icon="RefreshRight" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, watch, ref, onMounted } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getUsersWithChallenges } from '@/api/challenge'

const props = defineProps<{
  modelValue: {
    userId?: number | null
    mode?: string | null
    status?: number | null
  }
}>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
  'search': []
  'reset': []
}>()

const searchForm = reactive({
  userId: props.modelValue?.userId || null,
  mode: props.modelValue?.mode || null,
  status: props.modelValue?.status !== undefined ? props.modelValue.status : null
})

// 用户列表
const userList = ref<any[]>([])
const userListLoading = ref(false)

// 加载用户列表
const loadUserList = async () => {
  userListLoading.value = true
  try {
    const res = await getUsersWithChallenges()
    if (res.data) {
      userList.value = res.data
    }
  } catch (error) {
    console.error('获取用户列表失败', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    userListLoading.value = false
  }
}

onMounted(() => {
  loadUserList()
})

// 监听 props 变化，同步到 searchForm
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    searchForm.userId = newVal.userId !== undefined && newVal.userId !== null ? newVal.userId : null
    searchForm.mode = newVal.mode !== undefined && newVal.mode !== null && newVal.mode !== '' ? newVal.mode : null
    searchForm.status = newVal.status !== undefined && newVal.status !== null ? newVal.status : null
  } else {
    // 如果 newVal 为 null 或 undefined，清空表单
    searchForm.userId = null
    searchForm.mode = null
    searchForm.status = null
  }
}, { deep: true })

const handleSearch = () => {
  emit('update:modelValue', { ...searchForm })
  emit('search')
}

const handleReset = () => {
  searchForm.userId = null
  searchForm.mode = null
  searchForm.status = null
  emit('update:modelValue', { userId: null, mode: null, status: null })
  emit('reset')
}
</script>

<style scoped lang="scss">
.search-card {
  margin-bottom: 20px;
  
  .search-bar {
    .search-form {
      margin: 0;
    }
  }
}

.user-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>

