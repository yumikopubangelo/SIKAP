import { roleOptions, schoolProfileFallback } from '../config'
import { LoadingSpinner } from '../components/Common'

export default function AuthPage({
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

        <div className="mode-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'tab active' : 'tab'}
            onClick={() => onSwitchMode('login')}
            aria-pressed={mode === 'login'}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'tab active' : 'tab'}
            onClick={() => onSwitchMode('register')}
            aria-pressed={mode === 'register'}
          >
            Registrasi
          </button>
        </div>

        {mode === 'login' ? (
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
        ) : (
          <form onSubmit={onRegister} className="login-form" aria-busy={authBusy}>
            <label htmlFor="register_username">Username</label>
            <input id="register_username" name="username" type="text" value={registerForm.username} onChange={onRegisterChange} placeholder="contoh: ahmad.fadil" />

            <label htmlFor="register_full_name">Nama Lengkap</label>
            <input id="register_full_name" name="full_name" type="text" value={registerForm.full_name} onChange={onRegisterChange} placeholder="Nama lengkap user" />

            <label htmlFor="register_email">Email</label>
            <input id="register_email" name="email" type="email" value={registerForm.email} onChange={onRegisterChange} placeholder="contoh: user@sikap.local" />

            <label htmlFor="register_no_telp">No. Telepon</label>
            <input id="register_no_telp" name="no_telp" type="text" value={registerForm.no_telp} onChange={onRegisterChange} placeholder="08xxxxxxxxxx" />

            <label htmlFor="register_role">Role</label>
            <select id="register_role" name="role" value={registerForm.role} onChange={onRegisterChange}>
              {roleOptions.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>

            <label htmlFor="register_password">Password</label>
            <input id="register_password" name="password" type="password" value={registerForm.password} onChange={onRegisterChange} placeholder="Minimal 8 karakter" />

            <label htmlFor="register_confirm_password">Konfirmasi Password</label>
            <input id="register_confirm_password" name="confirmPassword" type="password" value={registerForm.confirmPassword} onChange={onRegisterChange} placeholder="Ulangi password" />

            <button type="submit" disabled={loading || checkingSession}>
              {loading ? 'Memproses...' : 'Daftar'}
            </button>
          </form>
        )}

        {error ? <p className="alert error">{error}</p> : null}
        {successMessage ? <p className="alert success">{successMessage}</p> : null}
      </section>
    </main>
  )
}
