import { login, logout, getInfo, register } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { resetRouter } from '@/router'

const getDefaultState = () => {
  return {
    token: getToken(),
    name: '',
    avatar: '',
    menuList: [],
    userId: null // 添加 userId
  }
}

const state = getDefaultState()

const mutations = {
  RESET_STATE: (state) => {
    Object.assign(state, getDefaultState())
  },
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_MENU_LIST: (state, menuList) => {
    state.menuList = menuList
  },
  SET_USER_ID: (state, userId) => {
    state.userId = userId
  }
}

const actions = {

  // 用户注册
  register({ commit }, userInfo) {
    const { username, password, phone, captcha, codeKey } = userInfo
    return new Promise((resolve, reject) => {
      register({
        username: username.trim(),
        password: password,
        phone: phone.trim(),
        captcha: captcha.trim(),
        codeKey: codeKey
      }).then(response => {
        // eslint-disable-next-line no-empty-pattern
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // user login
  login({ commit }, userInfo) {
    const { username, password, captcha, codeKey } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password, captcha: captcha.trim(), codeKey: codeKey }).then(response => {
        const { data } = response
        commit('SET_USER_ID', data.userId) // 设置 userId
        commit('SET_TOKEN', data.token)
        setToken(data.token)
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // get user info
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo(state.token).then(response => {
        const { data } = response
        if (!data) {
          reject('Verification failed, please Login again.')
        }
        const { name, avatar, menuList, userId } = data // 添加 userId

        commit('SET_NAME', name)
        commit('SET_AVATAR', avatar)
        commit('SET_MENU_LIST', menuList)
        commit('SET_USER_ID', userId) // 设置 userId
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // user logout
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      logout(state.token).then(() => {
        removeToken() // must remove  token  first
        resetRouter()
        commit('RESET_STATE')
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // remove token
  resetToken({ commit }) {
    return new Promise(resolve => {
      removeToken() // must remove  token  first
      commit('RESET_STATE')
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

