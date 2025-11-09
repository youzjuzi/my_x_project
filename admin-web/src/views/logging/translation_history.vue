<template>
  <div>
    <el-row :gutter="20" class="block">
      <el-col :span="11">
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="date-picker"
          @change="handleDateChange"
        />
      </el-col>
      <el-col :span="6">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入内容"
          clearable
        />
      </el-col>
      <el-col :span="3">
        <el-button type="primary" round @click="handleSearch">查询</el-button>
      </el-col>
    </el-row>
    <!-- 结果列表 -->
    <el-card>
      <el-table :data="historyList" border style="width: 100%">
        <el-table-column label="#" width="80">
          <template slot-scope="scope">
            {{ (searchModel.pageNo-1) * searchModel.pageSize + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="sessionId" label="ID" width="180" align="center" />
        <el-table-column prop="timestamp" label="检测时间" width="180" align="center" />
        <el-table-column prop="className" label="检测类型" width="180" align="center" />
        <el-table-column prop="confidence" label="准确度" align="center" />
        <el-table-column label="操作" width="180" align="center">
          <template slot-scope="scope">
            <el-button type="danger" icon="el-icon-delete" circle size="mini" @click="deleteHistoryById(scope.row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-pagination
      :current-page="searchModel.pageNo"
      :page-sizes="[5, 10, 20, 50]"
      :page-size="searchModel.pageSize"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script>
import historyApi from '@/api/history'
import menu from 'element-ui/packages/menu'

export default {
  data() {
    return {
      dateRange: [],
      formLabelWidth: '130px',
      searchKeyword: '',
      searchModel: {
        pageNo: 1,
        pageSize: 10,
        startDate: null,
        endDate: null,
        keyword: ''
      },
      historyList: [],
      total: 0
    }
  },
  computed: {
    menu() {
      return menu
    }
  },
  created() {
    this.getHistoryList()
  },
  methods: {
    handleDateChange(val) {
      if (val && val.length === 2) {
        this.searchModel.startDate = this.formatDate(val[0])
        this.searchModel.endDate = this.formatDate(val[1])
      } else {
        this.searchModel.startDate = null
        this.searchModel.endDate = null
      }
    },
    handleSearch() {
      this.searchModel.pageNo = 1 // 重置页码
      this.searchModel.keyword = this.searchKeyword
      this.getHistoryList()
    },
    formatDate(date) {
      return date.toISOString() // 或者使用您喜欢的日期格式
    },
    deleteHistoryById(detection) {
      this.$confirm(`您确认删除${detection.sessionId}此记录`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        historyApi.deleteHistoryById(detection.sessionId).then(respones => {
          this.$message({
            type: 'success',
            message: respones.message
          })
          this.getHistoryList()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handleSizeChange(pageSize) {
      this.searchModel.pageSize = pageSize
      this.getHistoryList()
    },
    handleCurrentChange(pageNo) {
      this.searchModel.pageNo = pageNo
      this.getHistoryList()
    },
    getHistoryList() {
      historyApi.getHistoryList(this.searchModel).then(response => {
        this.historyList = response.data.rows
        this.total = response.data.total

        // 检查当前页码是否超出范围
        const maxPage = Math.ceil(this.total / this.searchModel.pageSize)
        if (this.searchModel.pageNo > maxPage) {
          this.searchModel.pageNo = maxPage || 1 // 如果没有数据，设置为第1页
          this.getHistoryList() // 重新获取数据
        }
      }).catch(error => {
        console.error('获取历史列表失败:', error)
        this.$message.error('获取数据失败，请稍后重试')
      })
    }
  }
}
</script>

<style>
.el-dialog .el-input{
  width: 70%;
}
.block {
  display: flex;
  align-items: center;
}
.date-picker {
  width: 100%;
  max-width: 380px; /* 或者您认为合适的最大宽度 */
}
.text-center {
  text-align: center !important;
}

/* 如果需要垂直居中 */
.el-table .cell {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 对于操作列的按钮，可能需要特殊处理 */
.el-table .cell .el-button {
  margin: 0 5px;
}

</style>
