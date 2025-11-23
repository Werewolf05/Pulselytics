import React from 'react';

function formatNumber(value) {
  if (value == null || isNaN(value)) return '-';
  const n = Number(value);
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
  return n.toLocaleString();
}

export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div style={{
      background: 'white',
      border: '1px solid #e2e8f0',
      borderRadius: 8,
      padding: '10px 12px',
      boxShadow: '0 8px 24px rgba(2, 6, 23, 0.08)'
    }}>
      {label != null && (
        <div style={{ fontSize: 12, color: '#475569', marginBottom: 6 }}>{label}</div>
      )}
      <div style={{ display: 'grid', gap: 6 }}>
        {payload.map((entry, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              width: 10,
              height: 10,
              borderRadius: 3,
              background: entry.color || '#6366f1',
              display: 'inline-block'
            }}/>
            <span style={{ fontSize: 12, color: '#334155' }}>
              {entry.name || entry.dataKey}
            </span>
            <span style={{ marginLeft: 'auto', fontWeight: 600, color: '#0f172a' }}>
              {formatNumber(entry.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
