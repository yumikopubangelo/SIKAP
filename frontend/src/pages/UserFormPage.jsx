import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { roleOptions, userManagementPath } from '../config'
import { AppShell, LoadingSpinner } from '../components/Common'
import { buildInitialUserForm, flattenApiErrors } from '../utils/formatters'

export default function UserFormPage({
  mode,
  authUser,
  api,
  getAuthHeaders,
  onBackToUserManagement,
  onLogout,
}) {
  const navigate = useNavigate()
  const { userId } = useParams()
  const isEdit = mode === 'edit'

  const [form, setForm] = useState(buildInitialUserForm)
  const [studentCandidate, setStudentCandidate] = useState(null)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [pageLoading, setPageLoading] = useState(isEdit)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [rfidLoading, setRfidLoading] = useState(false)
  const [rfidSession, setRfidSession] = useState(null)
  const [revokeCardRequested, setRevokeCardRequested] = useState(false)
  const [linkedStudentLocked, setLinkedStudentLocked] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})

  const currentStudentCard = revokeCardRequested ? '' : studentCandidate?.id_card || ''
  const scannedUid = rfidSession?.first_uid || ''
  const confirmedUid = rfidSession?.confirmed_uid || ''
  const cardOwner = rfidSession?.card_owner || null
  const isCardTransfer =
    Boolean(cardOwner?.id_siswa) &&
    Boolean(studentCandidate?.id_siswa) &&
    cardOwner.id_siswa !== studentCandidate.id_siswa
  const rfidActionDisabled = lookupLoading || submitLoading || rfidLoading

  const stopRfidCapture = async ({ silent = false, clearLocal = true } = {}) => {
    const headers = getAuthHeaders()
    if (!headers) {
      if (!silent) {
        setError('Sesi login tidak ditemukan. Silakan login ulang.')
      }
      if (clearLocal) {
        setRfidSession(null)
      }
      return
    }

    try {
      await api.delete('/users/rfid-capture/session', { headers })
    } catch (requestError) {
      if (!silent) {
        const apiMessage =
          requestError?.response?.data?.message ||
          requestError?.message ||
          'Gagal menutup sesi scan UID RFID.'
        setError(apiMessage)
      }
    } finally {
      if (clearLocal) {
        setRfidSession(null)
      }
    }
  }

  const fetchRfidSession = async ({ silent = false } = {}) => {
    const headers = getAuthHeaders()
    if (!headers) {
      if (!silent) {
        setError('Sesi login tidak ditemukan. Silakan login ulang.')
      }
      return null
    }

    try {
      const { data } = await api.get('/users/rfid-capture/session', { headers })
      if (!data?.success) {
        throw new Error('Respons status scan UID tidak valid.')
      }

      setRfidSession(data.data || null)
      return data.data || null
    } catch (requestError) {
      if (!silent) {
        const apiMessage =
          requestError?.response?.data?.message ||
          requestError?.message ||
          'Gagal memuat status scan UID RFID.'
        setError(apiMessage)
      }
      return null
    }
  }

  const startRfidCapture = async () => {
    if (!studentCandidate?.id_siswa) {
      setFieldErrors((prev) => ({
        ...prev,
        id_card: 'Validasi siswa dulu sebelum memulai scan UID RFID.',
      }))
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setRfidLoading(true)
    setError('')
    setSuccessMessage('')
    setRevokeCardRequested(false)
    setFieldErrors((prev) => ({ ...prev, id_card: '' }))

    try {
      const { data } = await api.post(
        '/users/rfid-capture/session',
        { student_id: studentCandidate.id_siswa },
        { headers },
      )

      if (!data?.success || !data?.data) {
        throw new Error('Respons aktivasi scan UID RFID tidak valid.')
      }

      setRfidSession(data.data)
      setSuccessMessage(data.message || 'Mode scan UID aktif. Tempelkan kartu yang sama dua kali.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal mengaktifkan scan UID RFID.'
      setError(apiMessage)
    } finally {
      setRfidLoading(false)
    }
  }

  const resetRfidCapture = async () => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setRfidLoading(true)
    setError('')
    setSuccessMessage('')

    try {
      const { data } = await api.post('/users/rfid-capture/session/reset', {}, { headers })
      if (!data?.success || !data?.data) {
        throw new Error('Respons reset scan UID RFID tidak valid.')
      }

      setRfidSession(data.data)
      setRevokeCardRequested(false)
      setSuccessMessage(data.message || 'Scan UID direset. Tempelkan kartu lagi dari awal.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal mereset scan UID RFID.'
      setError(apiMessage)
    } finally {
      setRfidLoading(false)
    }
  }

  const handleRevokeCard = async () => {
    setError('')
    setSuccessMessage('')
    setFieldErrors((prev) => ({ ...prev, id_card: '' }))
    await stopRfidCapture({ silent: true })
    setRevokeCardRequested(true)
    setSuccessMessage('UID kartu akan dicabut saat perubahan user disimpan.')
  }

  const handleUndoRevokeCard = () => {
    setRevokeCardRequested(false)
    setFieldErrors((prev) => ({ ...prev, id_card: '' }))
    setSuccessMessage('Mode revoke UID dibatalkan.')
  }

  const fetchUserDetail = async () => {
    if (!isEdit) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      setPageLoading(false)
      return
    }

    setPageLoading(true)
    try {
      const { data } = await api.get(`/users/${userId}`, { headers })

      if (!data?.success || !data?.data) {
        throw new Error('Respons detail user tidak valid.')
      }

      const user = data.data
      setForm({
        username: user.username || '',
        full_name: user.full_name || '',
        email: user.email || '',
        no_telp: user.no_telp || '',
        role: user.role || 'guru_piket',
        password: '',
        confirmPassword: '',
        nisn: user.student?.nisn || '',
      })
      setStudentCandidate(user.student || null)
      setLinkedStudentLocked(Boolean(user.student))
      setRfidSession(null)
      setRevokeCardRequested(false)
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat detail user.'

      setError(apiMessage)
    } finally {
      setPageLoading(false)
    }
  }

  useEffect(() => {
    void fetchUserDetail()
  }, [isEdit, userId])

  useEffect(() => {
    if (!rfidSession?.session_id) {
      return undefined
    }

    const timer = window.setInterval(() => {
      void fetchRfidSession({ silent: true })
    }, 1500)

    return () => window.clearInterval(timer)
  }, [rfidSession?.session_id])

  useEffect(() => {
    return () => {
      if (rfidSession?.session_id) {
        void stopRfidCapture({ silent: true, clearLocal: false })
      }
    }
  }, [rfidSession?.session_id])

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    const nextValue = name === 'nisn' ? value.replace(/\D/g, '').slice(0, 10) : value

    if (name === 'nisn' && form.nisn !== nextValue) {
      if (rfidSession?.session_id) {
        void stopRfidCapture({ silent: true })
      }
      setStudentCandidate(linkedStudentLocked ? studentCandidate : null)
      setRevokeCardRequested(false)
    }

    if (name === 'role' && value !== 'siswa' && !linkedStudentLocked) {
      if (rfidSession?.session_id) {
        void stopRfidCapture({ silent: true })
      }
      setStudentCandidate(null)
      setRevokeCardRequested(false)
      setForm((prev) => ({
        ...prev,
        [name]: value,
        nisn: '',
      }))
      setFieldErrors((prev) => ({ ...prev, [name]: '', nisn: '', id_card: '' }))
      return
    }

    setFieldErrors((prev) => ({ ...prev, [name]: '' }))
    setForm((prev) => ({ ...prev, [name]: nextValue }))
  }

  const handleLookupStudent = async (explicitNisn) => {
    const nisn = (explicitNisn ?? form.nisn).trim()

    if (!/^\d{10}$/.test(nisn)) {
      setFieldErrors((prev) => ({
        ...prev,
        nisn: 'Masukkan NISN 10 digit untuk akun siswa.',
      }))
      return null
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return null
    }

    setLookupLoading(true)
    setError('')
    setSuccessMessage('')
    setFieldErrors((prev) => ({ ...prev, nisn: '' }))

    try {
      const { data } = await api.get('/auth/student-candidates', {
        headers,
        params: { nisn },
      })

      const student = data?.data?.student
      if (!data?.success || !student) {
        throw new Error('Respons validasi siswa tidak valid.')
      }

      setStudentCandidate(student)
      setRfidSession(null)
      setRevokeCardRequested(false)
      setSuccessMessage(
        `NISN valid. Akun akan terhubung ke ${student.nama}${student.kelas ? ` dari ${student.kelas}` : ''}.`,
      )
      return student
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memvalidasi NISN siswa.'

      setStudentCandidate(null)
      setError(apiMessage)
      return null
    } finally {
      setLookupLoading(false)
    }
  }

  const validateUserForm = (currentForm) => {
    const nextErrors = {}

    if (!currentForm.username.trim()) {
      nextErrors.username = 'Username wajib diisi.'
    }

    if (!currentForm.full_name.trim()) {
      nextErrors.full_name = 'Nama lengkap wajib diisi.'
    }

    if (!currentForm.role) {
      nextErrors.role = 'Role wajib dipilih.'
    }

    if (!isEdit && !currentForm.password) {
      nextErrors.password = 'Password wajib diisi.'
    }

    if (currentForm.password && currentForm.password.length < 8) {
      nextErrors.password = 'Password minimal 8 karakter.'
    }

    if (
      (!isEdit || currentForm.password || currentForm.confirmPassword) &&
      currentForm.password !== currentForm.confirmPassword
    ) {
      nextErrors.confirmPassword = 'Konfirmasi password tidak sama.'
    }

    if (currentForm.role === 'siswa' && !linkedStudentLocked && !/^\d{10}$/.test(currentForm.nisn)) {
      nextErrors.nisn = 'NISN 10 digit wajib diisi untuk akun siswa.'
    }

    if (currentForm.role === 'siswa' && !isEdit && !currentStudentCard && !confirmedUid) {
      nextErrors.id_card = 'Scan UID kartu RFID dua kali sebelum membuat akun siswa.'
    }

    if (currentForm.role === 'siswa' && scannedUid && !confirmedUid) {
      nextErrors.id_card = 'Tap kartu yang sama sekali lagi untuk mengonfirmasi UID.'
    }

    if (!isEdit && revokeCardRequested) {
      nextErrors.id_card = 'Revoke UID hanya tersedia saat edit akun siswa.'
    }

    return nextErrors
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    const localErrors = validateUserForm(form)
    if (Object.keys(localErrors).length) {
      setFieldErrors(localErrors)
      return
    }

    let candidate = studentCandidate
    if (form.role === 'siswa' && !linkedStudentLocked) {
      if (!candidate || candidate.nisn !== form.nisn) {
        candidate = await handleLookupStudent(form.nisn)
        if (!candidate) {
          return
        }
      }
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSubmitLoading(true)
    try {
      const payload = {
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        email: form.email.trim() || '',
        no_telp: form.no_telp.trim() || '',
        role: form.role,
      }

      if (form.password) {
        payload.password = form.password
      }

      if (!isEdit && !form.password) {
        payload.password = ''
      }

      if (form.role === 'siswa' && !linkedStudentLocked) {
        payload.nisn = candidate?.nisn || form.nisn.trim()
      }

      if (form.role === 'siswa') {
        if (revokeCardRequested && isEdit) {
          payload.id_card = ''
        } else if (confirmedUid) {
          payload.id_card = confirmedUid
        }
      }

      const request = isEdit
        ? api.put(`/users/${userId}`, payload, { headers })
        : api.post('/users', payload, { headers })

      const { data } = await request
      if (!data?.success) {
        throw new Error('Respons penyimpanan user tidak valid.')
      }

      await stopRfidCapture({ silent: true })

      navigate(userManagementPath, {
        replace: true,
        state: {
          userManagementMessage:
            data.message || (isEdit ? 'User berhasil diupdate.' : 'User berhasil dibuat.'),
        },
      })
    } catch (requestError) {
      const apiErrors = requestError?.response?.data?.errors || {}
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menyimpan data user.'

      setFieldErrors((prev) => ({
        ...prev,
        username: apiErrors?.username || prev.username || '',
        full_name: apiErrors?.full_name || '',
        email: apiErrors?.email || '',
        no_telp: apiErrors?.no_telp || '',
        role: apiErrors?.role || '',
        password: apiErrors?.password || '',
        nisn: apiErrors?.nisn || apiErrors?.student_lookup || '',
        id_card: apiErrors?.id_card || '',
      }))
      setError([apiMessage, flattenApiErrors(apiErrors)].filter(Boolean).join(' '))
    } finally {
      setSubmitLoading(false)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Kelola Akun"
      title={isEdit ? 'Ubah Akun' : 'Tambah Akun'}
      subtitle="Lengkapi data akun dan sambungkan ke data siswa bila diperlukan."
      actions={
        <>
          <button type="button" className="ghost-button" onClick={onBackToUserManagement}>
            Daftar Akun
          </button>
          <button type="button" onClick={onLogout}>
            Keluar
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      {pageLoading ? (
        <section className="dashboard-panel">
          <LoadingSpinner label="Memuat detail user..." />
        </section>
      ) : (
        <section className="manual-grid">
          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>{isEdit ? 'Form Edit User' : 'Form Tambah User'}</h2>
                <p className="api-note">
                  Data ini akan dipakai untuk login dan pengelolaan role di dalam sistem.
                </p>
              </div>
            </div>

            <form className="manual-form" onSubmit={handleSubmit}>
              <div className="manual-form-grid">
                <div className="manual-field">
                  <label htmlFor="user_username">Username</label>
                  <input
                    id="user_username"
                    name="username"
                    type="text"
                    value={form.username}
                    onChange={handleFieldChange}
                    placeholder="contoh: ahmad.fadil"
                  />
                  {fieldErrors.username ? <p className="field-error">{fieldErrors.username}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_full_name">Nama Lengkap</label>
                  <input
                    id="user_full_name"
                    name="full_name"
                    type="text"
                    value={form.full_name}
                    onChange={handleFieldChange}
                    placeholder="Nama lengkap pengguna"
                  />
                  {fieldErrors.full_name ? <p className="field-error">{fieldErrors.full_name}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_email">Email</label>
                  <input
                    id="user_email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleFieldChange}
                    placeholder="contoh: user@sikap.local"
                  />
                  {fieldErrors.email ? <p className="field-error">{fieldErrors.email}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_no_telp">No. Telepon</label>
                  <input
                    id="user_no_telp"
                    name="no_telp"
                    type="text"
                    value={form.no_telp}
                    onChange={handleFieldChange}
                    placeholder="08xxxxxxxxxx"
                  />
                  {fieldErrors.no_telp ? <p className="field-error">{fieldErrors.no_telp}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_role">Role</label>
                  <select
                    id="user_role"
                    name="role"
                    value={form.role}
                    onChange={handleFieldChange}
                    disabled={linkedStudentLocked}
                  >
                    {roleOptions.map((role) => (
                      <option key={role.value} value={role.value}>
                        {role.label}
                      </option>
                    ))}
                  </select>
                  {linkedStudentLocked ? (
                    <p className="helper-text">
                      Role dikunci karena akun ini sudah terhubung ke data siswa.
                    </p>
                  ) : null}
                  {fieldErrors.role ? <p className="field-error">{fieldErrors.role}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_password">{isEdit ? 'Password Baru' : 'Password'}</label>
                  <input
                    id="user_password"
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleFieldChange}
                    placeholder={isEdit ? 'Kosongkan jika tidak diubah' : 'Minimal 8 karakter'}
                  />
                  {fieldErrors.password ? <p className="field-error">{fieldErrors.password}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_confirm_password">Konfirmasi Password</label>
                  <input
                    id="user_confirm_password"
                    name="confirmPassword"
                    type="password"
                    value={form.confirmPassword}
                    onChange={handleFieldChange}
                    placeholder="Ulangi password"
                  />
                  {fieldErrors.confirmPassword ? (
                    <p className="field-error">{fieldErrors.confirmPassword}</p>
                  ) : null}
                </div>

                {form.role === 'siswa' ? (
                  <div className="manual-field manual-field-full">
                    <label htmlFor="user_nisn">NISN Siswa</label>
                    <div className="lookup-row">
                      <input
                        id="user_nisn"
                        name="nisn"
                        type="text"
                        inputMode="numeric"
                        value={form.nisn}
                        onChange={handleFieldChange}
                        placeholder="Masukkan 10 digit NISN"
                        maxLength={10}
                        disabled={linkedStudentLocked}
                      />
                      {!linkedStudentLocked ? (
                        <button
                          type="button"
                          className="ghost-button lookup-button"
                          onClick={() => void handleLookupStudent()}
                          disabled={lookupLoading || submitLoading}
                        >
                          {lookupLoading ? 'Memvalidasi...' : 'Validasi NISN'}
                        </button>
                      ) : null}
                    </div>
                    {fieldErrors.nisn ? <p className="field-error">{fieldErrors.nisn}</p> : null}
                  </div>
                ) : null}

                {form.role === 'siswa' ? (
                  <div className="manual-field manual-field-full">
                    <label>Konfirmasi UID Card RFID</label>
                    <div className="rfid-card-panel">
                      <div className="student-preview-head">
                        <div>
                          <p className="helper-text">
                            Tempelkan kartu yang sama dua kali pada RFID reader. Tap pertama mengisi UID,
                            tap kedua yang sama menjadi konfirmasi sebelum akun siswa bisa disimpan.
                          </p>
                        </div>
                        <div className="chip-group">
                          <span className="status-chip info">
                            {rfidSession?.status === 'confirmed'
                              ? 'UID Terverifikasi'
                              : rfidSession?.status === 'waiting_second_tap'
                                ? 'Menunggu Tap Kedua'
                                : revokeCardRequested
                                  ? 'UID Akan Dicabut'
                                  : 'Belum Scan'}
                          </span>
                        </div>
                      </div>

                      <div className="rfid-actions">
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => void startRfidCapture()}
                          disabled={!studentCandidate || rfidActionDisabled}
                        >
                          {rfidLoading
                            ? 'Menyiapkan...'
                            : rfidSession?.session_id
                              ? 'Mulai Ulang Scan UID'
                              : 'Mulai Scan UID'}
                        </button>
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => void resetRfidCapture()}
                          disabled={!rfidSession?.session_id || rfidActionDisabled}
                        >
                          Reset Scan
                        </button>
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => void stopRfidCapture()}
                          disabled={!rfidSession?.session_id || rfidActionDisabled}
                        >
                          Tutup Scan
                        </button>
                        {isEdit && linkedStudentLocked && currentStudentCard && !revokeCardRequested ? (
                          <button
                            type="button"
                            className="ghost-button danger-button"
                            onClick={() => void handleRevokeCard()}
                            disabled={rfidActionDisabled}
                          >
                            Revoke UID
                          </button>
                        ) : null}
                        {revokeCardRequested ? (
                          <button
                            type="button"
                            className="ghost-button"
                            onClick={handleUndoRevokeCard}
                            disabled={rfidActionDisabled}
                          >
                            Batal Revoke
                          </button>
                        ) : null}
                      </div>

                      <div className="manual-form-grid">
                        <div className="manual-field">
                          <label htmlFor="user_uid_tap_1">UID Tap Pertama</label>
                          <input
                            id="user_uid_tap_1"
                            type="text"
                            value={scannedUid}
                            readOnly
                            placeholder="Menunggu tap pertama"
                          />
                        </div>
                        <div className="manual-field">
                          <label htmlFor="user_uid_tap_2">Konfirmasi UID</label>
                          <input
                            id="user_uid_tap_2"
                            type="text"
                            value={confirmedUid}
                            readOnly
                            placeholder="Menunggu tap kedua yang sama"
                          />
                        </div>
                      </div>

                      {studentCandidate ? (
                        <p className="helper-text">
                          {currentStudentCard
                            ? `UID aktif siswa saat ini: ${currentStudentCard}`
                            : 'Siswa ini belum memiliki UID card.'}
                        </p>
                      ) : (
                        <p className="helper-text">
                          Validasi NISN siswa dulu agar mode scan UID bisa diaktifkan.
                        </p>
                      )}

                      {rfidSession?.message ? <p className="field-success">{rfidSession.message}</p> : null}
                      {revokeCardRequested ? (
                        <p className="field-error">UID kartu akan dihapus dari siswa ini saat perubahan disimpan.</p>
                      ) : null}
                      {isCardTransfer ? (
                        <p className="field-error">
                          UID ini saat ini dipakai oleh {cardOwner.nama} ({cardOwner.nisn}) dan akan dipindahkan
                          saat data disimpan.
                        </p>
                      ) : null}
                      {fieldErrors.id_card ? <p className="field-error">{fieldErrors.id_card}</p> : null}
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="manual-actions">
                <button type="submit" disabled={submitLoading || lookupLoading || rfidLoading}>
                  {submitLoading ? 'Menyimpan...' : isEdit ? 'Simpan Perubahan' : 'Buat User'}
                </button>
                <button
                  type="button"
                  className="ghost-button"
                  onClick={onBackToUserManagement}
                  disabled={submitLoading || lookupLoading || rfidLoading}
                >
                  Batal
                </button>
              </div>
            </form>
          </section>

          <aside className="manual-side-panel">
            <section className="dashboard-panel manual-panel highlighted-panel">
              <div className="panel-header">
                <div>
                  <h2>Preview Relasi Siswa</h2>
                  <p className="api-note">
                    Panel ini membantu memastikan akun siswa tersambung ke entitas siswa yang benar.
                  </p>
                </div>
              </div>

              {studentCandidate ? (
                <dl className="detail-list">
                  <div><dt>Nama</dt><dd>{studentCandidate.nama || '-'}</dd></div>
                  <div><dt>NISN</dt><dd>{studentCandidate.nisn || '-'}</dd></div>
                  <div><dt>Kelas</dt><dd>{studentCandidate.kelas || '-'}</dd></div>
                  <div><dt>ID Card Aktif</dt><dd>{currentStudentCard || confirmedUid || '-'}</dd></div>
                </dl>
              ) : (
                <div className="empty-state compact">
                  <p>
                    {form.role === 'siswa'
                      ? 'Belum ada siswa tervalidasi. Isi NISN lalu lakukan validasi.'
                      : 'Preview siswa hanya muncul bila role akun diatur sebagai siswa.'}
                  </p>
                </div>
              )}
            </section>
          </aside>
        </section>
      )}
    </AppShell>
  )
}
