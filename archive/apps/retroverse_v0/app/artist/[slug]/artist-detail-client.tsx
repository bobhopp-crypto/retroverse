"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

interface ArtistDetailClientProps {
  decades: { decade: string; count: number }[]
}

export function ArtistDetailClient({ decades }: ArtistDetailClientProps) {
  const colors = ["#9FCBCB", "#A7C9B7", "#E7927F", "#E7CC7C", "#8FBFBE"]

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={decades}
          margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#9FCBCB"
            opacity={0.4}
          />
          <XAxis
            dataKey="decade"
            tick={{ fill: "#5C5854", fontSize: 11 }}
          />
          <YAxis
            tick={{ fill: "#5C5854", fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFDF9",
              border: "2px solid #9FCBCB",
              borderRadius: "8px",
            }}
            formatter={(value: number) => [value, "Songs"]}
          />
          <Bar
            dataKey="count"
            fill="#9FCBCB"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
