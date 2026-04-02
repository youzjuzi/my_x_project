import { ref } from 'vue'
import useUserStore from '@/store/modules/user'

// ========== localStorage key ==========
const STORAGE_PREFIX = 'practice_passed'

function getStorageKey(userId) {
  // 用 userId 隔离多账号数据，未登录时用 guest
  return `${STORAGE_PREFIX}_${userId ?? 'guest'}`
}

function loadFromStorage(key) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return { letters: [], numbers: [] }
    return JSON.parse(raw)
  } catch {
    return { letters: [], numbers: [] }
  }
}

function saveToStorage(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (e) {
    console.warn('[usePassedChars] 存储失败', e)
  }
}

// ========== composable ==========
export function usePassedChars() {
  const userStore = useUserStore()

  // 懒加载（userId 可能初始为 null，首次调用时再读取）
  const _data = ref(null)

  /** 确保数据已加载 */
  const ensureLoaded = () => {
    if (!_data.value) {
      _data.value = loadFromStorage(getStorageKey(userStore.userId))
    }
    return _data.value
  }

  /** 持久化到 localStorage */
  const persist = () => {
    saveToStorage(getStorageKey(userStore.userId), _data.value)
  }

  /**
   * 标记某字符已掌握
   * @param {string} char  字符，如 'A' / '3'
   * @param {string} mode  'letters' | 'numbers'
   */
  const markPassed = (char, mode) => {
    const data = ensureLoaded()
    const key = mode === 'numbers' ? 'numbers' : 'letters'
    const upper = String(char).toUpperCase()
    if (!data[key].includes(upper)) {
      data[key] = [...data[key], upper]
      persist()
    }
  }

  /**
   * 检查某字符是否已掌握
   * @param {string} char
   * @param {string} mode  'letters' | 'numbers'
   * @returns {boolean}
   */
  const isCharPassed = (char, mode) => {
    const data = ensureLoaded()
    const key = mode === 'numbers' ? 'numbers' : 'letters'
    return data[key].includes(String(char).toUpperCase())
  }

  /**
   * 获取某模式下已掌握数量
   * @param {string} mode  'letters' | 'numbers'
   * @returns {number}
   */
  const getPassedCount = (mode) => {
    const data = ensureLoaded()
    const key = mode === 'numbers' ? 'numbers' : 'letters'
    return data[key].length
  }

  return { markPassed, isCharPassed, getPassedCount }
}
