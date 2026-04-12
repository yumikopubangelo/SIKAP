import { useEffect, useMemo, useRef, useState } from 'react'
import axios from 'axios'
import { Navigate, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom'
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'

const apiBaseUrl = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
const manualInputPath = '/guru-piket/manual-input'
const userManagementPath = '/admin/users'
const prayerTimePath = '/admin/waktu-sholat'
const profilePath = '/profil'
const schoolDataPath = '/data-sekolah'
import mqtt from 'mqtt'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import './App.css'

const apiBaseUrl =
  (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
const mqttWsUrl = import.meta.env.VITE_MQTT_WS_URL || 'ws://localhost:9001'
const mqttTopicAbsensi = import.meta.env.VITE_MQTT_TOPIC_ABSENSI || 'absensi/realtime'

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'kepsek', label: 'Kepala Sekolah' },
  { value: 'wali_kelas', label: 'Wali Kelas' },
  { value: 'guru_piket', label: 'Guru Piket' },
  { value: 'siswa', label: 'Siswa' },
  { value: 'orangtua', label: 'Orang Tua' },
]

const roleLabels = Object.fromEntries(roleOptions.map((role) => [role.value, role.label]))

const dashboardTitles = {
  admin: 'Dashboard Admin',
  kepsek: 'Dashboard Kepala Sekolah',
  wali_kelas: 'Dashboard Wali Kelas',
  guru_piket: 'Dashboard Guru Piket',
  siswa: 'Dashboard Siswa',
  orangtua: 'Dashboard Orang Tua',
}

const waktuSholatOptions = [
  { value: 'dzuhur', label: 'Dzuhur' },
  { value: 'ashar', label: 'Ashar' },
  { value: 'maghrib', label: 'Maghrib' },
]

const statusAbsensiOptions = [
  { value: 'tepat_waktu', label: 'Tepat Waktu' },
  { value: 'terlambat', label: 'Terlambat' },
  { value: 'alpha', label: 'Alpha' },
  { value: 'izin', label: 'Izin' },
  { value: 'sakit', label: 'Sakit' },
  { value: 'haid', label: 'Haid' },
]

const waktuSholatLabels = Object.fromEntries(
  waktuSholatOptions.map((option) => [option.value, option.label]),
)

const statusAbsensiLabels = Object.fromEntries(
  statusAbsensiOptions.map((option) => [option.value, option.label]),
)

const trendLineSeries = [
  { key: 'total', label: 'Total Hadir', color: '#0d5ca2' },
  { key: 'tepat_waktu', label: 'Tepat Waktu', color: '#0f6a37' },
  { key: 'terlambat', label: 'Terlambat', color: '#d98500' },
]

const statusChartColors = {
  tepat_waktu: '#0f6a37',
  terlambat: '#d98500',
  izin: '#3c7dd9',
  sakit: '#00838f',
  alpha: '#ac1f3a',
  haid: '#8f4a17',
}

const schoolProfileFallback = {
  name: 'SMK Bina Putra Nusantara',
  system: 'SIKAP',
  tagline: 'Sistem absensi sholat otomatis berbasis RFID & IoT untuk pemantauan kepatuhan ibadah peserta didik.',
  focus: 'Monitoring kehadiran sholat, rekap sekolah, dan administrasi multi-role.',
}

function formatColumnLabel(column) {
  return column
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function formatCellValue(value) {
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

  return String(value)
}

function formatOptionLabel(value, lookup) {
  const normalized = String(value || '').trim().toLowerCase()
  return lookup[normalized] || formatCellValue(value)
}

function flattenApiErrors(errors) {
  if (!errors || typeof errors !== 'object') {
    return ''
  }

  return Object.values(errors)
    .flatMap((value) => (Array.isArray(value) ? value : [value]))
    .filter(Boolean)
    .join(' ')
}

function getTodayInputValue() {
  const now = new Date()
  const adjusted = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
  return adjusted.toISOString().slice(0, 10)
}

function buildInitialManualForm() {
  return {
    nisn: '',
    tanggal: getTodayInputValue(),
    waktu_sholat: 'dzuhur',
    status: 'tepat_waktu',
    keterangan: '',
  }
}

function buildInitialUserForm() {
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

function DashboardCharts({ charts }) {
  const attendanceTrend = charts?.attendance_trend || {
    title: 'Trend Kehadiran',
    rows: [],
    note: 'Belum ada data trend.',
  }
  const statusDistribution = charts?.status_distribution || {
    title: 'Distribusi Status',
    rows: [],
    note: 'Belum ada distribusi status.',
  }

  const hasTrendData = attendanceTrend.rows?.some(
    (row) => row.total || row.tepat_waktu || row.terlambat,
  )
  const hasStatusData = statusDistribution.rows?.some((row) => row.value > 0)

  return (
    <section className="chart-grid">
      <section className="dashboard-panel chart-panel">
        <div className="panel-header">
          <div>
            <h2>{attendanceTrend.title}</h2>
            <p className="api-note">Line chart total hadir, tepat waktu, dan terlambat.</p>
          </div>
        </div>

        {hasTrendData ? (
          <div className="chart-shell">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={attendanceTrend.rows}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d9e6ef" />
                <XAxis dataKey="label" stroke="#587082" tickLine={false} axisLine={false} />
                <YAxis
                  allowDecimals={false}
                  stroke="#587082"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  formatter={(value, name) => [
                    formatCellValue(value),
                    trendLineSeries.find((item) => item.key === name)?.label || name,
                  ]}
                  labelFormatter={(label, payload) => payload?.[0]?.payload?.date || label}
                />
                <Legend
                  formatter={(value) =>
                    trendLineSeries.find((item) => item.key === value)?.label || value
                  }
                />
                {trendLineSeries.map((line) => (
                  <Line
                    key={line.key}
                    type="monotone"
                    dataKey={line.key}
                    stroke={line.color}
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="empty-state compact">
            <p>{attendanceTrend.note || 'Belum ada data trend untuk ditampilkan.'}</p>
          </div>
        )}
      </section>

      <section className="dashboard-panel chart-panel">
        <div className="panel-header">
          <div>
            <h2>{statusDistribution.title}</h2>
            <p className="api-note">Pie chart distribusi status absensi pada periode yang sama.</p>
          </div>
        </div>

        {hasStatusData ? (
          <>
            <div className="chart-shell">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={statusDistribution.rows}
                    dataKey="value"
                    nameKey="label"
                    innerRadius={60}
                    outerRadius={92}
                    paddingAngle={3}
                  >
                    {statusDistribution.rows.map((entry) => (
                      <Cell
                        key={entry.status}
                        fill={statusChartColors[entry.status] || '#0d5ca2'}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, _name, item) => [formatCellValue(value), item?.payload?.label]} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-stat-list">
              {statusDistribution.rows.map((item) => (
                <div key={item.status} className="chart-stat">
                  <span
                    className="chart-dot"
                    style={{ backgroundColor: statusChartColors[item.status] || '#0d5ca2' }}
                  />
                  <span>{item.label}</span>
                  <strong>{formatCellValue(item.value)}</strong>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="empty-state compact">
            <p>{statusDistribution.note || 'Belum ada distribusi status untuk ditampilkan.'}</p>
          </div>
        )}
      </section>
    </section>
  )
}

function ProfilePage({ authUser, dashboardData, onBackToDashboard, onLogout }) {
  const profileCards = dashboardData?.cards || []
  const linkedStudent = dashboardData?.student || null

  return (
    <AppShell
      authUser={authUser}
      eyebrow="F026 Profil Pengguna"
      title="Profil Pengguna"
      subtitle="Ringkasan identitas akun, role aktif, dan informasi operasional yang berkaitan dengan akses Anda di SIKAP."
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      <section className="manual-grid">
        <section className="dashboard-panel manual-panel">
          <div className="panel-header">
            <div>
              <h2>Identitas Akun</h2>
              <p className="api-note">
                Data ini diambil dari sesi login aktif dan endpoint profil pengguna.
              </p>
            </div>
          </div>

          <dl className="detail-list">
            <div><dt>Nama Lengkap</dt><dd>{authUser.full_name || '-'}</dd></div>
            <div><dt>Username</dt><dd>{authUser.username || '-'}</dd></div>
            <div><dt>Email</dt><dd>{authUser.email || '-'}</dd></div>
            <div><dt>No. Telepon</dt><dd>{authUser.no_telp || '-'}</dd></div>
            <div><dt>Role</dt><dd>{roleLabels[authUser.role] || authUser.role}</dd></div>
            <div><dt>ID User</dt><dd>{authUser.id_user || '-'}</dd></div>
          </dl>
        </section>

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel highlighted-panel">
            <div className="panel-header">
              <div>
                <h2>Ringkasan Aktivitas</h2>
                <p className="api-note">
                  Kartu ini mengikuti payload dashboard sesuai role Anda.
                </p>
              </div>
            </div>

            {profileCards.length ? (
              <div className="mini-metrics-grid">
                {profileCards.map((card) => (
                  <article key={card.key} className="mini-metric-card">
                    <span>{card.label}</span>
                    <strong>{formatCellValue(card.value)}</strong>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Belum ada kartu ringkasan untuk role ini.</p>
              </div>
            )}
          </section>

          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Keterkaitan Data</h2>
              </div>
            </div>

            {linkedStudent ? (
              <dl className="detail-list">
                <div><dt>Nama Siswa</dt><dd>{linkedStudent.nama || '-'}</dd></div>
                <div><dt>NISN</dt><dd>{linkedStudent.nisn || '-'}</dd></div>
                <div><dt>Kelas</dt><dd>{linkedStudent.kelas || '-'}</dd></div>
                <div><dt>ID Siswa</dt><dd>{linkedStudent.id_siswa || '-'}</dd></div>
              </dl>
            ) : (
              <div className="empty-state compact">
                <p>
                  {authUser.role === 'orangtua'
                    ? 'Akun orang tua ini belum memiliki data anak yang terhubung.'
                    : 'Tidak ada relasi data tambahan yang tersedia untuk akun ini saat ini.'}
                </p>
              </div>
            )}
          </section>
        </aside>
      </section>
    </AppShell>
  )
}

function SchoolDataPage({ authUser, api, getAuthHeaders, onBackToDashboard, onLogout }) {
  const [schoolData, setSchoolData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchSchoolData = async () => {
      const headers = getAuthHeaders()
      if (!headers) {
        setError('Sesi login tidak ditemukan. Silakan login ulang.')
        setLoading(false)
        return
      }

      setLoading(true)
      try {
        const { data } = await api.get('/rekapitulasi/sekolah', { headers })
        if (!data?.success || !data?.data) {
          throw new Error('Respons data sekolah tidak valid.')
        }
        setSchoolData(data.data)
      } catch (requestError) {
        const apiMessage =
          requestError?.response?.data?.message ||
          requestError?.message ||
          'Gagal memuat data sekolah.'
        setError(apiMessage)
      } finally {
        setLoading(false)
      }
    }

    void fetchSchoolData()
  }, [])

  const summary = schoolData?.summary || null
  const kelasRows = schoolData?.kelas || []

  return (
    <AppShell
      authUser={authUser}
      eyebrow="F027 Data Sekolah"
      title="Data Sekolah"
      subtitle="Ringkasan identitas sekolah dan performa kehadiran lintas kelas berdasarkan data rekap sekolah."
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}

      <section className="manual-grid">
        <section className="dashboard-panel manual-panel highlighted-panel">
          <div className="panel-header">
            <div>
              <h2>Profil Sekolah</h2>
              <p className="api-note">
                Identitas dasar sekolah saat ini masih memakai konfigurasi frontend yang aman sebagai fallback.
              </p>
            </div>
          </div>

          <dl className="detail-list">
            <div><dt>Nama Sekolah</dt><dd>{schoolProfileFallback.name}</dd></div>
            <div><dt>Sistem</dt><dd>{schoolProfileFallback.system}</dd></div>
            <div><dt>Fokus</dt><dd>{schoolProfileFallback.focus}</dd></div>
            <div><dt>Tagline</dt><dd>{schoolProfileFallback.tagline}</dd></div>
          </dl>
        </section>

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Ringkasan Rekap</h2>
                <p className="api-note">
                  Statistik global kehadiran seluruh sekolah dari endpoint rekapitulasi.
                </p>
              </div>
            </div>

            {loading ? (
              <div className="empty-state compact">
                <p>Memuat ringkasan sekolah...</p>
              </div>
            ) : summary ? (
              <div className="mini-metrics-grid">
                <article className="mini-metric-card">
                  <span>Tepat Waktu</span>
                  <strong>{formatCellValue(summary.tepat_waktu)}</strong>
                </article>
                <article className="mini-metric-card">
                  <span>Terlambat</span>
                  <strong>{formatCellValue(summary.terlambat)}</strong>
                </article>
                <article className="mini-metric-card">
                  <span>Alpha</span>
                  <strong>{formatCellValue(summary.alpha)}</strong>
                </article>
                <article className="mini-metric-card">
                  <span>Persentase</span>
                  <strong>{summary.persentase}%</strong>
                </article>
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Ringkasan sekolah belum tersedia.</p>
              </div>
            )}
          </section>
        </aside>
      </section>

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Performa per Kelas</h2>
            <p className="api-note">
              Tabel rekap kehadiran lintas kelas dari endpoint `rekapitulasi/sekolah`.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state compact">
            <p>Memuat data performa kelas...</p>
          </div>
        ) : kelasRows.length ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Kelas</th>
                  <th>Tepat Waktu</th>
                  <th>Terlambat</th>
                  <th>Alpha</th>
                  <th>Izin</th>
                  <th>Sakit</th>
                  <th>Haid</th>
                  <th>Persentase</th>
                </tr>
              </thead>
              <tbody>
                {kelasRows.map((row) => (
                  <tr key={row.id_kelas}>
                    <td>{row.nama_kelas}</td>
                    <td>{formatCellValue(row.tepat_waktu)}</td>
                    <td>{formatCellValue(row.terlambat)}</td>
                    <td>{formatCellValue(row.alpha)}</td>
                    <td>{formatCellValue(row.izin)}</td>
                    <td>{formatCellValue(row.sakit)}</td>
                    <td>{formatCellValue(row.haid)}</td>
                    <td>{row.persentase}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>Belum ada data rekap sekolah untuk ditampilkan.</p>
          </div>
        )}
      </section>
    </AppShell>
  )
}

function PrayerTimeSettingsPage({ authUser, api, getAuthHeaders, onBackToDashboard, onLogout }) {
  const [times, setTimes] = useState([])
  const [loading, setLoading] = useState(true)
  const [savingId, setSavingId] = useState(null)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const fetchPrayerTimes = async () => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      setLoading(false)
      return
    }

    setLoading(true)
    try {
      const { data } = await api.get('/waktu-sholat', { headers })
      if (!data?.success || !Array.isArray(data?.data)) {
        throw new Error('Respons waktu sholat tidak valid.')
      }

      setTimes(
        data.data.map((item) => ({
          ...item,
          waktu_adzan: (item.waktu_adzan || '').slice(0, 5),
          waktu_iqamah: (item.waktu_iqamah || '').slice(0, 5),
          waktu_selesai: (item.waktu_selesai || '').slice(0, 5),
        })),
      )
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat waktu sholat.'
      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchPrayerTimes()
  }, [])

  const handleTimeChange = (id, field, value) => {
    setTimes((prev) =>
      prev.map((item) => (item.id_waktu === id ? { ...item, [field]: value } : item)),
    )
  }

  const handleSavePrayerTime = async (item) => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSavingId(item.id_waktu)
    setError('')
    setSuccessMessage('')

    try {
      const { data } = await api.put(
        `/waktu-sholat/${item.id_waktu}`,
        {
          waktu_adzan: item.waktu_adzan,
          waktu_iqamah: item.waktu_iqamah,
          waktu_selesai: item.waktu_selesai,
        },
        { headers },
      )

      if (!data?.success || !data?.data) {
        throw new Error('Respons update waktu sholat tidak valid.')
      }

      setSuccessMessage(data.message || 'Waktu sholat berhasil diupdate.')
      setTimes((prev) =>
        prev.map((row) =>
          row.id_waktu === item.id_waktu
            ? {
                ...row,
                waktu_adzan: (data.data.waktu_adzan || '').slice(0, 5),
                waktu_iqamah: (data.data.waktu_iqamah || '').slice(0, 5),
                waktu_selesai: (data.data.waktu_selesai || '').slice(0, 5),
              }
            : row,
        ),
      )
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal mengupdate waktu sholat.'
      setError(apiMessage)
    } finally {
      setSavingId(null)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="F013 Pengaturan Waktu"
      title="Pengaturan Waktu Sholat"
      subtitle="Kelola waktu adzan, iqamah, dan selesai untuk setiap sesi sholat yang dipakai sistem absensi."
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Daftar Waktu Sholat</h2>
            <p className="api-note">
              Perubahan di halaman ini akan memengaruhi logika sesi aktif dan timestamp default input manual.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state compact">
            <p>Memuat pengaturan waktu sholat...</p>
          </div>
        ) : times.length ? (
          <div className="settings-grid">
            {times.map((item) => (
              <article key={item.id_waktu} className="setting-card">
                <div className="setting-card-head">
                  <h2>{item.nama_sholat}</h2>
                  <span className="status-chip prayer">{item.nama_sholat}</span>
                </div>

                <div className="manual-form-grid">
                  <div className="manual-field">
                    <label htmlFor={`adzan-${item.id_waktu}`}>Waktu Adzan</label>
                    <input
                      id={`adzan-${item.id_waktu}`}
                      type="time"
                      value={item.waktu_adzan}
                      onChange={(event) =>
                        handleTimeChange(item.id_waktu, 'waktu_adzan', event.target.value)
                      }
                    />
                  </div>

                  <div className="manual-field">
                    <label htmlFor={`iqamah-${item.id_waktu}`}>Waktu Iqamah</label>
                    <input
                      id={`iqamah-${item.id_waktu}`}
                      type="time"
                      value={item.waktu_iqamah}
                      onChange={(event) =>
                        handleTimeChange(item.id_waktu, 'waktu_iqamah', event.target.value)
                      }
                    />
                  </div>

                  <div className="manual-field manual-field-full">
                    <label htmlFor={`selesai-${item.id_waktu}`}>Waktu Selesai</label>
                    <input
                      id={`selesai-${item.id_waktu}`}
                      type="time"
                      value={item.waktu_selesai}
                      onChange={(event) =>
                        handleTimeChange(item.id_waktu, 'waktu_selesai', event.target.value)
                      }
                    />
                  </div>
                </div>

                <div className="manual-actions">
                  <button
                    type="button"
                    onClick={() => handleSavePrayerTime(item)}
                    disabled={savingId === item.id_waktu}
                  >
                    {savingId === item.id_waktu ? 'Menyimpan...' : 'Simpan Waktu'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>Belum ada data waktu sholat untuk ditampilkan.</p>
          </div>
        )}
      </section>
    </AppShell>
function LoadingSpinner({ label = 'Memuat...' }) {
  return (
    <span className="loading-inline" role="status" aria-live="polite" aria-label={label}>
      <span className="loading-spinner" aria-hidden="true" />
      <span>{label}</span>
    </span>
  )
}

function Toast({ toast, onClose }) {
  if (!toast?.message) {
    return null
  }

  return (
    <div className={`toast ${toast.type}`} role="alert" aria-live="assertive">
      <p>{toast.message}</p>
      <button type="button" className="toast-close" onClick={onClose} aria-label="Tutup notifikasi">
        ×
      </button>
    </div>
  )
}

function AuthPage({
  mode,
  loading,
  checkingSession,
  loginForm,
  registerForm,
  error,
  successMessage,
  onLoginChange,
  onRegisterChange,
  onLogin,
  onRegister,
  onSwitchMode,
  apiBaseUrlValue,
}) {
  const authBusy = loading || checkingSession
  const hasError = Boolean(error)

  return (
    <main className="login-page" aria-busy={authBusy}>
      <section className="login-card" aria-live="polite">
        <h1>SIKAP Auth</h1>
        <p className="subtitle">Sistem Informasi Kepatuhan Ibadah Peserta Didik</p>
        {checkingSession ? <p className="api-note">Memeriksa sesi login...</p> : null}

        <div className="mode-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'tab active' : 'tab'}
            onClick={() => onSwitchMode('login')}
            aria-pressed={mode === 'login'}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'tab active' : 'tab'}
            onClick={() => onSwitchMode('register')}
            aria-pressed={mode === 'register'}
          >
            Registrasi
          </button>
        </div>

        {mode === 'login' ? (
          <form onSubmit={onLogin} className="login-form" aria-busy={authBusy}>
            <label htmlFor="username">Username / Email</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              aria-invalid={hasError}
              aria-describedby={hasError ? 'auth-form-error' : undefined}
              value={loginForm.username}
              onChange={onLoginChange}
              placeholder="contoh: admin atau admin@sikap.local"
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              aria-invalid={hasError}
              aria-describedby={hasError ? 'auth-form-error' : undefined}
              value={loginForm.password}
              onChange={onLoginChange}
              placeholder="Masukkan password"
            />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? <LoadingSpinner label="Memproses..." /> : 'Masuk'}
            </button>
          </form>
        ) : (
          <form onSubmit={onRegister} className="login-form" aria-busy={authBusy}>
            <label htmlFor="register_username">Username</label>
            <input id="register_username" name="username" type="text" value={registerForm.username} onChange={onRegisterChange} placeholder="contoh: ahmad.fadil" />

            <label htmlFor="register_full_name">Nama Lengkap</label>
            <input id="register_full_name" name="full_name" type="text" value={registerForm.full_name} onChange={onRegisterChange} placeholder="Nama lengkap user" />

            <label htmlFor="register_email">Email</label>
            <input id="register_email" name="email" type="email" value={registerForm.email} onChange={onRegisterChange} placeholder="contoh: user@sikap.local" />

            <label htmlFor="register_no_telp">No. Telepon</label>
            <input id="register_no_telp" name="no_telp" type="text" value={registerForm.no_telp} onChange={onRegisterChange} placeholder="08xxxxxxxxxx" />

            <label htmlFor="register_role">Role</label>
            <select id="register_role" name="role" value={registerForm.role} onChange={onRegisterChange}>
              {roleOptions.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>

            <label htmlFor="register_password">Password</label>
            <input id="register_password" name="password" type="password" value={registerForm.password} onChange={onRegisterChange} placeholder="Minimal 8 karakter" />

            <label htmlFor="register_confirm_password">Konfirmasi Password</label>
            <input id="register_confirm_password" name="confirmPassword" type="password" value={registerForm.confirmPassword} onChange={onRegisterChange} placeholder="Ulangi password" />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? 'Memproses...' : 'Daftar'}
            </button>
          </form>
        )}

        {error ? <p className="alert error">{error}</p> : null}
        {successMessage ? <p className="alert success">{successMessage}</p> : null}
        <p className="api-note">
          Endpoint backend: {apiBaseUrlValue}/auth/login, /auth/me, /auth/logout, /dashboard, /users
        </p>
      </section>
    </main>
  )
}

function AppShell({ authUser, eyebrow, title, subtitle, actions, children }) {
  return (
    <main className="dashboard-page">
      <section className="dashboard-shell">
        <header className="dashboard-hero">
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <p className="subtitle dashboard-subtitle">{subtitle}</p>
          </div>
          <div className="dashboard-actions">{actions}</div>
        </header>

        <section className="identity-strip">
          <div className="identity-item">
            <span>Username</span>
            <strong>{authUser.username || '-'}</strong>
          </div>
          <div className="identity-item">
            <span>Email</span>
            <strong>{authUser.email || '-'}</strong>
          </div>
          <div className="identity-item">
            <span>Role</span>
            <strong>{roleLabels[authUser.role] || authUser.role}</strong>
          </div>
        </section>

        {children}
      </section>
    </main>
  )
}

function DashboardPage({
  authUser,
  dashboardData,
  dashboardLoading,
  error,
  successMessage,
  onRefresh,
  onOpenManualInput,
  onOpenProfile,
  onOpenSchoolData,
  onOpenPrayerTime,
  onOpenUserManagement,
  onLogout,
}) {
  const cards = dashboardData?.cards || []
  const charts = dashboardData?.charts || null
  const primaryTable = dashboardData?.primary_table || {
    title: 'Ringkasan',
    columns: [],
    rows: [],
    note: '',
  }

  const dashboardTitle = dashboardTitles[authUser.role] || 'Dashboard'

  return (
    <AppShell
      authUser={authUser}
      eyebrow={dashboardTitle}
      title={authUser.full_name || authUser.username}
      subtitle={`Masuk sebagai ${roleLabels[authUser.role] || authUser.role}. Dashboard ini menampilkan ringkasan data utama sesuai role Anda.`}
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onOpenProfile}>
            Profil
          </button>
          <button type="button" className="ghost-button" onClick={onOpenSchoolData}>
            Data Sekolah
          </button>
          {authUser.role === 'admin' ? (
            <button type="button" className="ghost-button" onClick={onOpenPrayerTime}>
              Waktu Sholat
            </button>
          ) : null}
          {authUser.role === 'admin' ? (
            <button type="button" className="ghost-button" onClick={onOpenUserManagement}>
              User Management
            </button>
          ) : null}
          {authUser.role === 'guru_piket' ? (
            <button type="button" className="ghost-button" onClick={onOpenManualInput}>
              Input Manual
            </button>
          ) : null}
          <button type="button" className="ghost-button" onClick={onRefresh}>
            Muat Ulang
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      {dashboardLoading ? (
        <section className="dashboard-panel">
          <p className="api-note">Memuat data dashboard...</p>
        </section>
      ) : null}

      {!dashboardLoading ? (
        <>
          <section className="metrics-grid">
            {cards.length ? (
              cards.map((card) => (
                <article key={card.key} className="metric-card">
                  <span>{card.label}</span>
                  <strong>{formatCellValue(card.value)}</strong>
                </article>
              ))
            ) : (
              <article className="metric-card empty">
                <span>Belum Ada Ringkasan</span>
                <strong>-</strong>
              </article>
            )}
          </section>

          <DashboardCharts charts={charts} />

          <section className="dashboard-panel">
            <div className="panel-header">
              <div>
                <h2>{primaryTable.title || 'Tabel Dashboard'}</h2>
                <p className="api-note">
                  {dashboardData?.generated_at
                    ? `Diperbarui ${formatCellValue(dashboardData.generated_at)}`
                    : 'Data dashboard sesuai role pengguna.'}
                </p>
              </div>
            </div>

            {primaryTable.rows?.length ? (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      {primaryTable.columns.map((column) => (
                        <th key={column}>{formatColumnLabel(column)}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {primaryTable.rows.map((row, index) => (
                      <tr key={`${primaryTable.title}-${index}`}>
                        {primaryTable.columns.map((column) => (
                          <td key={`${index}-${column}`}>{formatCellValue(row[column])}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <p>{primaryTable.note || 'Belum ada data untuk ditampilkan.'}</p>
              </div>
            )}
          </section>
        </>
      ) : null}
    </AppShell>
  )
}

function ManualInputPage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onLogout,
}) {
  const [form, setForm] = useState(buildInitialManualForm)
  const [studentCandidate, setStudentCandidate] = useState(null)
  const [lastCreatedAbsensi, setLastCreatedAbsensi] = useState(null)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [lookupError, setLookupError] = useState('')
  const [lookupMessage, setLookupMessage] = useState('')
  const [submitError, setSubmitError] = useState('')
  const [submitMessage, setSubmitMessage] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    const nextValue = name === 'nisn' ? value.replace(/\D/g, '').slice(0, 10) : value

    if (name === 'nisn' && form.nisn !== nextValue) {
      setStudentCandidate(null)
      setLookupError('')
      setLookupMessage('')
    }

    setFieldErrors((prev) => ({ ...prev, [name]: '' }))
    setForm((prev) => ({ ...prev, [name]: nextValue }))
  }

  const validateManualForm = (currentForm) => {
    const nextErrors = {}

    if (!/^\d{10}$/.test(currentForm.nisn)) {
      nextErrors.nisn = 'NISN harus terdiri dari 10 digit angka.'
    }
    if (!currentForm.tanggal) {
      nextErrors.tanggal = 'Tanggal wajib diisi.'
    }
    if (!currentForm.waktu_sholat) {
      nextErrors.waktu_sholat = 'Waktu sholat wajib dipilih.'
    }
    if (!currentForm.status) {
      nextErrors.status = 'Status absensi wajib dipilih.'
    }

    return nextErrors
  }

  const handleLookupStudent = async (explicitNisn) => {
    const nisn = (explicitNisn ?? form.nisn).trim()

    if (!/^\d{10}$/.test(nisn)) {
      setFieldErrors((prev) => ({
        ...prev,
        nisn: 'Masukkan NISN 10 digit sebelum validasi.',
      }))
      setStudentCandidate(null)
      setLookupError('')
      setLookupMessage('')
      return null
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setLookupError('Sesi login tidak ditemukan. Silakan login ulang.')
      return null
    }

    setLookupLoading(true)
    setLookupError('')
    setLookupMessage('')
    setFieldErrors((prev) => ({ ...prev, nisn: '' }))

    try {
      const { data } = await api.get('/auth/student-candidates', {
        headers,
        params: { nisn },
      })

      const student = data?.data?.student
      if (!data?.success || !student) {
        throw new Error('Respons validasi NISN tidak valid.')
      }

      const candidate = {
        ...student,
        has_account: Boolean(data?.data?.has_account),
      }

      setStudentCandidate(candidate)
      setLookupMessage(
        `NISN valid. ${candidate.nama}${candidate.kelas ? ` dari ${candidate.kelas}` : ''} siap diproses.`,
      )
      return candidate
    } catch (requestError) {
      const status = requestError?.response?.status
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memvalidasi NISN.'

      setStudentCandidate(null)

      if (status === 404) {
        setLookupError('NISN tidak ditemukan di data siswa.')
      } else if (status === 403) {
        setLookupError('Role saat ini belum diizinkan memvalidasi NISN.')
      } else {
        setLookupError(apiMessage)
      }

      return null
    } finally {
      setLookupLoading(false)
    }
  }

  const handleNisnBlur = () => {
    if (
      form.nisn.length === 10 &&
      (!studentCandidate || studentCandidate.nisn !== form.nisn)
    ) {
      void handleLookupStudent(form.nisn)
    }
  }

  const handleResetForm = () => {
    setForm(buildInitialManualForm())
    setStudentCandidate(null)
    setLastCreatedAbsensi(null)
    setLookupError('')
    setLookupMessage('')
    setSubmitError('')
    setSubmitMessage('')
    setFieldErrors({})
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitError('')
    setSubmitMessage('')

    const localErrors = validateManualForm(form)
    if (Object.keys(localErrors).length) {
      setFieldErrors(localErrors)
      return
    }

    let candidate = studentCandidate
    if (!candidate || candidate.nisn !== form.nisn) {
      candidate = await handleLookupStudent(form.nisn)
      if (!candidate) {
        return
      }
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setSubmitError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSubmitLoading(true)

    try {
      const payload = {
        siswa_id: candidate.id_siswa,
        tanggal: form.tanggal,
        waktu_sholat: form.waktu_sholat,
        status: form.status,
        keterangan: form.keterangan.trim() || undefined,
      }

      const { data } = await api.post('/absensi/manual', payload, { headers })

      if (!data?.success || !data?.data) {
        throw new Error('Respons absensi manual tidak valid.')
      }

      setLastCreatedAbsensi(data.data)
      setSubmitMessage(data.message || 'Absensi manual berhasil dicatat.')
      setFieldErrors({})
      setLookupError('')
      setLookupMessage('')
      setStudentCandidate(null)
      setForm((prev) => ({ ...prev, nisn: '', keterangan: '' }))
    } catch (requestError) {
      const apiErrors = requestError?.response?.data?.errors || {}
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menyimpan absensi manual.'

      setFieldErrors((prev) => ({
        ...prev,
        nisn: apiErrors?.siswa_id || prev.nisn || '',
        tanggal: apiErrors?.tanggal || '',
        waktu_sholat: apiErrors?.waktu_sholat || '',
        status: apiErrors?.status || '',
        keterangan: apiErrors?.keterangan || '',
      }))
      setSubmitError([apiMessage, flattenApiErrors(apiErrors)].filter(Boolean).join(' '))
    } finally {
      setSubmitLoading(false)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="F023 Manual Input"
      title="Manual Input Absensi"
      subtitle="Validasi NISN siswa, pilih sesi sholat, lalu simpan absensi manual untuk kasus kartu hilang, rusak, atau tertinggal."
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      <section className="manual-grid">
        <section className="dashboard-panel manual-panel">
          <div className="panel-header">
            <div>
              <h2>Form Absensi Manual</h2>
              <p className="api-note">
                NISN divalidasi dulu agar `siswa_id` yang dikirim ke backend sesuai data master siswa.
              </p>
            </div>
          </div>

          {submitError ? <p className="alert error">{submitError}</p> : null}
          {submitMessage ? <p className="alert success">{submitMessage}</p> : null}

          <form className="manual-form" onSubmit={handleSubmit}>
            <div className="manual-form-grid">
              <div className="manual-field manual-field-full">
                <label htmlFor="manual_nisn">NISN</label>
                <div className="lookup-row">
                  <input
                    id="manual_nisn"
                    name="nisn"
                    type="text"
                    inputMode="numeric"
                    value={form.nisn}
                    onChange={handleFieldChange}
                    onBlur={handleNisnBlur}
                    placeholder="Masukkan 10 digit NISN"
                    maxLength={10}
                  />
                  <button
                    type="button"
                    className="ghost-button lookup-button"
                    onClick={() => handleLookupStudent()}
                    disabled={lookupLoading || submitLoading}
                  >
                    {lookupLoading ? 'Memvalidasi...' : 'Validasi NISN'}
                  </button>
                </div>
                <p className="helper-text">
                  Validasi akan mencari siswa berdasarkan NISN dan menyiapkan `siswa_id` untuk submit manual input.
                </p>
                {fieldErrors.nisn ? <p className="field-error">{fieldErrors.nisn}</p> : null}
                {lookupError ? <p className="field-error">{lookupError}</p> : null}
                {lookupMessage ? <p className="field-success">{lookupMessage}</p> : null}
              </div>

              <div className="manual-field">
                <label htmlFor="manual_tanggal">Tanggal</label>
                <input id="manual_tanggal" name="tanggal" type="date" value={form.tanggal} onChange={handleFieldChange} />
                {fieldErrors.tanggal ? <p className="field-error">{fieldErrors.tanggal}</p> : null}
              </div>

              <div className="manual-field">
                <label htmlFor="manual_waktu_sholat">Waktu Sholat</label>
                <select id="manual_waktu_sholat" name="waktu_sholat" value={form.waktu_sholat} onChange={handleFieldChange}>
                  {waktuSholatOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {fieldErrors.waktu_sholat ? <p className="field-error">{fieldErrors.waktu_sholat}</p> : null}
              </div>

              <div className="manual-field">
                <label htmlFor="manual_status">Status</label>
                <select id="manual_status" name="status" value={form.status} onChange={handleFieldChange}>
                  {statusAbsensiOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {fieldErrors.status ? <p className="field-error">{fieldErrors.status}</p> : null}
              </div>

              <div className="manual-field manual-field-full">
                <label htmlFor="manual_keterangan">Keterangan</label>
                <textarea
                  id="manual_keterangan"
                  name="keterangan"
                  rows="4"
                  value={form.keterangan}
                  onChange={handleFieldChange}
                  placeholder="Contoh: kartu siswa tertinggal, diinput manual oleh guru piket."
                />
                <p className="helper-text">Keterangan opsional, tetapi sangat membantu untuk jejak audit.</p>
                {fieldErrors.keterangan ? <p className="field-error">{fieldErrors.keterangan}</p> : null}
              </div>
            </div>

            <div className="manual-actions">
              <button type="submit" disabled={submitLoading || lookupLoading}>
                {submitLoading ? 'Menyimpan...' : 'Simpan Absensi Manual'}
              </button>
              <button type="button" className="ghost-button" onClick={handleResetForm} disabled={submitLoading || lookupLoading}>
                Reset Form
              </button>
            </div>
          </form>
        </section>

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel highlighted-panel">
            <div className="panel-header">
              <div>
                <h2>Hasil Validasi NISN</h2>
                <p className="api-note">Data siswa akan muncul di sini setelah NISN berhasil dicek.</p>
              </div>
            </div>

            {studentCandidate ? (
              <div className="student-preview">
                <div className="student-preview-head">
                  <strong>{studentCandidate.nama}</strong>
                  <span className="status-chip info">
                    {studentCandidate.has_account ? 'Sudah punya akun' : 'Belum punya akun'}
                  </span>
                </div>

                <dl className="detail-list">
                  <div><dt>NISN</dt><dd>{studentCandidate.nisn}</dd></div>
                  <div><dt>Kelas</dt><dd>{studentCandidate.kelas || '-'}</dd></div>
                  <div><dt>ID Siswa</dt><dd>{studentCandidate.id_siswa}</dd></div>
                  <div><dt>ID Card</dt><dd>{studentCandidate.id_card || '-'}</dd></div>
                </dl>
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Belum ada siswa tervalidasi. Masukkan NISN lalu klik `Validasi NISN`.</p>
              </div>
            )}
          </section>

          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Input Terakhir</h2>
                <p className="api-note">Ringkasan absensi manual yang paling baru berhasil disimpan.</p>
              </div>
            </div>

            {lastCreatedAbsensi ? (
              <div className="submission-summary">
                <div className="chip-group">
                  <span className={`status-chip ${lastCreatedAbsensi.status}`}>
                    {formatOptionLabel(lastCreatedAbsensi.status, statusAbsensiLabels)}
                  </span>
                  <span className="status-chip prayer">
                    {formatOptionLabel(lastCreatedAbsensi.waktu_sholat, waktuSholatLabels)}
                  </span>
                </div>

                <dl className="detail-list">
                  <div><dt>Nama</dt><dd>{lastCreatedAbsensi.siswa?.nama || '-'}</dd></div>
                  <div><dt>NISN</dt><dd>{lastCreatedAbsensi.siswa?.nisn || '-'}</dd></div>
                  <div><dt>Kelas</dt><dd>{lastCreatedAbsensi.siswa?.kelas || '-'}</dd></div>
                  <div><dt>Tanggal</dt><dd>{formatCellValue(lastCreatedAbsensi.tanggal)}</dd></div>
                  <div><dt>Timestamp</dt><dd>{formatCellValue(lastCreatedAbsensi.timestamp)}</dd></div>
                  <div><dt>Keterangan</dt><dd>{lastCreatedAbsensi.keterangan || '-'}</dd></div>
                </dl>
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Belum ada absensi manual yang tersimpan pada sesi ini.</p>
              </div>
            )}
          </section>

          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div><h2>Panduan Singkat</h2></div>
            </div>

            <div className="tips-list">
              <p>1. Ketik NISN siswa sampai 10 digit, lalu validasi.</p>
              <p>2. Pilih tanggal dan waktu sholat sesuai kejadian absensi.</p>
              <p>3. Gunakan keterangan saat input dilakukan karena kartu hilang, rusak, atau tertinggal.</p>
              <p>4. Jika sistem menolak simpan, cek kemungkinan siswa sudah punya absensi pada sesi yang sama.</p>
            </div>
          </section>
        </aside>
      </section>
    </AppShell>
  )
}

function UserManagementPage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onOpenAddUser,
  onOpenEditUser,
  onLogout,
}) {
  const navigate = useNavigate()
  const location = useLocation()

  const [filters, setFilters] = useState({
    search: '',
    role: '',
  })
  const [appliedFilters, setAppliedFilters] = useState({
    search: '',
    role: '',
  })
  const [users, setUsers] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total_items: 0,
    total_pages: 1,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const fetchUsers = async ({ page, search, role } = {}) => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    const nextPage = page ?? pagination.page
    const nextSearch = search ?? appliedFilters.search
    const nextRole = role ?? appliedFilters.role

    setLoading(true)
    try {
      const { data } = await api.get('/users', {
        headers,
        params: {
          page: nextPage,
          limit: pagination.limit,
          search: nextSearch || undefined,
          role: nextRole || undefined,
        },
      })

      if (!data?.success || !Array.isArray(data?.data)) {
        throw new Error('Respons daftar user tidak valid.')
      }

      setUsers(data.data)
      setPagination((prev) => ({
        ...prev,
        page: data?.pagination?.page ?? nextPage,
        limit: data?.pagination?.limit ?? prev.limit,
        total_items: data?.pagination?.total_items ?? data.data.length,
        total_pages: data?.pagination?.total_pages ?? 1,
      }))
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat data user.'

      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchUsers()
  }, [pagination.page, appliedFilters.search, appliedFilters.role])

  useEffect(() => {
    const flashMessage = location.state?.userManagementMessage
    if (!flashMessage) {
      return
    }

    setSuccessMessage(flashMessage)
    navigate(location.pathname, { replace: true, state: null })
  }, [location.pathname, location.state, navigate])

  const handleFilterChange = (event) => {
    const { name, value } = event.target
    setFilters((prev) => ({ ...prev, [name]: value }))
  }

  const handleApplyFilters = (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')
    setAppliedFilters({
      search: filters.search.trim(),
      role: filters.role,
    })
    setPagination((prev) => ({ ...prev, page: 1 }))
  }

  const handleResetFilters = () => {
    setFilters({ search: '', role: '' })
    setAppliedFilters({ search: '', role: '' })
    setPagination((prev) => ({ ...prev, page: 1 }))
    setError('')
    setSuccessMessage('')
  }

  const handleDeleteUser = async (user) => {
    const confirmation = window.confirm(
      `Hapus user ${user.full_name || user.username}? Tindakan ini tidak bisa dibatalkan.`,
    )
    if (!confirmation) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setError('')
    setSuccessMessage('')

    try {
      const { data } = await api.delete(`/users/${user.id_user}`, { headers })
      setSuccessMessage(data?.message || 'User berhasil dihapus.')

      if (users.length === 1 && pagination.page > 1) {
        setPagination((prev) => ({ ...prev, page: prev.page - 1 }))
      } else {
        await fetchUsers()
      }
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menghapus user.'

      setError(apiMessage)
    }
  }

  const totalPages = pagination.total_pages || 1

  return (
    <AppShell
      authUser={authUser}
      eyebrow="F010 User Management"
      title="User Management"
      subtitle="Kelola akun pengguna sistem untuk semua role. Halaman ini hanya dapat diakses oleh admin."
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onOpenAddUser}>
            Tambah User
          </button>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Filter User</h2>
            <p className="api-note">
              Gunakan pencarian nama, username, email, atau filter role untuk mempercepat administrasi.
            </p>
          </div>
        </div>

        <form className="toolbar-form" onSubmit={handleApplyFilters}>
          <div className="toolbar-grid">
            <div className="manual-field">
              <label htmlFor="user_search">Cari User</label>
              <input
                id="user_search"
                name="search"
                type="text"
                value={filters.search}
                onChange={handleFilterChange}
                placeholder="Cari nama, username, atau email"
              />
            </div>
            <div className="manual-field">
              <label htmlFor="user_role_filter">Role</label>
              <select
                id="user_role_filter"
                name="role"
                value={filters.role}
                onChange={handleFilterChange}
              >
                <option value="">Semua Role</option>
                {roleOptions.map((role) => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="manual-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Memuat...' : 'Terapkan Filter'}
            </button>
            <button
              type="button"
              className="ghost-button"
              onClick={handleResetFilters}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Daftar User</h2>
            <p className="api-note">
              Menampilkan {users.length} user pada halaman ini dari total {pagination.total_items} data.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state compact">
            <p>Memuat daftar user...</p>
          </div>
        ) : users.length ? (
          <>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Nama</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Data Siswa</th>
                    <th>Dibuat</th>
                    <th>Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id_user}>
                      <td>{user.username}</td>
                      <td>{user.full_name}</td>
                      <td>{user.email || '-'}</td>
                      <td>{roleLabels[user.role] || user.role}</td>
                      <td>
                        {user.student ? `${user.student.nama} (${user.student.nisn})` : '-'}
                      </td>
                      <td>{formatCellValue(user.created_at)}</td>
                      <td>
                        <div className="table-actions">
                          <button
                            type="button"
                            className="ghost-button"
                            onClick={() => onOpenEditUser(user.id_user)}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="ghost-button danger-button"
                            onClick={() => handleDeleteUser(user)}
                            disabled={user.id_user === authUser.id_user}
                          >
                            Hapus
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination-row">
              <p className="api-note">
                Halaman {pagination.page} dari {totalPages}
              </p>
              <div className="table-actions">
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() => setPagination((prev) => ({ ...prev, page: prev.page - 1 }))}
                  disabled={loading || pagination.page <= 1}
                >
                  Sebelumnya
                </button>
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() => setPagination((prev) => ({ ...prev, page: prev.page + 1 }))}
                  disabled={loading || pagination.page >= totalPages}
                >
                  Berikutnya
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <p>Belum ada user yang cocok dengan filter saat ini.</p>
          </div>
        )}
      </section>
    </AppShell>
  )
}

function UserFormPage({
  mode,
  authUser,
  api,
  getAuthHeaders,
  onBackToUserManagement,
  onLogout,
}) {
  const navigate = useNavigate()
  const { userId } = useParams()
  const isEdit = mode === 'edit'

  const [form, setForm] = useState(buildInitialUserForm)
  const [studentCandidate, setStudentCandidate] = useState(null)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [pageLoading, setPageLoading] = useState(isEdit)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [linkedStudentLocked, setLinkedStudentLocked] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})

  const fetchUserDetail = async () => {
    if (!isEdit) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      setPageLoading(false)
      return
    }

    setPageLoading(true)
    try {
      const { data } = await api.get(`/users/${userId}`, { headers })

      if (!data?.success || !data?.data) {
        throw new Error('Respons detail user tidak valid.')
      }

      const user = data.data
      setForm({
        username: user.username || '',
        full_name: user.full_name || '',
        email: user.email || '',
        no_telp: user.no_telp || '',
        role: user.role || 'guru_piket',
        password: '',
        confirmPassword: '',
        nisn: user.student?.nisn || '',
      })
      setStudentCandidate(user.student || null)
      setLinkedStudentLocked(Boolean(user.student))
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat detail user.'

      setError(apiMessage)
    } finally {
      setPageLoading(false)
    }
  }

  useEffect(() => {
    void fetchUserDetail()
  }, [isEdit, userId])

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    const nextValue = name === 'nisn' ? value.replace(/\D/g, '').slice(0, 10) : value

    if (name === 'nisn' && form.nisn !== nextValue) {
      setStudentCandidate(linkedStudentLocked ? studentCandidate : null)
    }

    if (name === 'role' && value !== 'siswa' && !linkedStudentLocked) {
      setStudentCandidate(null)
      setForm((prev) => ({
        ...prev,
        [name]: value,
        nisn: '',
      }))
      setFieldErrors((prev) => ({ ...prev, [name]: '', nisn: '' }))
      return
    }

    setFieldErrors((prev) => ({ ...prev, [name]: '' }))
    setForm((prev) => ({ ...prev, [name]: nextValue }))
  }

  const handleLookupStudent = async (explicitNisn) => {
    const nisn = (explicitNisn ?? form.nisn).trim()

    if (!/^\d{10}$/.test(nisn)) {
      setFieldErrors((prev) => ({
        ...prev,
        nisn: 'Masukkan NISN 10 digit untuk akun siswa.',
      }))
      return null
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return null
    }

    setLookupLoading(true)
    setError('')
    setSuccessMessage('')
    setFieldErrors((prev) => ({ ...prev, nisn: '' }))

    try {
      const { data } = await api.get('/auth/student-candidates', {
        headers,
        params: { nisn },
      })

      const student = data?.data?.student
      if (!data?.success || !student) {
        throw new Error('Respons validasi siswa tidak valid.')
      }

      setStudentCandidate(student)
      setSuccessMessage(
        `NISN valid. Akun akan terhubung ke ${student.nama}${student.kelas ? ` dari ${student.kelas}` : ''}.`,
      )
      return student
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memvalidasi NISN siswa.'

      setStudentCandidate(null)
      setError(apiMessage)
      return null
    } finally {
      setLookupLoading(false)
    }
  }

  const validateUserForm = (currentForm) => {
    const nextErrors = {}

    if (!currentForm.username.trim()) {
      nextErrors.username = 'Username wajib diisi.'
    }

    if (!currentForm.full_name.trim()) {
      nextErrors.full_name = 'Nama lengkap wajib diisi.'
    }

    if (!currentForm.role) {
      nextErrors.role = 'Role wajib dipilih.'
    }

    if (!isEdit && !currentForm.password) {
      nextErrors.password = 'Password wajib diisi.'
    }

    if (currentForm.password && currentForm.password.length < 8) {
      nextErrors.password = 'Password minimal 8 karakter.'
    }

    if (
      (!isEdit || currentForm.password || currentForm.confirmPassword) &&
      currentForm.password !== currentForm.confirmPassword
    ) {
      nextErrors.confirmPassword = 'Konfirmasi password tidak sama.'
    }
            <input
              id="register_username"
              name="username"
              type="text"
              required
              aria-invalid={hasError}
              aria-describedby={hasError ? 'auth-form-error' : undefined}
              value={registerForm.username}
              onChange={onRegisterChange}
              placeholder="contoh: ahmad.fadil"
            />

            <label htmlFor="register_full_name">Nama Lengkap</label>
            <input
              id="register_full_name"
              name="full_name"
              type="text"
              required
              aria-invalid={hasError}
              aria-describedby={hasError ? 'auth-form-error' : undefined}
              value={registerForm.full_name}
              onChange={onRegisterChange}
              placeholder="Nama lengkap user"
            />

    if (currentForm.role === 'siswa' && !linkedStudentLocked && !/^\d{10}$/.test(currentForm.nisn)) {
      nextErrors.nisn = 'NISN 10 digit wajib diisi untuk akun siswa.'
    }

    return nextErrors
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    const localErrors = validateUserForm(form)
    if (Object.keys(localErrors).length) {
      setFieldErrors(localErrors)
      return
    }

    let candidate = studentCandidate
    if (form.role === 'siswa' && !linkedStudentLocked) {
      if (!candidate || candidate.nisn !== form.nisn) {
        candidate = await handleLookupStudent(form.nisn)
        if (!candidate) {
          return
        }
      }
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSubmitLoading(true)
    try {
      const payload = {
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        email: form.email.trim() || '',
        no_telp: form.no_telp.trim() || '',
        role: form.role,
      }
            <label htmlFor="register_password">Password</label>
            <input
              id="register_password"
              name="password"
              type="password"
              required
              aria-invalid={hasError}
              aria-describedby={hasError ? 'auth-form-error' : undefined}
              value={registerForm.password}
              onChange={onRegisterChange}
              placeholder="Minimal 8 karakter"
            />

            <label htmlFor="register_confirm_password">Konfirmasi Password</label>
            <input
              id="register_confirm_password"
              name="confirmPassword"
              type="password"
              required
              aria-invalid={hasError}
              aria-describedby={hasError ? 'auth-form-error' : undefined}
              value={registerForm.confirmPassword}
              onChange={onRegisterChange}
              placeholder="Ulangi password"
            />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? <LoadingSpinner label="Memproses..." /> : 'Daftar'}
            </button>
          </form>
        )}

        {error ? <p id="auth-form-error" className="alert error" role="alert">{error}</p> : null}
        {successMessage ? <p className="alert success" role="status">{successMessage}</p> : null}

      if (form.password) {
        payload.password = form.password
      }

      if (!isEdit && !form.password) {
        payload.password = ''
      }

      if (form.role === 'siswa' && !linkedStudentLocked) {
        payload.nisn = candidate?.nisn || form.nisn.trim()
      }

      const request = isEdit
        ? api.put(`/users/${userId}`, payload, { headers })
        : api.post('/users', payload, { headers })

      const { data } = await request
      if (!data?.success) {
        throw new Error('Respons penyimpanan user tidak valid.')
      }

      navigate(userManagementPath, {
        replace: true,
        state: {
          userManagementMessage:
            data.message || (isEdit ? 'User berhasil diupdate.' : 'User berhasil dibuat.'),
        },
      })
    } catch (requestError) {
      const apiErrors = requestError?.response?.data?.errors || {}
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menyimpan data user.'

      setFieldErrors((prev) => ({
        ...prev,
        username: apiErrors?.username || prev.username || '',
        full_name: apiErrors?.full_name || '',
        email: apiErrors?.email || '',
        no_telp: apiErrors?.no_telp || '',
        role: apiErrors?.role || '',
        password: apiErrors?.password || '',
        nisn: apiErrors?.nisn || apiErrors?.student_lookup || '',
      }))
      setError([apiMessage, flattenApiErrors(apiErrors)].filter(Boolean).join(' '))
    } finally {
      setSubmitLoading(false)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow={isEdit ? 'F010B Edit User' : 'F010A Tambah User'}
      title={isEdit ? 'Edit User' : 'Tambah User'}
      subtitle="Lengkapi data akun dan, bila role siswa dipilih, hubungkan dengan data siswa melalui validasi NISN."
      actions={
        <>
          <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
          <button type="button" className="ghost-button" onClick={onBackToUserManagement}>
            Daftar User
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}
function DashboardPage({
  authUser,
  dashboardData,
  dashboardLoading,
  realtimeStatus,
  realtimeLastUpdate,
  error,
  successMessage,
  onRefresh,
  onOpenNotifikasi,
  onLogout,
}) {
  const cards = dashboardData?.cards || []
  const primaryTable = dashboardData?.primary_table || {
    title: 'Ringkasan',
    columns: [],
    rows: [],
    note: '',
  }

  return (
    <main className="dashboard-page" aria-busy={dashboardLoading}>
      <section className="dashboard-shell">
        <header className="dashboard-hero">
          <div>
            <p className="eyebrow">{dashboardTitles[authUser.role] || 'Dashboard'}</p>
            <h1>{authUser.full_name || authUser.username}</h1>
            <p className="subtitle dashboard-subtitle">
              Masuk sebagai {roleLabels[authUser.role] || authUser.role}. Dashboard
              ini menampilkan ringkasan data utama sesuai role Anda.
            </p>
          </div>

          <div className="dashboard-actions">
            <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
            <span className={`role-pill realtime-pill ${realtimeStatus}`}>
              MQTT: {realtimeStatus}
              {realtimeLastUpdate ? ` | update ${formatCellValue(realtimeLastUpdate)}` : ''}
            </span>
            <button type="button" className="ghost-button" onClick={onRefresh}>
              Muat Ulang
            </button>
            <button type="button" onClick={onLogout} aria-label="Logout dari aplikasi">
              Logout
            </button>
          </div>
        </header>

      {pageLoading ? (
        <section className="dashboard-panel">
          <p className="api-note">Memuat detail user...</p>
        </section>
      ) : (
        <section className="manual-grid">
          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>{isEdit ? 'Form Edit User' : 'Form Tambah User'}</h2>
                <p className="api-note">
                  Data ini akan dipakai untuk login dan pengelolaan role di dalam sistem.
                </p>
              </div>
            </div>

            <form className="manual-form" onSubmit={handleSubmit}>
              <div className="manual-form-grid">
                <div className="manual-field">
                  <label htmlFor="user_username">Username</label>
                  <input
                    id="user_username"
                    name="username"
                    type="text"
                    value={form.username}
                    onChange={handleFieldChange}
                    placeholder="contoh: ahmad.fadil"
                  />
                  {fieldErrors.username ? <p className="field-error">{fieldErrors.username}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_full_name">Nama Lengkap</label>
                  <input
                    id="user_full_name"
                    name="full_name"
                    type="text"
                    value={form.full_name}
                    onChange={handleFieldChange}
                    placeholder="Nama lengkap pengguna"
                  />
                  {fieldErrors.full_name ? <p className="field-error">{fieldErrors.full_name}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_email">Email</label>
                  <input
                    id="user_email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleFieldChange}
                    placeholder="contoh: user@sikap.local"
                  />
                </div>
        {error ? <p className="alert error" role="alert">{error}</p> : null}
        {successMessage ? <p className="alert success" role="status">{successMessage}</p> : null}

        {dashboardLoading ? (
          <section className="dashboard-panel">
            <LoadingSpinner label="Memuat data dashboard..." />
          </section>
        ) : null}

                <div className="manual-field">
                  <label htmlFor="user_no_telp">No. Telepon</label>
                  <input
                    id="user_no_telp"
                    name="no_telp"
                    type="text"
                    value={form.no_telp}
                    onChange={handleFieldChange}
                    placeholder="08xxxxxxxxxx"
                  />
                </div>

                <div className="manual-field">
                  <label htmlFor="user_role">Role</label>
                  <select
                    id="user_role"
                    name="role"
                    value={form.role}
                    onChange={handleFieldChange}
                    disabled={linkedStudentLocked}
                  >
                    {roleOptions.map((role) => (
                      <option key={role.value} value={role.value}>
                        {role.label}
                      </option>
                    ))}
                  </select>
                  {linkedStudentLocked ? (
                    <p className="helper-text">
                      Role dikunci karena akun ini sudah terhubung ke data siswa.
                    </p>
                  ) : null}
                  {fieldErrors.role ? <p className="field-error">{fieldErrors.role}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_password">
                    {isEdit ? 'Password Baru' : 'Password'}
                  </label>
                  <input
                    id="user_password"
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleFieldChange}
                    placeholder={isEdit ? 'Kosongkan jika tidak diubah' : 'Minimal 8 karakter'}
                  />
                  {fieldErrors.password ? <p className="field-error">{fieldErrors.password}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_confirm_password">Konfirmasi Password</label>
                  <input
                    id="user_confirm_password"
                    name="confirmPassword"
                    type="password"
                    value={form.confirmPassword}
                    onChange={handleFieldChange}
                    placeholder="Ulangi password"
                  />
                  {fieldErrors.confirmPassword ? (
                    <p className="field-error">{fieldErrors.confirmPassword}</p>
                  ) : null}
                </div>

                {form.role === 'siswa' ? (
                  <div className="manual-field manual-field-full">
                    <label htmlFor="user_nisn">NISN Siswa</label>
                    <div className="lookup-row">
                      <input
                        id="user_nisn"
                        name="nisn"
                        type="text"
                        inputMode="numeric"
                        value={form.nisn}
                        onChange={handleFieldChange}
                        placeholder="Masukkan 10 digit NISN"
                        maxLength={10}
                        disabled={linkedStudentLocked}
                      />
                      {!linkedStudentLocked ? (
                        <button
                          type="button"
                          className="ghost-button lookup-button"
                          onClick={() => handleLookupStudent()}
                          disabled={lookupLoading || submitLoading}
                        >
                          {lookupLoading ? 'Memvalidasi...' : 'Validasi NISN'}
                        </button>
                      ) : null}
                    </div>
                    <p className="helper-text">
                      Akun siswa wajib terhubung ke data siswa agar relasi absensi dan profil tetap konsisten.
                    </p>
                    {fieldErrors.nisn ? <p className="field-error">{fieldErrors.nisn}</p> : null}
                  </div>
                ) : null}
              </div>

              <div className="manual-actions">
                <button type="submit" disabled={submitLoading || lookupLoading}>
                  {submitLoading
                    ? 'Menyimpan...'
                    : isEdit
                      ? 'Simpan Perubahan'
                      : 'Buat User'}
                </button>
                <button
                  type="button"
                  className="ghost-button"
                  onClick={onBackToUserManagement}
                  disabled={submitLoading || lookupLoading}
                >
                  Batal
                </button>
              </div>
            </form>
          </section>

          <aside className="manual-side-panel">
            <section className="dashboard-panel manual-panel highlighted-panel">
              <div className="panel-header">
                <div>
                  <h2>Preview Relasi Siswa</h2>
                  <p className="api-note">
                    Panel ini membantu memastikan akun siswa tersambung ke entitas siswa yang benar.
                  </p>
                </div>
              </div>

              {studentCandidate ? (
                <div className="student-preview">
                  <div className="student-preview-head">
                    <strong>{studentCandidate.nama}</strong>
                    <span className="status-chip info">
                      {studentCandidate.kelas || 'Tanpa kelas'}
                    </span>
                  </div>

                  <dl className="detail-list">
                    <div><dt>NISN</dt><dd>{studentCandidate.nisn}</dd></div>
                    <div><dt>ID Siswa</dt><dd>{studentCandidate.id_siswa}</dd></div>
                    <div><dt>Kelas</dt><dd>{studentCandidate.kelas || '-'}</dd></div>
                    <div><dt>ID Card</dt><dd>{studentCandidate.id_card || '-'}</dd></div>
                  </dl>
              {primaryTable.rows?.length ? (
                <div className="table-wrapper">
                  <table aria-label={primaryTable.title || 'Tabel dashboard'}>
                    <thead>
                      <tr>
                        {primaryTable.columns.map((column) => (
                          <th key={column}>{formatColumnLabel(column)}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {primaryTable.rows.map((row, index) => (
                        <tr key={`${primaryTable.title}-${index}`}>
                          {primaryTable.columns.map((column) => (
                            <td key={`${index}-${column}`}>
                              {formatCellValue(row[column])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state compact">
                  <p>
                    {form.role === 'siswa'
                      ? 'Belum ada siswa tervalidasi. Isi NISN lalu lakukan validasi.'
                      : 'Preview siswa hanya muncul bila role akun diatur sebagai siswa.'}
                  </p>
                </div>
              )}
            </section>

            <section className="dashboard-panel manual-panel">
              <div className="panel-header">
                <div>
                  <h2>Petunjuk</h2>
                </div>
              </div>

              <div className="tips-list">
                <p>1. Gunakan username yang mudah dikenali dan unik.</p>
                <p>2. Password minimal 8 karakter; saat edit boleh dikosongkan jika tidak diubah.</p>
                <p>3. Untuk role siswa, validasi NISN dulu sebelum menyimpan.</p>
                <p>4. Akun siswa yang sudah terhubung tidak bisa dipindah ke role lain dari halaman ini.</p>
              </div>
            </section>
          </aside>
        </section>
      )}
    </AppShell>
  )
}

function NotificationPage({
  notifications,
  unreadCount,
  loading,
  error,
  successMessage,
  onRefresh,
  onMarkAsRead,
  onBackToDashboard,
}) {
  return (
    <main className="dashboard-page">
      <section className="dashboard-shell">
        <header className="dashboard-hero">
          <div>
            <p className="eyebrow">F024</p>
            <h1>Notifikasi</h1>
            <p className="subtitle dashboard-subtitle">
              Badge unread count, list notifikasi, dan klik item untuk tandai sudah dibaca.
            </p>
          </div>

          <div className="dashboard-actions">
            <span className="role-pill">Belum dibaca: {unreadCount}</span>
            <button type="button" className="ghost-button" onClick={onRefresh} disabled={loading}>
              {loading ? 'Memuat...' : 'Muat Ulang'}
            </button>
            <button type="button" className="ghost-button" onClick={onBackToDashboard}>
              Kembali ke Dashboard
            </button>
          </div>
        </header>

        {error ? <p className="alert error">{error}</p> : null}
        {successMessage ? <p className="alert success">{successMessage}</p> : null}

        <section className="dashboard-panel">
          {notifications.length ? (
            <div className="notification-list">
              {notifications.map((item) => (
                <button
                  type="button"
                  key={item.id_notifikasi}
                  className={item.is_read ? 'notification-item read' : 'notification-item unread'}
                  onClick={() => onMarkAsRead(item)}
                >
                  <div className="notification-item-head">
                    <strong>{item.judul || 'Notifikasi'}</strong>
                    <span className={item.is_read ? 'chip-read' : 'chip-unread'}>
                      {item.is_read ? 'Sudah Dibaca' : 'Belum Dibaca'}
                    </span>
                  </div>
                  <p>{item.pesan || '-'}</p>
                  <small>
                    {item.created_at ? new Date(item.created_at).toLocaleString('id-ID') : '-'}
                  </small>
                </button>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Belum ada notifikasi untuk akun ini.</p>
            </div>
          )}
        </section>
      </section>
    </main>
  )
}

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
  })

  const [registerForm, setRegisterForm] = useState({
    username: '',
    full_name: '',
    email: '',
    no_telp: '',
    role: 'siswa',
    password: '',
    confirmPassword: '',
  })

  const [loading, setLoading] = useState(false)
  const [checkingSession, setCheckingSession] = useState(true)
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [authUser, setAuthUser] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)
  const [realtimeStatus, setRealtimeStatus] = useState('offline')
  const [realtimeLastUpdate, setRealtimeLastUpdate] = useState(null)
  const mqttRefreshTimerRef = useRef(null)

  const api = useMemo(
    () =>
      axios.create({
        baseURL: apiBaseUrl,
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      }),
    [],
  )

  const clearSession = () => {
    localStorage.removeItem('sikap_token')
    localStorage.removeItem('sikap_token_type')
    localStorage.removeItem('sikap_expires_at')
    localStorage.removeItem('sikap_user')
    setAuthUser(null)
    setDashboardData(null)
    setNotifications([])
    setUnreadCount(0)
  }

  const getAuthHeaders = () => {
    const token = localStorage.getItem('sikap_token')
    const tokenType = localStorage.getItem('sikap_token_type') || 'Bearer'

    if (!token) {
      return null
    }

    return {
      Authorization: `${tokenType} ${token}`,
    }
  }

  const fetchCurrentUser = async () => {
    const headers = getAuthHeaders()

    if (!headers) {
      throw new Error('Token tidak ditemukan.')
    }

    const { data } = await api.get('/auth/me', { headers })

    if (!data?.success || !data?.data) {
      throw new Error('Respons profil user tidak valid.')
    }

    setAuthUser(data.data)
    localStorage.setItem('sikap_user', JSON.stringify(data.data))
    return data.data
  }

  const fetchDashboard = async ({ silent = false } = {}) => {
    const headers = getAuthHeaders()

    if (!headers) {
      throw new Error('Token tidak ditemukan.')
    }

    if (!silent) {
      setDashboardLoading(true)
    }
    try {
      const { data } = await api.get('/dashboard', { headers })

      if (!data?.success || !data?.data) {
        throw new Error('Respons dashboard tidak valid.')
      }

      setDashboardData(data.data)
      return data.data
    } finally {
      if (!silent) {
        setDashboardLoading(false)
      }
    }
  }

  const getNotificationPayload = (responseBody) => {
    const candidates = [responseBody?.data, responseBody?.message]
    return (
      candidates.find(
        (item) =>
          item &&
          typeof item === 'object' &&
          (Array.isArray(item.notifikasi) || typeof item.unread_count === 'number'),
      ) || {}
    )
  }

  const requestNotifikasi = async (method, path = '', config = {}) => {
    const candidates = [...new Set([`${apiBaseUrl}/notifikasi${path}`, `/api/notifikasi${path}`])]
    let lastError = null

    for (const url of candidates) {
      try {
        return await axios({
          method,
          url,
          timeout: 10000,
          ...config,
        })
      } catch (error) {
        const status = error?.response?.status
        if (status === 404 && url !== candidates[candidates.length - 1]) {
          lastError = error
          continue
        }
        throw error
      }
    }

    throw lastError || new Error('Gagal mengakses endpoint notifikasi.')
  }

  const fetchNotifications = async ({ silent = false } = {}) => {
    const headers = getAuthHeaders()

    if (!headers) {
      return
    }

    if (!silent) {
      setNotificationLoading(true)
    }

    try {
      const { data } = await requestNotifikasi('get', '', {
        headers,
        params: { page: 1, per_page: 20 },
      })
      const payload = getNotificationPayload(data)
      setNotifications(Array.isArray(payload.notifikasi) ? payload.notifikasi : [])
      setUnreadCount(Number(payload.unread_count || 0))
    } catch (requestError) {
      if (!silent) {
        const apiMessage =
          requestError?.response?.data?.message ||
          requestError?.response?.data?.error ||
          requestError?.message ||
          'Gagal memuat notifikasi.'
        setError(apiMessage)
      }
    } finally {
      if (!silent) {
        setNotificationLoading(false)
      }
    }
  }

  useEffect(() => {
    const bootstrapSession = async () => {
      const token = localStorage.getItem('sikap_token')

      if (!token) {
        setCheckingSession(false)
        return
      }

      try {
        const user = await fetchCurrentUser()
        setSuccessMessage(
          `Sesi aktif. Selamat datang kembali, ${user.full_name || user.username}.`,
        )
        try {
          await fetchDashboard()
        } catch (_dashboardError) {
          setError('Sesi login aktif, tetapi data dashboard belum berhasil dimuat.')
        }
        await fetchNotifications({ silent: true })
      } catch (_err) {
        clearSession()
      } finally {
        setCheckingSession(false)
      }
    }

    bootstrapSession()
  }, [])

  useEffect(() => {
    if (error) {
      setToast({ type: 'error', message: error })
      return
    }

    if (successMessage) {
      setToast({ type: 'success', message: successMessage })
    }
  }, [error, successMessage])

  useEffect(() => {
    if (!toast?.message) {
      return
    }

    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current)
    }

    toastTimerRef.current = window.setTimeout(() => {
      setToast(null)
      toastTimerRef.current = null
    }, 3500)

    return () => {
      if (toastTimerRef.current) {
        window.clearTimeout(toastTimerRef.current)
      }
    }
  }, [toast])

  const handleLoginChange = (event) => {
    const { name, value } = event.target
    setLoginForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleRegisterChange = (event) => {
    const { name, value } = event.target
    setRegisterForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSwitchMode = (nextMode) => {
    setError('')
    setSuccessMessage('')
    navigate(nextMode === 'register' ? '/register' : '/login')
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!loginForm.username || !loginForm.password) {
      setError('Username dan password wajib diisi.')
      return
    }

    setLoading(true)

    try {
      const { data } = await api.post('/auth/login', loginForm)
      const responseData = data?.data

      if (!data?.success || !responseData?.access_token) {
        setError('Login gagal. Respons API tidak valid.')
        return
      }

      localStorage.setItem('sikap_token', responseData.access_token)
      localStorage.setItem('sikap_token_type', responseData.token_type || 'Bearer')
      localStorage.setItem('sikap_expires_at', String(responseData.expires_at || 0))

      const user = await fetchCurrentUser()
      try {
        await fetchDashboard()
      } catch (_dashboardError) {
        setError('Login berhasil, tetapi data dashboard belum berhasil dimuat.')
      }
      await fetchNotifications({ silent: true })

      const displayName = user?.full_name || user?.username || loginForm.username
      setSuccessMessage(`Login berhasil. Selamat datang, ${displayName}.`)
      setLoginForm((prev) => ({ ...prev, password: '' }))
      navigate('/dashboard', { replace: true })
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Terjadi kesalahan saat menghubungi server.'

      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!registerForm.username || !registerForm.full_name || !registerForm.password) {
      setError('Username, nama lengkap, dan password wajib diisi.')
      return
    }

    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Konfirmasi password tidak sama.')
      return
    }

    const headers = getAuthHeaders()

    if (!headers) {
      setError('Login dulu sebagai admin untuk membuat user baru.')
      return
    }

    setLoading(true)

    try {
      const payload = {
        username: registerForm.username,
        full_name: registerForm.full_name,
        email: registerForm.email || null,
        no_telp: registerForm.no_telp || null,
        role: registerForm.role,
        password: registerForm.password,
      }

      const { data } = await api.post('/users', payload, { headers })

      if (!data?.success) {
        setError(data?.message || 'Registrasi gagal.')
        return
      }

      setSuccessMessage(data?.message || 'Registrasi berhasil.')
      setRegisterForm({
        username: '',
        full_name: '',
        email: '',
        no_telp: '',
        role: 'siswa',
        password: '',
        confirmPassword: '',
      })
    } catch (requestError) {
      const status = requestError?.response?.status
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Terjadi kesalahan saat menghubungi server.'

      if (status === 404) {
        setError('Endpoint registrasi (/api/v1/users) belum tersedia di backend saat ini.')
      } else if (status === 403) {
        setError('Akses ditolak. Registrasi user hanya untuk admin.')
      } else {
        setError(apiMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    const headers = getAuthHeaders()

    try {
      if (headers) {
        await api.post('/auth/logout', {}, { headers })
      }
    } catch (_err) {
      // Tetap lanjut clear session walaupun revoke token gagal.
    } finally {
      clearSession()
      setSuccessMessage('Logout berhasil.')
      setError('')
      navigate('/login', { replace: true })
    }
  }

  const handleRefreshDashboard = async () => {
    setError('')
    setSuccessMessage('')

    try {
      await fetchDashboard()
      setSuccessMessage('Dashboard berhasil diperbarui.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Gagal memuat dashboard.'

      setError(apiMessage)
    }
  }

  const handleOpenManualInput = () => {
    setError('')
    setSuccessMessage('')
    navigate(manualInputPath)
  }

  const handleOpenProfile = () => {
    setError('')
    setSuccessMessage('')
    navigate(profilePath)
  }

  const handleOpenSchoolData = () => {
    setError('')
    setSuccessMessage('')
    navigate(schoolDataPath)
  }

  const handleOpenPrayerTime = () => {
    setError('')
    setSuccessMessage('')
    navigate(prayerTimePath)
  }

  const handleOpenUserManagement = () => {
    setError('')
    setSuccessMessage('')
    navigate(userManagementPath)
  }

  const handleOpenAddUser = () => {
    navigate(`${userManagementPath}/new`)
  }

  const handleOpenEditUser = (userId) => {
    navigate(`${userManagementPath}/${userId}/edit`)
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  const handleBackToUserManagement = () => {
    navigate(userManagementPath)
  }
  useEffect(() => {
    if (!authUser) {
      setRealtimeStatus('offline')
      setRealtimeLastUpdate(null)
      return
    }

    let isActive = true
    setRealtimeStatus('connecting')
    const client = mqtt.connect(mqttWsUrl, {
      reconnectPeriod: 5000,
      connectTimeout: 10000,
    })

    client.on('connect', () => {
      if (!isActive) {
        return
      }

      setRealtimeStatus('connected')
      client.subscribe(mqttTopicAbsensi, (subscribeError) => {
        if (subscribeError && isActive) {
          setRealtimeStatus('error')
        }
      })
    })

    client.on('reconnect', () => {
      if (isActive) {
        setRealtimeStatus('reconnecting')
      }
    })

    client.on('close', () => {
      if (isActive) {
        setRealtimeStatus('offline')
      }
    })

    client.on('error', () => {
      if (isActive) {
        setRealtimeStatus('error')
      }
    })

    client.on('message', (topic) => {
      if (topic !== mqttTopicAbsensi || !isActive) {
        return
      }

      if (mqttRefreshTimerRef.current) {
        window.clearTimeout(mqttRefreshTimerRef.current)
      }

      mqttRefreshTimerRef.current = window.setTimeout(async () => {
        try {
          await fetchDashboard({ silent: true })
          if (isActive) {
            setRealtimeLastUpdate(new Date().toISOString())
          }
        } catch (_err) {
          // Silent: tetap tunggu event berikutnya.
        }
      }, 350)
    })

    return () => {
      isActive = false
      if (mqttRefreshTimerRef.current) {
        window.clearTimeout(mqttRefreshTimerRef.current)
        mqttRefreshTimerRef.current = null
      }
      client.end(true)
    }
  }, [authUser])

  if (checkingSession) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>SIKAP</h1>
          <LoadingSpinner label="Memeriksa sesi login dan menyiapkan dashboard..." />
        </section>
      </main>
    )
  }

  const authMode = location.pathname === '/register' ? 'register' : 'login'

  return (
    <Routes>
      <Route path="/" element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />} />
      <Route
        path="/login"
        element={
          authUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              mode={authMode}
              loading={loading}
              checkingSession={checkingSession}
              loginForm={loginForm}
              registerForm={registerForm}
              error={error}
              successMessage={successMessage}
              onLoginChange={handleLoginChange}
              onRegisterChange={handleRegisterChange}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onSwitchMode={handleSwitchMode}
              apiBaseUrlValue={apiBaseUrl}
            />
          )
        }
      />
      <Route
        path="/register"
        element={
          authUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              mode={authMode}
              loading={loading}
              checkingSession={checkingSession}
              loginForm={loginForm}
              registerForm={registerForm}
              error={error}
              successMessage={successMessage}
              onLoginChange={handleLoginChange}
              onRegisterChange={handleRegisterChange}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onSwitchMode={handleSwitchMode}
              apiBaseUrlValue={apiBaseUrl}
            />
          )
        }
      />
      <Route
        path="/dashboard"
        element={
          authUser ? (
            <DashboardPage
              authUser={authUser}
              dashboardData={dashboardData}
              dashboardLoading={dashboardLoading}
              realtimeStatus={realtimeStatus}
              realtimeLastUpdate={realtimeLastUpdate}
              error={error}
              successMessage={successMessage}
              onRefresh={handleRefreshDashboard}
              onOpenManualInput={handleOpenManualInput}
              onOpenProfile={handleOpenProfile}
              onOpenSchoolData={handleOpenSchoolData}
              onOpenPrayerTime={handleOpenPrayerTime}
              onOpenUserManagement={handleOpenUserManagement}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={profilePath}
        element={
          authUser ? (
            <ProfilePage
              authUser={authUser}
              dashboardData={dashboardData}
              onBackToDashboard={handleBackToDashboard}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={schoolDataPath}
        element={
          authUser ? (
            <SchoolDataPage
              authUser={authUser}
              api={api}
              getAuthHeaders={getAuthHeaders}
              onBackToDashboard={handleBackToDashboard}
              onOpenNotifikasi={handleOpenNotifikasi}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={prayerTimePath}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <PrayerTimeSettingsPage
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
        path="/notifikasi"
        element={
          authUser ? (
            <NotificationPage
              notifications={notifications}
              unreadCount={unreadCount}
              loading={notificationLoading}
              error={error}
              successMessage={successMessage}
              onRefresh={handleRefreshNotifications}
              onMarkAsRead={handleMarkNotificationAsRead}
              onBackToDashboard={handleBackToDashboard}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={manualInputPath}
        element={
          authUser ? (
            authUser.role === 'guru_piket' ? (
              <ManualInputPage
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={userManagementPath}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <UserManagementPage
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToDashboard={handleBackToDashboard}
                onOpenAddUser={handleOpenAddUser}
                onOpenEditUser={handleOpenEditUser}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={`${userManagementPath}/new`}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <UserFormPage
                mode="create"
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToUserManagement={handleBackToUserManagement}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path={`${userManagementPath}/:userId/edit`}
        element={
          authUser ? (
            authUser.role === 'admin' ? (
              <UserFormPage
                mode="edit"
                authUser={authUser}
                api={api}
                getAuthHeaders={getAuthHeaders}
                onBackToUserManagement={handleBackToUserManagement}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
        path="*"
        element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />}
      />
      <Route path="*" element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}

export default App
