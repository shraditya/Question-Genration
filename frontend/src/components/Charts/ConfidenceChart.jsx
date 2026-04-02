import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function ConfidenceChart({ mcqs }) {
  // Calculate distribution
  const distribution = {
    'Low (0-60%)': 0,
    'Medium (60-80%)': 0,
    'High (80-100%)': 0
  };

  mcqs.forEach(mcq => {
    const confidence = mcq.confidence || 0;
    const score = confidence > 1 ? confidence : confidence * 100;

    if (score < 60) distribution['Low (0-60%)']++;
    else if (score < 80) distribution['Medium (60-80%)']++;
    else distribution['High (80-100%)']++;
  });

  const data = Object.entries(distribution).map(([range, count]) => ({
    range: range.split(' ')[0], // Short label
    fullRange: range,
    count,
    percentage: mcqs.length > 0 ? ((count / mcqs.length) * 100).toFixed(1) : 0
  }));

  const COLORS = {
    'Low': '#ef4444',
    'Medium': '#f59e0b',
    'High': '#10b981'
  };

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload[0]) return null;

    return (
      <div className="bg-white p-3 rounded-lg shadow-xl border border-gray-200">
        <p className="font-semibold text-gray-900">{payload[0].payload.fullRange}</p>
        <p className="text-gray-600 mt-1">
          <span className="font-bold text-lg">{payload[0].value}</span> questions
        </p>
        <p className="text-gray-500 text-sm">
          {payload[0].payload.percentage}% of total
        </p>
      </div>
    );
  };

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="range"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }} />
          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.range]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4">
        {Object.entries(COLORS).map(([label, color]) => (
          <div key={label} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
            <span className="text-sm text-gray-600">{label} Confidence</span>
          </div>
        ))}
      </div>
    </div>
  );
}
