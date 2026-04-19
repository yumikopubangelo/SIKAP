import { useEffect, useState } from 'react'

import { schoolProfileFallback } from '../config'
import { AppShell } from '../components/Common'
import { formatCellValue } from '../utils/formatters'

export default function SchoolDataPage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onOpenMonitoring,
  onLogout,
}) {
  const [schoolData, setSchoolData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
  })

  const fetchSchoolData = async (nextFilters = filters) => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const params = {}
      if (nextFilters.start_date) {
        params.start_date = nextFilters.start_date
      }
      if (nextFilters.end_date) {
        params.end_date = nextFilters.end_date
      }

      const { data } = await api.get('/rekapitulasi/sekolah', { headers, params })
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

  useEffect(() => {
    void fetchSchoolData()
  }, [])

  const summary = schoolData?.summary || null
  const metadata = schoolData?.metadata || null
  const period = schoolData?.period || {}
  const statusBreakdown = schoolData?.status_breakdown || []
  const topKelas = schoolData?.top_kelas || []
  const bottomKelas = schoolData?.bottom_kelas || []
  const kelasRows = schoolData?.kelas || []

  const handleFilterChange = (event) => {
    const { name, value } = event.target
    setFilters((prev) => ({ ...prev, [name]: value }))
  }

  const handleFilterSubmit = async (event) => {
    event.preventDefault()
    await fetchSchoolData(filters)
  }

  const handleResetFilters = async () => {
    const nextFilters = { start_date: '', end_date: '' }
    setFilters(nextFilters)
    await fetchSchoolData(nextFilters)
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Sekolah"
      title="Data Sekolah & Operasional"
      subtitle="Lihat kesehatan data sekolah, rekap kehadiran, kesiapan kartu RFID, dan kelas yang perlu perhatian."
      actions={
        <>
          {['admin', 'kepsek'].includes(authUser.role) ? (
            <button type="button" className="ghost-button" onClick={onOpenMonitoring}>
              Monitoring
            </button>
          ) : null}
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Keluar
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Filter Periode</h2>
            <p className="api-note">
              Gunakan filter tanggal agar analisis sekolah lebih fokus pada periode yang sedang ditinjau.
            </p>
          </div>
        </div>

        <form className="toolbar-form" onSubmit={handleFilterSubmit}>
          <div className="toolbar-grid">
            <label className="manual-field">
              <span>Tanggal Mulai</span>
              <input
                type="date"
                name="start_date"
                value={filters.start_date}
                onChange={handleFilterChange}
              />
            </label>
            <label className="manual-field">
              <span>Tanggal Akhir</span>
              <input
                type="date"
                name="end_date"
                value={filters.end_date}
                onChange={handleFilterChange}
              />
            </label>
          </div>
          <div className="manual-actions">
            <button type="submit" disabled={loading}>
              Terapkan Filter
            </button>
            <button
              type="button"
              className="ghost-button"
              onClick={handleResetFilters}
              disabled={loading}
            >
              Semua Periode
            </button>
          </div>
        </form>
      </section>

      <section className="insight-strip" aria-label="Ringkasan sekolah">
        <article className="insight-card insight-primary">
          <span className="insight-label">Total Siswa</span>
          <strong>{formatCellValue(metadata?.total_siswa)}</strong>
          <span className="insight-foot">Jumlah siswa aktif yang tercatat pada basis data sekolah.</span>
        </article>
        <article className="insight-card insight-success">
          <span className="insight-label">Kehadiran Sekolah</span>
          <strong>{summary ? `${summary.persentase}%` : '-'}</strong>
          <span className="insight-foot">
            {summary
              ? `${formatCellValue(summary.total_hadir)} hadir dari ${formatCellValue(summary.total_valid)} status valid.`
              : 'Ringkasan kehadiran belum tersedia.'}
          </span>
        </article>
        <article className="insight-card insight-warning">
          <span className="insight-label">Perangkat Online</span>
          <strong>{formatCellValue(metadata?.perangkat_online)}</strong>
          <span className="insight-foot">Gunakan Monitoring untuk melihat performa service dan scrape metrics.</span>
        </article>
        <article className="insight-card insight-neutral">
          <span className="insight-label">Periode</span>
          <strong>
            {period.filter_applied
              ? `${formatCellValue(period.start_date)} - ${formatCellValue(period.end_date)}`
              : 'Semua data'}
          </strong>
          <span className="insight-foot">
            {metadata
              ? `${formatCellValue(metadata.total_tap)} tap tercatat pada periode ini.`
              : 'Belum ada informasi periode.'}
          </span>
        </article>
      </section>

      <section className="manual-grid">
        <section className="dashboard-panel manual-panel highlighted-panel">
          <div className="panel-header">
            <div>
              <h2>Profil Sekolah</h2>
              <p className="api-note">
                Identitas dasar sekolah masih memakai fallback frontend, sementara ringkasan operasional berasal dari backend.
              </p>
            </div>
          </div>

          <dl className="detail-list">
            <div><dt>Nama Sekolah</dt><dd>{schoolProfileFallback.name}</dd></div>
            <div><dt>Sistem</dt><dd>{schoolProfileFallback.system}</dd></div>
            <div><dt>Fokus</dt><dd>{schoolProfileFallback.focus}</dd></div>
            <div><dt>Tagline</dt><dd>{schoolProfileFallback.tagline}</dd></div>
            <div><dt>Total Kelas</dt><dd>{formatCellValue(metadata?.total_kelas)}</dd></div>
            <div><dt>Rata-rata Kelas</dt><dd>{metadata ? `${metadata.rata_rata_persentase_kelas}%` : '-'}</dd></div>
            <div><dt>Siswa Berkartu</dt><dd>{formatCellValue(metadata?.siswa_berkartu)}</dd></div>
            <div><dt>Belum Punya Kartu</dt><dd>{formatCellValue(metadata?.siswa_tanpa_kartu)}</dd></div>
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
                <article className="mini-metric-card">
                  <span>Total Hadir</span>
                  <strong>{formatCellValue(summary.total_hadir)}</strong>
                </article>
                <article className="mini-metric-card">
                  <span>Total Tap</span>
                  <strong>{formatCellValue(summary.total_absensi)}</strong>
                </article>
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Ringkasan sekolah belum tersedia.</p>
              </div>
            )}
          </section>

          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Status Operasional</h2>
                <p className="api-note">
                  Indikator singkat untuk melihat apakah data sekolah sudah siap dipakai harian.
                </p>
              </div>
            </div>

            <div className="tips-list">
              <p>
                Perangkat online: <strong>{formatCellValue(metadata?.perangkat_online)}</strong>
              </p>
              <p>
                Siswa tanpa kartu RFID: <strong>{formatCellValue(metadata?.siswa_tanpa_kartu)}</strong>
              </p>
              <p>
                Jika perangkat online rendah atau kartu belum lengkap, absensi harian berisiko terganggu.
              </p>
            </div>
          </section>
        </aside>
      </section>

      <section className="metrics-grid">
        {statusBreakdown.map((item) => (
          <article key={item.status} className="metric-card">
            <span>{item.label}</span>
            <strong>{formatCellValue(item.count)}</strong>
          </article>
        ))}
      </section>

      <section className="manual-grid">
        <section className="dashboard-panel">
          <div className="panel-header">
            <div>
              <h2>Kelas Terbaik</h2>
              <p className="api-note">
                Kelas dengan performa kehadiran paling kuat pada periode yang sedang ditinjau.
              </p>
            </div>
          </div>

          {topKelas.length ? (
            <div className="tips-list">
              {topKelas.map((row, index) => (
                <p key={`${row.id_kelas}-top`}>
                  {index + 1}. {row.nama_kelas}: {row.persentase}% dengan {formatCellValue(row.total_hadir)} kehadiran dari {formatCellValue(row.total_valid)} status valid.
                </p>
              ))}
            </div>
          ) : (
            <div className="empty-state compact">
              <p>Belum ada kelas yang bisa diperingkat.</p>
            </div>
          )}
        </section>

        <section className="dashboard-panel">
          <div className="panel-header">
            <div>
              <h2>Perlu Perhatian</h2>
              <p className="api-note">
                Gunakan daftar ini untuk follow-up wali kelas, guru piket, atau evaluasi perangkat RFID.
              </p>
            </div>
          </div>

          {bottomKelas.length ? (
            <div className="tips-list">
              {bottomKelas.map((row, index) => (
                <p key={`${row.id_kelas}-bottom`}>
                  {index + 1}. {row.nama_kelas}: {row.persentase}% dengan {formatCellValue(row.alpha)} alpha dan {formatCellValue(row.terlambat)} keterlambatan.
                </p>
              ))}
            </div>
          ) : (
            <div className="empty-state compact">
              <p>Belum ada kelas yang membutuhkan perhatian khusus.</p>
            </div>
          )}
        </section>
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
                  <th>Siswa</th>
                  <th>Tepat Waktu</th>
                  <th>Terlambat</th>
                  <th>Alpha</th>
                  <th>Izin</th>
                  <th>Sakit</th>
                  <th>Haid</th>
                  <th>Total Hadir</th>
                  <th>Persentase</th>
                </tr>
              </thead>
              <tbody>
                {kelasRows.map((row) => (
                  <tr key={row.id_kelas}>
                    <td>{row.nama_kelas}</td>
                    <td>{formatCellValue(row.jumlah_siswa)}</td>
                    <td>{formatCellValue(row.tepat_waktu)}</td>
                    <td>{formatCellValue(row.terlambat)}</td>
                    <td>{formatCellValue(row.alpha)}</td>
                    <td>{formatCellValue(row.izin)}</td>
                    <td>{formatCellValue(row.sakit)}</td>
                    <td>{formatCellValue(row.haid)}</td>
                    <td>{formatCellValue(row.total_hadir)}</td>
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
