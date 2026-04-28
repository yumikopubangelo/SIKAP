import { schoolProfileFallback } from '../config'
import { LoadingSpinner } from '../components/Common'

export default function AuthPage({
  loading,
  checkingSession,
  loginForm,
  error,
  successMessage,
  onLoginChange,
  onLogin,
}) {
  const authBusy = loading || checkingSession
  const hasError = Boolean(error)

  return (
    <main className="login-page" aria-busy={authBusy}>
      <section className="login-card" aria-live="polite">
        <p className="login-eyebrow">Absensi Sholat Sekolah</p>
        <h1>{schoolProfileFallback.name}</h1>
        <p className="subtitle">Silakan masuk untuk memantau kehadiran sholat di sekolah.</p>
        {checkingSession ? <p className="api-note">Memeriksa sesi login...</p> : null}

        <form onSubmit={onLogin} className="login-form" aria-busy={authBusy}>
          <label htmlFor="username">Username / Email</label>
          <input
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            required
            aria-invalid={hasError}
            aria-describedby={hasError ? 'auth-form-error' : undefined}
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
            required
            aria-invalid={hasError}
            aria-describedby={hasError ? 'auth-form-error' : undefined}
            value={loginForm.password}
            onChange={onLoginChange}
            placeholder="Masukkan password"
          />

          <button type="submit" disabled={loading || checkingSession}>
            {loading ? <LoadingSpinner label="Memproses..." /> : 'Masuk'}
          </button>
        </form>

        {error ? <p className="alert error">{error}</p> : null}
        {successMessage ? <p className="alert success">{successMessage}</p> : null}
      </section>
    </main>
  )
}
