<template>
  <div class="question-bank-page">
    <el-card class="search-card" shadow="hover">
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="题目内容">
            <el-input
              v-model="searchForm.content"
              placeholder="输入题目内容"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="题目类型">
            <el-select
              v-model="searchForm.type"
              placeholder="请选择类型"
              clearable
              style="width: 150px"
            >
              <el-option label="单词" :value="1" />
              <el-option label="中文" :value="2" />
              <el-option label="数字" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="难度">
            <el-select
              v-model="searchForm.difficulty"
              placeholder="请选择难度"
              clearable
              style="width: 150px"
            >
              <el-option label="简单" :value="1" />
              <el-option label="中等" :value="2" />
              <el-option label="困难" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="关卡">
            <el-input
              v-model="searchForm.levelGroup"
              placeholder="输入关卡"
              clearable
              style="width: 150px"
            />
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
            新增题目
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="hover">
      <div class="table-toolbar">
        <div>
          <div class="table-title">题目列表</div>
          <div class="table-subtitle">
            共 {{ serverTotal }} 道题目，当前页显示 {{ pagedTableData.length }} 道
          </div>
        </div>
        <el-space>
          <el-button text :icon="RefreshRight" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table :data="pagedTableData" v-loading="loading" border>
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="content" label="题目内容" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="content-cell">
              <span class="content-text">{{ row.content }}</span>
              <el-tag v-if="row.pinyin" size="small" type="info" class="pinyin-tag">
                {{ row.pinyin }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getDifficultyTagType(row.difficulty)">
              {{ getDifficultyText(row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="levelGroup" label="关卡" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              第 {{ row.levelGroup || row.level_group || '—' }} 关
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="imgUrl" label="图片" width="120" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.imgUrl"
              :src="row.imgUrl"
              :preview-src-list="[row.imgUrl]"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px;"
              lazy
            />
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip content="查看" effect="dark" placement="top">
                <el-button
                  circle
                  class="action-icon"
                  type="primary"
                  :icon="View"
                  @click="handleView(row)"
                />
              </el-tooltip>
              <el-tooltip content="编辑" effect="dark" placement="top">
                <el-button
                  circle
                  class="action-icon"
                  type="warning"
                  :icon="Edit"
                  @click="handleEdit(row)"
                />
              </el-tooltip>
              <el-popconfirm
                title="确认要删除该题目吗？"
                :confirm-button-text="'删除'"
                :cancel-button-text="'取消'"
                :teleported="false"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <el-button
                    circle
                    class="action-icon danger"
                    type="danger"
                    :loading="deleteLoadingId === row.id"
                    :icon="Delete"
                  />
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
          :total="serverTotal"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增题目对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新增题目"
      width="600px"
      destroy-on-close
      @closed="resetCreateForm"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="createForm.content"
            placeholder="请输入题目内容"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="题目类型" prop="type">
          <el-radio-group v-model="createForm.type">
            <el-radio :label="1">单词</el-radio>
            <el-radio :label="2">中文</el-radio>
            <el-radio :label="3">数字</el-radio>
          </el-radio-group>
          <div class="form-tip">选择中文类型时，系统会自动生成拼音</div>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-radio-group v-model="createForm.difficulty">
            <el-radio :label="1">简单</el-radio>
            <el-radio :label="2">中等</el-radio>
            <el-radio :label="3">困难</el-radio>
          </el-radio-group>
        </el-form-item>
          <el-form-item label="关卡" prop="levelGroup">
            <el-input-number
              v-model="createForm.levelGroup"
              :min="1"
              :max="100"
              placeholder="请输入关卡数字"
              style="width: 100%"
            />
            <div class="form-tip">关卡编号，用于区分不同难度的题目集合</div>
          </el-form-item>
        <el-form-item label="图片URL">
          <el-input
            v-model="createForm.imgUrl"
            placeholder="请输入图片URL（可选）"
            clearable
          />
          <div class="form-tip">支持网络图片链接，如：https://example.com/image.png</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="createForm.status"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="createSubmitting" @click="handleCreateSubmit">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑题目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="修改题目"
      width="600px"
      destroy-on-close
      @closed="resetEditForm"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="editForm.content"
            placeholder="请输入题目内容"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="题目类型" prop="type">
          <el-radio-group v-model="editForm.type">
            <el-radio :label="1">单词</el-radio>
            <el-radio :label="2">中文</el-radio>
            <el-radio :label="3">数字</el-radio>
          </el-radio-group>
          <div class="form-tip">选择中文类型时，系统会自动生成拼音</div>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-radio-group v-model="editForm.difficulty">
            <el-radio :label="1">简单</el-radio>
            <el-radio :label="2">中等</el-radio>
            <el-radio :label="3">困难</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="关卡" prop="levelGroup">
          <el-input-number
            v-model="editForm.levelGroup"
            :min="1"
            :max="100"
            placeholder="请输入关卡数字"
            style="width: 100%"
          />
          <div class="form-tip">关卡编号，用于区分不同难度的题目集合</div>
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input
            v-model="editForm.imgUrl"
            placeholder="请输入图片URL（可选）"
            clearable
          />
          <div class="form-tip">支持网络图片链接，如：https://example.com/image.png</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="editForm.status"
            active-text="启用"
            inactive-text="停用"
          />
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

    <!-- 查看题目详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="题目详情"
      width="600px"
      destroy-on-close
      v-loading="viewLoading"
    >
      <el-skeleton v-if="viewLoading" rows="6" animated />
      <el-descriptions
        v-else-if="viewDetail"
        :column="1"
        border
        label-width="100px"
        class="detail-descriptions"
      >
        <el-descriptions-item label="题目ID">{{ viewDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="题目内容">
          <div class="detail-content">
            <span>{{ viewDetail.content }}</span>
            <el-tag v-if="viewDetail.pinyin" size="small" type="info" class="pinyin-tag">
              {{ viewDetail.pinyin }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="题目类型">
          <el-tag :type="getTypeTagType(viewDetail.type)">
            {{ getTypeText(viewDetail.type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="难度">
          <el-tag :type="getDifficultyTagType(viewDetail.difficulty)">
            {{ getDifficultyText(viewDetail.difficulty) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="关卡">
          <el-tag type="info" size="small">
            第 {{ viewDetail.levelGroup || viewDetail.level_group || '—' }} 关
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="拼音">
          {{ viewDetail.pinyin || '—' }}
        </el-descriptions-item>
        <el-descriptions-item label="图片">
          <el-image
            v-if="viewDetail.imgUrl"
            :src="viewDetail.imgUrl"
            :preview-src-list="[viewDetail.imgUrl]"
            fit="cover"
            style="width: 120px; height: 120px; border-radius: 4px;"
            lazy
          />
          <span v-else>—</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewDetail.status === 1 ? 'success' : 'danger'">
            {{ viewDetail.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Edit, Delete, Plus, RefreshRight, Search, View } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { computed, reactive, ref, onMounted } from 'vue'
import questionBankManageApi from '@/api/questionBankManage'

// 题目信息接口
interface Question {
  id: number
  content: string
  type: number // 1:单词 2:中文 3:数字
  difficulty: number // 1:简单 2:中等 3:困难
  pinyin?: string
  imgUrl?: string
  img_url?: string // 后端返回的字段名
  levelGroup?: string | number
  level_group?: string | number // 后端返回的字段名
  status: number // 1:启用 0:停用
}

const loading = ref(false)
const tableData = ref<Question[]>([])
const serverTotal = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索表单
const searchForm = reactive({
  content: '',
  type: undefined as number | undefined,
  difficulty: undefined as number | undefined,
  levelGroup: '',
})

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

// 新增题目弹窗状态 & 表单
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createFormDefault = {
  content: '',
  type: 1,
  difficulty: 1,
  levelGroup: 1,
  imgUrl: '',
  status: true,
}
const createForm = reactive({ ...createFormDefault })
const createRules: FormRules = {
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' },
    { max: 100, message: '题目内容不能超过100个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择题目类型', trigger: 'change' }
  ],
  difficulty: [
    { required: true, message: '请选择难度', trigger: 'change' }
  ],
  levelGroup: [
    { required: true, message: '请输入关卡', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '关卡必须在1-100之间', trigger: 'blur' }
  ]
}
const createSubmitting = ref(false)

// 编辑题目弹窗状态 & 表单
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editFormDefault = {
  id: 0,
  content: '',
  type: 1,
  difficulty: 1,
  levelGroup: 1,
  imgUrl: '',
  status: true,
}
const editForm = reactive({ ...editFormDefault })
const editRules: FormRules = {
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' },
    { max: 100, message: '题目内容不能超过100个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择题目类型', trigger: 'change' }
  ],
  difficulty: [
    { required: true, message: '请选择难度', trigger: 'change' }
  ],
  levelGroup: [
    { required: true, message: '请输入关卡', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '关卡必须在1-100之间', trigger: 'blur' }
  ]
}
const editSubmitting = ref(false)

// 查看详情
const viewDialogVisible = ref(false)
const viewDetail = ref<Question | null>(null)
const viewLoading = ref(false)

// 后端已实现分页+筛选，因此直接使用接口返回的数据
const pagedTableData = computed(() => tableData.value)

// 获取题目列表
const fetchQuestionList = async () => {
  loading.value = true
  try {
    const res = await questionBankManageApi.getQuestionList({
      pageNo: currentPage.value,
      pageSize: pageSize.value,
      content: searchForm.content.trim() || undefined,
      type: searchForm.type,
      difficulty: searchForm.difficulty,
      levelGroup: searchForm.levelGroup.trim() || undefined,
    })
    const data = res.data || { total: 0, rows: [] }
    const rows = Array.isArray(data.rows) ? data.rows : []
    // 转换字段名：将后端返回的 snake_case 转换为 camelCase
    tableData.value = rows.map((item: any) => ({
      ...item,
      levelGroup: item.levelGroup || item.level_group, // 兼容两种字段名
      imgUrl: item.imgUrl || item.img_url, // 兼容两种字段名
    }))
    serverTotal.value = Number(data.total) || 0
  } catch (error: any) {
    console.error('获取题目列表失败', error)
    const errorMsg = error.response?.data?.message || error.message || '获取题目列表失败，请稍后重试'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchQuestionList()
}

// 重置
const handleReset = () => {
  searchForm.content = ''
  searchForm.type = undefined
  searchForm.difficulty = undefined
  searchForm.levelGroup = ''
  currentPage.value = 1
  fetchQuestionList()
}

// 新增题目（打开弹窗）
const openCreateDialog = () => {
  createDialogVisible.value = true
}

// 新增题目提交
const handleCreateSubmit = () => {
  if (!createFormRef.value) return
  createFormRef.value.validate((valid) => {
    if (valid) {
      createSubmitting.value = true
      questionBankManageApi.addQuestion({
        content: createForm.content.trim(),
        type: createForm.type,
        difficulty: createForm.difficulty,
        levelGroup: String(createForm.levelGroup),
        imgUrl: createForm.imgUrl?.trim() || undefined,
        status: createForm.status ? 1 : 0,
      }).then(() => {
        ElMessage.success('新增题目成功')
        createDialogVisible.value = false
        fetchQuestionList()
      }).catch((error) => {
        console.error('新增题目失败', error)
        ElMessage.error(error.response?.data?.message || '新增题目失败，请稍后重试')
      }).finally(() => {
        createSubmitting.value = false
      })
    }
  })
}

// 重置新增弹窗表单
const resetCreateForm = () => {
  Object.assign(createForm, { ...createFormDefault })
  createFormRef.value?.clearValidate()
}

// 编辑题目（打开弹窗）
const handleEdit = (row: Question) => {
  Object.assign(editForm, {
    id: row.id,
    content: row.content,
    type: row.type,
    difficulty: row.difficulty,
    levelGroup: Number(row.levelGroup || row.level_group || 1),
    imgUrl: row.imgUrl || '',
    status: row.status === 1,
  })
  editFormRef.value?.clearValidate()
  editDialogVisible.value = true
}

// 编辑题目提交
const handleEditSubmit = () => {
  if (!editFormRef.value) return
  editFormRef.value.validate((valid) => {
    if (!valid) return
    editSubmitting.value = true
    questionBankManageApi.updateQuestion({
      id: editForm.id,
      content: editForm.content.trim(),
      type: editForm.type,
      difficulty: editForm.difficulty,
      levelGroup: String(editForm.levelGroup),
      imgUrl: editForm.imgUrl?.trim() || undefined,
      status: editForm.status ? 1 : 0,
    }).then(() => {
      ElMessage.success('修改题目成功')
      editDialogVisible.value = false
      fetchQuestionList()
    }).catch(error => {
      console.error('修改题目失败', error)
      ElMessage.error(error.response?.data?.message || '修改题目失败，请稍后重试')
    }).finally(() => {
      editSubmitting.value = false
    })
  })
}

// 重置编辑弹窗表单
const resetEditForm = () => {
  Object.assign(editForm, { ...editFormDefault })
  editFormRef.value?.clearValidate()
}

// 删除题目
const deleteLoadingId = ref<number | null>(null)
const handleDelete = (row: Question) => {
  deleteLoadingId.value = row.id
  questionBankManageApi.deleteQuestion(row.id)
    .then(() => {
      ElMessage.success('删除题目成功')
      fetchQuestionList()
    })
    .catch(error => {
      console.error('删除题目失败', error)
      ElMessage.error(error.response?.data?.message || '删除题目失败，请稍后重试')
    })
    .finally(() => {
      deleteLoadingId.value = null
    })
}

// 查看详情
const handleView = async (row: Question) => {
  viewDialogVisible.value = true
  viewLoading.value = true
  try {
    const res = await questionBankManageApi.getQuestionById(row.id)
    viewDetail.value = res.data as Question
  } catch (error) {
    console.error('获取题目详情失败', error)
    ElMessage.error('获取题目详情失败，请稍后重试')
    viewDialogVisible.value = false
  } finally {
    viewLoading.value = false
  }
}

// 刷新
const handleRefresh = () => {
  fetchQuestionList()
}

// 分页大小改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchQuestionList()
}

// 当前页改变
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchQuestionList()
}

// 挂载
onMounted(() => {
  fetchQuestionList()
})
</script>

<style scoped>
.question-bank-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: var(--el-bg-color-page);
  min-height: 100%;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.search-form {
  flex: 1;
  min-width: 280px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-card {
  flex: 1;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
}

.table-subtitle {
  color: var(--el-text-color-secondary);
  margin-top: 4px;
  font-size: 13px;
}

.content-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.content-text {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.pinyin-tag {
  font-size: 11px;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.action-icon {
  width: 42px;
  height: 42px;
  font-size: 18px;
}

.action-icon:deep(.el-icon) {
  font-size: 20px;
}

.text-muted {
  color: var(--el-text-color-secondary);
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.detail-descriptions {
  margin-bottom: 12px;
}

.detail-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}
</style>
