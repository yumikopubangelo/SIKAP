import { dashboardTitles, roleLabels } from '../config'
import { AppShell } from '../components/Common'
import DashboardCharts from '../components/DashboardCharts'
import StudentDashboardView from '../components/StudentDashboardView'
import { formatCellValue, formatColumnLabel } from '../utils/formatters'

function formatStatValue(value) {
  if (typeof value === 'string' && /^[a-z][a-z0-9]*(_[a-z0-9]+)+$/.test(value)) {
    return formatColumnLabel(value)
  }
  return formatCellValue(value)
}

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

function getStatusLabel(val) {
  if (typeof val !== 'string') return val;
  const match = {
    'tepat_waktu': 'Tepat Waktu',
    'terlambat': 'Terlambat',
    'izin': 'Izin',
    'sakit': 'Sakit',
    'alpha': 'Alpha',
    'haid': 'Haid',
    'belum_ada': 'Belum Ada',
  };
  return match[val] || val;
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
  onOpenCsvImport,
  onOpenDutySchedule,
  onOpenWarningLetters,
  onLogout,
}) {
  const cards = dashboardData?.cards || []
  const charts = dashboardData?.charts || null
  const highlightedCards = cards.slice(0, 4)
  const secondaryCards = cards.slice(4)
  const sapaan = getSapaan()
  const roleDescription = ROLE_DESCRIPTIONS[authUser.role] || ''
  const firstName = (authUser.full_name || authUser.username || '').split(' ')[0] || ''

  const pendingTasks = dashboardData?.pending_tasks || null
  const perangkatList = dashboardData?.perangkat_list || null
  const milestone = dashboardData?.milestone || null
  const zonaMerah = dashboardData?.zona_merah || null

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
    ...(['admin', 'guru_piket'].includes(authUser.role)
      ? [
          {
            key: 'duty-schedule',
            label: 'Jadwal Piket',
            description: 'Lihat giliran piket aktif dan jam tugas tiap guru piket.',
            onClick: onOpenDutySchedule,
          },
        ]
      : []),
    ...(['admin', 'kepsek', 'wali_kelas', 'orangtua', 'siswa'].includes(authUser.role)
      ? [
          {
            key: 'warning-letters',
            label: 'Surat Peringatan',
            description: 'Pantau SP yang sudah diterbitkan dan status kirimnya.',
            onClick: onOpenWarningLetters,
          },
        ]
      : []),
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
          {
            key: 'csv-import',
            label: 'Import CSV',
            description: 'Unggah data siswa, kelas, dan relasi orang tua dalam sekali proses.',
            onClick: onOpenCsvImport,
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

  const isPersonalRole = authUser.role === 'siswa' || authUser.role === 'orangtua'

  if (isPersonalRole) {
    return (
      <AppShell
        authUser={authUser}
        eyebrow={dashboardTitle}
        title={`${sapaan}${firstName ? `, ${firstName}` : ''}`}
        subtitle={roleDescription || `Masuk sebagai ${roleLabels[authUser.role] || authUser.role}.`}
        actions={
          <>
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
        ) : (
          <StudentDashboardView
            authUser={authUser}
            dashboardData={dashboardData}
            roleDescription={roleDescription}
            sapaan={sapaan}
            onOpenNotifikasi={onOpenNotifikasi}
            onOpenProfile={onOpenProfile}
            onRefresh={onRefresh}
          />
        )}
      </AppShell>
    )
  }

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
          {['admin', 'kepsek'].includes(authUser.role) ? (
            <button type="button" className="ghost-button" onClick={onOpenMonitoring}>
              Monitoring
            </button>
          ) : null}
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

          {pendingTasks && pendingTasks.total > 0 ? (
            <section className="dashboard-panel alert-panel alert-warning" style={{ backgroundColor: '#fff3cd', borderLeft: '4px solid #ffc107', padding: '1.25rem', marginBottom: '1.5rem', borderRadius: '6px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ margin: '0 0 0.5rem 0', color: '#856404', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    Tugas Menunggu Anda!
                  </h3>
                  <p style={{ margin: 0, color: '#856404', fontSize: '0.95rem', lineHeight: 1.5 }}>
                    Terdapat <strong>{pendingTasks.sengketa} sengketa absensi</strong> dan <strong>{pendingTasks.izin} pengajuan izin</strong> yang menunggu persetujuan Anda sebagai Wali Kelas.
                  </p>
                </div>
                <button type="button" className="primary-button" onClick={onOpenNotifikasi} style={{ whiteSpace: 'nowrap', backgroundColor: '#856404', color: '#fff', border: 'none' }}>
                  Periksa Sekarang
                </button>
              </div>
            </section>
          ) : null}

          {zonaMerah && zonaMerah.length > 0 ? (
            <section className="dashboard-panel alert-panel alert-danger" style={{ backgroundColor: '#fdf2f2', borderLeft: '4px solid #dc3545', padding: '1.5rem', marginBottom: '1.5rem', borderRadius: '6px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#9b1c1c', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Siswa Dalam Pengawasan Khusus (Zona Merah SP)
              </h3>
              <p style={{ margin: '0 0 1.25rem 0', color: '#771d1d', fontSize: '0.95rem' }}>Perhatian! Siswa di bawah ini telah mencapai 2 kali Alpha atau lebih dan hampir melewati ambang batas Surat Peringatan (SP).</p>
              <div style={{ background: '#fff', borderRadius: '4px', border: '1px solid #fecaca', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', margin: 0 }}>
                  <thead style={{ backgroundColor: '#fee2e2' }}>
                    <tr>
                      <th style={{ padding: '0.75rem 1rem', color: '#9b1c1c', borderBottom: '1px solid #fecaca', fontWeight: 600 }}>Nama Siswa</th>
                      <th style={{ padding: '0.75rem 1rem', color: '#9b1c1c', borderBottom: '1px solid #fecaca', fontWeight: 600 }}>Kelas</th>
                      <th style={{ padding: '0.75rem 1rem', color: '#9b1c1c', borderBottom: '1px solid #fecaca', textAlign: 'right', fontWeight: 600 }}>Total Alpha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {zonaMerah.map((siswa, idx) => (
                      <tr key={`zona-${idx}`} style={{ borderBottom: idx !== zonaMerah.length - 1 ? '1px solid #fecaca' : 'none' }}>
                        <td style={{ padding: '0.75rem 1rem', color: '#771d1d' }}><strong>{siswa.nama}</strong></td>
                        <td style={{ padding: '0.75rem 1rem', color: '#771d1d' }}>{siswa.kelas}</td>
                        <td style={{ padding: '0.75rem 1rem', color: '#dc3545', textAlign: 'right', fontWeight: 'bold' }}>{siswa.jumlah}x</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}

          {perangkatList && perangkatList.length > 0 ? (
            <section className="dashboard-panel" style={{ marginBottom: '1.5rem', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
              <div className="panel-header" style={{ marginBottom: '1rem' }}>
                <div>
                  <h2 style={{ fontSize: '1.1rem' }}>Status Fisik Terminal IoT SIKAP</h2>
                  <p className="api-note">Pantauan real-time mesin RFID melalui protokol heartbeat 3-menit.</p>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {perangkatList.map(p => (
                  <div key={p.device_id} style={{ display: 'flex', alignItems: 'center', padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#f8fafc', transition: 'all 0.2s', ':hover': { transform: 'translateY(-2px)' } }}>
                    <div style={{ width: '12px', height: '12px', flexShrink: 0, borderRadius: '50%', backgroundColor: p.status === 'online' ? '#10b981' : '#ef4444', marginRight: '1rem', boxShadow: `0 0 8px ${p.status === 'online' ? '#10b981' : '#ef4444'}` }}></div>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <h4 style={{ margin: '0 0 0.25rem 0', fontSize: '1rem', color: '#1e293b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.nama}</h4>
                      <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                        <span style={{ fontFamily: 'monospace' }}>{p.device_id}</span> <br/>
                        {p.status === 'online' ? <span style={{ color: '#10b981', fontWeight: 600 }}>Terkoneksi</span> : <span style={{ color: '#ef4444', fontWeight: 600 }}>Terputus</span>} 
                        {p.last_ping ? ` • ${new Date(p.last_ping).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}` : ''}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ) : null}

          {milestone ? (
            <section className="dashboard-panel" style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '2rem', padding: '0.5rem' }}>
                <div style={{ flex: '1 1 250px' }}>
                  <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.25rem' }}>
                    Milestone Kehadiran
                  </h2>
                  <p className="api-note" style={{ margin: 0 }}>
                    Pertahankan persentase kehadiran tepat waktu di atas <strong>80%</strong> untuk menyelesaikan target bulan ini secara memuaskan!
                  </p>
                </div>
                <div style={{ flex: '1 1 300px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', padding: '1rem', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', alignItems: 'flex-end' }}>
                    <span style={{ fontWeight: 500, color: '#475569', fontSize: '0.95rem' }}>Skor Tepat Waktu</span>
                    <span style={{ fontWeight: 'bold', fontSize: '1.5rem', lineHeight: 1, color: milestone.persentase_tepat >= 80 ? '#10b981' : '#f59e0b' }}>
                      {milestone.persentase_tepat}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '10px', backgroundColor: '#e2e8f0', borderRadius: '5px', overflow: 'hidden' }}>
                    <div style={{ width: `${milestone.persentase_tepat}%`, height: '100%', backgroundColor: milestone.persentase_tepat >= 80 ? '#10b981' : milestone.persentase_tepat >= 50 ? '#f59e0b' : '#ef4444', transition: 'width 1s ease-in-out', borderRadius: '5px' }}></div>
                  </div>
                  <div style={{ marginTop: '0.85rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8' }}>
                    <span>0%</span>
                    <span>Batas Aman 80%</span>
                    <span>100%</span>
                  </div>
                  <div style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '0.85rem', color: '#64748b', borderTop: '1px solid #e2e8f0', paddingTop: '0.5rem' }}>
                    Total pemakaian hak Izin bulan ini: <strong style={{ color: '#0f172a' }}>{milestone.total_izin} kali</strong>
                  </div>
                </div>
              </div>
            </section>
          ) : null}

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

          {dashboardData?.secondary_table ? (
            <section className="dashboard-panel">
              <div className="panel-header">
                <div>
                  <h2>{dashboardData.secondary_table.title}</h2>
                  <p className="api-note">{dashboardData.secondary_table.note}</p>
                </div>
              </div>

              {dashboardData.secondary_table.rows?.length ? (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {dashboardData.secondary_table.columns.map((column) => (
                          <th key={column}>{formatColumnLabel(column)}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {dashboardData.secondary_table.rows.map((row, index) => (
                        <tr key={`${dashboardData.secondary_table.title}-${index}`}>
                          {dashboardData.secondary_table.columns.map((column) => (
                            <td key={`${index}-${column}`}>{formatCellValue(row[column])}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">
                  <p>Belum ada data untuk ditampilkan.</p>
                </div>
              )}
            </section>
          ) : null}
        </>
      ) : null}
    </AppShell>
  )
}
