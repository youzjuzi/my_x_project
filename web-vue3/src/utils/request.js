import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import store from '@/store';
import { getToken } from '@/utils/auth';
import router from '@/router';

console.log('import.meta.env=', import.meta.env);

// create an axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_BASE_API, // url = base url + request url
  // withCredentials: true, // send cookies when cross-domain requests
  timeout: 30000 // request timeout (30 seconds)
});

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.user().token) {
      // let each request carry token
      // ['X-Token'] is a custom headers key
      // please modify it according to the actual situation
      config.headers['X-Token'] = getToken();
    }
    return config;
  },
  error => {
    // do something with request error
    console.log(error); // for debug
    return Promise.reject(error);
  }
);

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
  */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    const res = response.data;

    // if the custom code is not 20000, it is judged as an error.
    if (res.code !== 20000) {
      ElMessage({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      });

      // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
      if (res.code === 50008 || res.code === 50012 || res.code === 50014) {
        // to re-login
        ElMessageBox.confirm('You have been logged out, you can cancel to stay on this page, or log in again', 'Confirm logout', {
          confirmButtonText: 'Re-Login',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          store.user().resetToken();
          location.reload();
        });
      }
      return Promise.reject(new Error(res.message || 'Error'));
    } else {
      return res;
    }
  },
  error => {
    console.log(error); // for debug

    // 处理 HTTP 401 未授权错误 - Token 过期或无效
    if (error.response && error.response.status === 401) {
      // 1. 弹出轻提示
      ElMessage.error('登录已过期，请重新登录')

      // 2. 清除 Token
      store.user().resetToken()

      // 3. 这里的关键：不要用 location.reload()，那是“硬刷新”，体验不好
      // 应该用路由跳转到登录页，并带上当前页面路径，方便登录后跳回来
      router.push({
        path: '/login',
        query: { redirect: router.currentRoute.value.fullPath }
      })

      return Promise.reject(new Error('登录已过期'))
    }

    ElMessage({
      message: error.message,
      type: 'error',
      duration: 5 * 1000
    });
    return Promise.reject(error);
  }
);

export default service;
