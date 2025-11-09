<template>
  <div>
    <el-row :gutter="20">
      <!-- 顶部统计信息卡片 -->
      <el-col :span="18">
        <el-card class="box-card stat-card-fixed">
          <div slot="header" class="clearfix stat-card-header">
            <span>统计信息</span>
          </div>
          <el-row :gutter="20" class="stats-row">
            <el-col :span="12" class="stat-item">
              <el-card shadow="hover" class="stat-card stat-subcard">
                <div class="stat-content">
                  <i class="el-icon-user solid-icon" />
                  <div class="stat-text">
                    <p class="stat-label">用户数量</p>
                    <p class="stat-value">{{ userCount }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12" class="stat-item">
              <el-card shadow="hover" class="stat-card stat-subcard">
                <div class="stat-content">
                  <i class="el-icon-s-data solid-icon" />
                  <div class="stat-text">
                    <p class="stat-label">日活跃人数</p>
                    <p class="stat-value">{{dailyActiveUsers}}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 右侧系统日志卡片 -->
      <el-col :span="6">
        <el-card class="box-card log-card">
          <div slot="header" class="clearfix">
            <span>系统日志</span>
          </div>
          <div class="log-content">
            <p>日志信息1</p>
            <p>日志信息2</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部 ECharts 图表卡片 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>数据图表</span>
          </div>
          <div>
            <div id="chart1" style="width: 100%; height: 400px;" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import userManage from '@/api/userManage'
import history from '@/api/history'

export default {
  data() {
    return {
      userCount: 0, // 用户数量
      classCount: {},
      dailyActiveUsers: 0 // 日活跃用户数
    }
  },
  mounted() {
    this.fetchHistoryData()
    this.fetchUserCount()
    this.fetchDailyActiveUsers()
  },
  methods: {
    fetchUserCount() {
      userManage.getAllUsers().then(response => {
        if (response && response.data) {
          this.userCount = response.data.length // 假设返回的是用户数组
        }
      }).catch(error => {
        console.error('获取用户数据失败:', error)
        this.$message.error('获取用户数量失败，请稍后重试')
      })
    },
    fetchHistoryData() {
      history.getAllHistoryList().then(response => {
        if (response && response.data) {
          this.processHistoryData(response.data)
        }
      }).catch(error => {
        console.error('获取历史数据失败:', error)
        this.$message.error('获取历史数据失败，请稍后重试')
      })
    },
    fetchDailyActiveUsers() {
      userManage.getAllTime().then(response => {
        if (response && response.data) {
          this.calculateDailyActiveUsers(response.data)
        }
      }).catch(error => {
        console.error('获取活跃用户数据失败:', error)
        this.$message.error('获取活跃用户数据失败，请稍后重试')
      })
    },
    processHistoryData(data) {
      const classCount = {}
      data.forEach(item => {
        const className = item.class_name
        if (classCount[className]) {
          classCount[className]++
        } else {
          classCount[className] = 1
        }
      })
      this.initChart1(classCount)
    },
    calculateDailyActiveUsers(data) {
      const activeUsers = new Set()
      const today = new Date()
      const todayStr = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`

      data.forEach(item => {
        const [year, month, day] = item.activity_time
        if (`${year}-${month}-${day}` === todayStr) {
          activeUsers.add(item.user_id)
        }
      })

      this.dailyActiveUsers = activeUsers.size
    },
    initChart1(classCount) {
      const chart1 = echarts.init(document.getElementById('chart1'))
      const data = Object.entries(classCount).map(([name, value]) => ({ name, value }))

      const option1 = {
        title: [
          {
            text: '全部识别数据统计',
            left: '15%'
          },
          {
            text: '全部识别数据占比',
            left: '70%'
          }
        ],
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        grid: {
          left: '1%',
          right: '47%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: Object.keys(classCount),
          axisLabel: {
            rotate: 45,
            interval: 0
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '数量',
            type: 'bar',
            data: Object.values(classCount),
            itemStyle: {
              color: '#409EFF'
            },
            barWidth: '50%'
          },
          {
            name: '占比',
            type: 'pie',
            radius: '30%',
            center: ['75%', '50%'],
            data: data,
            label: {
              formatter: '{b}：{d}%',
              position: 'outside'
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      chart1.setOption(option1)
    }
  }
}
</script>

<style scoped>
.stat-card-header {
  text-align: center;
  font-size: 24px; /* 根据需要调整字体大小 */
}
.box-card {
  margin-bottom: -5px;
}
.stat-card-fixed {
  height: 300px; /* 固定高度 */
}
.stats-row {
  margin-top: 10px;
}
.stat-item {
  padding: 5px; /* 缩小卡片间距 */
}
.stat-subcard {
  height: 120px; /* 控制子卡片高度 */
}
.stat-card {
  text-align: center;
  background-color: #f9f9f9;
}
.log-card {
  height: 300px; /* 固定日志卡片高度 */
  align-items: center;
  text-align: center;
}
.clearfix {
  font-size: 24px;
}
.log-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.stat-content {
  display: flex;
  align-items: center; /* 垂直居中 */
  justify-content: flex-start; /* 水平靠左 */
}
.solid-icon {
  font-size: 36px;
  margin-right: 10px;
  color: #409EFF;
}
.stat-text {
  text-align: left;
}
.stat-label {
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.stat-value {
  font-size: 35px;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin: 0;
}
</style>
