import { AppShell } from '../components/Common'

export default function NotificationPage({
  authUser,
  notifications,
  unreadCount,
  loading,
  error,
  successMessage,
  onRefresh,
  onMarkAsRead,
  onBackToDashboard,
  onLogout,
}) {
  return (
    <AppShell
      authUser={authUser}
      eyebrow="Pesan"
      title="Notifikasi"
      subtitle="Lihat pesan baru dan tandai yang sudah dibaca."
      actions={
        <>
          <span className="role-pill">Belum dibaca: {unreadCount}</span>
          <button type="button" className="ghost-button" onClick={onRefresh} disabled={loading}>
            {loading ? 'Memuat...' : 'Muat Ulang'}
          </button>
          <button type="button" className="ghost-button" onClick={onBackToDashboard}>
            Dashboard
          </button>
          <button type="button" onClick={onLogout}>
            Keluar
          </button>
        </>
      }
    >
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      <section className="dashboard-panel">
        {notifications.length ? (
          <div className="notification-list">
            {notifications.map((item) => (
              <button
                type="button"
                key={item.id_notifikasi}
                className={item.is_read ? 'notification-item read' : 'notification-item unread'}
                onClick={() => onMarkAsRead(item)}
              >
                <div className="notification-item-head">
                  <strong>{item.judul || 'Notifikasi'}</strong>
                  <span className={item.is_read ? 'chip-read' : 'chip-unread'}>
                    {item.is_read ? 'Sudah Dibaca' : 'Belum Dibaca'}
                  </span>
                </div>
                <p>{item.pesan || '-'}</p>
                <small>
                  {item.created_at ? new Date(item.created_at).toLocaleString('id-ID') : '-'}
                </small>
              </button>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>Belum ada notifikasi untuk akun ini.</p>
          </div>
        )}
      </section>
    </AppShell>
  )
}
