<template>
  <div :id="chartId" :class="className" :style="{height:height,width:width}" />
</template>

<script>
import { defineComponent } from 'vue';
import * as echarts from 'echarts';
import resize from './mixins/resize';

export default defineComponent({
  name: 'LearningTimeChart',
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: 'learning-time-chart'
    },
    chartId: {
      type: String,
      default: 'learning-time-chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '350px'
    },
    // 最近7天的学习数据，格式: [{ date: '2024-01-01', hours: 2.5 }, ...]
    data: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chart: null
    };
  },
  watch: {
    data: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
    });
  },
  activated() {
    // 当使用 keep-alive 时，确保图表正确渲染
    this.$nextTick(() => {
      if (this.chart) {
        // 确保 DOM 存在
        const chartDom = document.getElementById(this.chartId);
        if (chartDom) {
          this.chart.resize();
          this.updateChart();
        } else {
          // DOM 不存在，重新初始化
          this.initChart();
        }
      } else {
        // 图表未初始化，初始化图表
        this.initChart();
      }
    });
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  },
  methods: {
    // 重写 resize mixin 的 resize 方法，添加安全检查
    resize() {
      if (this.chart) {
        try {
          this.chart.resize();
        } catch (error) {
          console.warn('Error resizing chart:', error);
        }
      }
    },
    initChart() {
      const chartDom = document.getElementById(this.chartId);
      if (!chartDom) {
        console.warn(`Chart container with id "${this.chartId}" not found`);
        return;
      }
      
      // 如果图表已存在，先销毁
      if (this.chart) {
        try {
          this.chart.dispose();
        } catch (e) {
          console.warn('Error disposing chart:', e);
        }
        this.chart = null;
      }
      
      try {
        this.chart = echarts.init(chartDom);
        if (this.chart) {
          this.updateChart();
        }
      } catch (error) {
        console.error('Error initializing chart:', error);
        this.chart = null;
      }
    },
    updateChart() {
      if (!this.chart) {
        return;
      }

      // 处理数据：如果没有传入数据，生成最近7天的示例数据
      const chartData = this.processData();
      
      // 验证数据
      if (!chartData || !chartData.dates || !chartData.hours) {
        console.warn('Invalid chart data');
        return;
      }
      
      if (chartData.dates.length === 0 || chartData.hours.length === 0) {
        console.warn('Empty chart data');
        return;
      }
      
      // 确保日期和时长数组长度一致
      if (chartData.dates.length !== chartData.hours.length) {
        console.warn('Chart data length mismatch:', {
          dates: chartData.dates.length,
          hours: chartData.hours.length
        });
        // 取较小的长度
        const minLength = Math.min(chartData.dates.length, chartData.hours.length);
        chartData.dates = chartData.dates.slice(0, minLength);
        chartData.hours = chartData.hours.slice(0, minLength);
      }
      
      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e4e7ed',
          borderWidth: 1,
          textStyle: {
            color: '#303133'
          },
          formatter: (params) => {
            const param = params[0];
            return `${param.axisValue}<br/>学习时长: <span style="color: #6366f1; font-weight: 600;">${param.value} 小时</span>`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: chartData.dates,
          axisLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#909399',
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '时长（小时）',
          nameTextStyle: {
            color: '#909399',
            fontSize: 12
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#909399',
            fontSize: 12,
            formatter: (value) => {
              return value.toFixed(1);
            }
          },
          splitLine: {
            lineStyle: {
              color: '#f0f2f5',
              type: 'dashed'
            }
          }
        },
        series: [
          {
            name: '学习时长',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              color: '#6366f1',
              width: 3
            },
            itemStyle: {
              color: '#6366f1',
              borderColor: '#fff',
              borderWidth: 2
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(99, 102, 241, 0.3)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(99, 102, 241, 0.05)'
                  }
                ]
              }
            },
            emphasis: {
              focus: 'series',
              itemStyle: {
                color: '#6366f1',
                borderColor: '#fff',
                borderWidth: 3,
                shadowBlur: 10,
                shadowColor: 'rgba(99, 102, 241, 0.5)'
              }
            },
            data: chartData.hours
          }
        ]
      };

      try {
        this.chart.setOption(option, true);
      } catch (error) {
        console.error('Error setting chart option:', error);
      }
    },
    processData() {
      // 如果没有传入数据，生成最近7天的示例数据
      if (!this.data || this.data.length === 0) {
        const dates = [];
        const hours = [];
        const today = new Date();
        
        for (let i = 6; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateStr = this.formatDate(date);
          dates.push(dateStr);
          // 生成随机示例数据（0.5-3小时）
          hours.push(Number((Math.random() * 2.5 + 0.5).toFixed(1)));
        }
        
        return { dates, hours };
      }

      // 处理传入的数据
      const dates = [];
      const hours = [];
      
      // 确保有7天的数据，如果不足7天，补齐
      const today = new Date();
      const dataMap = new Map();
      
      // 将传入的数据转换为Map，方便查找
      if (Array.isArray(this.data)) {
        this.data.forEach(item => {
          if (item && typeof item === 'object') {
            const dateKey = item.date || item.dateStr || item.day;
            const hour = item.hours || item.hour || item.duration || 0;
            if (dateKey) {
              dataMap.set(dateKey, Number(hour) || 0);
            }
          }
        });
      }

      // 生成最近7天的日期
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = this.formatDate(date);
        dates.push(dateStr);
        
        // 如果该日期有数据，使用数据；否则为0
        // 同时尝试匹配完整日期格式
        let hour = dataMap.get(dateStr) || 0;
        if (!hour) {
          // 尝试匹配完整日期格式 YYYY-MM-DD
          const fullDateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
          hour = dataMap.get(fullDateStr) || 0;
        }
        hours.push(Number(hour) || 0);
      }

      return { dates, hours };
    },
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${month}-${day}`;
    }
  }
});
</script>

<style lang="scss" scoped>
.learning-time-chart {
  width: 100%;
  height: 100%;
}
</style>

