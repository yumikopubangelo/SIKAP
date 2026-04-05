import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import './App.css'

const apiBaseUrl =
  (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'kepsek', label: 'Kepala Sekolah' },
  { value: 'wali_kelas', label: 'Wali Kelas' },
  { value: 'guru_piket', label: 'Guru Piket' },
  { value: 'siswa', label: 'Siswa' },
  { value: 'orangtua', label: 'Orang Tua' },
]

const roleLabels = Object.fromEntries(
  roleOptions.map((role) => [role.value, role.label]),
)

const dashboardTitles = {
  admin: 'Dashboard Admin',
  kepsek: 'Dashboard Kepala Sekolah',
  wali_kelas: 'Dashboard Wali Kelas',
  guru_piket: 'Dashboard Guru Piket',
  siswa: 'Dashboard Siswa',
  orangtua: 'Dashboard Orang Tua',
}

function formatColumnLabel(column) {
  return column
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function formatCellValue(value) {
  if (value === null || value === undefined || value === '') {
    return '-'
  }

  if (typeof value === 'number') {
    return value.toLocaleString('id-ID')
  }

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(value)) {
    const parsed = new Date(value)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleString('id-ID')
    }
  }

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const parsed = new Date(`${value}T00:00:00`)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleDateString('id-ID')
    }
  }

  return String(value)
}

function AuthPage({
  mode,
  loading,
  checkingSession,
  loginForm,
  registerForm,
  error,
  successMessage,
  onLoginChange,
  onRegisterChange,
  onLogin,
  onRegister,
  onSwitchMode,
  apiBaseUrlValue,
}) {
  return (
    <main className="login-page">
      <section className="login-card">
        <h1>SIKAP Auth</h1>
        <p className="subtitle">
          Sistem Informasi Kepatuhan Ibadah Peserta Didik
        </p>

        {checkingSession ? <p className="api-note">Memeriksa sesi login...</p> : null}

        <div className="mode-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'tab active' : 'tab'}
            onClick={() => onSwitchMode('login')}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'tab active' : 'tab'}
            onClick={() => onSwitchMode('register')}
          >
            Registrasi
          </button>
        </div>

        {mode === 'login' ? (
          <form onSubmit={onLogin} className="login-form">
            <label htmlFor="username">Username / Email</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={loginForm.username}
              onChange={onLoginChange}
              placeholder="contoh: admin atau admin@sikap.local"
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={loginForm.password}
              onChange={onLoginChange}
              placeholder="Masukkan password"
            />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? 'Memproses...' : 'Masuk'}
            </button>
          </form>
        ) : (
          <form onSubmit={onRegister} className="login-form">
            <label htmlFor="register_username">Username</label>
            <input
              id="register_username"
              name="username"
              type="text"
              value={registerForm.username}
              onChange={onRegisterChange}
              placeholder="contoh: ahmad.fadil"
            />

            <label htmlFor="register_full_name">Nama Lengkap</label>
            <input
              id="register_full_name"
              name="full_name"
              type="text"
              value={registerForm.full_name}
              onChange={onRegisterChange}
              placeholder="Nama lengkap user"
            />

            <label htmlFor="register_email">Email</label>
            <input
              id="register_email"
              name="email"
              type="email"
              value={registerForm.email}
              onChange={onRegisterChange}
              placeholder="contoh: user@sikap.local"
            />

            <label htmlFor="register_no_telp">No. Telepon</label>
            <input
              id="register_no_telp"
              name="no_telp"
              type="text"
              value={registerForm.no_telp}
              onChange={onRegisterChange}
              placeholder="08xxxxxxxxxx"
            />

            <label htmlFor="register_role">Role</label>
            <select
              id="register_role"
              name="role"
              value={registerForm.role}
              onChange={onRegisterChange}
            >
              {roleOptions.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>

            <label htmlFor="register_password">Password</label>
            <input
              id="register_password"
              name="password"
              type="password"
              value={registerForm.password}
              onChange={onRegisterChange}
              placeholder="Minimal 8 karakter"
            />

            <label htmlFor="register_confirm_password">Konfirmasi Password</label>
            <input
              id="register_confirm_password"
              name="confirmPassword"
              type="password"
              value={registerForm.confirmPassword}
              onChange={onRegisterChange}
              placeholder="Ulangi password"
            />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? 'Memproses...' : 'Daftar'}
            </button>
          </form>
        )}

        {error ? <p className="alert error">{error}</p> : null}
        {successMessage ? <p className="alert success">{successMessage}</p> : null}

        <p className="api-note">
          Endpoint backend: {apiBaseUrlValue}/auth/login, /auth/me, /auth/logout,
          /dashboard, /users
        </p>
      </section>
    </main>
  )
}

function DashboardPage({
  authUser,
  dashboardData,
  dashboardLoading,
  error,
  successMessage,
  onRefresh,
  onLogout,
}) {
  const cards = dashboardData?.cards || []
  const primaryTable = dashboardData?.primary_table || {
    title: 'Ringkasan',
    columns: [],
    rows: [],
    note: '',
  }

  return (
    <main className="dashboard-page">
      <section className="dashboard-shell">
        <header className="dashboard-hero">
          <div>
            <p className="eyebrow">{dashboardTitles[authUser.role] || 'Dashboard'}</p>
            <h1>{authUser.full_name || authUser.username}</h1>
            <p className="subtitle dashboard-subtitle">
              Masuk sebagai {roleLabels[authUser.role] || authUser.role}. Dashboard
              ini menampilkan ringkasan data utama sesuai role Anda.
            </p>
          </div>

          <div className="dashboard-actions">
            <span className="role-pill">{roleLabels[authUser.role] || authUser.role}</span>
            <button type="button" className="ghost-button" onClick={onRefresh}>
              Muat Ulang
            </button>
            <button type="button" onClick={onLogout}>
              Logout
            </button>
          </div>
        </header>

        <section className="identity-strip">
          <div className="identity-item">
            <span>Username</span>
            <strong>{authUser.username || '-'}</strong>
          </div>
          <div className="identity-item">
            <span>Email</span>
            <strong>{authUser.email || '-'}</strong>
          </div>
          <div className="identity-item">
            <span>Role</span>
            <strong>{roleLabels[authUser.role] || authUser.role}</strong>
          </div>
        </section>

        {error ? <p className="alert error">{error}</p> : null}
        {successMessage ? <p className="alert success">{successMessage}</p> : null}

        {dashboardLoading ? (
          <section className="dashboard-panel">
            <p className="api-note">Memuat data dashboard...</p>
          </section>
        ) : null}

        {!dashboardLoading ? (
          <>
            <section className="metrics-grid">
              {cards.length ? (
                cards.map((card) => (
                  <article key={card.key} className="metric-card">
                    <span>{card.label}</span>
                    <strong>{formatCellValue(card.value)}</strong>
                  </article>
                ))
              ) : (
                <article className="metric-card empty">
                  <span>Belum Ada Ringkasan</span>
                  <strong>-</strong>
                </article>
              )}
            </section>

            <section className="dashboard-panel">
              <div className="panel-header">
                <div>
                  <h2>{primaryTable.title || 'Tabel Dashboard'}</h2>
                  <p className="api-note">
                    {dashboardData?.generated_at
                      ? `Diperbarui ${formatCellValue(dashboardData.generated_at)}`
                      : 'Data dashboard sesuai role pengguna.'}
                  </p>
                </div>
              </div>

              {primaryTable.rows?.length ? (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {primaryTable.columns.map((column) => (
                          <th key={column}>{formatColumnLabel(column)}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {primaryTable.rows.map((row, index) => (
                        <tr key={`${primaryTable.title}-${index}`}>
                          {primaryTable.columns.map((column) => (
                            <td key={`${index}-${column}`}>
                              {formatCellValue(row[column])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">
                  <p>{primaryTable.note || 'Belum ada data untuk ditampilkan.'}</p>
                </div>
              )}
            </section>
          </>
        ) : null}
      </section>
    </main>
  )
}

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
  })

  const [registerForm, setRegisterForm] = useState({
    username: '',
    full_name: '',
    email: '',
    no_telp: '',
    role: 'siswa',
    password: '',
    confirmPassword: '',
  })

  const [loading, setLoading] = useState(false)
  const [checkingSession, setCheckingSession] = useState(true)
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [authUser, setAuthUser] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)

  const api = useMemo(
    () =>
      axios.create({
        baseURL: apiBaseUrl,
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      }),
    [],
  )

  const clearSession = () => {
    localStorage.removeItem('sikap_token')
    localStorage.removeItem('sikap_token_type')
    localStorage.removeItem('sikap_expires_at')
    localStorage.removeItem('sikap_user')
    setAuthUser(null)
    setDashboardData(null)
  }

  const getAuthHeaders = () => {
    const token = localStorage.getItem('sikap_token')
    const tokenType = localStorage.getItem('sikap_token_type') || 'Bearer'

    if (!token) {
      return null
    }

    return {
      Authorization: `${tokenType} ${token}`,
    }
  }

  const fetchCurrentUser = async () => {
    const headers = getAuthHeaders()

    if (!headers) {
      throw new Error('Token tidak ditemukan.')
    }

    const { data } = await api.get('/auth/me', { headers })

    if (!data?.success || !data?.data) {
      throw new Error('Respons profil user tidak valid.')
    }

    setAuthUser(data.data)
    localStorage.setItem('sikap_user', JSON.stringify(data.data))
    return data.data
  }

  const fetchDashboard = async () => {
    const headers = getAuthHeaders()

    if (!headers) {
      throw new Error('Token tidak ditemukan.')
    }

    setDashboardLoading(true)
    try {
      const { data } = await api.get('/dashboard', { headers })

      if (!data?.success || !data?.data) {
        throw new Error('Respons dashboard tidak valid.')
      }

      setDashboardData(data.data)
      return data.data
    } finally {
      setDashboardLoading(false)
    }
  }

  useEffect(() => {
    const bootstrapSession = async () => {
      const token = localStorage.getItem('sikap_token')

      if (!token) {
        setCheckingSession(false)
        return
      }

      try {
        const user = await fetchCurrentUser()
        setSuccessMessage(
          `Sesi aktif. Selamat datang kembali, ${user.full_name || user.username}.`,
        )
        try {
          await fetchDashboard()
        } catch (_dashboardError) {
          setError('Sesi login aktif, tetapi data dashboard belum berhasil dimuat.')
        }
      } catch (_err) {
        clearSession()
      } finally {
        setCheckingSession(false)
      }
    }

    bootstrapSession()
  }, [])

  const handleLoginChange = (event) => {
    const { name, value } = event.target
    setLoginForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleRegisterChange = (event) => {
    const { name, value } = event.target
    setRegisterForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSwitchMode = (nextMode) => {
    setError('')
    setSuccessMessage('')
    navigate(nextMode === 'register' ? '/register' : '/login')
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!loginForm.username || !loginForm.password) {
      setError('Username dan password wajib diisi.')
      return
    }

    setLoading(true)

    try {
      const { data } = await api.post('/auth/login', loginForm)
      const responseData = data?.data

      if (!data?.success || !responseData?.access_token) {
        setError('Login gagal. Respons API tidak valid.')
        return
      }

      localStorage.setItem('sikap_token', responseData.access_token)
      localStorage.setItem('sikap_token_type', responseData.token_type || 'Bearer')
      localStorage.setItem('sikap_expires_at', String(responseData.expires_at || 0))

      const user = await fetchCurrentUser()
      try {
        await fetchDashboard()
      } catch (_dashboardError) {
        setError('Login berhasil, tetapi data dashboard belum berhasil dimuat.')
      }

      const displayName = user?.full_name || user?.username || loginForm.username
      setSuccessMessage(`Login berhasil. Selamat datang, ${displayName}.`)
      setLoginForm((prev) => ({ ...prev, password: '' }))
      navigate('/dashboard', { replace: true })
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Terjadi kesalahan saat menghubungi server.'

      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!registerForm.username || !registerForm.full_name || !registerForm.password) {
      setError('Username, nama lengkap, dan password wajib diisi.')
      return
    }

    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Konfirmasi password tidak sama.')
      return
    }

    const headers = getAuthHeaders()

    if (!headers) {
      setError('Login dulu sebagai admin untuk membuat user baru.')
      return
    }

    setLoading(true)

    try {
      const payload = {
        username: registerForm.username,
        full_name: registerForm.full_name,
        email: registerForm.email || null,
        no_telp: registerForm.no_telp || null,
        role: registerForm.role,
        password: registerForm.password,
      }

      const { data } = await api.post('/users', payload, { headers })

      if (!data?.success) {
        setError(data?.message || 'Registrasi gagal.')
        return
      }

      setSuccessMessage(data?.message || 'Registrasi berhasil.')
      setRegisterForm({
        username: '',
        full_name: '',
        email: '',
        no_telp: '',
        role: 'siswa',
        password: '',
        confirmPassword: '',
      })
    } catch (requestError) {
      const status = requestError?.response?.status
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Terjadi kesalahan saat menghubungi server.'

      if (status === 404) {
        setError(
          'Endpoint registrasi (/api/v1/users) belum tersedia di backend saat ini.',
        )
      } else if (status === 403) {
        setError('Akses ditolak. Registrasi user hanya untuk admin.')
      } else {
        setError(apiMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    const headers = getAuthHeaders()

    try {
      if (headers) {
        await api.post('/auth/logout', {}, { headers })
      }
    } catch (_err) {
      // Tetap lanjut clear session walaupun revoke token gagal.
    } finally {
      clearSession()
      setSuccessMessage('Logout berhasil.')
      setError('')
      navigate('/login', { replace: true })
    }
  }

  const handleRefreshDashboard = async () => {
    setError('')
    setSuccessMessage('')

    try {
      await fetchDashboard()
      setSuccessMessage('Dashboard berhasil diperbarui.')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.response?.data?.error ||
        requestError?.message ||
        'Gagal memuat dashboard.'

      setError(apiMessage)
    }
  }

  if (checkingSession) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>SIKAP</h1>
          <p className="subtitle">Memeriksa sesi login dan menyiapkan dashboard...</p>
        </section>
      </main>
    )
  }

  const authMode = location.pathname === '/register' ? 'register' : 'login'

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />}
      />
      <Route
        path="/login"
        element={
          authUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              mode={authMode}
              loading={loading}
              checkingSession={checkingSession}
              loginForm={loginForm}
              registerForm={registerForm}
              error={error}
              successMessage={successMessage}
              onLoginChange={handleLoginChange}
              onRegisterChange={handleRegisterChange}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onSwitchMode={handleSwitchMode}
              apiBaseUrlValue={apiBaseUrl}
            />
          )
        }
      />
      <Route
        path="/register"
        element={
          authUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              mode={authMode}
              loading={loading}
              checkingSession={checkingSession}
              loginForm={loginForm}
              registerForm={registerForm}
              error={error}
              successMessage={successMessage}
              onLoginChange={handleLoginChange}
              onRegisterChange={handleRegisterChange}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onSwitchMode={handleSwitchMode}
              apiBaseUrlValue={apiBaseUrl}
            />
          )
        }
      />
      <Route
        path="/dashboard"
        element={
          authUser ? (
            <DashboardPage
              authUser={authUser}
              dashboardData={dashboardData}
              dashboardLoading={dashboardLoading}
              error={error}
              successMessage={successMessage}
              onRefresh={handleRefreshDashboard}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="*"
        element={<Navigate to={authUser ? '/dashboard' : '/login'} replace />}
      />
    </Routes>
  )
}

export default App
