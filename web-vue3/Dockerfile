# 1.构建阶段
FROM node:22-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
# 设置npm镜像
RUN npm config set registry https://registry.npmmirror.com
RUN npm install
COPY . .

RUN npm run build:prod

# 2.nginx部署
FROM nginx:alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]