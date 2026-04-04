/**
 * 帮助引导对话框的所有静态数据
 * 统一管理，避免堆在组件内部
 */

/* Tab 定义 */
export const HELP_TABS = [
  { key: 'quickstart', emoji: '🚀', label: '快速上手' },
  { key: 'alphabet',   emoji: '✋', label: '手势字母' },
  { key: 'commands',   emoji: '🎮', label: '指令手势' },
  { key: 'pinyin',     emoji: '⌨️', label: '拼音输入' },
  { key: 'faq',        emoji: '❓', label: '常见问题' },
]

/* Tab 1: 快速上手步骤 */
export const QUICK_START_STEPS = [
  {
    title: '开启摄像头',
    desc: '点击视频区域的「开启摄像头」按钮，允许浏览器摄像头权限。系统将自动连接识别服务。',
  },
  {
    title: '比划手势',
    desc: '面对摄像头比划 ASL 字母手势，画面中会实时显示识别框和字母标签。',
  },
  {
    title: '拼写拼音',
    desc: '连续比划字母手势拼出拼音（如 n-i-h-a-o），底部拼音缓冲区会实时显示拼写进度。',
  },
  {
    title: '确认选词',
    desc: '使用「确认」指令手势选择候选汉字，确认的词语进入暂存区，可以继续拼写下一个词。',
  },
  {
    title: '提交润色',
    desc: '使用「提交」指令手势将暂存的所有词语发送给 AI 润色，生成通顺的语句并显示在结果区。',
  },
]

/* Tab 2: 手势字母表 */
export const LETTER_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map((c) => ({
  char: c,
  label: c,
  image: `https://avatar.youzilite.us.kg/letter/${c}.png`,
}))

export const DIGIT_ALPHABET = '0123456789'.split('').map((c) => ({
  char: c,
  label: c,
  image: `https://avatar.youzilite.us.kg/number/${c}.png`,
}))

/* Tab 3: 指令手势 */
export const COMMAND_GESTURES = [
  {
    key: 'confirm',
    symbol: '✓',
    label: '确认',
    hint: '保持手势',
    color: '#25a165',
    bg: 'rgba(37, 161, 101, 0.08)',
    desc: '确认当前候选词，将词语加入暂存等待区。',
  },
  {
    key: 'delete',
    symbol: '←',
    label: '删除',
    hint: '继续按住',
    color: '#d74a4a',
    bg: 'rgba(215, 74, 74, 0.08)',
    desc: '删除拼音缓冲区最后一个字符，支持逐字回退。',
  },
  {
    key: 'clear',
    symbol: '✕',
    label: '清空',
    hint: '继续按住',
    color: '#f0822b',
    bg: 'rgba(240, 130, 43, 0.08)',
    desc: '清空当前所有拼写内容，重新开始输入。',
  },
  {
    key: 'next',
    symbol: '→',
    label: '下一个',
    hint: '保持手势',
    color: '#4a8fd7',
    bg: 'rgba(74, 143, 215, 0.08)',
    desc: '切换到下一个候选词，在多个候选间循环选择。',
  },
  {
    key: 'submit',
    symbol: '↑',
    label: '提交',
    hint: '保持手势',
    color: '#8b5cf6',
    bg: 'rgba(139, 92, 246, 0.08)',
    desc: '将暂存区的所有词语提交至 AI 进行润色生成句子。',
  },
]

/* Tab 4: 拼音输入流程节点 */
export const PINYIN_FLOW_NODES = [
  { icon: '✋', title: '比划字母', detail: '手势识别' },
  { icon: '🔤', title: '字母缓存', detail: '稳定确认' },
  { icon: '📝', title: '拼音拼写', detail: '自动匹配' },
  { icon: '📋', title: '候选词', detail: '切换选择' },
  { icon: '✅', title: '确认词语', detail: '进入暂存' },
  { icon: '🤖', title: 'AI 润色', detail: '生成句子' },
]

/* Tab 5: FAQ 列表 */
export const FAQ_LIST = [
  {
    key: 'camera',
    question: '摄像头打不开怎么办？',
    answer:
      '请确保浏览器已授予摄像头权限。在 Chrome 中，点击地址栏左侧的锁头图标，确认摄像头权限为"允许"。如果使用的是笔记本电脑，请检查是否有物理开关关闭了摄像头。另外，确保没有其他程序正在占用摄像头。',
  },
  {
    key: 'accuracy',
    question: '识别准确率不高，如何提升？',
    answer:
      '建议在光线充足的环境下使用，避免背光。手势尽量位于画面中央，手指清晰可见。保持手势稳定 1~2 秒，让系统有足够时间识别。可以先在「手势练习」模块练习标准手势。',
  },
  {
    key: 'not-recognized',
    question: '手势没有被识别是什么原因？',
    answer:
      '可能的原因包括：1) 手势不在摄像头可视范围内；2) 手势角度偏差较大；3) 背景过于复杂干扰了检测；4) WebRTC 连接断开（检查左上角状态标签）。请尝试将手放在画面正中央，并确保连接状态为"识别中"。',
  },
  {
    key: 'latency',
    question: '延迟太高如何优化？',
    answer:
      '识别延迟主要受网络环境影响。建议使用有线网络或稳定的 Wi-Fi 连接。关闭带宽占用大的程序（如视频下载）。当前延迟值显示在视频画面左上角的状态徽章上，理想延迟应在 200ms 以内。',
  },
  {
    key: 'browser',
    question: '支持哪些浏览器？',
    answer:
      '推荐使用最新版 Chrome（90+）或 Edge（90+），这两款浏览器对 WebRTC 和摄像头 API 支持最好。Firefox 也可使用，但部分功能可能有兼容性差异。不建议使用 Safari 或 IE。',
  },
  {
    key: 'mode-switch',
    question: '如何切换数字/字母模式？',
    answer:
      '在工作台控制栏右侧，点击模式切换按钮即可在「字母识别」和「数字识别」之间切换。切换后识别系统会自动重新校准，当前拼写内容会被清空。',
  },
]
