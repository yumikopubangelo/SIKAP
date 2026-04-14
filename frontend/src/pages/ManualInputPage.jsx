import { useState } from 'react'

import {
  statusAbsensiLabels,
  statusAbsensiOptions,
  waktuSholatLabels,
  waktuSholatOptions,
} from '../config'
import { AppShell } from '../components/Common'
import {
  buildInitialManualForm,
  flattenApiErrors,
  formatCellValue,
  formatOptionLabel,
} from '../utils/formatters'

export default function ManualInputPage({
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
      eyebrow="Input Absensi"
      title="Input Absensi Manual"
      subtitle="Catat absensi jika kartu tidak bisa dipakai."
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
