import { roleLabels } from '../config'
import { AppShell } from '../components/Common'
import { formatCellValue } from '../utils/formatters'

export default function ProfilePage({ authUser, dashboardData, onBackToDashboard, onLogout }) {
  const profileCards = dashboardData?.cards || []
  const linkedStudent = dashboardData?.student || null

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Profil"
      title="Profil Pengguna"
      subtitle="Data akun dan keterkaitan pengguna."
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
              <h2>Identitas Akun</h2>
              <p className="api-note">
                Data ini diambil dari sesi login aktif dan endpoint profil pengguna.
              </p>
            </div>
          </div>

          <dl className="detail-list">
            <div><dt>Nama Lengkap</dt><dd>{authUser.full_name || '-'}</dd></div>
            <div><dt>Username</dt><dd>{authUser.username || '-'}</dd></div>
            <div><dt>Email</dt><dd>{authUser.email || '-'}</dd></div>
            <div><dt>No. Telepon</dt><dd>{authUser.no_telp || '-'}</dd></div>
            <div><dt>Role</dt><dd>{roleLabels[authUser.role] || authUser.role}</dd></div>
            <div><dt>ID User</dt><dd>{authUser.id_user || '-'}</dd></div>
          </dl>
        </section>

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel highlighted-panel">
            <div className="panel-header">
              <div>
                <h2>Ringkasan Aktivitas</h2>
                <p className="api-note">
                  Kartu ini mengikuti payload dashboard sesuai role Anda.
                </p>
              </div>
            </div>

            {profileCards.length ? (
              <div className="mini-metrics-grid">
                {profileCards.map((card) => (
                  <article key={card.key} className="mini-metric-card">
                    <span>{card.label}</span>
                    <strong>{formatCellValue(card.value)}</strong>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state compact">
                <p>Belum ada kartu ringkasan untuk role ini.</p>
              </div>
            )}
          </section>

          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Keterkaitan Data</h2>
              </div>
            </div>

            {linkedStudent ? (
              <dl className="detail-list">
                <div><dt>Nama Siswa</dt><dd>{linkedStudent.nama || '-'}</dd></div>
                <div><dt>NISN</dt><dd>{linkedStudent.nisn || '-'}</dd></div>
                <div><dt>Kelas</dt><dd>{linkedStudent.kelas || '-'}</dd></div>
                <div><dt>ID Siswa</dt><dd>{linkedStudent.id_siswa || '-'}</dd></div>
              </dl>
            ) : (
              <div className="empty-state compact">
                <p>
                  {authUser.role === 'orangtua'
                    ? 'Akun orang tua ini belum memiliki data anak yang terhubung.'
                    : 'Tidak ada relasi data tambahan yang tersedia untuk akun ini saat ini.'}
                </p>
              </div>
            )}
          </section>
        </aside>
      </section>
    </AppShell>
  )
}
