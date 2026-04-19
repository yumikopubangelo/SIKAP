import { statusChartColors } from '../config'
import { formatCellValue } from '../utils/formatters'
import DashboardCharts from './DashboardCharts'

const STATUS_META = {
  tepat_waktu: { label: 'Tepat Waktu', tone: 'success', icon: 'check' },
  terlambat: { label: 'Terlambat', tone: 'warning', icon: 'clock' },
  izin: { label: 'Izin', tone: 'info', icon: 'doc' },
  sakit: { label: 'Sakit', tone: 'info', icon: 'heart' },
  alpha: { label: 'Alpha', tone: 'danger', icon: 'cross' },
  haid: { label: 'Haid', tone: 'info', icon: 'doc' },
  belum_ada: { label: 'Belum Ada Tap', tone: 'muted', icon: 'dash' },
}

const SHOLAT_ICON = {
  subuh: '🌅',
  dzuhur: '🌞',
  ashar: '🌤️',
  maghrib: '🌇',
  isya: '🌙',
  default: '🕌',
}

function StatusBadge({ status, size = 'md' }) {
  const meta = STATUS_META[status] || STATUS_META.belum_ada
  return (
    <span className={`status-chip status-chip-${meta.tone} size-${size}`}>
      <span className="status-chip-dot" aria-hidden="true" />
      {meta.label}
    </span>
  )
}

function ProgressRing({ value, label, sublabel }) {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0))
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (clamped / 100) * circumference
  const color = clamped >= 80 ? '#167a47' : clamped >= 50 ? '#f6a63b' : '#b6243b'

  return (
    <div className="progress-ring">
      <svg viewBox="0 0 140 140" width="140" height="140">
        <circle cx="70" cy="70" r={radius} className="progress-ring-track" />
        <circle
          cx="70"
          cy="70"
          r={radius}
          className="progress-ring-value"
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
        <text x="70" y="68" textAnchor="middle" className="progress-ring-number" fill={color}>
          {clamped}%
        </text>
        <text x="70" y="92" textAnchor="middle" className="progress-ring-caption">
          tepat waktu
        </text>
      </svg>
      <div className="progress-ring-meta">
        <strong>{label}</strong>
        <span>{sublabel}</span>
      </div>
    </div>
  )
}

function formatTimeOnly(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

function formatDatePretty(iso) {
  if (!iso) return '-'
  const d = new Date(iso.length <= 10 ? `${iso}T00:00:00` : iso)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('id-ID', { weekday: 'short', day: 'numeric', month: 'short' })
}

function getSholatIcon(name) {
  if (!name) return SHOLAT_ICON.default
  const key = String(name).toLowerCase()
  return SHOLAT_ICON[key] || SHOLAT_ICON.default
}

export default function StudentDashboardView({
  authUser,
  dashboardData,
  roleDescription,
  sapaan,
  onOpenNotifikasi,
  onOpenProfile,
  onRefresh,
}) {
  const cards = dashboardData?.cards || []
  const charts = dashboardData?.charts || null
  const milestone = dashboardData?.milestone || null
  const student = dashboardData?.student || null
  const rows = dashboardData?.primary_table?.rows || []
  const note = dashboardData?.primary_table?.note
  const role = authUser.role
  const isOrtu = role === 'orangtua'
  const firstName = (authUser.full_name || authUser.username || '').split(' ')[0] || ''

  const cardByKey = Object.fromEntries(cards.map((c) => [c.key, c]))
  const statusTerakhir = cardByKey.status_terakhir?.value || 'belum_ada'
  const absensiBulan = Number(cardByKey.absensi_bulan_ini?.value || 0)
  const tepatWaktu = Number(cardByKey.tepat_waktu?.value || 0)
  const terlambat = Number(cardByKey.terlambat?.value || 0)
  const totalIzin = milestone?.total_izin ?? 0
  const persentaseTepat = milestone?.persentase_tepat ?? 0

  const displayName = isOrtu
    ? (student?.nama || 'Ananda belum terhubung')
    : (authUser.full_name || authUser.username)
  const displayKelas = isOrtu ? student?.kelas : null
  const displayNisn = isOrtu ? student?.nisn : null

  const heroTitle = isOrtu
    ? `${sapaan}${firstName ? `, ${firstName}` : ''}`
    : `${sapaan}${firstName ? `, ${firstName}` : ''}`
  const heroSubtitle = isOrtu
    ? student
      ? `Pantau kehadiran sholat ${student.nama} di sekolah.`
      : 'Akun orang tua belum terhubung ke data siswa. Hubungi wali kelas untuk menautkan nomor telepon Anda.'
    : roleDescription

  const latestRow = rows[0]
  const lastTapTime = latestRow?.timestamp ? formatTimeOnly(latestRow.timestamp) : null
  const lastTapSholat = latestRow?.waktu_sholat || null

  return (
    <div className="student-dashboard">
      {/* HERO */}
      <section className="sd-hero">
        <div className="sd-hero-bg" aria-hidden="true" />
        <div className="sd-hero-inner">
          <div className="sd-hero-copy">
            <span className="sd-hero-eyebrow">{isOrtu ? 'Dashboard Orang Tua' : 'Dashboard Siswa'}</span>
            <h1>{heroTitle}</h1>
            <p>{heroSubtitle}</p>

            {student || !isOrtu ? (
              <div className="sd-hero-meta">
                <div>
                  <span>Nama {isOrtu ? 'Ananda' : 'Siswa'}</span>
                  <strong>{displayName}</strong>
                </div>
                {displayKelas ? (
                  <div>
                    <span>Kelas</span>
                    <strong>{displayKelas}</strong>
                  </div>
                ) : null}
                {displayNisn ? (
                  <div>
                    <span>NISN</span>
                    <strong>{displayNisn}</strong>
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>

          <div className="sd-hero-status">
            <span className="sd-hero-status-label">Status Sholat Terakhir</span>
            <StatusBadge status={statusTerakhir} size="lg" />
            {lastTapTime ? (
              <span className="sd-hero-status-meta">
                {getSholatIcon(lastTapSholat)} {lastTapSholat ? String(lastTapSholat).charAt(0).toUpperCase() + String(lastTapSholat).slice(1) : 'Sholat'} · {lastTapTime}
              </span>
            ) : (
              <span className="sd-hero-status-meta">Belum ada tap tercatat</span>
            )}
            <div className="sd-hero-actions">
              <button type="button" className="sd-btn-ghost" onClick={onOpenNotifikasi}>
                Lihat Pesan
              </button>
              <button type="button" className="sd-btn-outline" onClick={onRefresh}>
                Muat Ulang
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="sd-stats">
        <article className="sd-stat sd-stat-primary">
          <span className="sd-stat-icon" aria-hidden="true">📅</span>
          <div>
            <span>Absensi Bulan Ini</span>
            <strong>{formatCellValue(absensiBulan)}</strong>
            <small>Total tap tercatat bulan berjalan</small>
          </div>
        </article>
        <article className="sd-stat sd-stat-success">
          <span className="sd-stat-icon" aria-hidden="true">✓</span>
          <div>
            <span>Tepat Waktu</span>
            <strong>{formatCellValue(tepatWaktu)}</strong>
            <small>Hadir sebelum iqamah</small>
          </div>
        </article>
        <article className="sd-stat sd-stat-warning">
          <span className="sd-stat-icon" aria-hidden="true">⏰</span>
          <div>
            <span>Terlambat</span>
            <strong>{formatCellValue(terlambat)}</strong>
            <small>Tap setelah iqamah</small>
          </div>
        </article>
        <article className="sd-stat sd-stat-info">
          <span className="sd-stat-icon" aria-hidden="true">📝</span>
          <div>
            <span>Total Izin</span>
            <strong>{formatCellValue(totalIzin)}</strong>
            <small>Izin resmi bulan ini</small>
          </div>
        </article>
      </section>

      {/* MILESTONE + TIMELINE */}
      <section className="sd-split">
        <article className="sd-panel sd-milestone">
          <header>
            <h2>Konsistensi Bulan Ini</h2>
            <p>Pertahankan skor tepat waktu di atas 80% agar tetap berada di zona aman.</p>
          </header>

          <ProgressRing
            value={persentaseTepat}
            label={
              persentaseTepat >= 80
                ? 'Hebat! Pertahankan ya.'
                : persentaseTepat >= 50
                  ? 'Lumayan, masih bisa lebih baik.'
                  : 'Perlu perhatian lebih.'
            }
            sublabel={`${tepatWaktu} dari ${absensiBulan} tap berstatus tepat waktu`}
          />

          <div className="sd-milestone-legend">
            <div>
              <span className="legend-dot dot-success" />
              <span>≥ 80% Zona Aman</span>
            </div>
            <div>
              <span className="legend-dot dot-warning" />
              <span>50–79% Perlu Dorongan</span>
            </div>
            <div>
              <span className="legend-dot dot-danger" />
              <span>&lt; 50% Zona Perhatian</span>
            </div>
          </div>
        </article>

        <article className="sd-panel sd-timeline-panel">
          <header>
            <h2>Riwayat Sholat Terakhir</h2>
            <p>Sepuluh tap terakhir, urut dari yang paling baru.</p>
          </header>

          {rows.length === 0 ? (
            <div className="sd-empty">
              <span aria-hidden="true">🕌</span>
              <p>{note || 'Belum ada riwayat absensi untuk ditampilkan.'}</p>
            </div>
          ) : (
            <ol className="sd-timeline">
              {rows.map((row, idx) => {
                const meta = STATUS_META[row.status] || STATUS_META.belum_ada
                return (
                  <li key={`${row.timestamp || idx}-${idx}`} className={`sd-timeline-item tone-${meta.tone}`}>
                    <div className="sd-timeline-icon" aria-hidden="true">
                      {getSholatIcon(row.waktu_sholat)}
                    </div>
                    <div className="sd-timeline-body">
                      <div className="sd-timeline-head">
                        <strong>
                          {row.waktu_sholat
                            ? String(row.waktu_sholat).charAt(0).toUpperCase() + String(row.waktu_sholat).slice(1)
                            : 'Sholat'}
                        </strong>
                        <StatusBadge status={row.status} size="sm" />
                      </div>
                      <div className="sd-timeline-meta">
                        <span>{formatDatePretty(row.tanggal)}</span>
                        <span aria-hidden="true">•</span>
                        <span>Tap pukul {formatTimeOnly(row.timestamp)}</span>
                      </div>
                    </div>
                  </li>
                )
              })}
            </ol>
          )}
        </article>
      </section>

      {/* CHARTS */}
      <DashboardCharts charts={charts} />

      {/* QUICK ACTIONS */}
      <section className="sd-panel sd-quick">
        <header>
          <h2>Akses Cepat</h2>
          <p>Pilih kebutuhan Anda hari ini.</p>
        </header>
        <div className="sd-quick-grid">
          <button type="button" className="sd-quick-card" onClick={onOpenProfile}>
            <span className="sd-quick-emoji" aria-hidden="true">👤</span>
            <strong>Profil Saya</strong>
            <span>Lihat data akun dan hubungan pengguna.</span>
          </button>
          <button type="button" className="sd-quick-card" onClick={onOpenNotifikasi}>
            <span className="sd-quick-emoji" aria-hidden="true">📬</span>
            <strong>Pesan & Notifikasi</strong>
            <span>Cek pemberitahuan dari sekolah.</span>
          </button>
          <button type="button" className="sd-quick-card" onClick={onRefresh}>
            <span className="sd-quick-emoji" aria-hidden="true">🔄</span>
            <strong>Muat Ulang Data</strong>
            <span>Ambil informasi terbaru dari server.</span>
          </button>
        </div>
      </section>
    </div>
  )
}
