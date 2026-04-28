import { useEffect, useState } from 'react'

import { AppShell } from '../components/Common'
import { dayLabels, dayOptions } from '../config'
import { formatCellValue } from '../utils/formatters'

function buildInitialForm() {
  return {
    user_id: '',
    hari: 'senin',
    jam_mulai: '06:30',
    jam_selesai: '09:00',
  }
}

export default function DutySchedulePage({
  authUser,
  api,
  getAuthHeaders,
  onBackToDashboard,
  onLogout,
}) {
  const isAdmin = authUser.role === 'admin'
  const [form, setForm] = useState(buildInitialForm)
  const [editingId, setEditingId] = useState(null)
  const [teachers, setTeachers] = useState([])
  const [schedules, setSchedules] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total_items: 0,
    total_pages: 1,
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const fetchTeachers = async () => {
    if (!isAdmin) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    try {
      const { data } = await api.get('/users', {
        headers,
        params: { role: 'guru_piket', limit: 100 },
      })

      if (!data?.success || !Array.isArray(data?.data)) {
        throw new Error('Respons daftar guru piket tidak valid.')
      }

      setTeachers(data.data)
      setForm((prev) => ({
        ...prev,
        user_id: prev.user_id || data.data[0]?.id_user || '',
      }))
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat daftar guru piket.'
      setError(apiMessage)
    }
  }

  const fetchSchedules = async () => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setLoading(true)
    try {
      const { data } = await api.get('/jadwal-piket', {
        headers,
        params: { page: 1, limit: 100 },
      })

      if (!data?.success || !Array.isArray(data?.data)) {
        throw new Error('Respons jadwal piket tidak valid.')
      }

      setSchedules(data.data)
      setPagination({
        page: data?.pagination?.page ?? 1,
        limit: data?.pagination?.limit ?? 100,
        total_items: data?.pagination?.total_items ?? data.data.length,
        total_pages: data?.pagination?.total_pages ?? 1,
      })
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat jadwal piket.'
      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchTeachers()
    void fetchSchedules()
  }, [])

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleEdit = (item) => {
    setEditingId(item.id_jadwal)
    setForm({
      user_id: item.user?.id_user || '',
      hari: item.hari || 'senin',
      jam_mulai: item.jam_mulai?.slice(0, 5) || '06:30',
      jam_selesai: item.jam_selesai?.slice(0, 5) || '09:00',
    })
    setError('')
    setSuccessMessage('')
  }

  const resetForm = () => {
    setEditingId(null)
    setForm({
      ...buildInitialForm(),
      user_id: teachers[0]?.id_user || '',
    })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!isAdmin) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSaving(true)
    setError('')
    setSuccessMessage('')

    try {
      const payload = {
        user_id: Number(form.user_id),
        hari: form.hari,
        jam_mulai: form.jam_mulai,
        jam_selesai: form.jam_selesai,
      }

      const request = editingId
        ? api.put(`/jadwal-piket/${editingId}`, payload, { headers })
        : api.post('/jadwal-piket', payload, { headers })

      const { data } = await request
      if (!data?.success) {
        throw new Error('Respons simpan jadwal piket tidak valid.')
      }

      setSuccessMessage(data.message || 'Jadwal piket berhasil disimpan.')
      resetForm()
      await fetchSchedules()
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menyimpan jadwal piket.'
      setError(apiMessage)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (item) => {
    if (!isAdmin) {
      return
    }
    const confirmed = window.confirm(`Hapus jadwal ${item.user?.full_name || '-'} di hari ${dayLabels[item.hari] || item.hari}?`)
    if (!confirmed) {
      return
    }

    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    try {
      const { data } = await api.delete(`/jadwal-piket/${item.id_jadwal}`, { headers })
      setSuccessMessage(data?.message || 'Jadwal piket berhasil dihapus.')
      await fetchSchedules()
      if (editingId === item.id_jadwal) {
        resetForm()
      }
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal menghapus jadwal piket.'
      setError(apiMessage)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Jadwal Piket"
      title="Jadwal Guru Piket"
      subtitle={
        isAdmin
          ? 'Atur giliran guru piket dan pastikan semua shift sudah terdistribusi.'
          : 'Lihat jadwal piket Anda yang aktif di sistem.'
      }
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
      {error ? <p className="alert error">{error}</p> : null}
      {successMessage ? <p className="alert success">{successMessage}</p> : null}

      <section className="manual-grid">
        {isAdmin ? (
          <section className="dashboard-panel manual-panel highlighted-panel">
            <div className="panel-header">
              <div>
                <h2>{editingId ? 'Edit Jadwal Piket' : 'Tambah Jadwal Piket'}</h2>
                <p className="api-note">Pilih guru, hari, dan rentang jam piket.</p>
              </div>
            </div>

            <form className="manual-form" onSubmit={handleSubmit}>
              <div className="manual-form-grid">
                <div className="manual-field">
                  <label htmlFor="schedule_user">Guru Piket</label>
                  <select id="schedule_user" name="user_id" value={form.user_id} onChange={handleFieldChange}>
                    <option value="">Pilih Guru</option>
                    {teachers.map((teacher) => (
                      <option key={teacher.id_user} value={teacher.id_user}>
                        {teacher.full_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="manual-field">
                  <label htmlFor="schedule_day">Hari</label>
                  <select id="schedule_day" name="hari" value={form.hari} onChange={handleFieldChange}>
                    {dayOptions.map((day) => (
                      <option key={day.value} value={day.value}>
                        {day.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="manual-field">
                  <label htmlFor="schedule_start">Jam Mulai</label>
                  <input id="schedule_start" name="jam_mulai" type="time" value={form.jam_mulai} onChange={handleFieldChange} />
                </div>

                <div className="manual-field">
                  <label htmlFor="schedule_end">Jam Selesai</label>
                  <input id="schedule_end" name="jam_selesai" type="time" value={form.jam_selesai} onChange={handleFieldChange} />
                </div>
              </div>

              <div className="manual-actions">
                <button type="submit" disabled={saving}>
                  {saving ? 'Menyimpan...' : editingId ? 'Simpan Perubahan' : 'Tambah Jadwal'}
                </button>
                <button type="button" className="ghost-button" onClick={resetForm} disabled={saving}>
                  Reset
                </button>
              </div>
            </form>
          </section>
        ) : null}

        <aside className="manual-side-panel">
          <section className="dashboard-panel manual-panel">
            <div className="panel-header">
              <div>
                <h2>Ringkasan</h2>
                <p className="api-note">Total jadwal tersimpan: {pagination.total_items}</p>
              </div>
            </div>

            <div className="mini-metrics-grid">
              <article className="mini-metric-card">
                <span>Total Jadwal</span>
                <strong>{pagination.total_items}</strong>
              </article>
              <article className="mini-metric-card">
                <span>Role Akses</span>
                <strong>{isAdmin ? 'Admin' : 'Guru Piket'}</strong>
              </article>
            </div>
          </section>
        </aside>
      </section>

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Daftar Jadwal Piket</h2>
            <p className="api-note">Menampilkan jadwal sesuai hak akses akun yang sedang login.</p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state compact">
            <p>Memuat jadwal piket...</p>
          </div>
        ) : schedules.length ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Hari</th>
                  <th>Guru</th>
                  <th>Mulai</th>
                  <th>Selesai</th>
                  {isAdmin ? <th>Aksi</th> : null}
                </tr>
              </thead>
              <tbody>
                {schedules.map((item) => (
                  <tr key={item.id_jadwal}>
                    <td>{dayLabels[item.hari] || item.hari}</td>
                    <td>{item.user?.full_name || '-'}</td>
                    <td>{formatCellValue(item.jam_mulai)}</td>
                    <td>{formatCellValue(item.jam_selesai)}</td>
                    {isAdmin ? (
                      <td>
                        <div className="table-actions">
                          <button type="button" className="ghost-button" onClick={() => handleEdit(item)}>
                            Edit
                          </button>
                          <button type="button" className="ghost-button danger-button" onClick={() => handleDelete(item)}>
                            Hapus
                          </button>
                        </div>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>Belum ada jadwal piket yang tersimpan.</p>
          </div>
        )}
      </section>
    </AppShell>
  )
}
