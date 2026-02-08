import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import questionSetManage from '@/api/questionSetManage'
import { queryQuestions, startChallenge } from '@/api/challenge'

export function useChallengeConfig() {
  // --- 配置状态 ---
  const showConfig = ref(true)
  const challengeMode = ref<'random' | 'questionSet'>('random')
  const selectedQuestionSetId = ref<number | null>(null)
  const randomFromQuestionSet = ref(true)
  const selectedTypes = ref<string[]>(['1', '2', '3'])
  const selectedDifficulties = ref<string[]>(['1', '2', '3'])
  const questionCount = ref(20)
  const challengeTime = ref(60)

  // --- 题库数据 ---
  const questionSetList = ref<any[]>([])

  // 配置对象
  const config = computed(() => ({
    challengeMode: challengeMode.value,
    selectedQuestionSetId: selectedQuestionSetId.value,
    randomFromQuestionSet: randomFromQuestionSet.value,
    selectedTypes: selectedTypes.value,
    selectedDifficulties: selectedDifficulties.value,
    questionCount: questionCount.value,
    challengeTime: challengeTime.value
  }))

  const currentQuestionSetName = computed(() => {
    const set = questionSetList.value.find(s => s.id === selectedQuestionSetId.value)
    return set?.name || ''
  })

  // 更新配置
  const handleConfigUpdate = (key: string, value: any) => {
    switch (key) {
      case 'challengeMode':
        challengeMode.value = value
        break
      case 'selectedQuestionSetId':
        selectedQuestionSetId.value = value
        break
      case 'randomFromQuestionSet':
        randomFromQuestionSet.value = value
        break
      case 'selectedTypes':
        selectedTypes.value = value
        break
      case 'selectedDifficulties':
        selectedDifficulties.value = value
        break
      case 'questionCount':
        questionCount.value = value
        break
      case 'challengeTime':
        challengeTime.value = value
        break
    }
  }

  // 加载题库列表
  const loadQuestionSets = async () => {
    try {
      const res = await questionSetManage.getAllQuestionSets()
      if (res.data) {
        const setsWithCount = await Promise.all(
          res.data.map(async (set: any) => {
            try {
              const questionIdsRes = await questionSetManage.getQuestionIdsByQuestionSetId(set.id)
              const questionCount = questionIdsRes.data?.length || 0
              return {
                ...set,
                questionCount
              }
            } catch (error) {
              console.error(`获取题库 ${set.id} 的题目数量失败`, error)
              return {
                ...set,
                questionCount: 0
              }
            }
          })
        )
        questionSetList.value = setsWithCount
      }
    } catch (error) {
      console.error('加载题库列表失败', error)
    }
  }

  // 加载题目
  const loadQuestions = async () => {
    try {
      const params: any = {
        mode: challengeMode.value,
        count: questionCount.value,
        random: challengeMode.value === 'questionSet' ? randomFromQuestionSet.value : true
      }

      if (challengeMode.value === 'random') {
        params.types = selectedTypes.value.join(',')
        if (selectedDifficulties.value.length > 0) {
          params.difficulties = selectedDifficulties.value.join(',')
        }
      } else if (challengeMode.value === 'questionSet' && selectedQuestionSetId.value) {
        params.questionSetId = selectedQuestionSetId.value
      }

      const res = await queryQuestions(params)
      const data = res.data || {}
      const questions = data.questions || []

      if (questions.length === 0) {
        ElMessage.warning('没有符合条件的题目，请调整筛选条件')
        return null
      }

      return questions
    } catch (error) {
      console.error('加载题目失败', error)
      ElMessage.error('加载题目失败，请稍后重试')
      return null
    }
  }

  return {
    // 状态
    showConfig,
    challengeMode,
    selectedQuestionSetId,
    randomFromQuestionSet,
    selectedTypes,
    selectedDifficulties,
    questionCount,
    challengeTime,
    questionSetList,
    // 计算属性
    config,
    currentQuestionSetName,
    // 方法
    handleConfigUpdate,
    loadQuestionSets,
    loadQuestions
  }
}

