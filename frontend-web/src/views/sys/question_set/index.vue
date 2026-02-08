<template>
  <div class="question-set-page">
    <el-card class="search-card" shadow="hover">
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="题库名称">
            <el-input
              v-model="searchForm.name"
              placeholder="输入题库名称"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="请选择状态"
              clearable
              style="width: 150px"
            >
              <el-option label="启用" :value="1" />
              <el-option label="禁用" :value="0" />
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
        <div class="actions">
          <el-button type="primary" :icon="Plus" @click="openCreateDialog">
            新增题库
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="hover">
      <div class="table-toolbar">
        <div class="table-title">题库列表</div>
        <div class="table-subtitle">共 {{ total }} 个题库</div>
      </div>
      <el-table :data="tableData" v-loading="loading" border>
        <el-table-column type="index" width="70" align="center" label="#" />
        <el-table-column prop="id" label="题库ID" width="100" align="center" />
        <el-table-column prop="name" label="题库名称" min-width="180" />
        <el-table-column prop="description" label="题库描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.description || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="cover" label="封面" width="120" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.cover"
              :src="row.cover"
              :preview-src-list="[row.cover]"
              fit="cover"
              style="width: 80px; height: 80px; border-radius: 4px"
              :preview-teleported="true"
            />
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              :loading="statusLoadingId === row.id"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-links">
              <span class="action-link manage-link" @click="handleManageQuestions(row)">管理题目</span>
              <el-divider direction="vertical" />
              <span class="action-link view-link" @click="handleView(row)">查看</span>
              <el-divider direction="vertical" />
              <span class="action-link edit-link" @click="handleEdit(row)">编辑</span>
              <el-divider direction="vertical" />
              <el-popconfirm
                title="确认要删除该题库吗？"
                :confirm-button-text="'删除'"
                :cancel-button-text="'取消'"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <span
                    class="action-link delete-link"
                    :class="{ 'is-loading': deleteLoadingId === row.id }"
                  >
                    {{ deleteLoadingId === row.id ? '删除中...' : '删除' }}
                  </span>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增题库对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新增题库"
      width="600px"
      destroy-on-close
      @closed="resetCreateForm"
    >
      <el-form :model="createForm" :rules="formRules" ref="createFormRef" label-width="100px">
        <el-form-item label="题库名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入题库名称" />
        </el-form-item>
        <el-form-item label="题库描述">
          <el-input
            v-model="createForm.description"
            placeholder="请输入题库描述"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="封面图片">
          <el-input v-model="createForm.cover" placeholder="请输入封面图片URL" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="createForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="createSubmitting" @click="handleCreateSubmit">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑题库对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑题库"
      width="600px"
      destroy-on-close
      @closed="resetEditForm"
    >
      <el-form :model="editForm" :rules="formRules" ref="editFormRef" label-width="100px">
        <el-form-item label="题库ID">
          <el-input v-model="editForm.id" disabled />
        </el-form-item>
        <el-form-item label="题库名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入题库名称" />
        </el-form-item>
        <el-form-item label="题库描述">
          <el-input
            v-model="editForm.description"
            placeholder="请输入题库描述"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="封面图片">
          <el-input v-model="editForm.cover" placeholder="请输入封面图片URL" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="editSubmitting" @click="handleEditSubmit">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看题库详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="题库详情"
      width="600px"
      destroy-on-close
    >
      <div v-if="viewData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="题库ID">{{ viewData.id }}</el-descriptions-item>
          <el-descriptions-item label="题库名称">{{ viewData.name }}</el-descriptions-item>
          <el-descriptions-item label="题库描述">
            {{ viewData.description || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="封面图片">
            <el-image
              v-if="viewData.cover"
              :src="viewData.cover"
              :preview-src-list="[viewData.cover]"
              fit="cover"
              style="width: 200px; height: 200px; border-radius: 4px"
              :preview-teleported="true"
            />
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="viewData.status === 1 ? 'success' : 'danger'">
              {{ viewData.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 管理题目对话框 -->
    <el-dialog
      v-model="manageQuestionsDialogVisible"
      title="管理题目"
      width="900px"
      destroy-on-close
      @closed="resetManageQuestions"
    >
      <div v-if="currentQuestionSet">
        <div class="question-set-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="题库ID">{{ currentQuestionSet.id }}</el-descriptions-item>
            <el-descriptions-item label="题库名称">{{ currentQuestionSet.name }}</el-descriptions-item>
            <el-descriptions-item label="题目数量" :span="2">
              <el-tag type="info">{{ currentQuestionIds.length }} 道题目</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <el-divider />

        <div class="manage-questions-content">
          <div class="section-header">
            <span class="section-title">当前题库题目</span>
            <el-button
              type="primary"
              size="small"
              :icon="Plus"
              @click="openAddQuestionDialog"
            >
              添加题目
            </el-button>
          </div>

          <el-table
            :data="currentQuestionList"
            v-loading="questionsLoading"
            border
            max-height="400"
            style="margin-top: 12px"
          >
            <el-table-column type="index" width="60" align="center" label="#" />
            <el-table-column prop="content" label="题目内容" min-width="180">
              <template #default="{ row }">
                <div class="content-cell-dict">
                  <div class="content-main">{{ row.content }}</div>
                  <div v-if="row.pinyin" class="content-pinyin">
                    {{ formatPinyin(row.pinyin) }}
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getTypeTagType(row.type)" size="small">
                  {{ getTypeText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="difficulty" label="难度" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getDifficultyTagType(row.difficulty)" size="small">
                  {{ getDifficultyText(row.difficulty) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-popconfirm
                  title="确认要从题库中移除该题目吗？"
                  :confirm-button-text="'移除'"
                  :cancel-button-text="'取消'"
                  @confirm="handleRemoveQuestion(row.id)"
                >
                  <template #reference>
                    <span class="action-link delete-link">移除</span>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="manageQuestionsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加题目对话框 -->
    <el-dialog
      v-model="addQuestionDialogVisible"
      title="添加题目到题库"
      width="800px"
      destroy-on-close
      @closed="resetAddQuestion"
    >
      <div class="add-question-content">
        <el-form :inline="true" :model="questionSearchForm" class="search-form">
          <el-form-item label="题目内容">
            <el-input
              v-model="questionSearchForm.content"
              placeholder="输入题目内容"
              clearable
              @keyup.enter="handleQuestionSearch"
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="类型">
            <el-select
              v-model="questionSearchForm.type"
              placeholder="请选择类型"
              clearable
              style="width: 120px"
            >
              <el-option label="单词" :value="1" />
              <el-option label="中文" :value="2" />
              <el-option label="数字" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleQuestionSearch">查询</el-button>
            <el-button :icon="RefreshRight" @click="handleQuestionReset">重置</el-button>
          </el-form-item>
        </el-form>

        <el-table
          ref="addQuestionTableRef"
          :data="allQuestionList"
          v-loading="allQuestionsLoading"
          border
          max-height="400"
          @selection-change="handleQuestionSelectionChange"
        >
          <el-table-column
            type="selection"
            width="55"
            align="center"
            :selectable="(row: QuestionItem) => !currentQuestionIds.includes(row.id)"
          />
          <el-table-column type="index" width="60" align="center" label="#" />
          <el-table-column prop="content" label="题目内容" min-width="180">
            <template #default="{ row }">
              <div class="content-cell-dict">
                <div class="content-main">{{ row.content }}</div>
                <div v-if="row.pinyin" class="content-pinyin">
                  {{ formatPinyin(row.pinyin) }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.type)" size="small">
                {{ getTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getDifficultyTagType(row.difficulty)" size="small">
                {{ getDifficultyText(row.difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="currentQuestionIds.includes(row.id)" type="success" size="small">
                已在题库
              </el-tag>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper" style="margin-top: 16px">
          <el-pagination
            v-model:current-page="questionCurrentPage"
            v-model:page-size="questionPageSize"
            :page-sizes="[10, 20, 50]"
            :total="questionTotal"
            layout="total, sizes, prev, pager, next"
            background
            @size-change="handleQuestionSizeChange"
            @current-change="handleQuestionCurrentChange"
          />
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addQuestionDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="addQuestionSubmitting"
            @click="handleAddQuestions"
          >
            添加选中题目 ({{ selectedQuestions.length }})
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'questionSet' // ⚠️ 必须与路由 name 完全一致！
})

import { RefreshRight, Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { reactive, ref, onMounted, nextTick } from 'vue'
import questionSetManageApi from '@/api/questionSetManage'
import questionBankManageApi from '@/api/questionBankManage'

interface QuestionSetItem {
  id: number
  name: string
  description: string | null
  cover: string | null
  status: number
}

const loading = ref(false)
const tableData = ref<QuestionSetItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchForm = reactive({
  name: '',
  status: undefined as number | undefined
})

const createDialogVisible = ref(false)
const createSubmitting = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive({
  name: '',
  description: '',
  cover: '',
  status: 1
})

const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  id: 0,
  name: '',
  description: '',
  cover: '',
  status: 1
})

const viewDialogVisible = ref(false)
const viewData = ref<QuestionSetItem | null>(null)

const deleteLoadingId = ref<number | null>(null)
const statusLoadingId = ref<number | null>(null)

// 管理题目相关
const manageQuestionsDialogVisible = ref(false)
const currentQuestionSet = ref<QuestionSetItem | null>(null)
const currentQuestionIds = ref<number[]>([])
const currentQuestionList = ref<any[]>([])
const questionsLoading = ref(false)

// 添加题目相关
const addQuestionDialogVisible = ref(false)
const addQuestionTableRef = ref()
const allQuestionList = ref<any[]>([])
const allQuestionsLoading = ref(false)
const selectedQuestions = ref<any[]>([])
const questionSearchForm = reactive({
  content: '',
  type: undefined as number | undefined
})
const questionCurrentPage = ref(1)
const questionPageSize = ref(20)
const questionTotal = ref(0)
const addQuestionSubmitting = ref(false)

interface QuestionItem {
  id: number
  content: string
  type: number
  difficulty: number
  pinyin?: string
  levelGroup?: string | number
  level_group?: string | number
  imgUrl?: string
  img_url?: string
  status: number
}

// 表单验证规则
const formRules: FormRules = {
  name: [{ required: true, message: '请输入题库名称', trigger: 'blur' }]
}

// 获取题库列表
const fetchQuestionSetList = async () => {
  loading.value = true
  try {
    const res = await questionSetManageApi.getQuestionSetList({
      pageNo: currentPage.value,
      pageSize: pageSize.value,
      name: searchForm.name.trim() || undefined,
      status: searchForm.status
    })
    const data = res.data || { total: 0, rows: [] }
    const rows = Array.isArray(data.rows) ? data.rows : []
    // 确保每个题库都有 status 字段，默认为 1（启用）
    tableData.value = rows.map((item: QuestionSetItem) => ({
      ...item,
      status: item.status !== undefined ? item.status : 1
    }))
    total.value = Number(data.total) || 0
  } catch (error) {
    console.error('获取题库列表失败', error)
    ElMessage.error('获取题库列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchQuestionSetList()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.status = undefined
  currentPage.value = 1
  fetchQuestionSetList()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchQuestionSetList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchQuestionSetList()
}

const openCreateDialog = () => {
  createDialogVisible.value = true
}

const resetCreateForm = () => {
  createForm.name = ''
  createForm.description = ''
  createForm.cover = ''
  createForm.status = 1
  createFormRef.value?.resetFields()
}

const handleCreateSubmit = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      createSubmitting.value = true
      try {
        const data: any = {
          name: createForm.name.trim(),
          status: createForm.status
        }
        if (createForm.description) {
          data.description = createForm.description.trim()
        }
        if (createForm.cover) {
          data.cover = createForm.cover.trim()
        }
        await questionSetManageApi.addQuestionSet(data)
        ElMessage.success('新增题库成功')
        createDialogVisible.value = false
        resetCreateForm()
        fetchQuestionSetList()
      } catch (error) {
        console.error('新增题库失败', error)
        ElMessage.error('新增题库失败，请稍后重试')
      } finally {
        createSubmitting.value = false
      }
    }
  })
}

const handleEdit = async (row: QuestionSetItem) => {
  try {
    const res = await questionSetManageApi.getQuestionSetById(row.id)
    const data = res.data || {}
    editForm.id = data.id
    editForm.name = data.name || ''
    editForm.description = data.description || ''
    editForm.cover = data.cover || ''
    editForm.status = data.status !== undefined ? data.status : 1
    editDialogVisible.value = true
  } catch (error) {
    console.error('获取题库详情失败', error)
    ElMessage.error('获取题库详情失败，请稍后重试')
  }
}

const resetEditForm = () => {
  editForm.id = 0
  editForm.name = ''
  editForm.description = ''
  editForm.cover = ''
  editForm.status = 1
  editFormRef.value?.resetFields()
}

const handleEditSubmit = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      editSubmitting.value = true
      try {
        const data: any = {
          id: editForm.id,
          name: editForm.name.trim(),
          status: editForm.status
        }
        if (editForm.description) {
          data.description = editForm.description.trim()
        }
        if (editForm.cover) {
          data.cover = editForm.cover.trim()
        }
        await questionSetManageApi.updateQuestionSet(data)
        ElMessage.success('修改题库成功')
        editDialogVisible.value = false
        resetEditForm()
        fetchQuestionSetList()
      } catch (error) {
        console.error('修改题库失败', error)
        ElMessage.error('修改题库失败，请稍后重试')
      } finally {
        editSubmitting.value = false
      }
    }
  })
}

const handleView = async (row: QuestionSetItem) => {
  try {
    const res = await questionSetManageApi.getQuestionSetById(row.id)
    viewData.value = res.data || null
    viewDialogVisible.value = true
  } catch (error) {
    console.error('获取题库详情失败', error)
    ElMessage.error('获取题库详情失败，请稍后重试')
  }
}

const handleDelete = async (row: QuestionSetItem) => {
  deleteLoadingId.value = row.id
  try {
    await questionSetManageApi.deleteQuestionSet(row.id)
    ElMessage.success('删除题库成功')
    fetchQuestionSetList()
  } catch (error: any) {
    console.error('删除题库失败', error)
    const errorMessage = error?.response?.data?.message || error?.message || '删除题库失败，请稍后重试'
    ElMessage.error(errorMessage)
  } finally {
    deleteLoadingId.value = null
  }
}

// 处理状态切换
const handleStatusChange = async (row: QuestionSetItem) => {
  const oldStatus = row.status === 1 ? 0 : 1 // 保存原状态
  statusLoadingId.value = row.id
  try {
    await questionSetManageApi.updateQuestionSet({
      id: row.id,
      name: row.name,
      description: row.description,
      cover: row.cover,
      status: row.status
    })
    ElMessage.success(row.status === 1 ? '题库已启用' : '题库已禁用')
  } catch (error) {
    console.error('修改题库状态失败', error)
    ElMessage.error('修改题库状态失败，请稍后重试')
    // 恢复原状态
    row.status = oldStatus
  } finally {
    statusLoadingId.value = null
  }
}

// 辅助函数：格式化拼音
const formatPinyin = (pinyin: string | undefined): string => {
  if (!pinyin) return ''
  let formatted = pinyin.toLowerCase().trim()
  if (!formatted.includes(' ')) {
    formatted = formatted.replace(/([a-z]{1,3}\d?)/g, '$1 ').trim()
    formatted = formatted.replace(/\s+/g, ' ')
  }
  return formatted
}

// 类型文本映射
const getTypeText = (type: number) => {
  const map: Record<number, string> = {
    1: '单词',
    2: '中文',
    3: '数字'
  }
  return map[type] || '未知'
}

// 类型标签类型
const getTypeTagType = (type: number) => {
  const map: Record<number, 'success' | 'warning' | 'info'> = {
    1: 'success',
    2: 'warning',
    3: 'info'
  }
  return map[type] || 'info'
}

// 难度文本映射
const getDifficultyText = (difficulty: number) => {
  const map: Record<number, string> = {
    1: '简单',
    2: '中等',
    3: '困难'
  }
  return map[difficulty] || '未知'
}

// 难度标签类型
const getDifficultyTagType = (difficulty: number) => {
  const map: Record<number, 'success' | 'warning' | 'danger'> = {
    1: 'success',
    2: 'warning',
    3: 'danger'
  }
  return map[difficulty] || 'info'
}

// 管理题目：打开对话框
const handleManageQuestions = async (row: QuestionSetItem) => {
  currentQuestionSet.value = row
  manageQuestionsDialogVisible.value = true
  await fetchCurrentQuestionList()
}

// 获取当前题库下的题目列表
const fetchCurrentQuestionList = async () => {
  if (!currentQuestionSet.value) return
  
  questionsLoading.value = true
  try {
    // 获取题库下的题目ID列表
    const res = await questionSetManageApi.getQuestionIdsByQuestionSetId(currentQuestionSet.value.id)
    currentQuestionIds.value = res.data || []
    
    // 如果没有题目，直接返回
    if (currentQuestionIds.value.length === 0) {
      currentQuestionList.value = []
      return
    }
    
    // 根据题目ID列表获取题目详情
    const questionPromises = currentQuestionIds.value.map((id: number) =>
      questionBankManageApi.getQuestionById(id).catch(() => null)
    )
    const questionResults = await Promise.all(questionPromises)
    
    // 过滤掉获取失败的题目，并处理数据格式
    currentQuestionList.value = questionResults
      .filter((result: any) => result && result.data)
      .map((result: any) => {
        const question = result.data
        return {
          ...question,
          levelGroup: question.levelGroup || question.level_group,
          imgUrl: question.imgUrl || question.img_url
        }
      })
  } catch (error) {
    console.error('获取题库题目列表失败', error)
    ElMessage.error('获取题库题目列表失败，请稍后重试')
  } finally {
    questionsLoading.value = false
  }
}

// 重置管理题目对话框
const resetManageQuestions = () => {
  currentQuestionSet.value = null
  currentQuestionIds.value = []
  currentQuestionList.value = []
}

// 打开添加题目对话框
const openAddQuestionDialog = () => {
  addQuestionDialogVisible.value = true
  fetchAllQuestionList()
}

// 获取所有题目列表（用于添加题目）
const fetchAllQuestionList = async () => {
  allQuestionsLoading.value = true
  try {
    const res = await questionBankManageApi.getQuestionList({
      pageNo: questionCurrentPage.value,
      pageSize: questionPageSize.value,
      content: questionSearchForm.content.trim() || undefined,
      type: questionSearchForm.type
    })
    const data = res.data || { total: 0, rows: [] }
    const rows = Array.isArray(data.rows) ? data.rows : []
    
    // 处理数据格式，兼容后端字段名
    allQuestionList.value = rows.map((item: any) => ({
      ...item,
      levelGroup: item.levelGroup || item.level_group,
      imgUrl: item.imgUrl || item.img_url
    }))
    
    questionTotal.value = Number(data.total) || 0
    
    // 标记已在题库中的题目
    nextTick(() => {
      // 这里可以通过设置表格的默认选中状态来实现
    })
  } catch (error) {
    console.error('获取题目列表失败', error)
    ElMessage.error('获取题目列表失败，请稍后重试')
  } finally {
    allQuestionsLoading.value = false
  }
}

// 题目搜索
const handleQuestionSearch = () => {
  questionCurrentPage.value = 1
  fetchAllQuestionList()
}

// 题目搜索重置
const handleQuestionReset = () => {
  questionSearchForm.content = ''
  questionSearchForm.type = undefined
  questionCurrentPage.value = 1
  fetchAllQuestionList()
}

// 题目分页大小改变
const handleQuestionSizeChange = (val: number) => {
  questionPageSize.value = val
  questionCurrentPage.value = 1
  fetchAllQuestionList()
}

// 题目当前页改变
const handleQuestionCurrentChange = (val: number) => {
  questionCurrentPage.value = val
  fetchAllQuestionList()
}

// 题目选择改变
const handleQuestionSelectionChange = (selection: any[]) => {
  selectedQuestions.value = selection
}

// 重置添加题目对话框
const resetAddQuestion = () => {
  selectedQuestions.value = []
  questionSearchForm.content = ''
  questionSearchForm.type = undefined
  questionCurrentPage.value = 1
}

// 添加题目到题库
const handleAddQuestions = async () => {
  if (selectedQuestions.value.length === 0) {
    ElMessage.warning('请至少选择一个题目')
    return
  }
  
  if (!currentQuestionSet.value) return
  
  addQuestionSubmitting.value = true
  try {
    // 获取新选中的题目ID，过滤掉已在题库中的题目
    const newQuestionIds = selectedQuestions.value
      .map((q: any) => q.id)
      .filter((id: number) => !currentQuestionIds.value.includes(id))
    
    if (newQuestionIds.length === 0) {
      ElMessage.warning('所选题目已全部在题库中')
      addQuestionSubmitting.value = false
      return
    }
    
    // 合并到现有题目ID列表
    const allQuestionIds = [...new Set([...currentQuestionIds.value, ...newQuestionIds])]
    
    // 更新题库的题目关联
    await questionSetManageApi.updateQuestionSetQuestions(
      currentQuestionSet.value.id,
      allQuestionIds
    )
    
    ElMessage.success(`成功添加 ${newQuestionIds.length} 道题目到题库`)
    addQuestionDialogVisible.value = false
    resetAddQuestion()
    
    // 刷新当前题库的题目列表
    await fetchCurrentQuestionList()
  } catch (error) {
    console.error('添加题目失败', error)
    ElMessage.error('添加题目失败，请稍后重试')
  } finally {
    addQuestionSubmitting.value = false
  }
}

// 从题库中移除题目
const handleRemoveQuestion = async (questionId: number) => {
  if (!currentQuestionSet.value) return
  
  try {
    // 从题目ID列表中移除
    const newQuestionIds = currentQuestionIds.value.filter((id: number) => id !== questionId)
    
    // 更新题库的题目关联
    await questionSetManageApi.updateQuestionSetQuestions(
      currentQuestionSet.value.id,
      newQuestionIds
    )
    
    ElMessage.success('题目已从题库中移除')
    
    // 刷新当前题库的题目列表
    await fetchCurrentQuestionList()
  } catch (error) {
    console.error('移除题目失败', error)
    ElMessage.error('移除题目失败，请稍后重试')
  }
}

onMounted(() => {
  fetchQuestionSetList()
})
</script>

<style scoped lang="scss">
.question-set-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: var(--el-bg-color-page);
  min-height: 100%;
}

.search-card {
  flex: none;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-card {
  flex: 1;
  min-height: 0;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
}

.table-subtitle {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.action-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-link {
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  padding: 2px 4px;
  border-radius: 2px;
}

.action-link:hover {
  opacity: 0.8;
}

.view-link {
  color: #409eff;
}

.view-link:hover {
  color: #66b1ff;
  background-color: rgba(64, 158, 255, 0.1);
}

.edit-link {
  color: #e6a23c;
}

.edit-link:hover {
  color: #ebb563;
  background-color: rgba(230, 162, 60, 0.1);
}

.delete-link {
  color: #f56c6c;
}

.delete-link:hover {
  color: #f78989;
  background-color: rgba(245, 108, 108, 0.1);
}

.delete-link.is-loading {
  color: #c0c4cc;
  cursor: not-allowed;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.manage-link {
  color: #409eff;
}

.manage-link:hover {
  color: #66b1ff;
  background-color: rgba(64, 158, 255, 0.1);
}

.question-set-info {
  margin-bottom: 16px;
}

.manage-questions-content {
  margin-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.add-question-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-cell-dict {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.content-main {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.5;
}

.content-pinyin {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}
</style>
