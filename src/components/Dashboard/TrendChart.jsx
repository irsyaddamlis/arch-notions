import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

/**
 * data: array of { date, ihsg, exchange } matching your trend() output
 * (Date, IHSG, $-Exchange columns).
 *
 * NOTE: IHSG (~thousands) and USD/IDR (~tens of thousands) are on very
 * different scales. The original mockup plots both on one 0-40 axis,
 * which only works for placeholder numbers - with real data they need
 * separate axes, so this uses a left axis for IHSG and a right axis for
 * $-Exchange rather than reproducing that mismatch.
 */
export default function TrendChart({ data = [] }) {
  return (
    <div className="w-full h-72">
      <div className="flex items-center gap-6 mb-4">
        <span className="flex items-center gap-2 text-white text-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-[#3B7CF6]" />
          IHSG
        </span>
        <span className="flex items-center gap-2 text-white text-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-[#7BA0F6]" />$ Exchange
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
          <YAxis
            yAxisId="ihsg"
            stroke="#6B7280"
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            yAxisId="exchange"
            orientation="right"
            stroke="#6B7280"
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Line
            yAxisId="ihsg"
            type="monotone"
            dataKey="ihsg"
            stroke="#3B7CF6"
            strokeWidth={2}
            dot={{ r: 3, fill: "#3B7CF6" }}
          />
          <Line
            yAxisId="exchange"
            type="monotone"
            dataKey="exchange"
            stroke="#7BA0F6"
            strokeWidth={2}
            dot={{ r: 3, fill: "#7BA0F6" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
