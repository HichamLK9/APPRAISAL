import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  fetchDomainBySector,
  fetchEntitiesPerDay,
  fetchSectorDistribution,
  fetchTopJurisdictions,
} from "../api/client";
import type {
  DomainAvailabilityBySector,
  EntitiesPerDay,
  JurisdictionStat,
  SectorDistribution,
} from "../types";

const SECTOR_COLORS: Record<string, string> = {
  fintech: "#34d399",
  artificial_intelligence: "#a78bfa",
  digital_health_biotech: "#22d3ee",
  cybersecurity: "#f87171",
  saas_cloud_infra: "#60a5fa",
  ecommerce_marketplaces: "#fb923c",
  real_estate_proptech: "#fbbf24",
  cleantech_energy: "#a3e635",
  fitness_wellness: "#f472b6",
  education_creator: "#38bdf8",
  other: "#4b5563",
};

const SECTOR_LABELS: Record<string, string> = {
  fintech: "Fintech",
  artificial_intelligence: "AI",
  digital_health_biotech: "Health",
  cybersecurity: "Cybersec",
  saas_cloud_infra: "SaaS",
  ecommerce_marketplaces: "E-com",
  real_estate_proptech: "PropTech",
  cleantech_energy: "CleanTech",
  fitness_wellness: "Fitness",
  education_creator: "Edu",
  other: "Other",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-500">
        {title}
      </h3>
      {children}
    </div>
  );
}

interface Props {
  dateFrom?: string;
  dateTo?: string;
}

export default function Analytics({ dateFrom, dateTo }: Props) {
  const [perDay, setPerDay] = useState<EntitiesPerDay[]>([]);
  const [sectors, setSectors] = useState<SectorDistribution[]>([]);
  const [domains, setDomains] = useState<DomainAvailabilityBySector[]>([]);
  const [jurisdictions, setJurisdictions] = useState<JurisdictionStat[]>([]);

  useEffect(() => {
    fetchEntitiesPerDay(30).then(setPerDay).catch(() => setPerDay([]));
    fetchSectorDistribution(dateFrom, dateTo).then(setSectors).catch(() => setSectors([]));
    fetchDomainBySector(dateFrom, dateTo).then(setDomains).catch(() => setDomains([]));
    fetchTopJurisdictions(dateFrom, dateTo).then(setJurisdictions).catch(() => setJurisdictions([]));
  }, [dateFrom, dateTo]);

  const tickStyle = { fill: "#6b7280", fontSize: 11 };
  const tooltipStyle = {
    backgroundColor: "#111827",
    border: "1px solid #374151",
    borderRadius: 8,
    fontSize: 12,
    color: "#e5e7eb",
  };

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      {/* Entities per day */}
      <Section title="Entities / day (last 30 days)">
        {perDay.length === 0 ? (
          <Empty />
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={perDay} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="date"
                tick={tickStyle}
                tickFormatter={(d) => d.slice(5)}
                interval="preserveStartEnd"
              />
              <YAxis tick={tickStyle} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Section>

      {/* Sector distribution */}
      <Section title="Sector distribution">
        {sectors.length === 0 ? (
          <Empty />
        ) : (
          <div className="flex items-center gap-4">
            <ResponsiveContainer width="55%" height={220}>
              <PieChart>
                <Pie
                  data={sectors}
                  dataKey="count"
                  nameKey="sector"
                  cx="50%"
                  cy="50%"
                  outerRadius={85}
                  paddingAngle={2}
                >
                  {sectors.map((entry) => (
                    <Cell
                      key={entry.sector}
                      fill={SECTOR_COLORS[entry.sector] ?? "#4b5563"}
                    />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
            <ul className="flex flex-1 flex-col gap-1.5 text-xs">
              {sectors.slice(0, 8).map((s) => (
                <li key={s.sector} className="flex items-center gap-2">
                  <span
                    className="h-2 w-2 flex-shrink-0 rounded-full"
                    style={{ background: SECTOR_COLORS[s.sector] ?? "#4b5563" }}
                  />
                  <span className="flex-1 text-gray-400">
                    {SECTOR_LABELS[s.sector] ?? s.sector}
                  </span>
                  <span className="font-semibold text-gray-300">{s.count}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Section>

      {/* .com availability by sector */}
      <Section title="% .com available by sector">
        {domains.length === 0 ? (
          <Empty />
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={domains}
              layout="vertical"
              margin={{ top: 0, right: 30, left: 60, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
              <XAxis
                type="number"
                domain={[0, 100]}
                tick={tickStyle}
                tickFormatter={(v) => `${v}%`}
              />
              <YAxis
                type="category"
                dataKey="sector"
                tick={tickStyle}
                tickFormatter={(s) => SECTOR_LABELS[s] ?? s}
                width={58}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(v) => [`${v}%`, "Available"]}
              />
              <Bar dataKey="pct_available" fill="#34d399" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Section>

      {/* Top jurisdictions */}
      <Section title="Top jurisdictions">
        {jurisdictions.length === 0 ? (
          <Empty />
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={jurisdictions}
              margin={{ top: 0, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="jurisdiction" tick={tickStyle} />
              <YAxis tick={tickStyle} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="#a78bfa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Section>
    </div>
  );
}

function Empty() {
  return (
    <div className="flex h-[220px] items-center justify-center text-sm text-gray-600">
      No data — run a collection first.
    </div>
  );
}
