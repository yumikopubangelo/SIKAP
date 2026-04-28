export function formatColumnLabel(column) {
  return column
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function formatCellValue(value) {
  if (value === null || value === undefined || value === '') {
    return '-'
  }

  if (typeof value === 'number') {
    return value.toLocaleString('id-ID')
  }

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(value)) {
    const parsed = new Date(value)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleString('id-ID')
    }
  }

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const parsed = new Date(`${value}T00:00:00`)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleDateString('id-ID')
    }
  }

  const STATUS_LABELS = {
    tepat_waktu: 'Tepat Waktu',
    terlambat: 'Terlambat',
    izin: 'Izin',
    sakit: 'Sakit',
    alpha: 'Alpha',
    haid: 'Haid',
    belum_ada: 'Belum Ada',
    online: 'Online',
    offline: 'Offline',
    pending: 'Menunggu',
    disetujui: 'Disetujui',
    ditolak: 'Ditolak',
  }
  if (typeof value === 'string' && STATUS_LABELS[value]) {
    return STATUS_LABELS[value]
  }

  return String(value)
}

export function formatOptionLabel(value, lookup) {
  const normalized = String(value || '').trim().toLowerCase()
  return lookup[normalized] || formatCellValue(value)
}

export function flattenApiErrors(errors) {
  if (!errors || typeof errors !== 'object') {
    return ''
  }

  return Object.values(errors)
    .flatMap((value) => (Array.isArray(value) ? value : [value]))
    .filter(Boolean)
    .join(' ')
}

export function getTodayInputValue() {
  const now = new Date()
  const adjusted = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
  return adjusted.toISOString().slice(0, 10)
}

export function buildInitialManualForm() {
  return {
    nisn: '',
    tanggal: getTodayInputValue(),
    waktu_sholat: 'dzuhur',
    status: 'tepat_waktu',
    keterangan: '',
  }
}

export function buildInitialUserForm() {
  return {
    username: '',
    full_name: '',
    email: '',
    no_telp: '',
    role: 'guru_piket',
    password: '',
    confirmPassword: '',
    nisn: '',
  }
}
