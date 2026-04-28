import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { roleOptions, userManagementPath } from '../config'
import { AppShell, LoadingSpinner } from '../components/Common'
import { buildInitialUserForm, flattenApiErrors } from '../utils/formatters'

const RFID_POLL_MS = 2000

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
  const [linkedStudentLocked, setLinkedStudentLocked] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})

  // RFID capture state
  // pendingIdCard: undefined = no change | null = revoke | string = new uid
  const [pendingIdCard, setPendingIdCard] = useState(undefined)
  const [rfidPhase, setRfidPhase] = useState('idle') // idle | scanning | confirmed | error
  const [rfidSession, setRfidSession] = useState(null)
  const [rfidError, setRfidError] = useState('')
  const rfidPollRef = useRef(null)

  const stopRfidPoll = () => {
    if (rfidPollRef.current) {
      clearInterval(rfidPollRef.current)
      rfidPollRef.current = null
    }
  }

  useEffect(() => () => stopRfidPoll(), [])

  const fetchUserDetail = async () => {
    if (!isEdit) return
    const headers = getAuthHeaders()
    if (!headers) { setError('Sesi login tidak ditemukan.'); setPageLoading(false); return }

    setPageLoading(true)
    try {
      const { data } = await api.get(`/users/${userId}`, { headers })
      if (!data?.success || !data?.data) throw new Error('Respons tidak valid.')
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
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Gagal memuat detail user.')
    } finally {
      setPageLoading(false)
    }
  }

  useEffect(() => { void fetchUserDetail() }, [isEdit, userId])

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    const nextValue = name === 'nisn' ? value.replace(/\D/g, '').slice(0, 10) : value

    if (name === 'nisn' && form.nisn !== nextValue) {
      setStudentCandidate(linkedStudentLocked ? studentCandidate : null)
    }

    if (name === 'role' && value !== 'siswa' && !linkedStudentLocked) {
      setStudentCandidate(null)
      stopRfidPoll()
      setRfidPhase('idle')
      setRfidSession(null)
      setPendingIdCard(undefined)
      setForm((prev) => ({ ...prev, [name]: value, nisn: '' }))
      setFieldErrors((prev) => ({ ...prev, [name]: '', nisn: '' }))
      return
    }

    setFieldErrors((prev) => ({ ...prev, [name]: '' }))
    setForm((prev) => ({ ...prev, [name]: nextValue }))
  }

  const handleLookupStudent = async (explicitNisn) => {
    const nisn = (explicitNisn ?? form.nisn).trim()
    if (!/^\d{10}$/.test(nisn)) {
      setFieldErrors((prev) => ({ ...prev, nisn: 'Masukkan NISN 10 digit.' }))
      return null
    }
    const headers = getAuthHeaders()
    if (!headers) { setError('Sesi login tidak ditemukan.'); return null }

    setLookupLoading(true)
    setError('')
    setSuccessMessage('')
    setFieldErrors((prev) => ({ ...prev, nisn: '' }))

    try {
      const { data } = await api.get('/auth/student-candidates', { headers, params: { nisn } })
      const student = data?.data?.student
      if (!data?.success || !student) throw new Error('Respons validasi tidak valid.')
      setStudentCandidate(student)
      setSuccessMessage(`NISN valid. Akun akan terhubung ke ${student.nama}${student.kelas ? ` dari ${student.kelas}` : ''}.`)
      return student
    } catch (err) {
      setStudentCandidate(null)
      setError(err?.response?.data?.message || err?.message || 'Gagal memvalidasi NISN.')
      return null
    } finally {
      setLookupLoading(false)
    }
  }

  // ── RFID capture helpers ──────────────────────────────────────────────────

  const pollRfidSession = async () => {
    const headers = getAuthHeaders()
    if (!headers) return
    try {
      const { data } = await api.get('/users/rfid-capture/session', { headers })
      if (!data?.success || !data?.data) return
      const session = data.data
      setRfidSession(session)

      if (session.status === 'confirmed') {
        stopRfidPoll()
        setRfidPhase('confirmed')
        setPendingIdCard(session.confirmed_uid)
      } else if (session.status === 'waiting_second_tap') {
        setRfidPhase('scanning') // keep scanning phase, message comes from session
      }
    } catch {
      // silent — poll will retry
    }
  }

  const handleStartRfidScan = async () => {
    const headers = getAuthHeaders()
    if (!headers) { setRfidError('Sesi login tidak ditemukan.'); return }

    setRfidError('')
    setRfidSession(null)
    setPendingIdCard(undefined)

    const candidate = studentCandidate
    const payload = candidate?.id_siswa ? { student_id: candidate.id_siswa } : {}

    try {
      const { data } = await api.post('/users/rfid-capture/session', payload, { headers })
      if (!data?.success) throw new Error('Gagal memulai sesi scan.')
      setRfidSession(data.data)
      setRfidPhase('scanning')
      stopRfidPoll()
      rfidPollRef.current = setInterval(pollRfidSession, RFID_POLL_MS)
    } catch (err) {
      setRfidError(err?.response?.data?.message || err?.message || 'Gagal memulai scan RFID.')
      setRfidPhase('idle')
    }
  }

  const handleResetRfidScan = async () => {
    const headers = getAuthHeaders()
    if (!headers) return
    try {
      const { data } = await api.post('/users/rfid-capture/session/reset', {}, { headers })
      if (data?.success) {
        setRfidSession(data.data)
        setRfidPhase('scanning')
        setPendingIdCard(undefined)
        stopRfidPoll()
        rfidPollRef.current = setInterval(pollRfidSession, RFID_POLL_MS)
      }
    } catch (err) {
      setRfidError(err?.response?.data?.message || err?.message || 'Gagal mereset sesi scan.')
    }
  }

  const handleCancelRfidScan = async () => {
    stopRfidPoll()
    setRfidPhase('idle')
    setRfidSession(null)
    setPendingIdCard(undefined)
    const headers = getAuthHeaders()
    if (!headers) return
    try { await api.delete('/users/rfid-capture/session', { headers }) } catch { /* silent */ }
  }

  const handleRevokeRfid = () => {
    setPendingIdCard(null)
    stopRfidPoll()
    setRfidPhase('idle')
    setRfidSession(null)
  }

  // ── Validation & submit ───────────────────────────────────────────────────

  const validateUserForm = (currentForm) => {
    const nextErrors = {}
    if (!currentForm.username.trim()) nextErrors.username = 'Username wajib diisi.'
    if (!currentForm.full_name.trim()) nextErrors.full_name = 'Nama lengkap wajib diisi.'
    if (!currentForm.role) nextErrors.role = 'Role wajib dipilih.'
    if (!isEdit && !currentForm.password) nextErrors.password = 'Password wajib diisi.'
    if (currentForm.password && currentForm.password.length < 8) nextErrors.password = 'Password minimal 8 karakter.'
    if (
      (!isEdit || currentForm.password || currentForm.confirmPassword) &&
      currentForm.password !== currentForm.confirmPassword
    ) nextErrors.confirmPassword = 'Konfirmasi password tidak sama.'
    if (currentForm.role === 'siswa' && !linkedStudentLocked && !/^\d{10}$/.test(currentForm.nisn)) {
      nextErrors.nisn = 'NISN 10 digit wajib diisi.'
    }
    if (currentForm.role === 'siswa' && !isEdit && rfidPhase !== 'confirmed' && pendingIdCard === undefined) {
      nextErrors.rfid = 'Kartu RFID wajib discan dua kali sebelum akun baru dibuat.'
    }
    return nextErrors
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    const localErrors = validateUserForm(form)
    if (Object.keys(localErrors).length) { setFieldErrors(localErrors); return }

    let candidate = studentCandidate
    if (form.role === 'siswa' && !linkedStudentLocked) {
      if (!candidate || candidate.nisn !== form.nisn) {
        candidate = await handleLookupStudent(form.nisn)
        if (!candidate) return
      }
    }

    const headers = getAuthHeaders()
    if (!headers) { setError('Sesi login tidak ditemukan.'); return }

    setSubmitLoading(true)
    try {
      const payload = {
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        email: form.email.trim() || '',
        no_telp: form.no_telp.trim() || '',
        role: form.role,
      }
      if (form.password) payload.password = form.password
      if (!isEdit && !form.password) payload.password = ''
      if (form.role === 'siswa' && !linkedStudentLocked) {
        payload.nisn = candidate?.nisn || form.nisn.trim()
      }
      if (form.role === 'siswa' && pendingIdCard !== undefined) {
        payload.id_card = pendingIdCard
      }

      const request = isEdit
        ? api.put(`/users/${userId}`, payload, { headers })
        : api.post('/users', payload, { headers })

      const { data } = await request
      if (!data?.success) throw new Error('Respons penyimpanan tidak valid.')

      stopRfidPoll()
      navigate(userManagementPath, {
        replace: true,
        state: { userManagementMessage: data.message || (isEdit ? 'User berhasil diupdate.' : 'User berhasil dibuat.') },
      })
    } catch (err) {
      const apiErrors = err?.response?.data?.errors || {}
      const apiMessage = err?.response?.data?.message || err?.message || 'Gagal menyimpan data user.'
      setFieldErrors((prev) => ({
        ...prev,
        username: apiErrors?.username || prev.username || '',
        full_name: apiErrors?.full_name || '',
        email: apiErrors?.email || '',
        no_telp: apiErrors?.no_telp || '',
        role: apiErrors?.role || '',
        password: apiErrors?.password || '',
        nisn: apiErrors?.nisn || apiErrors?.student_lookup || '',
      }))
      setError([apiMessage, flattenApiErrors(apiErrors)].filter(Boolean).join(' '))
    } finally {
      setSubmitLoading(false)
    }
  }

  // ── RFID widget render helper ─────────────────────────────────────────────

  const currentCard = studentCandidate?.id_card || null
  const showRfidWidget = form.role === 'siswa'

  const rfidStatusText = () => {
    if (rfidPhase === 'confirmed') return `Kartu terkonfirmasi: ${pendingIdCard}`
    if (!rfidSession) return 'Tekan tombol untuk mulai scan.'
    if (rfidSession.status === 'waiting_first_tap') return 'Tempelkan kartu RFID ke perangkat...'
    if (rfidSession.status === 'waiting_second_tap') return 'Tap pertama diterima. Tempelkan kartu yang sama sekali lagi.'
    return rfidSession.message || ''
  }

  const rfidTapCount = rfidSession?.tap_count || 0

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Kelola Akun"
      title={isEdit ? 'Ubah Akun' : 'Tambah Akun'}
      subtitle="Lengkapi data akun dan sambungkan ke data siswa bila diperlukan."
      actions={
        <>
          <button type="button" className="ghost-button" onClick={onBackToUserManagement}>Daftar Akun</button>
          <button type="button" onClick={onLogout}>Keluar</button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      {pageLoading ? (
        <section className="dashboard-panel"><LoadingSpinner label="Memuat detail user..." /></section>
      ) : (
        <section className="manual-grid">
          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>{isEdit ? 'Form Edit User' : 'Form Tambah User'}</h2>
                <p className="api-note">Data ini akan dipakai untuk login dan pengelolaan role.</p>
              </div>
            </div>

            <form className="manual-form" onSubmit={handleSubmit}>
              <div className="manual-form-grid">
                <div className="manual-field">
                  <label htmlFor="user_username">Username</label>
                  <input id="user_username" name="username" type="text" value={form.username} onChange={handleFieldChange} placeholder="contoh: ahmad.fadil" />
                  {fieldErrors.username ? <p className="field-error">{fieldErrors.username}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_full_name">Nama Lengkap</label>
                  <input id="user_full_name" name="full_name" type="text" value={form.full_name} onChange={handleFieldChange} placeholder="Nama lengkap pengguna" />
                  {fieldErrors.full_name ? <p className="field-error">{fieldErrors.full_name}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_email">Email</label>
                  <input id="user_email" name="email" type="email" value={form.email} onChange={handleFieldChange} placeholder="contoh: user@sikap.local" />
                  {fieldErrors.email ? <p className="field-error">{fieldErrors.email}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_no_telp">No. Telepon</label>
                  <input id="user_no_telp" name="no_telp" type="text" value={form.no_telp} onChange={handleFieldChange} placeholder="08xxxxxxxxxx" />
                  {fieldErrors.no_telp ? <p className="field-error">{fieldErrors.no_telp}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_role">Role</label>
                  <select id="user_role" name="role" value={form.role} onChange={handleFieldChange} disabled={linkedStudentLocked}>
                    {roleOptions.map((role) => (
                      <option key={role.value} value={role.value}>{role.label}</option>
                    ))}
                  </select>
                  {linkedStudentLocked ? <p className="helper-text">Role dikunci karena akun ini sudah terhubung ke data siswa.</p> : null}
                  {fieldErrors.role ? <p className="field-error">{fieldErrors.role}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_password">{isEdit ? 'Password Baru' : 'Password'}</label>
                  <input id="user_password" name="password" type="password" value={form.password} onChange={handleFieldChange} placeholder={isEdit ? 'Kosongkan jika tidak diubah' : 'Minimal 8 karakter'} />
                  {fieldErrors.password ? <p className="field-error">{fieldErrors.password}</p> : null}
                </div>

                <div className="manual-field">
                  <label htmlFor="user_confirm_password">Konfirmasi Password</label>
                  <input id="user_confirm_password" name="confirmPassword" type="password" value={form.confirmPassword} onChange={handleFieldChange} placeholder="Ulangi password" />
                  {fieldErrors.confirmPassword ? <p className="field-error">{fieldErrors.confirmPassword}</p> : null}
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
                        <button type="button" className="ghost-button lookup-button" onClick={() => handleLookupStudent()} disabled={lookupLoading || submitLoading}>
                          {lookupLoading ? 'Memvalidasi...' : 'Validasi NISN'}
                        </button>
                      ) : null}
                    </div>
                    {fieldErrors.nisn ? <p className="field-error">{fieldErrors.nisn}</p> : null}
                  </div>
                ) : null}
              </div>

              {/* RFID capture widget */}
              {showRfidWidget ? (
                <div className="rfid-widget">
                  <div className="rfid-widget-header">
                    <h3>Kartu RFID</h3>
                    {pendingIdCard === null ? (
                      <span className="rfid-revoke-badge">Kartu akan dicabut saat disimpan</span>
                    ) : pendingIdCard ? (
                      <span className="rfid-confirmed-badge">Kartu baru siap disimpan</span>
                    ) : currentCard ? (
                      <span className="rfid-current-badge">Kartu terdaftar: {currentCard}</span>
                    ) : (
                      <span className="rfid-empty-badge">Belum ada kartu</span>
                    )}
                  </div>

                  {rfidError ? <p className="field-error">{rfidError}</p> : null}
                  {fieldErrors.rfid ? <p className="field-error">{fieldErrors.rfid}</p> : null}

                  {rfidPhase === 'idle' ? (
                    <div className="rfid-widget-actions">
                      <button type="button" className="ghost-button" onClick={handleStartRfidScan} disabled={submitLoading}>
                        {currentCard || pendingIdCard ? 'Ganti Kartu RFID' : 'Mulai Scan Kartu RFID'}
                      </button>
                      {(currentCard && pendingIdCard === undefined) ? (
                        <button type="button" className="ghost-button danger-ghost" onClick={handleRevokeRfid} disabled={submitLoading}>
                          Cabut Kartu RFID
                        </button>
                      ) : null}
                      {pendingIdCard === null ? (
                        <button type="button" className="ghost-button" onClick={() => setPendingIdCard(undefined)} disabled={submitLoading}>
                          Batalkan Pencabutan
                        </button>
                      ) : null}
                    </div>
                  ) : rfidPhase === 'confirmed' ? (
                    <div className="rfid-scan-status rfid-scan-status--confirmed">
                      <span className="rfid-tap-dots">
                        <span className="rfid-tap-dot rfid-tap-dot--filled" />
                        <span className="rfid-tap-dot rfid-tap-dot--filled" />
                      </span>
                      <p>{rfidStatusText()}</p>
                      {rfidSession?.card_owner ? (
                        <p className="rfid-warn">
                          Kartu ini sebelumnya terdaftar atas nama <strong>{rfidSession.card_owner.nama}</strong>. Menyimpan akan memindahkan kartu ke akun ini.
                        </p>
                      ) : null}
                      <button type="button" className="ghost-button" onClick={handleResetRfidScan}>Ulangi Scan</button>
                    </div>
                  ) : (
                    <div className="rfid-scan-status rfid-scan-status--scanning">
                      <span className="rfid-tap-dots">
                        <span className={`rfid-tap-dot${rfidTapCount >= 1 ? ' rfid-tap-dot--filled' : ''}`} />
                        <span className={`rfid-tap-dot${rfidTapCount >= 2 ? ' rfid-tap-dot--filled' : ''}`} />
                      </span>
                      <p>{rfidStatusText()}</p>
                      <div className="rfid-widget-actions">
                        <button type="button" className="ghost-button" onClick={handleResetRfidScan}>Ulangi</button>
                        <button type="button" className="ghost-button danger-ghost" onClick={handleCancelRfidScan}>Batalkan</button>
                      </div>
                    </div>
                  )}
                </div>
              ) : null}

              <div className="manual-actions">
                <button type="submit" disabled={submitLoading || lookupLoading}>
                  {submitLoading ? 'Menyimpan...' : isEdit ? 'Simpan Perubahan' : 'Buat User'}
                </button>
                <button type="button" className="ghost-button" onClick={onBackToUserManagement} disabled={submitLoading || lookupLoading}>
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
                  <p className="api-note">Pastikan akun tersambung ke entitas siswa yang benar.</p>
                </div>
              </div>

              {studentCandidate ? (
                <dl className="detail-list">
                  <div><dt>Nama</dt><dd>{studentCandidate.nama || '-'}</dd></div>
                  <div><dt>NISN</dt><dd>{studentCandidate.nisn || '-'}</dd></div>
                  <div><dt>Kelas</dt><dd>{studentCandidate.kelas || '-'}</dd></div>
                  <div><dt>ID Card</dt>
                    <dd>
                      {pendingIdCard === null
                        ? <span style={{ color: '#c0392b' }}>Akan dicabut</span>
                        : pendingIdCard
                          ? <span style={{ color: '#0f8f9f' }}>{pendingIdCard} (baru)</span>
                          : (studentCandidate.id_card || '-')}
                    </dd>
                  </div>
                </dl>
              ) : (
                <div className="empty-state compact">
                  <p>
                    {form.role === 'siswa'
                      ? 'Belum ada siswa tervalidasi. Isi NISN lalu validasi.'
                      : 'Preview siswa hanya muncul bila role diatur sebagai siswa.'}
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
