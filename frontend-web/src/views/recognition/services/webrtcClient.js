const DEFAULT_WEBRTC_URL = 'http://127.0.0.1:8002/webrtc/offer'

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

export function createRecognitionWebRtcClient(options) {
  const {
    mediaStream,
    offerUrl = DEFAULT_WEBRTC_URL,
    mode = 'digits',
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
    if (closed) {
      return
    }

    closed = true
    if (typeof onClose === 'function') {
      onClose()
    }
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
        if (!peerConnection) {
          return
        }

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
        if (typeof onOpen === 'function') {
          onOpen()
        }
        dataChannel.send(`mode:${currentMode}`)
      }

      dataChannel.onclose = () => {
        safeOnClose()
      }

      dataChannel.onerror = (error) => {
        const message = error?.message || 'WebRTC data channel error'
        if (typeof onError === 'function') {
          onError(new Error(message))
        }
      }

      dataChannel.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data)
          if (typeof onResult === 'function') {
            onResult(payload)
          }
        } catch (error) {
          if (typeof onError === 'function') {
            onError(error)
          }
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
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sdp: peerConnection.localDescription?.sdp,
          type: peerConnection.localDescription?.type,
          mode: currentMode
        })
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || `WebRTC offer failed with HTTP ${response.status}`)
      }

      const answer = await response.json()
      await peerConnection.setRemoteDescription(answer)
    } catch (error) {
      disconnect()
      if (typeof onError === 'function') {
        onError(error)
      }
      throw error
    }
  }

  return {
    connect,
    disconnect,
    setMode(nextMode) {
      currentMode = nextMode
      if (dataChannel && dataChannel.readyState === 'open') {
        dataChannel.send(`mode:${currentMode}`)
      }
    },
  }
}
