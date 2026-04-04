import { ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getScenePolishUrl } from '@/services/webrtcClient'
import { useRecognitionSession } from '../../recognition/composables/useRecognitionSession'
import useUserStore from '@/store/modules/user'
import { saveHistory } from '@/api/translationHistory'

export function useWorkspace() {
  const router = useRouter()
  const userStore = useUserStore()

  const navItems = [
    { label: '工作台', path: '/workspace' },
    { label: '识别', path: '/recognition' },
    { label: '练习', path: '/learning/practive' },
    { label: '挑战', path: '/learning/challenge' },
    { label: '记录', path: '' },
    { label: '个人中心', path: '/profile/index' }
  ]

  const handleNav = (item: { path?: string }) => {
    if (!item.path) {
      ElMessage.info('暂无该模块页面')
      return
    }
    router.push(item.path)
  }

  const recognitionState = useRecognitionSession()
  const { actionToast, actionType, actionTick } = recognitionState

  const pendingWords = ref('')
  const finalSentence = ref('')
  const polishedResult = ref('')
  const isSubmitting = ref(false)

  watch(
    () => actionTick.value,
    () => {
      if (actionType.value === 'CONFIRM' && actionToast.value) {
        pendingWords.value += actionToast.value
        return
      }

      if (actionType.value === 'CLEAR') {
        pendingWords.value = ''
        ElMessage.warning('已清空暂存词语')
        return
      }

      if (actionType.value === 'SUBMIT') {
        handleSubmit()
      }
    }
  )

  const handleSubmit = async () => {
    if (!pendingWords.value || isSubmitting.value) {
      return
    }

    isSubmitting.value = true
    const wordsToSubmit = pendingWords.value
    pendingWords.value = ''

    try {
      const response = await fetch(getScenePolishUrl('recognition'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: wordsToSubmit })
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || '网络请求失败')
      }

      const result = await response.json()
      if (result && result.polishedText) {
        finalSentence.value += result.polishedText + ' '
        polishedResult.value = result.polishedText
        ElMessage.success('AI 润色成功')
        saveHistory({
          userId: userStore.userId,
          originalWords: wordsToSubmit,
          resultSentence: result.polishedText,
          isAiPolished: 1
        }).catch((err: any) => console.error('保存历史记录失败:', err))
      } else {
        finalSentence.value += wordsToSubmit + ' '
        saveHistory({
          userId: userStore.userId,
          originalWords: wordsToSubmit,
          resultSentence: wordsToSubmit,
          isAiPolished: 0
        }).catch((err: any) => console.error('保存降级历史记录失败:', err))
      }
    } catch (error) {
      console.error('提交失败:', error)
      pendingWords.value = wordsToSubmit + pendingWords.value
      ElMessage.warning('提交失败，词语已还原')
    } finally {
      isSubmitting.value = false
    }
  }

  const clearAll = () => {
    pendingWords.value = ''
    finalSentence.value = ''
  }

  const copyResult = async () => {
    if (!finalSentence.value) {
      return
    }

    await navigator.clipboard.writeText(finalSentence.value)
    ElMessage.success('已复制')
  }

  const speakResult = () => {
    ElMessage.info('语音播报暂未实现')
  }

  onBeforeUnmount(() => {
    recognitionState.clearActionToast()
    recognitionState.stopCamera()
  })

  // 将所有状态扁平化返回，利用 Vue template 的自动解包特性
  return {
    ...recognitionState,
    navItems,
    handleNav,
    pendingWords,
    finalSentence,
    polishedResult,
    isSubmitting,
    clearAll,
    copyResult,
    speakResult
  }
}
