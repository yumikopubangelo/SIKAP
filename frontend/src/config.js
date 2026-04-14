export const apiBaseUrl = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
export const manualInputPath = '/guru-piket/manual-input'
export const userManagementPath = '/admin/users'
export const prayerTimePath = '/admin/waktu-sholat'
export const profilePath = '/profil'
export const schoolDataPath = '/data-sekolah'
export const reportPath = '/laporan'
export const notificationPath = '/notifikasi'
export const mqttWsUrl = import.meta.env.VITE_MQTT_WS_URL || 'ws://localhost:9001'
export const mqttTopicAbsensi = import.meta.env.VITE_MQTT_TOPIC_ABSENSI || 'absensi/realtime'

export const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'kepsek', label: 'Kepala Sekolah' },
  { value: 'wali_kelas', label: 'Wali Kelas' },
  { value: 'guru_piket', label: 'Guru Piket' },
  { value: 'siswa', label: 'Siswa' },
  { value: 'orangtua', label: 'Orang Tua' },
]

export const roleLabels = Object.fromEntries(roleOptions.map((role) => [role.value, role.label]))

export const dashboardTitles = {
  admin: 'Dashboard Admin',
  kepsek: 'Dashboard Kepala Sekolah',
  wali_kelas: 'Dashboard Wali Kelas',
  guru_piket: 'Dashboard Guru Piket',
  siswa: 'Dashboard Siswa',
  orangtua: 'Dashboard Orang Tua',
}

export const waktuSholatOptions = [
  { value: 'dzuhur', label: 'Dzuhur' },
  { value: 'ashar', label: 'Ashar' },
  { value: 'maghrib', label: 'Maghrib' },
]

export const statusAbsensiOptions = [
  { value: 'tepat_waktu', label: 'Tepat Waktu' },
  { value: 'terlambat', label: 'Terlambat' },
  { value: 'alpha', label: 'Alpha' },
  { value: 'izin', label: 'Izin' },
  { value: 'sakit', label: 'Sakit' },
  { value: 'haid', label: 'Haid' },
]

export const waktuSholatLabels = Object.fromEntries(
  waktuSholatOptions.map((option) => [option.value, option.label]),
)

export const statusAbsensiLabels = Object.fromEntries(
  statusAbsensiOptions.map((option) => [option.value, option.label]),
)

export const trendLineSeries = [
  { key: 'total', label: 'Total Hadir', color: '#0f8f9f' },
  { key: 'tepat_waktu', label: 'Tepat Waktu', color: '#167a47' },
  { key: 'terlambat', label: 'Terlambat', color: '#f6a63b' },
]

export const statusChartColors = {
  tepat_waktu: '#167a47',
  terlambat: '#f6a63b',
  izin: '#2f74b5',
  sakit: '#0f8f9f',
  alpha: '#b6243b',
  haid: '#9b5b1b',
}

export const schoolProfileFallback = {
  name: 'SMK Bina Putera Nusantara',
  system: 'SIKAP',
  tagline: 'Sistem absensi sholat untuk SMK Bina Putera Nusantara.',
  focus: 'Monitoring kehadiran sholat, rekap sekolah, dan administrasi pengguna.',
}
