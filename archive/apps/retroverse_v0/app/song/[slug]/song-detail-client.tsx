"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

/**
 * Generates a conceptual chart history from peak position and weeks on chart.
 * The dataset doesn't include week-by-week positions, so we simulate a typical
 * chart run: start at peak, gradually decline until off the chart.
 */
function buildChartData(
  peakPosition: number,
  weeksOnChart: number
): { week: number; position: number }[] {
  const points: { week: number; position: number }[] = []
  const steps = Math.min(weeksOnChart, 52)

  for (let i = 0; i <= steps; i++) {
    const t = i / steps
    const position = Math.round(
      peakPosition + (101 - peakPosition) * Math.pow(t, 1.2)
    )
    points.push({ week: Math.round((i * weeksOnChart) / steps), position })
  }

  if (weeksOnChart > 0 && points[points.length - 1].position < 101) {
    points.push({ week: weeksOnChart, position: 101 })
  }

  return points
}

interface SongDetailClientProps {
  peakPosition: number
  weeksOnChart: number
}

export function SongDetailClient({
  peakPosition,
  weeksOnChart,
}: SongDetailClientProps) {
  const data = buildChartData(peakPosition, weeksOnChart)

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#9FCBCB"
            opacity={0.4}
          />
          <XAxis
            dataKey="week"
            tick={{ fill: "#5C5854", fontSize: 11 }}
            tickFormatter={(v) => `Wk ${v}`}
          />
          <YAxis
            domain={[1, 101]}
            reversed
            tick={{ fill: "#5C5854", fontSize: 11 }}
            tickFormatter={(v) => (v <= 100 ? `#${v}` : "Off")}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFDF9",
              border: "2px solid #9FCBCB",
              borderRadius: "8px",
            }}
            formatter={(value: number) => [
              value <= 100 ? `#${value}` : "Off chart",
              "Position",
            ]}
            labelFormatter={(label) => `Week ${label}`}
          />
          <Line
            type="monotone"
            dataKey="position"
            stroke="#E7927F"
            strokeWidth={2}
            dot={{ fill: "#E7927F", r: 2 }}
            activeDot={{ r: 4, fill: "#E7CC7C" }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-muted-foreground mt-2">
        Conceptual chart run (week-by-week data not in dataset)
      </p>
    </div>
  )
}
