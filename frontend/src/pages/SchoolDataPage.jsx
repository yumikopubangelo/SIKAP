import { useEffect, useState } from 'react'

import { schoolProfileFallback } from '../config'
import { AppShell } from '../components/Common'
import { formatCellValue } from '../utils/formatters'

export default function SchoolDataPage({ authUser, api, getAuthHeaders, onBackToDashboard, onLogout }) {
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
      eyebrow="Sekolah"
      title="Data Sekolah"
      subtitle="Ringkasan kondisi sekolah dan kehadiran per kelas."
      actions={
        <>
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
