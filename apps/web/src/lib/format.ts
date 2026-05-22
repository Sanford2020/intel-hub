/**
 * Unified date/time formatting utilities (Chinese locale).
 */

const zhDateFmt = new Intl.DateTimeFormat("zh-CN", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

const zhDateTimeFmt = new Intl.DateTimeFormat("zh-CN", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

const zhTimeFmt = new Intl.DateTimeFormat("zh-CN", {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export function formatDateZh(date: string | Date): string {
  return zhDateFmt.format(new Date(date));
}

export function formatDateTimeZh(date: string | Date): string {
  return zhDateTimeFmt.format(new Date(date));
}

export function formatTimeZh(date: string | Date): string {
  return zhTimeFmt.format(new Date(date));
}

export function relativeTime(date: string | Date): string {
  const now = Date.now();
  const ts = new Date(date).getTime();
  const diff = now - ts;
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins} 分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} 小时前`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} 天前`;
  return formatDateZh(date);
}
