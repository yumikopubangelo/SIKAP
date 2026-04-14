import { useEffect, useState } from 'react'

import { AppShell } from '../components/Common'

export default function PrayerTimeSettingsPage({ authUser, api, getAuthHeaders, onBackToDashboard, onLogout }) {
  const [times, setTimes] = useState([])
  const [loading, setLoading] = useState(true)
  const [savingId, setSavingId] = useState(null)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const fetchPrayerTimes = async () => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      setLoading(false)
      return
    }

    setLoading(true)
    try {
      const { data } = await api.get('/waktu-sholat', { headers })
      if (!data?.success || !Array.isArray(data?.data)) {
        throw new Error('Respons waktu sholat tidak valid.')
      }

      setTimes(
        data.data.map((item) => ({
          ...item,
          waktu_adzan: (item.waktu_adzan || '').slice(0, 5),
          waktu_iqamah: (item.waktu_iqamah || '').slice(0, 5),
          waktu_selesai: (item.waktu_selesai || '').slice(0, 5),
        })),
      )
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat waktu sholat.'
      setError(apiMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchPrayerTimes()
  }, [])

  const handleTimeChange = (id, field, value) => {
    setTimes((prev) =>
      prev.map((item) => (item.id_waktu === id ? { ...item, [field]: value } : item)),
    )
  }

  const handleSavePrayerTime = async (item) => {
    const headers = getAuthHeaders()
    if (!headers) {
      setError('Sesi login tidak ditemukan. Silakan login ulang.')
      return
    }

    setSavingId(item.id_waktu)
    setError('')
    setSuccessMessage('')

    try {
      const { data } = await api.put(
        `/waktu-sholat/${item.id_waktu}`,
        {
          waktu_adzan: item.waktu_adzan,
          waktu_iqamah: item.waktu_iqamah,
          waktu_selesai: item.waktu_selesai,
        },
        { headers },
      )

      if (!data?.success || !data?.data) {
        throw new Error('Respons update waktu sholat tidak valid.')
      }

      setSuccessMessage(data.message || 'Waktu sholat berhasil diupdate.')
      setTimes((prev) =>
        prev.map((row) =>
          row.id_waktu === item.id_waktu
            ? {
                ...row,
                waktu_adzan: (data.data.waktu_adzan || '').slice(0, 5),
                waktu_iqamah: (data.data.waktu_iqamah || '').slice(0, 5),
                waktu_selesai: (data.data.waktu_selesai || '').slice(0, 5),
              }
            : row,
        ),
      )
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal mengupdate waktu sholat.'
      setError(apiMessage)
    } finally {
      setSavingId(null)
    }
  }

  return (
    <AppShell
      authUser={authUser}
      eyebrow="Waktu Sholat"
      title="Pengaturan Waktu Sholat"
      subtitle="Atur jadwal adzan, iqamah, dan batas sesi."
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

      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <h2>Daftar Waktu Sholat</h2>
            <p className="api-note">
              Perubahan di halaman ini akan memengaruhi logika sesi aktif dan timestamp default input manual.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state compact">
            <p>Memuat pengaturan waktu sholat...</p>
          </div>
        ) : times.length ? (
          <div className="settings-grid">
            {times.map((item) => (
              <article key={item.id_waktu} className="setting-card">
                <div className="setting-card-head">
                  <h2>{item.nama_sholat}</h2>
                  <span className="status-chip prayer">{item.nama_sholat}</span>
                </div>

                <div className="manual-form-grid">
                  <div className="manual-field">
                    <label htmlFor={`adzan-${item.id_waktu}`}>Waktu Adzan</label>
                    <input
                      id={`adzan-${item.id_waktu}`}
                      type="time"
                      value={item.waktu_adzan}
                      onChange={(event) =>
                        handleTimeChange(item.id_waktu, 'waktu_adzan', event.target.value)
                      }
                    />
                  </div>

                  <div className="manual-field">
                    <label htmlFor={`iqamah-${item.id_waktu}`}>Waktu Iqamah</label>
                    <input
                      id={`iqamah-${item.id_waktu}`}
                      type="time"
                      value={item.waktu_iqamah}
                      onChange={(event) =>
                        handleTimeChange(item.id_waktu, 'waktu_iqamah', event.target.value)
                      }
                    />
                  </div>

                  <div className="manual-field manual-field-full">
                    <label htmlFor={`selesai-${item.id_waktu}`}>Waktu Selesai</label>
                    <input
                      id={`selesai-${item.id_waktu}`}
                      type="time"
                      value={item.waktu_selesai}
                      onChange={(event) =>
                        handleTimeChange(item.id_waktu, 'waktu_selesai', event.target.value)
                      }
                    />
                  </div>
                </div>

                <div className="manual-actions">
                  <button
                    type="button"
                    onClick={() => handleSavePrayerTime(item)}
                    disabled={savingId === item.id_waktu}
                  >
                    {savingId === item.id_waktu ? 'Menyimpan...' : 'Simpan Waktu'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>Belum ada data waktu sholat untuk ditampilkan.</p>
          </div>
        )}
      </section>
    </AppShell>
  )
}
