import { ref } from 'vue'
import useUserStore from '@/store/modules/user'

const STORAGE_PREFIX = 'practice_passed'

function getStorageKey(userId) {
  return `${STORAGE_PREFIX}_${userId ?? 'guest'}`
}

function createEmptyData() {
  return { letters: [], numbers: [], commands: [] }
}

function resolveBucket(mode) {
  if (mode === 'numbers') return 'numbers'
  if (mode === 'commands') return 'commands'
  return 'letters'
}

function loadFromStorage(key) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return createEmptyData()
    return { ...createEmptyData(), ...JSON.parse(raw) }
  } catch {
    return createEmptyData()
  }
}

function saveToStorage(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (e) {
    console.warn('[usePassedChars] 存储失败', e)
  }
}

export function usePassedChars() {
  const userStore = useUserStore()
  const _data = ref(null)

  const ensureLoaded = () => {
    if (!_data.value) {
      _data.value = loadFromStorage(getStorageKey(userStore.userId))
    }
    return _data.value
  }

  const persist = () => {
    saveToStorage(getStorageKey(userStore.userId), _data.value)
  }

  const markPassed = (char, mode) => {
    const data = ensureLoaded()
    const key = resolveBucket(mode)
    const upper = String(char).toUpperCase()
    if (!data[key].includes(upper)) {
      data[key] = [...data[key], upper]
      persist()
    }
  }

  const isCharPassed = (char, mode) => {
    const data = ensureLoaded()
    const key = resolveBucket(mode)
    return data[key].includes(String(char).toUpperCase())
  }

  const getPassedCount = (mode) => {
    const data = ensureLoaded()
    const key = resolveBucket(mode)
    return data[key].length
  }

  return { markPassed, isCharPassed, getPassedCount }
}
