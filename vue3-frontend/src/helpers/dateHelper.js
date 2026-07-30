export function formatWIB(dateStr, options = {}) {
  if (!dateStr) return '\u2014'
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }
  const merged = { ...defaultOptions, ...options }
  const hasTz = /[Zz]|[+-]\d{2}:\d{2}$/.test(dateStr)
  const date = hasTz ? new Date(dateStr) : new Date(dateStr + '+07:00')
  return new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Jakarta',
    ...merged,
  }).format(date)
}
