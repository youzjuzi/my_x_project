import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createRecognitionWebRtcClient } from '../services/webrtcClient'

export function useRecognitionSession() {
  const isCameraActive = ref(false)
  const connectionState = ref('idle')
  const selectedMode = ref('digits')
  const inputFps = ref(0)
  const processedFps = ref(0)
  const latency = ref(0)
  const gestureStream = ref([])
  const pinyinBuffer = ref('')
  const cachedBuffer = ref('')
  const stabilityProgress = ref(0)
  const localStream = ref(null)
  const overlayResult = ref(null)
  const isRecognitionReady = ref(false)
  const actionToast = ref('')
  const actionTitle = ref('')
  const deletedCacheChar = ref('')
  const deletedCacheTick = ref(0)

  let webrtcClient = null
  let actionToastTimer = null
  let deletedCacheTimer = null

  const modeLabelMap = {
    digits: '数字',
    letters: '字母',
  }

  const connectionText = computed(() => {
    const modeLabel = modeLabelMap[selectedMode.value] || selectedMode.value

    if (connectionState.value === 'connected') {
      return `WebRTC 已连接，当前为${modeLabel}模式`
    }

    if (connectionState.value === 'connecting') {
      return `WebRTC 连接中，准备进入${modeLabel}模式`
    }

    return `开启摄像头后，将进入${modeLabel}模式`
  })

  const resetDisplayState = () => {
    inputFps.value = 0
    processedFps.value = 0
    latency.value = 0
    overlayResult.value = null
    gestureStream.value = []
    pinyinBuffer.value = ''
    cachedBuffer.value = ''
    stabilityProgress.value = 0
    isRecognitionReady.value = false
    clearDeleteAnimation()
  }

  const clearActionToast = () => {
    if (actionToastTimer) {
      window.clearTimeout(actionToastTimer)
      actionToastTimer = null
    }
    actionToast.value = ''
    actionTitle.value = ''
  }

  const showActionToast = (actionType, actionValue) => {
    if (actionType !== 'SWITCH') {
      return
    }

    const modeLabel = modeLabelMap[actionValue] || actionValue
    clearActionToast()
    actionTitle.value = '模式切换'
    actionToast.value = `已切换到${modeLabel}模式`

    actionToastTimer = window.setTimeout(() => {
      actionToast.value = ''
      actionTitle.value = ''
      actionToastTimer = null
    }, 1500)
  }

  const clearDeleteAnimation = () => {
    if (deletedCacheTimer) {
      window.clearTimeout(deletedCacheTimer)
      deletedCacheTimer = null
    }
    deletedCacheChar.value = ''
  }

  const triggerDeleteAnimation = (nextCachedBuffer) => {
    const previous = cachedBuffer.value || ''
    const nextValue = nextCachedBuffer || ''

    if (previous.length <= nextValue.length) {
      cachedBuffer.value = nextValue
      return
    }

    const removed = previous.slice(nextValue.length)
    cachedBuffer.value = nextValue
    deletedCacheChar.value = removed
    deletedCacheTick.value += 1

    if (deletedCacheTimer) {
      window.clearTimeout(deletedCacheTimer)
    }

    deletedCacheTimer = window.setTimeout(() => {
      deletedCacheChar.value = ''
      deletedCacheTimer = null
    }, 900)
  }

  const mapProcessItems = (items) => {
    if (!Array.isArray(items)) {
      return []
    }

    return items.map((item, index) => ({
      id: `${index}-${item}`,
      char: item,
    }))
  }

  const handleServerMessage = (payload) => {
    if (!payload || typeof payload !== 'object') {
      return
    }

    if (payload.type === 'error') {
      ElMessage.error(payload.message || '识别服务发生异常')
      return
    }

    if (payload.type === 'mode_changed') {
      selectedMode.value = payload.mode || selectedMode.value
      resetDisplayState()
      return
    }

    if (payload.type !== 'result') {
      return
    }

    if (payload.actionPerformed) {
      isRecognitionReady.value = true
      inputFps.value = Number(payload.inputFps || 0)
      processedFps.value = Number(payload.processedFps || 0)
      latency.value = Number(payload.latencyMs || 0)
      gestureStream.value = []
      pinyinBuffer.value = ''
      stabilityProgress.value = 0
      overlayResult.value = null

      if (payload.modeChangedByCommand) {
        selectedMode.value = payload.mode || selectedMode.value
      }

      if (payload.actionType === 'DELETE') {
        triggerDeleteAnimation(String(payload.cachedBuffer || ''))
      } else {
        cachedBuffer.value = String(payload.cachedBuffer || '')
      }

      showActionToast(payload.actionType, payload.actionToast)
      return
    }

    overlayResult.value = payload
    isRecognitionReady.value = true
    inputFps.value = Number(payload.inputFps || 0)
    processedFps.value = Number(payload.processedFps || 0)
    latency.value = Number(payload.latencyMs || 0)
    gestureStream.value = mapProcessItems(payload.processItems)
    pinyinBuffer.value = String(payload.spellingBuffer || '')
    cachedBuffer.value = String(payload.cachedBuffer || '')
    stabilityProgress.value = Number(payload.stabilityProgress || 0)
  }

  const disconnectWebRtc = () => {
    if (!webrtcClient) {
      connectionState.value = 'idle'
      return
    }

    webrtcClient.disconnect()
    webrtcClient = null
    connectionState.value = 'idle'
  }

  const connectWebRtc = async (stream) => {
    disconnectWebRtc()
    connectionState.value = 'connecting'

    webrtcClient = createRecognitionWebRtcClient({
      mediaStream: stream,
      mode: selectedMode.value,
      onResult: handleServerMessage,
      onOpen: () => {
        connectionState.value = 'connected'
      },
      onClose: () => {
        connectionState.value = 'idle'
        webrtcClient = null
      },
      onConnectionStateChange: (state) => {
        connectionState.value = state
      },
      onError: (error) => {
        console.error(error)
      },
    })

    await webrtcClient.connect()
  }

  const startCamera = async () => {
    let stream = null

    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false,
      })

      localStream.value = stream
      isCameraActive.value = true
      resetDisplayState()

      await connectWebRtc(stream)
    } catch (error) {
      console.error(error)
      if (stream) {
        stream.getTracks().forEach((track) => {
          track.stop()
        })
      }
      isCameraActive.value = false
      localStream.value = null
      resetDisplayState()
      connectionState.value = 'idle'
      ElMessage.error(error?.message || '无法开启摄像头或连接 WebRTC 服务')
    }
  }

  const stopCamera = () => {
    disconnectWebRtc()
    isCameraActive.value = false
    resetDisplayState()
    clearActionToast()

    if (localStream.value) {
      localStream.value.getTracks().forEach((track) => {
        track.stop()
      })
      localStream.value = null
    }
  }

  const changeMode = (mode) => {
    if (selectedMode.value === mode) {
      return
    }

    selectedMode.value = mode
    resetDisplayState()

    if (!webrtcClient) {
      return
    }

    try {
      webrtcClient.setMode(mode)
    } catch (error) {
      console.error(error)
      ElMessage.error(error?.message || '模式切换失败')
    }
  }

  return {
    isCameraActive,
    connectionState,
    connectionText,
    selectedMode,
    inputFps,
    processedFps,
    latency,
    gestureStream,
    pinyinBuffer,
    cachedBuffer,
    stabilityProgress,
    localStream,
    overlayResult,
    isRecognitionReady,
    actionToast,
    actionTitle,
    deletedCacheChar,
    deletedCacheTick,
    clearActionToast,
    startCamera,
    stopCamera,
    changeMode,
  }
}
