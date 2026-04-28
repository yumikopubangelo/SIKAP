import { useMemo, useState } from 'react'

import { AppShell } from '../components/Common'

const CSV_TEMPLATE = `nama_kelas,tingkat,jurusan,tahun_ajaran,nisn,nama,jenis_kelamin,alamat,id_card,parent_full_name,parent_email,parent_phone
XI RPL 1,XI,RPL,2025/2026,5000001001,Ahmad Fadil,L,Jl. Melati 1,CARD-1001,Bapak Ahmad,ahmad.parent@sikap.local,081234560001
XI RPL 1,XI,RPL,2025/2026,5000001002,Nabila Putri,P,Jl. Mawar 2,CARD-1002,Ibu Nabila,nabila.parent@sikap.local,081234560002`

export default function CsvImportPage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onLogout,
}) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [summary, setSummary] = useState(null)

  const templateLines = useMemo(() => CSV_TEMPLATE.split('\n').length, [])

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null
    setSelectedFile(file)
    setError('')
    setSuccessMessage('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!selectedFile) {
      setError('Pilih file CSV terlebih dahulu.')
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setUploading(true)
    setError('')
    setSuccessMessage('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const { data } = await api.post('/siswa/import-csv', formData, {
        headers: {
          ...headers,
          'Content-Type': 'multipart/form-data',
        },
      })

      if (!data?.success || !data?.data) {
        throw new Error('Respons import CSV tidak valid.')
      }

      setSummary(data.data)
      setSuccessMessage(data.message || 'Import CSV selesai diproses.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memproses import CSV.'
      setError(apiMessage)
    } finally {
      setUploading(false)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Import Data"
      title="Upload CSV Sekolah"
      subtitle="Unggah data siswa, kelas, dan relasi orang tua untuk onboarding massal."
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
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      <section className="manual-grid">
        <section className="dashboard-panel manual-panel highlighted-panel">
          <div className="panel-header">
            <div>
              <h2>Form Upload</h2>
              <p className="api-note">
                CSV ini akan membuat atau memperbarui kelas, siswa, akun orang tua, dan relasinya.
              </p>
            </div>
          </div>

          <form className="manual-form" onSubmit={handleSubmit}>
            <div className="manual-field">
              <label htmlFor="csv_import_file">File CSV</label>
              <input
                id="csv_import_file"
                name="file"
                type="file"
                accept=".csv,text/csv"
                onChange={handleFileChange}
              />
              <p className="helper-text">
                Header wajib: `nama_kelas`, `tingkat`, `jurusan`, `tahun_ajaran`, `nisn`, `nama`.
              </p>
            </div>

            <div className="manual-actions">
              <button type="submit" disabled={uploading}>
                {uploading ? 'Mengunggah...' : 'Proses Import CSV'}
              </button>
            </div>
          </form>
        </section>

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Template CSV</h2>
                <p className="api-note">
                  Template ringkas {templateLines} baris ini bisa dipakai sebagai acuan kolom.
                </p>
              </div>
            </div>
            <pre className="import-template">{CSV_TEMPLATE}</pre>
          </section>
        </aside>
      </section>

      {summary ? (
        <section className="dashboard-panel">
          <div className="panel-header">
            <div>
              <h2>Ringkasan Import</h2>
              <p className="api-note">Menampilkan hasil proses upload terakhir.</p>
            </div>
          </div>

          <div className="mini-metrics-grid">
            <article className="mini-metric-card">
              <span>Baris Diproses</span>
              <strong>{summary.processed_rows}</strong>
            </article>
            <article className="mini-metric-card">
              <span>Kelas Baru</span>
              <strong>{summary.created_classes}</strong>
            </article>
            <article className="mini-metric-card">
              <span>Siswa Baru</span>
              <strong>{summary.created_students}</strong>
            </article>
            <article className="mini-metric-card">
              <span>Parent Baru</span>
              <strong>{summary.created_parent_users}</strong>
            </article>
          </div>

          {summary.errors?.length ? (
            <div className="table-wrapper import-errors-table">
              <table>
                <thead>
                  <tr>
                    <th>Baris</th>
                    <th>Pesan</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.errors.map((item, index) => (
                    <tr key={`${item.row}-${index}`}>
                      <td>{item.row}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state compact">
              <p>Tidak ada error pada proses import terakhir.</p>
            </div>
          )}
        </section>
      ) : null}
    </AppShell>
  )
}
