import { useEffect, useMemo, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

import {
  csvImportPath,
  dutySchedulePath,
  manualInputPath,
  monitoringPath,
  notificationPath,
  prayerTimePath,
  profilePath,
  reportPath,
  roleLabels,
  schoolDataPath,
  schoolProfileFallback,
  userManagementPath,
  warningLetterPath,
} from '../config'

const HARI_ID = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
const BULAN_ID = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]

function formatTanggalPanjang(date) {
  return `${HARI_ID[date.getDay()]}, ${date.getDate()} ${BULAN_ID[date.getMonth()]} ${date.getFullYear()}`
}

function formatJam(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(date.getHours())}.${pad(date.getMinutes())}`
}

function getInitials(name) {
  if (!name) {
    return 'SI'
  }

  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || '')
    .join('')
}

function buildNavItems(role) {
  const items = [
    { to: '/', label: 'Beranda', roles: ['admin', 'kepsek', 'wali_kelas', 'guru_piket', 'siswa', 'orangtua'] },
    { to: notificationPath, label: 'Pesan', roles: ['admin', 'kepsek', 'wali_kelas', 'guru_piket', 'siswa', 'orangtua'] },
    { to: schoolDataPath, label: 'Data Sekolah', roles: ['admin', 'kepsek', 'wali_kelas'] },
    { to: monitoringPath, label: 'Monitoring', roles: ['admin', 'kepsek'] },
    { to: reportPath, label: 'Laporan', roles: ['admin', 'kepsek', 'wali_kelas'] },
    { to: monitoringPath, label: 'Monitoring', roles: ['admin', 'kepsek'] },
    { to: manualInputPath, label: 'Input Absensi', roles: ['guru_piket'] },
    { to: dutySchedulePath, label: 'Jadwal Piket', roles: ['admin', 'guru_piket'] },
    { to: warningLetterPath, label: 'Surat Peringatan', roles: ['admin', 'kepsek', 'wali_kelas', 'orangtua', 'siswa'] },
    { to: prayerTimePath, label: 'Waktu Sholat', roles: ['admin'] },
    { to: userManagementPath, label: 'Kelola Akun', roles: ['admin'] },
    { to: profilePath, label: 'Profil Saya', roles: ['admin', 'kepsek', 'wali_kelas', 'guru_piket', 'siswa', 'orangtua'] },
  ]

  return items.filter((item) => item.roles.includes(role))
}

export function LoadingSpinner({ label = 'Memuat...' }) {
  return (
    <span className="loading-inline" role="status" aria-live="polite" aria-label={label}>
      <span className="loading-spinner" aria-hidden="true" />
      <span>{label}</span>
    </span>
  )
}

export function Toast({ toast, onClose }) {
  if (!toast?.message) {
    return null
  }

  return (
    <div className="toast-layer">
      <div className={`toast ${toast.type}`} role="alert" aria-live="assertive">
        <p>{toast.message}</p>
        <button type="button" className="toast-close" onClick={onClose} aria-label="Tutup notifikasi">
          x
        </button>
      </div>
    </div>
  )
}

export function AppShell({ authUser, eyebrow, title, subtitle, actions, children }) {
  const location = useLocation()
  const initials = getInitials(authUser.full_name || authUser.username)
  const navItems = buildNavItems(authUser.role)
  const [navOpen, setNavOpen] = useState(false)
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    setNavOpen(false)
  }, [location.pathname])

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 30_000)
    return () => window.clearInterval(timer)
  }, [])

  const tanggalSekarang = useMemo(() => formatTanggalPanjang(now), [now])
  const jamSekarang = useMemo(() => formatJam(now), [now])

  return (
    <main className="dashboard-page">
      <section className="dashboard-shell">
        <header className="app-topbar">
          <div className="app-brand">
            <div className="app-brand-copy">
              <span className="app-brand-eyebrow">Absensi Sholat Sekolah</span>
              <strong>{schoolProfileFallback.name}</strong>
              <span className="app-brand-tagline">{tanggalSekarang} &middot; pukul {jamSekarang} WIB</span>
            </div>
          </div>

          <div className="app-user-chip">
            <div className="app-user-avatar" aria-hidden="true">
              {initials}
            </div>
            <div className="app-user-copy">
              <strong>{authUser.full_name || authUser.username}</strong>
              <span>{roleLabels[authUser.role] || authUser.role}</span>
            </div>
          </div>
        </header>

        <div className="app-nav-shell">
          <div className="app-nav-hero-row">
            <div className="dashboard-hero-copy">
              {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
              <h1>{title}</h1>
              {subtitle ? <p className="subtitle dashboard-subtitle">{subtitle}</p> : null}
            </div>
            <div className="dashboard-actions">{actions}</div>
          </div>

          <button
            type="button"
            className="app-nav-toggle"
            aria-expanded={navOpen}
            aria-controls="app-main-nav"
            onClick={() => setNavOpen((prev) => !prev)}
          >
            <span className="app-nav-toggle-icon" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <span>Menu</span>
          </button>

          <nav
            id="app-main-nav"
            className={`app-nav ${navOpen ? 'open' : ''}`}
            aria-label="Menu utama"
          >
          {navItems.map((item) => {
            const isActive =
              item.to === '/'
                ? location.pathname === '/'
                : location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)

            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`app-nav-link ${isActive ? 'active' : ''}`}
              >
                {item.label}
              </NavLink>
            )
          })}
          </nav>
        </div>

        {children}
      </section>
    </main>
  )
}
