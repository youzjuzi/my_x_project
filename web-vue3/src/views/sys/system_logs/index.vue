<template>
  <div class="log-container">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="queryParams" class="demo-form-inline">
        <el-form-item label="操作模块">
          <el-select v-model="queryParams.module" placeholder="全部模块" clearable style="width: 140px">
            <el-option label="用户管理" value="user" />
            <el-option label="题库管理" value="question" />
            <el-option label="识别系统" value="ai" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作时间">
          <el-date-picker
            v-model="queryParams.dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleSearch">查询</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="table-card">
      <el-table :data="logList" style="width: 100%" v-loading="loading">

        <el-table-column prop="id" label="ID" width="80" />

        <el-table-column prop="module" label="功能模块" width="150">
          <template #default="scope">
            <el-tag :type="getModuleTag(scope.row.module).type" effect="light" round>
              <el-icon class="mr-1"><component :is="getModuleTag(scope.row.module).icon" /></el-icon>
              {{ scope.row.moduleName }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="action" label="操作类型" width="120">
          <template #default="scope">
            <span style="font-weight: 600">{{ scope.row.action }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="operator" label="操作人员" width="120">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="24" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span>{{ scope.row.operator }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="ip" label="IP地址" width="140" show-overflow-tooltip />

        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <div class="status-dot" :class="scope.row.status === 1 ? 'success' : 'error'">
              <span class="dot"></span>
              <span>{{ scope.row.status === 1 ? '成功' : '失败' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="操作时间" width="180" />

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="viewDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination background layout="prev, pager, next" :total="100" />
      </div>
    </el-card>

    <el-drawer v-model="drawerVisible" title="日志详情" size="40%">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="请求路径">/api/question/add</el-descriptions-item>
        <el-descriptions-item label="请求方式">POST</el-descriptions-item>
        <el-descriptions-item label="操作方法">com.example.controller.QuestionController.add()</el-descriptions-item>
        <el-descriptions-item label="请求参数">
          <code class="json-code">
            { "content": "Hello", "type": "English" }
          </code>
        </el-descriptions-item>
        <el-descriptions-item label="异常信息" v-if="currentDetail.status === 0">
          <span class="error-text">NullPointerException at line 45...</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, Refresh, User, List, VideoCamera } from '@element-plus/icons-vue'

const loading = ref(false)
const drawerVisible = ref(false)
const currentDetail = ref({})
const queryParams = ref({
  module: '',
  dateRange: []
})

// 模拟数据
const logList = ref([
  { id: 101, module: 'ai', moduleName: '识别系统', action: '开启摄像头', operator: 'User_Admin', ip: '192.168.1.10', status: 1, createTime: '2025-11-29 10:00:00' },
  { id: 102, module: 'question', moduleName: '题库管理', action: '新增题目', operator: 'User_Admin', ip: '192.168.1.10', status: 1, createTime: '2025-11-29 10:05:23' },
  { id: 103, module: 'user', moduleName: '用户管理', action: '重置密码', operator: 'SuperAdmin', ip: '127.0.0.1', status: 0, createTime: '2025-11-29 10:15:00' },
  { id: 104, module: 'ai', moduleName: '识别系统', action: '模型加载', operator: 'System', ip: 'Localhost', status: 1, createTime: '2025-11-29 09:00:00' },
])

// 辅助函数：根据模块返回 Tag 样式
const getModuleTag = (module) => {
  const map = {
    user: { type: 'info', icon: 'User' },
    question: { type: 'warning', icon: 'List' },
    ai: { type: 'success', icon: 'VideoCamera' } // 紫色/AI 相关
  }
  return map[module] || { type: 'info', icon: 'List' }
}

const handleSearch = () => { console.log('Searching...') }
const resetQuery = () => { queryParams.value = {} }
const viewDetail = (row) => {
  currentDetail.value = row
  drawerVisible.value = true
}
</script>

<style scoped lang="scss">
.log-container {
  padding: 20px;
  background-color: #f5f7fa; /* 保持你的全局灰底 */
  min-height: calc(100vh - 84px);
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: none;
}

.table-card {
  border-radius: 8px;
  border: none;
}

.mr-1 { margin-right: 4px; }

/* 用户头像行 */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 状态指示点 */
.status-dot {
  display: flex;
  align-items: center;
  gap: 6px;

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  &.success { color: #67C23A; .dot { background: #67C23A; } }
  &.error { color: #F56C6C; .dot { background: #F56C6C; } }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* JSON 代码块样式 */
.json-code {
  background: #2d2d2d;
  color: #ccc;
  padding: 10px
}
</style>