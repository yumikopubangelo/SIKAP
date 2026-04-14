import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

import { reportPath } from '../config'
import { AppShell } from '../components/Common'
import { flattenApiErrors, formatCellValue, getTodayInputValue } from '../utils/formatters'

function buildInitialForm() {
  const today = getTodayInputValue()
  return {
    jenis: 'kelas',
    filter_id: '',
    tanggal_mulai: today,
    tanggal_selesai: today,
    format: 'pdf',
  }
}

function buildDownloadUrl(apiBaseUrl, reportId) {
  return `${apiBaseUrl}/laporan/download/${reportId}`
}

export default function ReportPage({
  authUser,
  api,
  apiBaseUrlValue,
  getAuthHeaders,
  onBackToDashboard,
  onLogout,
}) {
  const [form, setForm] = useState(buildInitialForm)
  const [availableClasses, setAvailableClasses] = useState([])
  const [loadingClasses, setLoadingClasses] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [lastReport, setLastReport] = useState(null)

  useEffect(() => {
    const fetchClassOptions = async () => {
      const headers = getAuthHeaders()
      if (!headers) {
        setError('Sesi login tidak ditemukan. Silakan login ulang.')
        setLoadingClasses(false)
        return
      }

      setLoadingClasses(true)
      try {
        const { data } = await api.get('/rekapitulasi/sekolah', { headers })
        const kelasRows = Array.isArray(data?.data?.kelas) ? data.data.kelas : []
        setAvailableClasses(kelasRows)
      } catch (requestError) {
        const apiMessage =
          requestError?.response?.data?.message ||
          requestError?.message ||
          'Gagal memuat daftar kelas.'
        setError(apiMessage)
      } finally {
        setLoadingClasses(false)
      }
    }

    void fetchClassOptions()
  }, [])

  const selectedClass = useMemo(
    () => availableClasses.find((item) => String(item.id_kelas) === String(form.filter_id)),
    [availableClasses, form.filter_id],
  )

  const isClassReport = form.jenis === 'kelas'
  const isStudentReport = form.jenis === 'siswa'

  const handleFieldChange = (event) => {
    const { name, value } = event.target

    setFieldErrors((prev) => ({ ...prev, [name]: '', date_range: '' }))
    setError('')
    setSuccessMessage('')

    if (name === 'jenis') {
      setForm((prev) => ({
        ...prev,
        jenis: value,
        filter_id: value === 'kelas' ? prev.filter_id : '',
      }))
      return
    }

    if (name === 'filter_id' && isStudentReport) {
      setForm((prev) => ({ ...prev, [name]: value.replace(/\D/g, '') }))
      return
    }

    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const validateForm = () => {
    const nextErrors = {}

    if (isClassReport && !form.filter_id) {
      nextErrors.filter_id = 'Pilih kelas terlebih dahulu.'
    }

    if (isStudentReport && !form.filter_id) {
      nextErrors.filter_id = 'Isi ID siswa untuk laporan per siswa.'
    }

    if (isStudentReport && form.filter_id && !/^\d+$/.test(form.filter_id)) {
      nextErrors.filter_id = 'ID siswa harus berupa angka.'
    }

    if (form.tanggal_mulai && form.tanggal_selesai && form.tanggal_mulai > form.tanggal_selesai) {
      nextErrors.date_range = 'Tanggal mulai tidak boleh melebihi tanggal selesai.'
    }

    return nextErrors
  }

  const handleGenerateReport = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    const localErrors = validateForm()
    if (Object.keys(localErrors).length) {
      setFieldErrors(localErrors)
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSubmitting(true)

    try {
      const payload = {
        jenis: form.jenis,
        format: form.format,
        tanggal_mulai: form.tanggal_mulai || undefined,
        tanggal_selesai: form.tanggal_selesai || undefined,
      }

      if (form.jenis !== 'sekolah') {
        payload.filter_id = Number(form.filter_id)
      }

      const { data } = await api.post('/laporan/generate', payload, { headers })
      if (!data?.success || !data?.data?.id_laporan) {
        throw new Error('Respons generate laporan tidak valid.')
      }

      const reportMeta = {
        ...data.data,
        download_url: buildDownloadUrl(apiBaseUrlValue, data.data.id_laporan),
        jenis_label:
          form.jenis === 'kelas'
            ? selectedClass?.nama_kelas || `Kelas #${form.filter_id}`
            : form.jenis === 'siswa'
              ? `Siswa #${form.filter_id}`
              : 'Sekolah',
        periode:
          form.tanggal_mulai && form.tanggal_selesai
            ? `${form.tanggal_mulai} s.d. ${form.tanggal_selesai}`
            : 'Semua periode',
      }

      setLastReport(reportMeta)
      setSuccessMessage(data?.message || 'Laporan berhasil digenerate.')
      setFieldErrors({})
    } catch (requestError) {
      const apiErrors = requestError?.response?.data?.errors || {}
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal generate laporan.'

      setFieldErrors((prev) => ({
        ...prev,
        filter_id: apiErrors.filter_id || prev.filter_id || '',
      }))
      setError([apiMessage, flattenApiErrors(apiErrors)].filter(Boolean).join(' '))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!lastReport?.id_laporan) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setDownloading(true)
    setError('')
    setSuccessMessage('')

    try {
      const response = await axios.get(lastReport.download_url, {
        headers,
        responseType: 'blob',
        timeout: 20000,
      })

      const extension = lastReport.format === 'excel' ? 'xlsx' : 'pdf'
      const filename = `laporan-${lastReport.jenis}-${lastReport.id_laporan}.${extension}`
      const blobUrl = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(blobUrl)

      setSuccessMessage('File laporan berhasil diunduh.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal mengunduh file laporan.'
      setError(apiMessage)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Laporan"
      title="Buat Laporan"
      subtitle="Pilih jenis laporan dan unduh hasilnya."
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
        <section className="dashboard-panel manual-panel">
          <div className="panel-header">
            <div>
              <h2>Form Generate</h2>
              <p className="api-note">
                Backend saat ini menerima jenis `kelas`, `siswa`, atau `sekolah`, dengan `filter_id`
                wajib untuk laporan kelas dan siswa.
              </p>
            </div>
          </div>

          <form className="manual-form" onSubmit={handleGenerateReport}>
            <div className="manual-form-grid">
              <div className="manual-field">
                <label htmlFor="report_jenis">Jenis Laporan</label>
                <select
                  id="report_jenis"
                  name="jenis"
                  value={form.jenis}
                  onChange={handleFieldChange}
                >
                  <option value="kelas">Per Kelas</option>
                  <option value="sekolah">Sekolah</option>
                  <option value="siswa">Per Siswa</option>
                </select>
              </div>

              <div className="manual-field">
                <label htmlFor="report_format">Format File</label>
                <select
                  id="report_format"
                  name="format"
                  value={form.format}
                  onChange={handleFieldChange}
                >
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                </select>
              </div>

              {isClassReport ? (
                <div className="manual-field manual-field-full">
                  <label htmlFor="report_filter_kelas">Kelas</label>
                  <select
                    id="report_filter_kelas"
                    name="filter_id"
                    value={form.filter_id}
                    onChange={handleFieldChange}
                    disabled={loadingClasses}
                  >
                    <option value="">
                      {loadingClasses ? 'Memuat daftar kelas...' : 'Pilih kelas'}
                    </option>
                    {availableClasses.map((kelas) => (
                      <option key={kelas.id_kelas} value={kelas.id_kelas}>
                        {kelas.nama_kelas}
                      </option>
                    ))}
                  </select>
                  {fieldErrors.filter_id ? (
                    <p className="field-error">{fieldErrors.filter_id}</p>
                  ) : (
                    <p className="helper-text">
                      Daftar kelas diambil dari endpoint rekap sekolah yang sudah tersedia.
                    </p>
                  )}
                </div>
              ) : null}

              {isStudentReport ? (
                <div className="manual-field manual-field-full">
                  <label htmlFor="report_filter_siswa">ID Siswa</label>
                  <input
                    id="report_filter_siswa"
                    name="filter_id"
                    type="text"
                    inputMode="numeric"
                    value={form.filter_id}
                    onChange={handleFieldChange}
                    placeholder="Masukkan ID siswa dari database"
                  />
                  {fieldErrors.filter_id ? (
                    <p className="field-error">{fieldErrors.filter_id}</p>
                  ) : (
                    <p className="helper-text">
                      Backend belum menyediakan daftar pilihan siswa khusus laporan, jadi input ini
                      masih memakai ID siswa.
                    </p>
                  )}
                </div>
              ) : null}

              <div className="manual-field">
                <label htmlFor="report_tanggal_mulai">Tanggal Mulai</label>
                <input
                  id="report_tanggal_mulai"
                  name="tanggal_mulai"
                  type="date"
                  value={form.tanggal_mulai}
                  onChange={handleFieldChange}
                />
              </div>

              <div className="manual-field">
                <label htmlFor="report_tanggal_selesai">Tanggal Selesai</label>
                <input
                  id="report_tanggal_selesai"
                  name="tanggal_selesai"
                  type="date"
                  value={form.tanggal_selesai}
                  onChange={handleFieldChange}
                />
              </div>
            </div>

            {fieldErrors.date_range ? <p className="field-error">{fieldErrors.date_range}</p> : null}

            <div className="manual-actions">
              <button type="submit" disabled={submitting}>
                {submitting ? 'Menggenerate...' : 'Generate Laporan'}
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => {
                  setForm(buildInitialForm())
                  setFieldErrors({})
                  setError('')
                  setSuccessMessage('')
                }}
                disabled={submitting}
              >
                Reset Form
              </button>
            </div>
          </form>
        </section>

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel highlighted-panel">
            <div className="panel-header">
              <div>
                <h2>Hasil Terakhir</h2>
                <p className="api-note">
                  Metadata file yang paling baru digenerate dari halaman ini.
                </p>
              </div>
            </div>

            {lastReport ? (
              <div className="submission-summary">
                <dl className="detail-list">
                  <div><dt>ID Laporan</dt><dd>{lastReport.id_laporan}</dd></div>
                  <div><dt>Jenis</dt><dd>{lastReport.jenis_label}</dd></div>
                  <div><dt>Format</dt><dd>{String(lastReport.format || '').toUpperCase()}</dd></div>
                  <div><dt>Dibuat</dt><dd>{formatCellValue(lastReport.created_at)}</dd></div>
                  <div><dt>Periode</dt><dd>{lastReport.periode}</dd></div>
                  <div><dt>Endpoint</dt><dd>{reportPath}</dd></div>
                </dl>

                <div className="manual-actions">
                  <button type="button" onClick={handleDownloadReport} disabled={downloading}>
                    {downloading ? 'Mengunduh...' : 'Download File'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Belum ada laporan yang digenerate dari sesi ini.</p>
              </div>
            )}
          </section>

          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Panduan Singkat</h2>
              </div>
            </div>

            <div className="tips-list">
              <p>Gunakan laporan kelas untuk kebutuhan rekap wali kelas atau pimpinan sekolah.</p>
              <p>Pilih periode yang sempit bila file PDF mulai terasa terlalu panjang.</p>
              <p>Format Excel lebih enak dipakai saat data ingin diolah ulang di spreadsheet.</p>
              <p>Laporan sekolah tidak memerlukan filter tambahan.</p>
            </div>
          </section>
        </aside>
      </section>
    </AppShell>
  )
}
