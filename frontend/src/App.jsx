import { useMemo, useState } from 'react'
import axios from 'axios'
import './App.css'

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'kepsek', label: 'Kepala Sekolah' },
  { value: 'wali', label: 'Wali Kelas' },
  { value: 'piket', label: 'Guru Piket' },
  { value: 'siswa', label: 'Siswa' },
  { value: 'ortu', label: 'Orang Tua' },
]

const apiBaseUrl =
  (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')

function App() {
  const [form, setForm] = useState({
    username: '',
    password: '',
    role: 'siswa',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

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

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!form.username || !form.password || !form.role) {
      setError('Username, password, dan role wajib diisi.')
      return
    }

    setLoading(true)

    try {
      const { data } = await api.post('/auth/login', form)

      if (!data?.success || !data?.token) {
        setError('Login gagal. Respons API tidak valid.')
        return
      }

      localStorage.setItem('sikap_token', data.token)
      localStorage.setItem('sikap_user', JSON.stringify(data.user || {}))
      localStorage.setItem('sikap_expires_in', String(data.expires_in || 0))

      const displayName = data.user?.nama || data.user?.username || form.username
      setSuccessMessage(`Login berhasil. Selamat datang, ${displayName}.`)
      setForm((prev) => ({ ...prev, password: '' }))
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

  return (
    <main className="login-page">
      <section className="login-card">
        <h1>SIKAP Login</h1>
        <p className="subtitle">
          Sistem Informasi Kepatuhan Ibadah Peserta Didik
        </p>

        <form onSubmit={handleSubmit} className="login-form">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            value={form.username}
            onChange={handleChange}
            placeholder="contoh: ahmad.fadil"
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            onChange={handleChange}
            placeholder="Masukkan password"
          />

          <label htmlFor="role">Role</label>
          <select id="role" name="role" value={form.role} onChange={handleChange}>
            {roleOptions.map((role) => (
              <option key={role.value} value={role.value}>
                {role.label}
              </option>
            ))}
          </select>

          <button type="submit" disabled={loading}>
            {loading ? 'Memproses...' : 'Masuk'}
          </button>

          {error ? <p className="alert error">{error}</p> : null}
          {successMessage ? (
            <p className="alert success">{successMessage}</p>
          ) : null}
        </form>

        <p className="api-note">Endpoint: {apiBaseUrl}/auth/login</p>
      </section>
    </main>
  )
}

export default App
