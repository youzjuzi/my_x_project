import { defineStore } from 'pinia';
import { login as apiLogin, logout as apiLogout, getInfo as apiGetInfo ,register as apiRister} from '@/api/user';
import { getToken, setToken, removeToken } from '@/utils/auth';
import router, { resetRouter } from '@/router';
import tagsViewStore from './tagsView';
import permissionStore from './permission';

export interface IUserState {
  token: string,
  name: '',
  avatar: '',
  menuList: [],
  userId: null // 添加 userId
  email: '',
  phone: ''
}

export default defineStore({
  id: 'user',
  state: ():IUserState => ({
    token: getToken(),
    name: '',
    avatar: '',
    menuList: [],
    userId: null,
    email: '',
    phone: ''

  }),
  getters: {},
  actions: {
    // user login
    login(userInfo):Promise<void> {
      const { username, password } = userInfo;
      return new Promise((resolve, reject) => {
        apiLogin({ username: username.trim(), password: password }).then(response => {
          const { data } = response;
          this.token = data.token;
          this.userId = data.userId;
          setToken(data.token);
          resolve();
        }).catch(error => {
          reject(error);
        });
      });
    },
    // register
    register(userInfo):Promise<void> {
      const { username, password, email, phone} = userInfo
        return new Promise((resolve, reject) => {
        apiRister({
            username: username.trim(),
            password: password,
            email: email,
            phone: phone
        }).then(response => {
            const { data } = response;
            this.token = data.token;
            this.userId = data.userId;
            this.email = data.email;
            this.phone = data.phone;
            setToken(data.token);
            resolve();
          }).catch(error => {
            reject(error);
          });
        });
    },


    // get user info
    getInfo() {
      return new Promise((resolve, reject) => {
        apiGetInfo(this.token).then(response => {
          const { data } = response;

          if (!data) {
            reject('Verification failed, please Login again.');
          }

          const { name, avatar, menuList, userId } = data;

          this.name = name;
          this.avatar = avatar;
          this.menuList = menuList;
          this.userId = userId;
          resolve(data);
        }).catch(error => {
          reject(error);
        });
      });
    },

    // user logout
    logout():Promise<void> {
      return new Promise((resolve, reject) => {
        apiLogout(this.token).then(() => {
          this.token = '';
          removeToken();
          resetRouter();

          // reset visited views and cached views
          // to fixed https://github.com/PanJiaChen/vue-element-admin/issues/2485
          tagsViewStore().delAllViews();

          resolve();
        }).catch(error => {
          reject(error);
        });
      });
    },

    // remove token
    resetToken() {
      this.token = '';
      removeToken();
    },

    // dynamically modify permissions
    async changeRoles(role) {
      const token = role + '-token';

      this.token = token;
      setToken(token);

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const infoRes = await this.getInfo() as any;
      let roles = [];
      if (infoRes.roles) {
        roles = infoRes.roles;
      }

      resetRouter();

      // generate accessible routes map based on roles
      const accessRoutes = await permissionStore().generateRoutes(roles);
      // dynamically add accessible routes
      // router.addRoutes(accessRoutes);
      accessRoutes.forEach(item => {
        router.addRoute(item);
      });

      // reset visited views and cached views
      tagsViewStore().delAllViews();
    }
  }
});
