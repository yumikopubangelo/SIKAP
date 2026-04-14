import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { statusChartColors, trendLineSeries } from '../config'
import { formatCellValue } from '../utils/formatters'

export default function DashboardCharts({ charts }) {
  const attendanceTrend = charts?.attendance_trend || {
    title: 'Trend Kehadiran',
    rows: [],
    note: 'Belum ada data trend.',
  }
  const statusDistribution = charts?.status_distribution || {
    title: 'Distribusi Status',
    rows: [],
    note: 'Belum ada distribusi status.',
  }

  const hasTrendData = attendanceTrend.rows?.some(
    (row) => row.total || row.tepat_waktu || row.terlambat,
  )
  const hasStatusData = statusDistribution.rows?.some((row) => row.value > 0)

  return (
    <section className="chart-grid">
      <section className="dashboard-panel chart-panel">
        <div className="panel-header">
          <div>
            <h2>{attendanceTrend.title}</h2>
            <p className="api-note">Grafik ini membantu melihat naik turun kehadiran dalam beberapa hari terakhir.</p>
          </div>
        </div>

        {hasTrendData ? (
          <div className="chart-shell">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={attendanceTrend.rows}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d9e6ef" />
                <XAxis dataKey="label" stroke="#587082" tickLine={false} axisLine={false} />
                <YAxis
                  allowDecimals={false}
                  stroke="#587082"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  formatter={(value, name) => [
                    formatCellValue(value),
                    trendLineSeries.find((item) => item.key === name)?.label || name,
                  ]}
                  labelFormatter={(label, payload) => payload?.[0]?.payload?.date || label}
                />
                <Legend
                  formatter={(value) =>
                    trendLineSeries.find((item) => item.key === value)?.label || value
                  }
                />
                {trendLineSeries.map((line) => (
                  <Line
                    key={line.key}
                    type="monotone"
                    dataKey={line.key}
                    stroke={line.color}
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="empty-state compact">
            <p>{attendanceTrend.note || 'Belum ada data trend untuk ditampilkan.'}</p>
          </div>
        )}
      </section>

      <section className="dashboard-panel chart-panel">
        <div className="panel-header">
          <div>
            <h2>{statusDistribution.title}</h2>
            <p className="api-note">Bagian ini menunjukkan status absensi yang paling sering muncul pada periode yang sama.</p>
          </div>
        </div>

        {hasStatusData ? (
          <>
            <div className="chart-shell">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={statusDistribution.rows}
                    dataKey="value"
                    nameKey="label"
                    innerRadius={60}
                    outerRadius={92}
                    paddingAngle={3}
                  >
                    {statusDistribution.rows.map((entry) => (
                      <Cell
                        key={entry.status}
                        fill={statusChartColors[entry.status] || '#0d5ca2'}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, _name, item) => [formatCellValue(value), item?.payload?.label]} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-stat-list">
              {statusDistribution.rows.map((item) => (
                <div key={item.status} className="chart-stat">
                  <span
                    className="chart-dot"
                    style={{ backgroundColor: statusChartColors[item.status] || '#0d5ca2' }}
                  />
                  <span>{item.label}</span>
                  <strong>{formatCellValue(item.value)}</strong>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="empty-state compact">
            <p>{statusDistribution.note || 'Belum ada distribusi status untuk ditampilkan.'}</p>
          </div>
        )}
      </section>
    </section>
  )
}
