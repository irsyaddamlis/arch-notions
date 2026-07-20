import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function TrendChart({ data = [] }) {
  return (
    <div className="w-full h-72">
      {/* Legend header split to align left legend with left Y-axis, right legend with right Y-axis */}
      <div className="flex items-center justify-between mb-4">
        <span className="flex items-center gap-2 text-white text-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-[#3B7CF6]" />
          IHSG
        </span>
        <span className="flex items-center gap-2 text-white text-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-[#7BA0F6]" />
          $ Exchange
        </span>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#1F2937" vertical={false} />
          
          <XAxis
            dataKey="date"
            stroke="#6B7280"
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={{ stroke: "#374151" }}
            tickLine={false}
          />

          {/* Left Y-Axis for IHSG with flexible dynamic range */}
          <YAxis
            yAxisId="ihsg"
            stroke="#6B7280"
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            domain={['dataMin - 100', 'dataMax + 100']}
          />

          {/* Right Y-Axis for Exchange with flexible dynamic range */}
          <YAxis
            yAxisId="exchange"
            orientation="right"
            stroke="#6B7280"
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            domain={['dataMin - 100', 'dataMax + 100']}
          />

          {/* Pop-up Tooltip on Mouse Hover */}
          <Tooltip
            contentStyle={{
              backgroundColor: "#111827",
              borderColor: "#374151",
              borderRadius: "8px",
              color: "#FFF",
            }}
            labelStyle={{ color: "#9CA3AF", fontWeight: "bold" }}
          />

          <Line
            yAxisId="ihsg"
            type="monotone"
            dataKey="ihsg"
            name="IHSG"
            stroke="#3B7CF6"
            strokeWidth={2}
            dot={{ r: 3, fill: "#3B7CF6" }}
            activeDot={{ r: 6 }}
          />
          <Line
            yAxisId="exchange"
            type="monotone"
            dataKey="exchange"
            name="$ Exchange"
            stroke="#7BA0F6"
            strokeWidth={2}
            dot={{ r: 3, fill: "#7BA0F6" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}