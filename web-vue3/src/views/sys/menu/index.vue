<template>
  <div class="menu-page">
    <el-card class="search-card" shadow="hover">
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="菜单名称">
            <el-input
              v-model="searchForm.title"
              placeholder="输入菜单名称"
              clearable
              @keyup.enter="handleSearch"
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
            新增菜单
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="hover">
      <div class="table-toolbar">
        <div class="table-title">菜单列表</div>
        <div class="table-subtitle">共 {{ total }} 个菜单</div>
      </div>
      <el-table
        :data="filteredMenuData"
        v-loading="loading"
        border
        row-key="menuId"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        default-expand-all
      >
        <el-table-column type="index" width="70" align="center" label="#" />
        <el-table-column prop="title" label="菜单名称" min-width="180" />
        <el-table-column prop="name" label="路由名称" min-width="150" />
        <el-table-column prop="path" label="路由路径" min-width="150" />
        <el-table-column prop="component" label="组件路径" min-width="180" show-overflow-tooltip />
        <el-table-column prop="icon" label="图标" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.icon" size="small">{{ row.icon }}</el-tag>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="isLeaf" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.isLeaf === 'Y' ? 'success' : 'info'" size="small">
              {{ row.isLeaf === 'Y' ? '菜单' : '目录' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hidden" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.hidden ? 'danger' : 'success'" size="small">
              {{ row.hidden ? '隐藏' : '显示' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-links">
              <span class="action-link edit-link" @click="handleEdit(row)">编辑</span>
              <el-divider direction="vertical" />
              <el-popconfirm
                title="确认要删除该菜单吗？"
                :confirm-button-text="'删除'"
                :cancel-button-text="'取消'"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <span
                    class="action-link delete-link"
                    :class="{ 'is-loading': deleteLoadingId === row.menuId }"
                  >
                    {{ deleteLoadingId === row.menuId ? '删除中...' : '删除' }}
                  </span>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增菜单对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新增菜单"
      width="600px"
      destroy-on-close
      @closed="resetCreateForm"
    >
      <el-form :model="createForm" :rules="formRules" ref="createFormRef" label-width="100px">
        <el-form-item label="菜单名称" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="路由名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入路由名称（英文）" />
        </el-form-item>
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="createForm.path" placeholder="请输入路由路径" />
        </el-form-item>
        <el-form-item label="组件路径" prop="component">
          <el-input v-model="createForm.component" placeholder="例如：sys/user" />
        </el-form-item>
        <el-form-item label="重定向路径">
          <el-input v-model="createForm.redirect" placeholder="可选，例如：/sys/user" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="createForm.icon" placeholder="请输入图标名称" />
        </el-form-item>
        <el-form-item label="父级菜单">
          <el-tree-select
            v-model="createForm.parentId"
            :data="menuTreeOptions"
            :props="{ label: 'title', value: 'menuId', children: 'children' }"
            placeholder="选择父级菜单（不选则为根菜单）"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="菜单类型" prop="isLeaf">
          <el-radio-group v-model="createForm.isLeaf">
            <el-radio label="Y">菜单</el-radio>
            <el-radio label="N">目录</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否隐藏">
          <el-switch v-model="createForm.hidden" />
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

    <!-- 编辑菜单对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑菜单"
      width="600px"
      destroy-on-close
      @closed="resetEditForm"
    >
      <el-form :model="editForm" :rules="formRules" ref="editFormRef" label-width="100px">
        <el-form-item label="菜单ID">
          <el-input v-model="editForm.menuId" disabled />
        </el-form-item>
        <el-form-item label="菜单名称" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="路由名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入路由名称（英文）" />
        </el-form-item>
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="editForm.path" placeholder="请输入路由路径" />
        </el-form-item>
        <el-form-item label="组件路径" prop="component">
          <el-input v-model="editForm.component" placeholder="例如：sys/user" />
        </el-form-item>
        <el-form-item label="重定向路径">
          <el-input v-model="editForm.redirect" placeholder="可选，例如：/sys/user" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="editForm.icon" placeholder="请输入图标名称" />
        </el-form-item>
        <el-form-item label="父级菜单">
          <el-tree-select
            v-model="editForm.parentId"
            :data="menuTreeOptions"
            :props="{ label: 'title', value: 'menuId', children: 'children' }"
            placeholder="选择父级菜单（不选则为根菜单）"
            check-strictly
            clearable
            style="width: 100%"
            :disabled="editForm.menuId === editForm.parentId"
          />
        </el-form-item>
        <el-form-item label="菜单类型" prop="isLeaf">
          <el-radio-group v-model="editForm.isLeaf">
            <el-radio label="Y">菜单</el-radio>
            <el-radio label="N">目录</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否隐藏">
          <el-switch v-model="editForm.hidden" />
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
  </div>
</template>

<script setup lang="ts">
import { RefreshRight, Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { reactive, ref, onMounted, computed } from 'vue'
import menuManageApi from '@/api/menuManage'

interface MenuItem {
  menuId: number
  component: string | null
  path: string | null
  redirect: string | null
  name: string | null
  title: string | null
  icon: string | null
  parentId: number | null
  isLeaf: string | null
  hidden: boolean | null
  children?: MenuItem[]
}

const loading = ref(false)
const tableData = ref<MenuItem[]>([])
const total = ref(0)

const searchForm = reactive({
  title: ''
})

const createDialogVisible = ref(false)
const createSubmitting = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive({
  title: '',
  name: '',
  path: '',
  component: '',
  redirect: '',
  icon: '',
  parentId: null as number | null,
  isLeaf: 'Y' as string,
  hidden: false
})

const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  menuId: 0,
  title: '',
  name: '',
  path: '',
  component: '',
  redirect: '',
  icon: '',
  parentId: null as number | null,
  isLeaf: 'Y' as string,
  hidden: false
})

const deleteLoadingId = ref<number | null>(null)

// 菜单树形选项（用于选择父级菜单）
const menuTreeOptions = ref<MenuItem[]>([])

// 表单验证规则
const formRules: FormRules = {
  title: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  name: [{ required: true, message: '请输入路由名称', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路由路径', trigger: 'blur' }],
  component: [{ required: true, message: '请输入组件路径', trigger: 'blur' }],
  isLeaf: [{ required: true, message: '请选择菜单类型', trigger: 'change' }]
}

// 扁平化菜单树，用于计算总数和搜索
const flattenMenu = (menus: MenuItem[]): MenuItem[] => {
  let result: MenuItem[] = []
  menus.forEach(menu => {
    result.push(menu)
    if (menu.children && menu.children.length > 0) {
      result = result.concat(flattenMenu(menu.children))
    }
  })
  return result
}

// 过滤菜单数据（树形结构）
const filteredMenuData = computed(() => {
  if (!searchForm.title.trim()) {
    return tableData.value
  }
  const searchText = searchForm.title.toLowerCase()
  const filterMenu = (menus: MenuItem[]): MenuItem[] => {
    return menus
      .map(menu => {
        const match = menu.title?.toLowerCase().includes(searchText)
        const children = menu.children ? filterMenu(menu.children) : []
        if (match || children.length > 0) {
          return {
            ...menu,
            children: children.length > 0 ? children : undefined
          }
        }
        return null
      })
      .filter(Boolean) as MenuItem[]
  }
  return filterMenu(tableData.value)
})

// 计算总数
const updateTotal = () => {
  total.value = flattenMenu(tableData.value).length
}

// 获取菜单列表
const fetchMenuList = async () => {
  loading.value = true
  try {
    const res = await menuManageApi.getAllMenus()
    tableData.value = Array.isArray(res.data) ? res.data : []
    menuTreeOptions.value = tableData.value
    updateTotal()
  } catch (error) {
    console.error('获取菜单列表失败', error)
    ElMessage.error('获取菜单列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchMenuList()
}

const handleReset = () => {
  searchForm.title = ''
  fetchMenuList()
}

const openCreateDialog = () => {
  createDialogVisible.value = true
}

const resetCreateForm = () => {
  createForm.title = ''
  createForm.name = ''
  createForm.path = ''
  createForm.component = ''
  createForm.redirect = ''
  createForm.icon = ''
  createForm.parentId = null
  createForm.isLeaf = 'Y'
  createForm.hidden = false
  createFormRef.value?.resetFields()
}

const handleCreateSubmit = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      createSubmitting.value = true
      try {
        const data: any = {
          title: createForm.title.trim(),
          name: createForm.name.trim(),
          path: createForm.path.trim(),
          component: createForm.component.trim(),
          isLeaf: createForm.isLeaf,
          hidden: createForm.hidden
        }
        if (createForm.redirect) {
          data.redirect = createForm.redirect.trim()
        }
        if (createForm.icon) {
          data.icon = createForm.icon.trim()
        }
        if (createForm.parentId !== null) {
          data.parentId = createForm.parentId
        } else {
          data.parentId = 0
        }
        await menuManageApi.addMenu(data)
        ElMessage.success('新增菜单成功')
        createDialogVisible.value = false
        resetCreateForm()
        fetchMenuList()
      } catch (error) {
        console.error('新增菜单失败', error)
        ElMessage.error('新增菜单失败，请稍后重试')
      } finally {
        createSubmitting.value = false
      }
    }
  })
}

const handleEdit = async (row: MenuItem) => {
  try {
    const res = await menuManageApi.getMenuById(row.menuId)
    const data = res.data || {}
    editForm.menuId = data.menuId
    editForm.title = data.title || ''
    editForm.name = data.name || ''
    editForm.path = data.path || ''
    editForm.component = data.component || ''
    editForm.redirect = data.redirect || ''
    editForm.icon = data.icon || ''
    editForm.parentId = data.parentId !== undefined ? data.parentId : null
    editForm.isLeaf = data.isLeaf || 'Y'
    editForm.hidden = data.hidden !== undefined ? data.hidden : false
    editDialogVisible.value = true
  } catch (error) {
    console.error('获取菜单详情失败', error)
    ElMessage.error('获取菜单详情失败，请稍后重试')
  }
}

const resetEditForm = () => {
  editForm.menuId = 0
  editForm.title = ''
  editForm.name = ''
  editForm.path = ''
  editForm.component = ''
  editForm.redirect = ''
  editForm.icon = ''
  editForm.parentId = null
  editForm.isLeaf = 'Y'
  editForm.hidden = false
  editFormRef.value?.resetFields()
}

const handleEditSubmit = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      editSubmitting.value = true
      try {
        const data: any = {
          menuId: editForm.menuId,
          title: editForm.title.trim(),
          name: editForm.name.trim(),
          path: editForm.path.trim(),
          component: editForm.component.trim(),
          isLeaf: editForm.isLeaf,
          hidden: editForm.hidden
        }
        if (editForm.redirect) {
          data.redirect = editForm.redirect.trim()
        }
        if (editForm.icon) {
          data.icon = editForm.icon.trim()
        }
        if (editForm.parentId !== null) {
          data.parentId = editForm.parentId
        } else {
          data.parentId = 0
        }
        await menuManageApi.updateMenu(data)
        ElMessage.success('修改菜单成功')
        editDialogVisible.value = false
        resetEditForm()
        fetchMenuList()
      } catch (error) {
        console.error('修改菜单失败', error)
        ElMessage.error('修改菜单失败，请稍后重试')
      } finally {
        editSubmitting.value = false
      }
    }
  })
}

const handleDelete = async (row: MenuItem) => {
  deleteLoadingId.value = row.menuId
  try {
    await menuManageApi.deleteMenu(row.menuId)
    ElMessage.success('删除菜单成功')
    fetchMenuList()
  } catch (error: any) {
    console.error('删除菜单失败', error)
    const errorMessage = error?.response?.data?.message || error?.message || '删除菜单失败，请稍后重试'
    ElMessage.error(errorMessage)
  } finally {
    deleteLoadingId.value = null
  }
}

onMounted(() => {
  fetchMenuList()
})
</script>

<style scoped lang="scss">
.menu-page {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
