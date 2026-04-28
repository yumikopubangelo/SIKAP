import { useEffect, useState } from 'react'

import { AppShell } from '../components/Common'
import { warningLetterTypeOptions } from '../config'
import { formatCellValue } from '../utils/formatters'

export default function WarningLetterPage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onLogout,
}) {
  const [filterJenis, setFilterJenis] = useState('')
  const [letters, setLetters] = useState([])
  const [selectedDetail, setSelectedDetail] = useState(null)
  const [pagination, setPagination] = useState({ page: 1, limit: 50, total_items: 0, total_pages: 1 })
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchLetters = async () => {
    const headers = getAuthHeaders()
    if (!headers) { setError('Sesi login tidak ditemukan.'); setLoading(false); return }

    setLoading(true)
    try {
      const { data } = await api.get('/surat-peringatan', {
        headers,
        params: { jenis: filterJenis || undefined, page: 1, limit: 50 },
      })
      if (!data?.success || !Array.isArray(data?.data)) throw new Error('Respons tidak valid.')
      setLetters(data.data)
      setPagination({
        page: data?.pagination?.page ?? 1,
        limit: data?.pagination?.limit ?? 50,
        total_items: data?.pagination?.total_items ?? data.data.length,
        total_pages: data?.pagination?.total_pages ?? 1,
      })
      if (data.data[0]?.id_sp) void fetchDetail(data.data[0].id_sp)
      else setSelectedDetail(null)
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Gagal memuat surat peringatan.')
    } finally {
      setLoading(false)
    }
  }

  const fetchDetail = async (idSp) => {
    const headers = getAuthHeaders()
    if (!headers) return
    setDetailLoading(true)
    try {
      const { data } = await api.get(`/surat-peringatan/${idSp}`, { headers })
      if (!data?.success || !data?.data) throw new Error('Respons detail tidak valid.')
      setSelectedDetail(data.data)
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Gagal memuat detail SP.')
    } finally {
      setDetailLoading(false)
    }
  }

  useEffect(() => { void fetchLetters() }, [filterJenis])

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Surat Peringatan"
      title="Daftar Surat Peringatan"
      subtitle="Pantau SP yang terbit, siswa terkait, dan status pengiriman ke orang tua."
      actions={
        <>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>Dashboard</button>
          <button type="button" onClick={onLogout}>Keluar</button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}

      <section className="dashboard-panel">
        <div className="sp-filter-bar">
          <div className="manual-field sp-filter-field">
            <label htmlFor="sp_filter_jenis">Jenis SP</label>
            <select
              id="sp_filter_jenis"
              value={filterJenis}
              onChange={(e) => setFilterJenis(e.target.value)}
            >
              {warningLetterTypeOptions.map((item) => (
                <option key={item.label} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
          <p className="api-note sp-filter-count">
            Menampilkan <strong>{letters.length}</strong> dari {pagination.total_items} surat peringatan.
          </p>
        </div>

        {loading ? (
          <div className="empty-state compact"><p>Memuat surat peringatan...</p></div>
        ) : letters.length ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Jenis</th>
                  <th>Tanggal</th>
                  <th>Siswa</th>
                  <th>Kelas</th>
                  <th>Status Kirim</th>
                  <th>Pengirim</th>
                </tr>
              </thead>
              <tbody>
                {letters.map((item) => (
                  <tr
                    key={item.id_sp}
                    onClick={() => void fetchDetail(item.id_sp)}
                    className={`clickable-row${selectedDetail?.id_sp === item.id_sp ? ' active-row' : ''}`}
                  >
                    <td><span className={`sp-badge sp-badge--${(item.jenis || '').toLowerCase()}`}>{item.jenis}</span></td>
                    <td>{formatCellValue(item.tanggal)}</td>
                    <td>{item.siswa?.nama || '-'}</td>
                    <td>{item.siswa?.kelas || '-'}</td>
                    <td>{item.status_kirim || '-'}</td>
                    <td>{item.pengirim?.full_name || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state"><p>Belum ada surat peringatan untuk filter ini.</p></div>
        )}
      </section>

      {selectedDetail || detailLoading ? (
        <section className="dashboard-panel highlighted-panel">
          <div className="panel-header">
            <div>
              <h2>Detail Surat Peringatan</h2>
              <p className="api-note">Informasi lengkap SP yang dipilih dari tabel di atas.</p>
            </div>
          </div>

          {detailLoading ? (
            <div className="empty-state compact"><p>Memuat detail...</p></div>
          ) : selectedDetail ? (
            <dl className="detail-list">
              <div><dt>Jenis</dt><dd>{selectedDetail.jenis || '-'}</dd></div>
              <div><dt>Tanggal</dt><dd>{formatCellValue(selectedDetail.tanggal)}</dd></div>
              <div><dt>Siswa</dt><dd>{selectedDetail.siswa?.nama || '-'}</dd></div>
              <div><dt>Kelas</dt><dd>{selectedDetail.siswa?.kelas || '-'}</dd></div>
              <div><dt>Status Kirim</dt><dd>{selectedDetail.status_kirim || '-'}</dd></div>
              <div><dt>Orang Tua</dt><dd>{selectedDetail.orangtua?.full_name || '-'}</dd></div>
              <div><dt>Email</dt><dd>{selectedDetail.orangtua?.email || '-'}</dd></div>
              <div><dt>Alasan</dt><dd>{selectedDetail.alasan || '-'}</dd></div>
            </dl>
          ) : null}
        </section>
      ) : null}
    </AppShell>
  )
}
