import { useState } from 'react'
import { grafanaBaseUrl } from '../config'
import { AppShell } from '../components/Common'

const GRAFANA_DASHBOARD_UID = 'sikap-main'

const PANEL_CONFIGS = [
  { id: 'overview', title: 'Status Sistem', panelIds: [1, 2, 3, 4, 5, 6], height: 200 },
  { id: 'requests', title: 'Request Rate', panelIds: [10], height: 380 },
  { id: 'latency', title: 'Response Time', panelIds: [11], height: 380 },
  { id: 'status-codes', title: 'HTTP Status Codes', panelIds: [12], height: 380 },
  { id: 'users', title: 'User per Role', panelIds: [13], height: 380 },
  { id: 'sp', title: 'Surat Peringatan', panelIds: [20, 21, 22], height: 220 },
  { id: 'notif', title: 'Notifikasi', panelIds: [30], height: 180 },
]

function buildGrafanaPanelUrl(panelId) {
  return `${grafanaBaseUrl}/d-solo/${GRAFANA_DASHBOARD_UID}/sikap-monitoring-sistem?orgId=1&panelId=${panelId}&theme=light&refresh=10s`
}

function buildGrafanaDashboardUrl() {
  return `${grafanaBaseUrl}/d/${GRAFANA_DASHBOARD_UID}/sikap-monitoring-sistem?orgId=1&theme=light&kiosk`
}

export default function MonitoringPage({
  authUser,
  onBackToDashboard,
  onLogout,
}) {
  const [viewMode, setViewMode] = useState('panels')
  const [grafanaError, setGrafanaError] = useState(false)

  const canAccess = ['admin', 'kepsek'].includes(authUser?.role)

  if (!canAccess) {
    return (
      <AppShell
        authUser={authUser}
        eyebrow="Akses Ditolak"
        title="Halaman Monitoring"
        subtitle="Anda tidak memiliki akses ke halaman ini."
        actions={
          <button type="button" onClick={onBackToDashboard}>
            Kembali ke Dashboard
          </button>
        }
      >
        <section className="dashboard-panel">
          <p className="alert error">
            Hanya Admin dan Kepala Sekolah yang dapat mengakses monitoring sistem.
          </p>
        </section>
      </AppShell>
    )
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Monitoring Sistem"
      title="Status & Performa SIKAP"
      subtitle="Pantau kesehatan server, traffic API, dan kondisi perangkat secara real-time melalui Grafana."
      actions={
        <>
          <button
            type="button"
            className={viewMode === 'panels' ? 'ghost-button' : ''}
            onClick={() => setViewMode('panels')}
          >
            Panel
          </button>
          <button
            type="button"
            className={viewMode === 'full' ? 'ghost-button' : ''}
            onClick={() => setViewMode('full')}
          >
            Dashboard Penuh
          </button>
          <a
            href={`${grafanaBaseUrl}/d/${GRAFANA_DASHBOARD_UID}`}
            target="_blank"
            rel="noopener noreferrer"
            className="ghost-button"
            style={{ textDecoration: 'none' }}
          >
            Buka Grafana ↗
          </a>
          <button type="button" onClick={onBackToDashboard}>
            Kembali
          </button>
          <button type="button" onClick={onLogout}>
            Keluar
          </button>
        </>
      }
    >
      {grafanaError ? (
        <section className="dashboard-panel">
          <p className="alert error">
            Gagal memuat Grafana. Pastikan service Grafana sedang berjalan di{' '}
            <code>{grafanaBaseUrl}</code>.
          </p>
          <div className="tips-list">
            <p>
              Jalankan{' '}
              <code>docker compose up -d</code>{' '}
              untuk memulai semua service termasuk monitoring.
            </p>
          </div>
        </section>
      ) : null}

      {viewMode === 'full' ? (
        <section className="dashboard-panel" style={{ padding: 0, overflow: 'hidden' }}>
          <iframe
            src={buildGrafanaDashboardUrl()}
            title="Grafana Dashboard Penuh"
            style={{
              width: '100%',
              height: 'calc(100vh - 200px)',
              minHeight: '600px',
              border: 'none',
              borderRadius: '12px',
            }}
            onError={() => setGrafanaError(true)}
          />
        </section>
      ) : (
        <>
          {PANEL_CONFIGS.map((section) => (
            <section key={section.id} className="dashboard-panel">
              <div className="panel-header">
                <div>
                  <h2>{section.title}</h2>
                </div>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: section.panelIds.length > 1
                    ? `repeat(${Math.min(section.panelIds.length, 3)}, 1fr)`
                    : '1fr',
                  gap: '12px',
                }}
              >
                {section.panelIds.map((panelId) => (
                  <iframe
                    key={panelId}
                    src={buildGrafanaPanelUrl(panelId)}
                    title={`Grafana Panel ${panelId}`}
                    style={{
                      width: '100%',
                      height: `${section.height}px`,
                      border: 'none',
                      borderRadius: '8px',
                      background: '#f8f9fa',
                    }}
                    onError={() => setGrafanaError(true)}
                  />
                ))}
              </div>
            </section>
          ))}
        </>
      )}
    </AppShell>
  )
}
