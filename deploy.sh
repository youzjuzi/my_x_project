#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
COMPOSE="${COMPOSE:-docker compose}"
ALLOW_DIRTY="${ALLOW_DIRTY:-0}"
SKIP_BUILD="${SKIP_BUILD:-0}"

log() {
  printf '[%s] [信息] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  printf '[%s] [警告] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

fail() {
  printf '[%s] [错误] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
  exit 1
}

trap 'fail "部署在第 ${LINENO} 行附近失败，请查看上方日志。"' ERR

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "缺少必要命令：$1"
}

log "开始部署，项目目录：${APP_DIR}"
cd "${APP_DIR}"

require_cmd git
require_cmd docker

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "当前 APP_DIR 不是 Git 仓库。"

if [[ "${ALLOW_DIRTY}" != "1" ]] && [[ -n "$(git status --porcelain)" ]]; then
  warn "检测到服务器本地存在未提交改动，为避免覆盖现场，本次停止拉取。"
  warn "请先提交或暂存这些改动；如果确认要继续，可使用 ALLOW_DIRTY=1 ./deploy.sh。"
  git status --short
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"
log "当前分支：${CURRENT_BRANCH:-detached}"

log "开始拉取最新代码..."
git pull --ff-only

log "当前 Docker Compose 版本："
${COMPOSE} version

if [[ "${SKIP_BUILD}" == "1" ]]; then
  log "检测到 SKIP_BUILD=1，跳过镜像构建。"
else
  log "开始构建后端镜像..."
  ${COMPOSE} build backend

  log "开始构建前端镜像..."
  ${COMPOSE} build frontend
fi

log "开始启动服务..."
${COMPOSE} up -d

log "当前服务状态："
${COMPOSE} ps

log "后端最近日志："
${COMPOSE} logs backend --tail 80

log "前端最近日志："
${COMPOSE} logs frontend --tail 40

log "Redis 最近日志："
${COMPOSE} logs redis --tail 40

log "部署完成。"
