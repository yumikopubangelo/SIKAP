import { useEffect, useState } from 'react'

import { AppShell } from '../components/Common'

const dateTimeFormatter = new Intl.DateTimeFormat('id-ID', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

function formatDateTime(value) {
  if (!value) {
    return '-'
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return dateTimeFormatter.format(parsed)
}

export default function PrayerTimeSettingsPage({ authUser, api, getAuthHeaders, onBackToDashboard, onLogout }) {
  const [times, setTimes] = useState([])
  const [prayerStatus, setPrayerStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [statusLoading, setStatusLoading] = useState(true)
  const [savingId, setSavingId] = useState(null)
  const [error, setError] = useState('')
  const [statusError, setStatusError] = useState('')
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

  const fetchPrayerStatus = async ({ silent = false } = {}) => {
    const headers = getAuthHeaders()
    if (!headers) {
      if (!silent) {
        setStatusError('Sesi login tidak ditemukan. Silakan login ulang.')
        setStatusLoading(false)
      }
      return
    }

    if (!silent) {
      setStatusLoading(true)
    }

    try {
      const { data } = await api.get('/waktu-sholat/status', {
        headers,
        params: {
          timestamp: new Date().toISOString(),
        },
      })
      if (!data?.success || !data?.data) {
        throw new Error('Respons status waktu sholat tidak valid.')
      }

      setPrayerStatus(data.data)
      setStatusError('')
    } catch (requestError) {
      const apiMessage =
        requestError?.response?.data?.message ||
        requestError?.message ||
        'Gagal memuat status waktu sholat.'
      if (!silent) {
        setStatusError(apiMessage)
      }
    } finally {
      if (!silent) {
        setStatusLoading(false)
      }
    }
  }

  useEffect(() => {
    void fetchPrayerTimes()
    void fetchPrayerStatus()

    const timer = window.setInterval(() => {
      void fetchPrayerStatus({ silent: true })
    }, 30_000)

    return () => {
      window.clearInterval(timer)
    }
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
            <h2>Status Waktu Sholat Saat Ini</h2>
            <p className="api-note">
              Indikator ini refresh otomatis tiap 30 detik untuk membantu debugging sesi aktif backend.
            </p>
          </div>
        </div>

        {statusError ? <p className="alert error">{statusError}</p> : null}

        {statusLoading ? (
          <div className="empty-state compact">
            <p>Memuat status waktu sholat...</p>
          </div>
        ) : prayerStatus ? (
          <div className="settings-grid">
            <article className="setting-card">
              <div className="setting-card-head">
                <h2>{prayerStatus.is_active ? 'Sesi Aktif' : 'Belum Ada Sesi Aktif'}</h2>
                <span className={`status-chip ${prayerStatus.is_active ? 'prayer' : 'info'}`}>
                  {prayerStatus.is_active ? 'Aktif' : 'Menunggu'}
                </span>
              </div>
              <p>
                {prayerStatus.is_active
                  ? `${prayerStatus.active_prayer?.nama_sholat || 'Sesi'} sedang berlangsung.`
                  : 'Belum masuk ke rentang waktu sholat aktif.'}
              </p>
              <p className="api-note">
                Waktu acuan: {formatDateTime(prayerStatus.reference_timestamp)}
              </p>
              {prayerStatus.active_prayer ? (
                <p className="api-note">
                  Fase: {prayerStatus.active_prayer.phase === 'menuju_iqamah' ? 'sebelum iqamah' : 'setelah iqamah'}.
                  Sesi berakhir pukul {(prayerStatus.active_prayer.waktu_selesai || '').slice(0, 5)}.
                </p>
              ) : null}
            </article>

            <article className="setting-card">
              <div className="setting-card-head">
                <h2>Jadwal Berikutnya</h2>
                <span className="status-chip info">Selanjutnya</span>
              </div>
              {prayerStatus.next_prayer ? (
                <>
                  <p>
                    {prayerStatus.next_prayer.nama_sholat} mulai pukul{' '}
                    {(prayerStatus.next_prayer.waktu_adzan || '').slice(0, 5)}.
                  </p>
                  <p className="api-note">
                    Referensi tanggal: {prayerStatus.next_prayer.reference_date || '-'}
                  </p>
                </>
              ) : (
                <p className="api-note">Belum ada jadwal berikutnya yang bisa ditampilkan.</p>
              )}
            </article>
          </div>
        ) : (
          <div className="empty-state compact">
            <p>Status waktu sholat belum tersedia.</p>
          </div>
        )}
      </section>

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
