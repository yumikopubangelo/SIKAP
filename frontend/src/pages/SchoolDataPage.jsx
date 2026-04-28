import { useMemo, useEffect, useState } from 'react'

import { schoolProfileFallback } from '../config'
import { AppShell } from '../components/Common'
import { formatCellValue } from '../utils/formatters'

const CSV_TEMPLATE = `nama_kelas,tingkat,jurusan,tahun_ajaran,nisn,nama,jenis_kelamin,alamat,id_card,parent_full_name,parent_email,parent_phone
XI RPL 1,XI,RPL,2025/2026,5000001001,Ahmad Fadil,L,Jl. Melati 1,CARD-1001,Bapak Ahmad,ahmad.parent@sikap.local,081234560001
XI RPL 1,XI,RPL,2025/2026,5000001002,Nabila Putri,P,Jl. Mawar 2,CARD-1002,Ibu Nabila,nabila.parent@sikap.local,081234560002`

export default function SchoolDataPage({ authUser, api, getAuthHeaders, onBackToDashboard, onLogout }) {
  const [schoolData, setSchoolData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // CSV import state
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [csvError, setCsvError] = useState('')
  const [csvSuccess, setCsvSuccess] = useState('')
  const [importSummary, setImportSummary] = useState(null)

  const templateLines = useMemo(() => CSV_TEMPLATE.split('\n').length, [])

  useEffect(() => {
    const fetchSchoolData = async () => {
      const headers = getAuthHeaders()
      if (!headers) { setError('Sesi login tidak ditemukan.'); setLoading(false); return }
      setLoading(true)
      try {
        const { data } = await api.get('/rekapitulasi/sekolah', { headers })
        if (!data?.success || !data?.data) throw new Error('Respons tidak valid.')
        setSchoolData(data.data)
      } catch (err) {
        setError(err?.response?.data?.message || err?.message || 'Gagal memuat data sekolah.')
      } finally {
        setLoading(false)
      }
    }
    void fetchSchoolData()
  }, [])

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files?.[0] || null)
    setCsvError('')
    setCsvSuccess('')
    setImportSummary(null)
  }

  const handleCsvImport = async (event) => {
    event.preventDefault()
    if (!selectedFile) { setCsvError('Pilih file CSV terlebih dahulu.'); return }
    const headers = getAuthHeaders()
    if (!headers) { setCsvError('Sesi login tidak ditemukan.'); return }

    setUploading(true)
    setCsvError('')
    setCsvSuccess('')
    setImportSummary(null)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      const { data } = await api.post('/siswa/import-csv', formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' },
      })
      if (!data?.success || !data?.data) throw new Error('Respons tidak valid.')
      setImportSummary(data.data)
      setCsvSuccess(data.message || 'Import CSV selesai.')
    } catch (err) {
      setCsvError(err?.response?.data?.message || err?.message || 'Gagal memproses CSV.')
    } finally {
      setUploading(false)
    }
  }

  const summary = schoolData?.summary || null
  const kelasRows = schoolData?.kelas || []
  const isAdmin = authUser?.role === 'admin'

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Sekolah"
      title="Data Sekolah"
      subtitle="Ringkasan kondisi sekolah, kehadiran per kelas, dan impor data massal."
      actions={
        <>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>Dashboard</button>
          <button type="button" onClick={onLogout}>Keluar</button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}

      <section className="manual-grid">
        <section className="dashboard-panel manual-panel highlighted-panel">
          <div className="panel-header">
            <div>
              <h2>Profil Sekolah</h2>
              <p className="api-note">Identitas dasar sekolah dari konfigurasi sistem.</p>
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
                <p className="api-note">Statistik kehadiran seluruh sekolah.</p>
              </div>
            </div>
            {loading ? (
              <div className="empty-state compact"><p>Memuat ringkasan...</p></div>
            ) : summary ? (
              <div className="mini-metrics-grid">
                <article className="mini-metric-card"><span>Tepat Waktu</span><strong>{formatCellValue(summary.tepat_waktu)}</strong></article>
                <article className="mini-metric-card"><span>Terlambat</span><strong>{formatCellValue(summary.terlambat)}</strong></article>
                <article className="mini-metric-card"><span>Alpha</span><strong>{formatCellValue(summary.alpha)}</strong></article>
                <article className="mini-metric-card"><span>Persentase</span><strong>{summary.persentase}%</strong></article>
              </div>
            ) : (
              <div className="empty-state compact"><p>Ringkasan belum tersedia.</p></div>
            )}
          </section>
        </aside>
      </section>

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Performa per Kelas</h2>
            <p className="api-note">Rekap kehadiran lintas kelas dari endpoint rekapitulasi.</p>
          </div>
        </div>
        {loading ? (
          <div className="empty-state compact"><p>Memuat data kelas...</p></div>
        ) : kelasRows.length ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Kelas</th><th>Tepat Waktu</th><th>Terlambat</th><th>Alpha</th>
                  <th>Izin</th><th>Sakit</th><th>Haid</th><th>Persentase</th>
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
          <div className="empty-state"><p>Belum ada data rekap sekolah.</p></div>
        )}
      </section>

      {isAdmin ? (
        <section className="dashboard-panel">
          <div className="panel-header">
            <div>
              <h2>Import Data CSV</h2>
              <p className="api-note">Onboarding massal: kelas, siswa, akun orang tua, dan relasi — dalam satu file.</p>
            </div>
          </div>

          {csvError ? <p className="alert error">{csvError}</p> : null}
          {csvSuccess ? <p className="alert success">{csvSuccess}</p> : null}

          <div className="manual-grid">
            <section className="manual-panel">
              <form className="manual-form" onSubmit={handleCsvImport}>
                <div className="manual-field">
                  <label htmlFor="csv_import_file">File CSV</label>
                  <input id="csv_import_file" name="file" type="file" accept=".csv,text/csv" onChange={handleFileChange} />
                  <p className="helper-text">
                    Header wajib: <code>nama_kelas</code>, <code>tingkat</code>, <code>jurusan</code>, <code>tahun_ajaran</code>, <code>nisn</code>, <code>nama</code>.
                  </p>
                </div>
                <div className="manual-actions">
                  <button type="submit" disabled={uploading || !selectedFile}>
                    {uploading ? 'Mengunggah...' : 'Proses Import CSV'}
                  </button>
                </div>
              </form>

              {importSummary ? (
                <div style={{ marginTop: '1.25rem' }}>
                  <div className="mini-metrics-grid">
                    <article className="mini-metric-card"><span>Baris Diproses</span><strong>{importSummary.processed_rows}</strong></article>
                    <article className="mini-metric-card"><span>Kelas Baru</span><strong>{importSummary.created_classes}</strong></article>
                    <article className="mini-metric-card"><span>Siswa Baru</span><strong>{importSummary.created_students}</strong></article>
                    <article className="mini-metric-card"><span>Orang Tua Baru</span><strong>{importSummary.created_parent_users}</strong></article>
                  </div>
                  {importSummary.errors?.length ? (
                    <div className="table-wrapper" style={{ marginTop: '0.85rem' }}>
                      <table>
                        <thead><tr><th>Baris</th><th>Pesan Error</th></tr></thead>
                        <tbody>
                          {importSummary.errors.map((item, i) => (
                            <tr key={`${item.row}-${i}`}><td>{item.row}</td><td>{item.message}</td></tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="empty-state compact" style={{ marginTop: '0.85rem' }}>
                      <p>Tidak ada error pada proses import.</p>
                    </div>
                  )}
                </div>
              ) : null}
            </section>

            <aside className="manual-side-panel">
              <section className="dashboard-panel manual-panel">
                <div className="panel-header">
                  <div>
                    <h2>Template CSV</h2>
                    <p className="api-note">Contoh {templateLines} baris sebagai acuan format kolom.</p>
                  </div>
                </div>
                <pre className="import-template">{CSV_TEMPLATE}</pre>
              </section>
            </aside>
          </div>
        </section>
      ) : null}
    </AppShell>
  )
}
