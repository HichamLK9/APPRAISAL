import clsx from "clsx";
import type { Filters, SectorLabel } from "../types";

interface Props {
  filters: Filters;
  sectors: SectorLabel[];
  onChange: (f: Partial<Filters>) => void;
  onReset: () => void;
}

const JURISDICTIONS = ["HI", "CT", "CA", "WY", "NY", "TX", "FL", "WA", "IL", "CO"];

export default function FiltersPanel({ filters, sectors, onChange, onReset }: Props) {
  function toggleMulti(
    field: "sector" | "jurisdiction",
    value: string
  ) {
    const current = filters[field];
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    onChange({ [field]: next });
  }

  return (
    <aside className="flex flex-col gap-5 rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-400">
          Filters
        </h2>
        <button
          onClick={onReset}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Date mode */}
      <div className="flex flex-col gap-2">
        <label className="text-xs text-gray-500 uppercase tracking-wider">Mode</label>
        <div className="flex gap-2">
          {(["exact", "range"] as const).map((m) => {
            const active = m === "exact" ? !!filters.date : !filters.date;
            return (
              <button
                key={m}
                onClick={() =>
                  onChange(
                    m === "exact"
                      ? { date: new Date().toISOString().slice(0, 10), date_from: "", date_to: "" }
                      : { date: "", date_from: new Date().toISOString().slice(0, 10), date_to: "" }
                  )
                }
                className={clsx(
                  "flex-1 rounded-lg border py-1.5 text-xs font-medium transition-colors",
                  active
                    ? "border-blue-600 bg-blue-600/20 text-blue-400"
                    : "border-gray-700 text-gray-500 hover:border-gray-600"
                )}
              >
                {m === "exact" ? "Single day" : "Date range"}
              </button>
            );
          })}
        </div>
      </div>

      {/* Date inputs */}
      {filters.date ? (
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">Date</label>
          <input
            type="date"
            value={filters.date}
            onChange={(e) => onChange({ date: e.target.value })}
            className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-blue-500 focus:outline-none"
          />
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-500">From</label>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => onChange({ date_from: e.target.value })}
              className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-500">To</label>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => onChange({ date_to: e.target.value })}
              className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* Search */}
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-500">Search</label>
        <input
          type="text"
          placeholder="Name, description…"
          value={filters.q}
          onChange={(e) => onChange({ q: e.target.value })}
          className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-blue-500 focus:outline-none"
        />
      </div>

      {/* Sectors */}
      <div className="flex flex-col gap-2">
        <label className="text-xs text-gray-500 uppercase tracking-wider">Sector</label>
        <div className="flex flex-wrap gap-1.5">
          {sectors.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => toggleMulti("sector", key)}
              className={clsx(
                "rounded-full border px-2.5 py-0.5 text-xs transition-colors",
                filters.sector.includes(key)
                  ? "border-blue-600 bg-blue-600/20 text-blue-400"
                  : "border-gray-700 text-gray-500 hover:border-gray-500 hover:text-gray-300"
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Jurisdictions */}
      <div className="flex flex-col gap-2">
        <label className="text-xs text-gray-500 uppercase tracking-wider">Jurisdiction</label>
        <div className="flex flex-wrap gap-1.5">
          {JURISDICTIONS.map((j) => (
            <button
              key={j}
              onClick={() => toggleMulti("jurisdiction", j)}
              className={clsx(
                "rounded-full border px-2.5 py-0.5 text-xs font-mono transition-colors",
                filters.jurisdiction.includes(j)
                  ? "border-emerald-600 bg-emerald-600/20 text-emerald-400"
                  : "border-gray-700 text-gray-500 hover:border-gray-500 hover:text-gray-300"
              )}
            >
              {j}
            </button>
          ))}
        </div>
      </div>

      {/* Min score */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <label className="text-xs text-gray-500 uppercase tracking-wider">Min score</label>
          <span className="text-xs font-semibold text-blue-400">{filters.min_score}</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={filters.min_score}
          onChange={(e) => onChange({ min_score: Number(e.target.value) })}
          className="h-1.5 w-full cursor-pointer accent-blue-500"
        />
        <div className="flex justify-between text-[10px] text-gray-600">
          <span>0</span><span>50</span><span>100</span>
        </div>
      </div>

      {/* Domain available */}
      <div className="flex flex-col gap-2">
        <label className="text-xs text-gray-500 uppercase tracking-wider">.com status</label>
        <div className="flex gap-2">
          {([null, true, false] as const).map((val) => {
            const label = val === null ? "All" : val ? "Available" : "Taken";
            const active = filters.domain_available === val;
            return (
              <button
                key={String(val)}
                onClick={() => onChange({ domain_available: val })}
                className={clsx(
                  "flex-1 rounded-lg border py-1.5 text-xs font-medium transition-colors",
                  active
                    ? "border-blue-600 bg-blue-600/20 text-blue-400"
                    : "border-gray-700 text-gray-500 hover:border-gray-600"
                )}
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
