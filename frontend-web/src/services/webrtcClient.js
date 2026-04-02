/**
 * 公共 WebRTC 识别客户端
 * 供识别端（recognition）和练习端（practice）共享使用
 * 不要在此处写业务逻辑，只负责建立连接、收发数据
 */

const DEFAULT_WEBRTC_URL = (import.meta.env.VITE_AI_SERVER_URL || 'http://127.0.0.1:8002') + '/webrtc/offer'

function waitForIceGatheringComplete(pc) {
  if (pc.iceGatheringState === 'complete') {
    return Promise.resolve()
  }

  return new Promise((resolve) => {
    const timeoutId = window.setTimeout(() => {
      pc.removeEventListener('icegatheringstatechange', handleStateChange)
      resolve()
    }, 1500)

    function handleStateChange() {
      if (pc.iceGatheringState === 'complete') {
        window.clearTimeout(timeoutId)
        pc.removeEventListener('icegatheringstatechange', handleStateChange)
        resolve()
      }
    }

    pc.addEventListener('icegatheringstatechange', handleStateChange)
  })
}

/**
 * 创建 WebRTC 识别客户端
 * @param {object} options
 * @param {MediaStream}  options.mediaStream            - 摄像头媒体流
 * @param {string}       [options.offerUrl]             - WebRTC offer 接口地址
 * @param {string}       [options.mode='letters']       - 识别模式：letters / digits
 * @param {function}     options.onResult               - 收到 AI 推送数据的回调
 * @param {function}     [options.onOpen]               - DataChannel 建立成功回调
 * @param {function}     [options.onClose]              - 连接关闭回调
 * @param {function}     [options.onError]              - 错误回调
 * @param {function}     [options.onConnectionStateChange] - PeerConnection 状态变化回调
 */
export function createRecognitionWebRtcClient(options) {
  const {
    mediaStream,
    offerUrl = DEFAULT_WEBRTC_URL,
    mode = 'letters',
    onResult,
    onOpen,
    onClose,
    onError,
    onConnectionStateChange
  } = options

  let peerConnection = null
  let dataChannel = null
  let closed = false
  let currentMode = mode

  const safeOnClose = () => {
    if (closed) return
    closed = true
    if (typeof onClose === 'function') onClose()
  }

  const disconnect = () => {
    if (dataChannel) {
      dataChannel.onopen = null
      dataChannel.onmessage = null
      dataChannel.onerror = null
      dataChannel.onclose = null
      dataChannel.close()
      dataChannel = null
    }

    if (peerConnection) {
      peerConnection.onconnectionstatechange = null
      peerConnection.close()
      peerConnection = null
    }

    safeOnClose()
  }

  const connect = async () => {
    if (!mediaStream) {
      throw new Error('Media stream is required for WebRTC connection.')
    }

    try {
      peerConnection = new RTCPeerConnection()

      peerConnection.onconnectionstatechange = () => {
        if (!peerConnection) return

        const state = peerConnection.connectionState
        if (typeof onConnectionStateChange === 'function') {
          onConnectionStateChange(state)
        }

        if (state === 'failed' || state === 'closed' || state === 'disconnected') {
          disconnect()
        }
      }

      dataChannel = peerConnection.createDataChannel('results')

      dataChannel.onopen = () => {
        if (typeof onOpen === 'function') onOpen()
        // 连接建立后立即告知服务端当前模式
        dataChannel.send(`mode:${currentMode}`)
      }

      dataChannel.onclose = () => {
        safeOnClose()
      }

      dataChannel.onerror = (error) => {
        const message = error?.message || 'WebRTC data channel error'
        if (typeof onError === 'function') onError(new Error(message))
      }

      dataChannel.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data)
          if (typeof onResult === 'function') onResult(payload)
        } catch (error) {
          if (typeof onError === 'function') onError(error)
        }
      }

      mediaStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, mediaStream)
      })

      const offer = await peerConnection.createOffer()
      await peerConnection.setLocalDescription(offer)
      await waitForIceGatheringComplete(peerConnection)

      const response = await fetch(offerUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sdp: peerConnection.localDescription?.sdp,
          type: peerConnection.localDescription?.type,
          mode: currentMode,
        }),
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || `WebRTC offer failed with HTTP ${response.status}`)
      }

      const answer = await response.json()
      await peerConnection.setRemoteDescription(answer)
    } catch (error) {
      disconnect()
      if (typeof onError === 'function') onError(error)
      throw error
    }
  }

  return {
    connect,
    disconnect,
    /** 动态切换识别模式（连接中也可调用）*/
    setMode(nextMode) {
      currentMode = nextMode
      if (dataChannel && dataChannel.readyState === 'open') {
        dataChannel.send(`mode:${currentMode}`)
      }
    },
  }
}
