import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
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

function App() {
  const [mode, setMode] = useState('login')

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
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [authUser, setAuthUser] = useState(null)

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

      const displayName = user?.full_name || user?.username || loginForm.username
      setSuccessMessage(`Login berhasil. Selamat datang, ${displayName}.`)
      setLoginForm((prev) => ({ ...prev, password: '' }))
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
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <h1>SIKAP Auth</h1>
        <p className="subtitle">
          Sistem Informasi Kepatuhan Ibadah Peserta Didik
        </p>

        {checkingSession ? <p className="api-note">Memeriksa sesi login...</p> : null}

        {authUser ? (
          <div className="profile-card">
            <p>
              <strong>Nama:</strong> {authUser.full_name || '-'}
            </p>
            <p>
              <strong>Username:</strong> {authUser.username || '-'}
            </p>
            <p>
              <strong>Role:</strong> {authUser.role || '-'}
            </p>
            <button type="button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        ) : null}

        <div className="mode-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'tab active' : 'tab'}
            onClick={() => {
              setMode('login')
              setError('')
              setSuccessMessage('')
            }}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'tab active' : 'tab'}
            onClick={() => {
              setMode('register')
              setError('')
              setSuccessMessage('')
            }}
          >
            Registrasi
          </button>
        </div>

        {mode === 'login' ? (
          <form onSubmit={handleLogin} className="login-form">
            <label htmlFor="username">Username / Email</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={loginForm.username}
              onChange={handleLoginChange}
              placeholder="contoh: admin atau admin@sikap.local"
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={loginForm.password}
              onChange={handleLoginChange}
              placeholder="Masukkan password"
            />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? 'Memproses...' : 'Masuk'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="login-form">
            <label htmlFor="register_username">Username</label>
            <input
              id="register_username"
              name="username"
              type="text"
              value={registerForm.username}
              onChange={handleRegisterChange}
              placeholder="contoh: ahmad.fadil"
            />

            <label htmlFor="register_full_name">Nama Lengkap</label>
            <input
              id="register_full_name"
              name="full_name"
              type="text"
              value={registerForm.full_name}
              onChange={handleRegisterChange}
              placeholder="Nama lengkap user"
            />

            <label htmlFor="register_email">Email</label>
            <input
              id="register_email"
              name="email"
              type="email"
              value={registerForm.email}
              onChange={handleRegisterChange}
              placeholder="contoh: user@sikap.local"
            />

            <label htmlFor="register_no_telp">No. Telepon</label>
            <input
              id="register_no_telp"
              name="no_telp"
              type="text"
              value={registerForm.no_telp}
              onChange={handleRegisterChange}
              placeholder="08xxxxxxxxxx"
            />

            <label htmlFor="register_role">Role</label>
            <select
              id="register_role"
              name="role"
              value={registerForm.role}
              onChange={handleRegisterChange}
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
              onChange={handleRegisterChange}
              placeholder="Minimal 8 karakter"
            />

            <label htmlFor="register_confirm_password">Konfirmasi Password</label>
            <input
              id="register_confirm_password"
              name="confirmPassword"
              type="password"
              value={registerForm.confirmPassword}
              onChange={handleRegisterChange}
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
          Endpoint backend: {apiBaseUrl}/auth/login, /auth/me, /auth/logout, /users
        </p>
      </section>
    </main>
  )
}

export default App
