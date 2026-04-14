import { dashboardTitles, roleLabels } from '../config'
import { AppShell } from '../components/Common'
import DashboardCharts from '../components/DashboardCharts'
import { formatCellValue, formatColumnLabel } from '../utils/formatters'

function getInitials(name) {
  if (!name) {
    return 'SI'
  }

  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || '')
    .join('')
}

function getSapaan() {
  const jam = new Date().getHours()
  if (jam < 11) return 'Selamat pagi'
  if (jam < 15) return 'Selamat siang'
  if (jam < 18) return 'Selamat sore'
  return 'Selamat malam'
}

const ROLE_DESCRIPTIONS = {
  admin: 'Anda memegang kendali penuh sistem. Pantau data, kelola akun, dan atur jadwal sholat dari sini.',
  kepsek: 'Ringkasan kehadiran sholat seluruh kelas dan siswa tersaji dalam satu halaman.',
  wali_kelas: 'Pantau kehadiran sholat kelas binaan Anda dan tindak lanjuti siswa yang perlu perhatian.',
  guru_piket: 'Catat absensi sholat hari ini dan pastikan seluruh data tersimpan dengan benar.',
  siswa: 'Lihat rekam kehadiran sholat Anda dan pantau perkembangannya dari waktu ke waktu.',
  orangtua: 'Pantau kehadiran sholat putra/putri Anda di sekolah secara transparan.',
}

export default function DashboardPage({
  authUser,
  dashboardData,
  dashboardLoading,
  realtimeStatus,
  realtimeLastUpdate,
  error,
  successMessage,
  onRefresh,
  onOpenNotifikasi,
  onOpenManualInput,
  onOpenProfile,
  onOpenSchoolData,
  onOpenPrayerTime,
  onOpenReport,
  onOpenUserManagement,
  onOpenMonitoring,
  onLogout,
}) {
  const cards = dashboardData?.cards || []
  const charts = dashboardData?.charts || null
  const highlightedCards = cards.slice(0, 3)
  const secondaryCards = cards.slice(3)
  const sapaan = getSapaan()
  const roleDescription = ROLE_DESCRIPTIONS[authUser.role] || ''
  const firstName = (authUser.full_name || authUser.username || '').split(' ')[0] || ''

  const statusDistribution = charts?.status_distribution?.rows || []
  const totalHadir = statusDistribution.reduce((sum, row) => sum + (row.value || 0), 0)
  const hadirTepat = statusDistribution.find((r) => r.status === 'tepat_waktu')?.value || 0
  const hadirTerlambat = statusDistribution.find((r) => r.status === 'terlambat')?.value || 0
  const persentaseTepat = totalHadir > 0 ? Math.round((hadirTepat / totalHadir) * 100) : 0
  const persentaseTerlambat = totalHadir > 0 ? Math.round((hadirTerlambat / totalHadir) * 100) : 0

  const attendanceTrendRows = charts?.attendance_trend?.rows || []
  const lastTrend = attendanceTrendRows[attendanceTrendRows.length - 1] || null
  const prevTrend = attendanceTrendRows[attendanceTrendRows.length - 2] || null
  const trendDelta = lastTrend && prevTrend ? (lastTrend.total || 0) - (prevTrend.total || 0) : 0
  const primaryTable = dashboardData?.primary_table || {
    title: 'Ringkasan',
    columns: [],
    rows: [],
    note: '',
  }
  const initials = getInitials(authUser.full_name || authUser.username)

  const dashboardTitle = dashboardTitles[authUser.role] || 'Dashboard'
  const quickActions = [
    {
      key: 'profile',
      label: 'Lihat Profil Saya',
      description: 'Buka data akun dan hubungan data yang terpasang pada pengguna ini.',
      onClick: onOpenProfile,
    },
    {
      key: 'school',
      label: 'Data Sekolah',
      description: 'Lihat ringkasan kehadiran sekolah dan kondisi tiap kelas.',
      onClick: onOpenSchoolData,
    },
    {
      key: 'notifications',
      label: 'Buka Pesan',
      description: 'Cek pemberitahuan baru, informasi penting, dan status yang belum dibaca.',
      onClick: onOpenNotifikasi,
    },
    {
      key: 'refresh',
      label: 'Muat Ulang Data',
      description: 'Ambil data terbaru dari server saat tampilan perlu disegarkan.',
      onClick: onRefresh,
    },
    ...(['admin', 'kepsek', 'wali_kelas'].includes(authUser.role)
      ? [
          {
            key: 'report',
            label: 'Buat Laporan',
            description: 'Unduh rekap PDF atau Excel untuk kelas, siswa, atau sekolah.',
            onClick: onOpenReport,
          },
        ]
      : []),
    ...(['admin', 'kepsek'].includes(authUser.role)
      ? [
          {
            key: 'monitoring',
            label: 'Monitoring Sistem',
            description: 'Pantau kesehatan server, traffic API, dan status perangkat real-time.',
            onClick: onOpenMonitoring,
          },
        ]
      : []),
    ...(authUser.role === 'admin'
      ? [
          {
            key: 'prayer-time',
            label: 'Waktu Sholat',
            description: 'Atur waktu adzan, iqamah, dan batas sesi absensi.',
            onClick: onOpenPrayerTime,
          },
          {
            key: 'user-management',
            label: 'Kelola Akun',
            description: 'Tambah, ubah, dan rapikan akun yang memakai sistem ini.',
            onClick: onOpenUserManagement,
          },
        ]
      : []),
    ...(authUser.role === 'guru_piket'
      ? [
          {
            key: 'manual-input',
            label: 'Input Manual',
            description: 'Catat absensi bila kartu RFID tidak bisa digunakan.',
            onClick: onOpenManualInput,
          },
        ]
      : []),
  ]
  const liveStatusLabel =
    realtimeStatus === 'connected'
      ? 'Terhubung'
      : realtimeStatus === 'connecting' || realtimeStatus === 'reconnecting'
        ? 'Menghubungkan'
        : 'Offline'

  return (
    <AppShell
      authUser={authUser}
      eyebrow={dashboardTitle}
      title={`${sapaan}${firstName ? `, ${firstName}` : ''}`}
      subtitle={roleDescription || `Masuk sebagai ${roleLabels[authUser.role] || authUser.role}. Halaman ini merangkum informasi penting dan menu utama yang paling sering dipakai.`}
      actions={
        <>
          <span className={`role-pill realtime-pill ${realtimeStatus || 'offline'}`}>
            Status perangkat: {liveStatusLabel}
            {realtimeLastUpdate ? ` | update ${formatCellValue(realtimeLastUpdate)}` : ''}
          </span>
          <button type="button" className="ghost-button" onClick={onOpenNotifikasi}>
            Pesan
          </button>
          <button type="button" onClick={onLogout}>
            Keluar
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
          <section className="insight-strip" aria-label="Ringkasan cepat">
            <article className="insight-card insight-primary">
              <span className="insight-label">Total kehadiran tercatat</span>
              <strong>{formatCellValue(totalHadir)}</strong>
              <span className="insight-foot">
                {trendDelta === 0
                  ? 'Stabil dibanding periode sebelumnya.'
                  : trendDelta > 0
                    ? `Naik ${formatCellValue(trendDelta)} dari hari sebelumnya.`
                    : `Turun ${formatCellValue(Math.abs(trendDelta))} dari hari sebelumnya.`}
              </span>
            </article>
            <article className="insight-card insight-success">
              <span className="insight-label">Tepat waktu</span>
              <strong>{persentaseTepat}%</strong>
              <span className="insight-foot">{formatCellValue(hadirTepat)} siswa hadir tepat waktu.</span>
            </article>
            <article className="insight-card insight-warning">
              <span className="insight-label">Terlambat</span>
              <strong>{persentaseTerlambat}%</strong>
              <span className="insight-foot">{formatCellValue(hadirTerlambat)} siswa hadir terlambat.</span>
            </article>
            <article className="insight-card insight-neutral">
              <span className="insight-label">Status data</span>
              <strong>
                {dashboardData?.generated_at
                  ? formatCellValue(dashboardData.generated_at)
                  : 'Siap dipakai'}
              </strong>
              <span className="insight-foot">
                Gunakan tombol Muat Ulang Data untuk menyegarkan tampilan.
              </span>
            </article>
          </section>

          <section className="dashboard-overview-grid">
            <aside className="dashboard-sidebar-stack">
              <section className="dashboard-profile-card">
                <div className="dashboard-profile-head">
                  <div className="dashboard-profile-avatar" aria-hidden="true">
                    {initials}
                  </div>
                  <div className="dashboard-profile-copy">
                    <h2>{authUser.full_name || authUser.username}</h2>
                    <p>{roleLabels[authUser.role] || authUser.role}</p>
                    <span>{authUser.username || '-'}</span>
                  </div>
                </div>

                <div className="dashboard-profile-meta">
                  <div>
                    <span>Email</span>
                    <strong>{authUser.email || '-'}</strong>
                  </div>
                  <div>
                    <span>Status Data</span>
                    <strong>
                      {dashboardData?.generated_at
                        ? `Diperbarui ${formatCellValue(dashboardData.generated_at)}`
                        : 'Siap dipakai'}
                    </strong>
                  </div>
                </div>

                <div className="dashboard-profile-stats">
                  {highlightedCards.length ? (
                    highlightedCards.map((card) => (
                      <article key={card.key} className="profile-stat-card">
                        <span>{card.label}</span>
                        <strong>{formatCellValue(card.value)}</strong>
                      </article>
                    ))
                  ) : (
                    <article className="profile-stat-card empty">
                      <span>Ringkasan</span>
                      <strong>-</strong>
                    </article>
                  )}
                </div>
              </section>

              <section className="dashboard-panel">
                <div className="panel-header">
                  <div>
                    <h2>Petunjuk Singkat</h2>
                    <p className="api-note">Urutan ini cocok untuk pengguna yang baru pertama memakai sistem.</p>
                  </div>
                </div>

                <div className="tips-list dashboard-tips-list">
                  <p>1. Baca ringkasan di sisi kiri untuk melihat kondisi akun dan data utama.</p>
                  <p>2. Pilih menu pada bagian Akses Cepat sesuai kebutuhan hari ini.</p>
                  <p>3. Buka Pesan jika ada informasi baru dari sistem atau sekolah.</p>
                </div>
              </section>
            </aside>

            <div className="dashboard-main-stack">
              <section className="dashboard-panel">
                <div className="panel-header">
                  <div>
                    <h2>Akses Cepat</h2>
                    <p className="api-note">
                      Pilih kebutuhan Anda. Setiap tombol memakai kalimat sederhana agar lebih mudah dipahami.
                    </p>
                  </div>
                </div>

                <div className="quick-actions-grid">
                  {quickActions.map((action, index) => (
                    <button
                      key={action.key}
                      type="button"
                      className="quick-action-button"
                      onClick={action.onClick}
                    >
                      <span className="quick-action-index">{index + 1}</span>
                      <div className="quick-action-copy">
                        <strong>{action.label}</strong>
                        <span>{action.description}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </section>

              {secondaryCards.length ? (
                <section className="metrics-grid">
                  {secondaryCards.map((card) => (
                    <article key={card.key} className="metric-card">
                      <span>{card.label}</span>
                      <strong>{formatCellValue(card.value)}</strong>
                    </article>
                  ))}
                </section>
              ) : null}
            </div>
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
