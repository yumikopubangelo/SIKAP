import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { roleLabels, roleOptions } from '../config'
import { AppShell } from '../components/Common'
import { formatCellValue } from '../utils/formatters'

export default function UserManagementPage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onOpenAddUser,
  onOpenEditUser,
  onLogout,
}) {
  const navigate = useNavigate()
  const location = useLocation()

  const [filters, setFilters] = useState({
    search: '',
    role: '',
  })
  const [appliedFilters, setAppliedFilters] = useState({
    search: '',
    role: '',
  })
  const [users, setUsers] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total_items: 0,
    total_pages: 1,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const fetchUsers = async ({ page, search, role } = {}) => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    const nextPage = page ?? pagination.page
    const nextSearch = search ?? appliedFilters.search
    const nextRole = role ?? appliedFilters.role

    setLoading(true)
    try {
      const { data } = await api.get('/users', {
        headers,
        params: {
          page: nextPage,
          limit: pagination.limit,
          search: nextSearch || undefined,
          role: nextRole || undefined,
        },
      })

      if (!data?.success || !Array.isArray(data?.data)) {
        throw new Error('Respons daftar user tidak valid.')
      }

      setUsers(data.data)
      setPagination((prev) => ({
        ...prev,
        page: data?.pagination?.page ?? nextPage,
        limit: data?.pagination?.limit ?? prev.limit,
        total_items: data?.pagination?.total_items ?? data.data.length,
        total_pages: data?.pagination?.total_pages ?? 1,
      }))
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat data user.'

      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchUsers()
  }, [pagination.page, appliedFilters.search, appliedFilters.role])

  useEffect(() => {
    const flashMessage = location.state?.userManagementMessage
    if (!flashMessage) {
      return
    }

    setSuccessMessage(flashMessage)
    navigate(location.pathname, { replace: true, state: null })
  }, [location.pathname, location.state, navigate])

  const handleFilterChange = (event) => {
    const { name, value } = event.target
    setFilters((prev) => ({ ...prev, [name]: value }))
  }

  const handleApplyFilters = (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')
    setAppliedFilters({
      search: filters.search.trim(),
      role: filters.role,
    })
    setPagination((prev) => ({ ...prev, page: 1 }))
  }

  const handleResetFilters = () => {
    setFilters({ search: '', role: '' })
    setAppliedFilters({ search: '', role: '' })
    setPagination((prev) => ({ ...prev, page: 1 }))
    setError('')
    setSuccessMessage('')
  }

  const handleDeleteUser = async (user) => {
    const confirmation = window.confirm(
      `Hapus user ${user.full_name || user.username}? Tindakan ini tidak bisa dibatalkan.`,
    )
    if (!confirmation) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setError('')
    setSuccessMessage('')

    try {
      const { data } = await api.delete(`/users/${user.id_user}`, { headers })
      setSuccessMessage(data?.message || 'User berhasil dihapus.')

      if (users.length === 1 && pagination.page > 1) {
        setPagination((prev) => ({ ...prev, page: prev.page - 1 }))
      } else {
        await fetchUsers()
      }
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menghapus user.'

      setError(apiMessage)
    }
  }

  const totalPages = pagination.total_pages || 1

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Kelola Akun"
      title="Kelola Akun"
      subtitle="Tambah, ubah, dan cari akun pengguna."
      actions={
        <>
          <button type="button" className="ghost-button" onClick={onOpenAddUser}>
            Tambah User
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
        <div className="panel-header">
          <div>
            <h2>Filter User</h2>
            <p className="api-note">
              Gunakan pencarian nama, username, email, atau filter role untuk mempercepat administrasi.
            </p>
          </div>
        </div>

        <form className="toolbar-form" onSubmit={handleApplyFilters}>
          <div className="toolbar-grid">
            <div className="manual-field">
              <label htmlFor="user_search">Cari User</label>
              <input
                id="user_search"
                name="search"
                type="text"
                value={filters.search}
                onChange={handleFilterChange}
                placeholder="Cari nama, username, atau email"
              />
            </div>
            <div className="manual-field">
              <label htmlFor="user_role_filter">Role</label>
              <select
                id="user_role_filter"
                name="role"
                value={filters.role}
                onChange={handleFilterChange}
              >
                <option value="">Semua Role</option>
                {roleOptions.map((role) => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="manual-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Memuat...' : 'Terapkan Filter'}
            </button>
            <button
              type="button"
              className="ghost-button"
              onClick={handleResetFilters}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Daftar User</h2>
            <p className="api-note">
              Menampilkan {users.length} user pada halaman ini dari total {pagination.total_items} data.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state compact">
            <p>Memuat daftar user...</p>
          </div>
        ) : users.length ? (
          <>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Nama</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Data Siswa</th>
                    <th>Dibuat</th>
                    <th>Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id_user}>
                      <td>{user.username}</td>
                      <td>{user.full_name}</td>
                      <td>{user.email || '-'}</td>
                      <td>{roleLabels[user.role] || user.role}</td>
                      <td>
                        {user.student ? `${user.student.nama} (${user.student.nisn})` : '-'}
                      </td>
                      <td>{formatCellValue(user.created_at)}</td>
                      <td>
                        <div className="table-actions">
                          <button
                            type="button"
                            className="ghost-button"
                            onClick={() => onOpenEditUser(user.id_user)}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="ghost-button danger-button"
                            onClick={() => handleDeleteUser(user)}
                            disabled={user.id_user === authUser.id_user}
                          >
                            Hapus
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination-row">
              <p className="api-note">
                Halaman {pagination.page} dari {totalPages}
              </p>
              <div className="table-actions">
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() => setPagination((prev) => ({ ...prev, page: prev.page - 1 }))}
                  disabled={loading || pagination.page <= 1}
                >
                  Sebelumnya
                </button>
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() => setPagination((prev) => ({ ...prev, page: prev.page + 1 }))}
                  disabled={loading || pagination.page >= totalPages}
                >
                  Berikutnya
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <p>Belum ada user yang cocok dengan filter saat ini.</p>
          </div>
        )}
      </section>
    </AppShell>
  )
}
