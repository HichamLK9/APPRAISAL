import { useCallback, useEffect, useState } from "react";
import {
  exportCsvUrl,
  fetchEntities,
  fetchHotProspects,
  fetchOverview,
  fetchSectors,
} from "../api/client";
import type { Entity, Filters, Overview, PaginatedEntities, SectorLabel } from "../types";
import Analytics from "./Analytics";
import EntityTable from "./EntityTable";
import FiltersPanel from "./Filters";
import ProspectBadge from "./ProspectBadge";
import StatsCard from "./StatsCard";

const DEFAULT_FILTERS: Filters = {
  date: new Date().toISOString().slice(0, 10),
  date_from: "",
  date_to: "",
  sector: [],
  jurisdiction: [],
  min_score: 0,
  domain_available: null,
  q: "",
  sort_by: "prospect_score",
  sort_dir: "desc",
};

type Tab = "entities" | "hot" | "analytics";

export default function Dashboard() {
  const [tab, setTab] = useState<Tab>("entities");
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [paginated, setPaginated] = useState<PaginatedEntities>({
    total: 0,
    page: 1,
    per_page: 50,
    items: [],
  });
  const [hotProspects, setHotProspects] = useState<Entity[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [sectors, setSectors] = useState<SectorLabel[]>([]);
  const [loading, setLoading] = useState(false);

  // Load sectors once
  useEffect(() => {
    fetchSectors().then(setSectors).catch(() => {});
  }, []);

  // Load overview
  useEffect(() => {
    const from = filters.date_from || filters.date || undefined;
    const to = filters.date_to || filters.date || undefined;
    fetchOverview(from, to)
      .then(setOverview)
      .catch(() => setOverview(null));
  }, [filters.date, filters.date_from, filters.date_to]);

  // Load entities
  useEffect(() => {
    if (tab !== "entities") return;
    setLoading(true);
    fetchEntities(filters, page, 50)
      .then(setPaginated)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filters, page, tab]);

  // Load hot prospects
  useEffect(() => {
    if (tab !== "hot") return;
    fetchHotProspects(60, 30)
      .then(setHotProspects)
      .catch(() => setHotProspects([]));
  }, [tab]);

  const updateFilters = useCallback((partial: Partial<Filters>) => {
    setFilters((f) => ({ ...f, ...partial }));
    setPage(1);
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
    setPage(1);
  }, []);

  const csvUrl = exportCsvUrl(filters);

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950 px-6 py-4">
        <div className="mx-auto flex max-w-screen-2xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-lg">
              📡
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-white">Entity Radar</h1>
              <p className="text-[11px] text-gray-500">USA Business Tracker · SaaS</p>
            </div>
          </div>
          <nav className="flex gap-1">
            {(["entities", "hot", "analytics"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`rounded-lg px-4 py-1.5 text-xs font-medium capitalize transition-colors ${
                  tab === t
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:bg-gray-800 hover:text-white"
                }`}
              >
                {t === "hot" ? "🔥 Hot Prospects" : t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* KPI row */}
      {overview && (
        <div className="border-b border-gray-800 bg-gray-950 px-6 py-4">
          <div className="mx-auto grid max-w-screen-2xl grid-cols-2 gap-3 sm:grid-cols-4">
            <StatsCard
              label="Total entities"
              value={overview.total_entities.toLocaleString()}
            />
            <StatsCard
              label="Hot prospects"
              value={overview.hot_prospects.toLocaleString()}
              accent="text-red-400"
            />
            <StatsCard
              label=".com available"
              value={overview.with_com_available.toLocaleString()}
              accent="text-emerald-400"
            />
            <StatsCard
              label="Avg score"
              value={overview.avg_prospect_score}
              sub="out of 100"
              accent="text-yellow-400"
            />
          </div>
        </div>
      )}

      {/* Main */}
      <div className="mx-auto flex w-full max-w-screen-2xl flex-1 gap-6 px-6 py-6">
        {/* Sidebar filters (only on entities tab) */}
        {tab === "entities" && (
          <div className="w-64 flex-shrink-0">
            <FiltersPanel
              filters={filters}
              sectors={sectors}
              onChange={updateFilters}
              onReset={resetFilters}
            />
          </div>
        )}

        {/* Content */}
        <div className="min-w-0 flex-1">
          {tab === "entities" && (
            <>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-300">
                  Entities
                  {filters.date && (
                    <span className="ml-2 font-normal text-gray-500">
                      · {filters.date}
                    </span>
                  )}
                </h2>
                <a
                  href={csvUrl}
                  download
                  className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-blue-700"
                >
                  ↓ Export CSV
                </a>
              </div>
              <EntityTable
                data={paginated.items}
                total={paginated.total}
                page={page}
                perPage={50}
                onPageChange={setPage}
                loading={loading}
              />
            </>
          )}

          {tab === "hot" && (
            <div>
              <h2 className="mb-4 text-sm font-semibold text-gray-300">
                🔥 Hot Prospects
                <span className="ml-2 font-normal text-gray-500">
                  · score ≥ 60, last 30 days
                </span>
              </h2>
              {hotProspects.length === 0 ? (
                <div className="rounded-xl border border-gray-800 p-10 text-center text-gray-600">
                  No hot prospects found. Run a collection or lower the score threshold.
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {hotProspects.map((e) => (
                    <ProspectCard key={e.id} entity={e} />
                  ))}
                </div>
              )}
            </div>
          )}

          {tab === "analytics" && (
            <Analytics
              dateFrom={filters.date_from || filters.date || undefined}
              dateTo={filters.date_to || filters.date || undefined}
            />
          )}
        </div>
      </div>
    </div>
  );
}

function ProspectCard({ entity: e }: { entity: Entity }) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-gray-800 bg-gray-900 p-4 transition-colors hover:border-gray-700">
      <div className="flex items-start justify-between gap-2">
        <h3 className="flex-1 text-sm font-semibold leading-tight text-gray-100">
          {e.name}
        </h3>
        <ProspectBadge score={e.prospect_score} />
      </div>

      <div className="flex flex-wrap gap-2 text-xs">
        <span className="rounded border border-gray-700 bg-gray-800 px-1.5 py-0.5 font-mono text-gray-400">
          {e.jurisdiction}
        </span>
        <span className="rounded-full bg-gray-800 px-2 py-0.5 text-gray-400">
          {e.sector}
        </span>
        <span className="font-mono text-gray-500">{e.date}</span>
      </div>

      {e.domain_com && (
        <div className="flex items-center gap-1.5 text-xs">
          <span
            className={`h-2 w-2 rounded-full ${
              e.domain_available === true
                ? "bg-emerald-500"
                : e.domain_available === false
                  ? "bg-red-500"
                  : "bg-gray-600"
            }`}
          />
          <span className={e.domain_available ? "text-emerald-400" : "text-gray-500"}>
            {e.domain_com}
          </span>
          {e.domain_available === true && (
            <span className="rounded bg-emerald-900/30 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-500">
              AVAILABLE
            </span>
          )}
        </div>
      )}

      {e.description && (
        <p className="line-clamp-2 text-xs text-gray-500">{e.description}</p>
      )}

      <a
        href={e.source}
        target="_blank"
        rel="noreferrer"
        className="mt-auto text-[10px] text-blue-500 hover:text-blue-400 hover:underline"
      >
        Source ↗
      </a>
    </div>
  );
}
