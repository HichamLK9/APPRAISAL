import axios from "axios";
import type {
  DomainAvailabilityBySector,
  EntitiesPerDay,
  Entity,
  Filters,
  JurisdictionStat,
  Overview,
  PaginatedEntities,
  SectorDistribution,
  SectorLabel,
} from "../types";

const api = axios.create({ baseURL: "/api" });

function buildParams(filters: Partial<Filters>, extras: Record<string, unknown> = {}) {
  const params: Record<string, unknown> = { ...extras };
  if (filters.date) params.date = filters.date;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  if (filters.sector?.length) params.sector = filters.sector;
  if (filters.jurisdiction?.length) params.jurisdiction = filters.jurisdiction;
  if (filters.min_score) params.min_score = filters.min_score;
  if (filters.domain_available !== null && filters.domain_available !== undefined)
    params.domain_available = filters.domain_available;
  if (filters.q) params.q = filters.q;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_dir) params.sort_dir = filters.sort_dir;
  return params;
}

export async function fetchEntities(
  filters: Partial<Filters>,
  page = 1,
  perPage = 50
): Promise<PaginatedEntities> {
  const params = buildParams(filters, { page, per_page: perPage });
  const { data } = await api.get<PaginatedEntities>("/entities", { params });
  return data;
}

export async function fetchEntity(id: number): Promise<Entity> {
  const { data } = await api.get<Entity>(`/entities/${id}`);
  return data;
}

export function exportCsvUrl(filters: Partial<Filters>): string {
  const params = new URLSearchParams();
  if (filters.date) params.set("date", filters.date);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  filters.sector?.forEach((s) => params.append("sector", s));
  filters.jurisdiction?.forEach((j) => params.append("jurisdiction", j));
  if (filters.min_score) params.set("min_score", String(filters.min_score));
  if (filters.domain_available !== null && filters.domain_available !== undefined)
    params.set("domain_available", String(filters.domain_available));
  if (filters.q) params.set("q", filters.q);
  return `/api/entities/export?${params.toString()}`;
}

export async function fetchOverview(dateFrom?: string, dateTo?: string): Promise<Overview> {
  const { data } = await api.get<Overview>("/analytics/overview", {
    params: { date_from: dateFrom, date_to: dateTo },
  });
  return data;
}

export async function fetchEntitiesPerDay(days = 30): Promise<EntitiesPerDay[]> {
  const { data } = await api.get<EntitiesPerDay[]>("/analytics/entities-per-day", {
    params: { days },
  });
  return data;
}

export async function fetchSectorDistribution(
  dateFrom?: string,
  dateTo?: string
): Promise<SectorDistribution[]> {
  const { data } = await api.get<SectorDistribution[]>("/analytics/sector-distribution", {
    params: { date_from: dateFrom, date_to: dateTo },
  });
  return data;
}

export async function fetchDomainBySector(
  dateFrom?: string,
  dateTo?: string
): Promise<DomainAvailabilityBySector[]> {
  const { data } = await api.get<DomainAvailabilityBySector[]>(
    "/analytics/domain-availability-by-sector",
    { params: { date_from: dateFrom, date_to: dateTo } }
  );
  return data;
}

export async function fetchTopJurisdictions(
  dateFrom?: string,
  dateTo?: string
): Promise<JurisdictionStat[]> {
  const { data } = await api.get<JurisdictionStat[]>("/analytics/top-jurisdictions", {
    params: { date_from: dateFrom, date_to: dateTo },
  });
  return data;
}

export async function fetchHotProspects(
  minScore = 60,
  days = 30
): Promise<Entity[]> {
  const { data } = await api.get<Entity[]>("/analytics/hot-prospects", {
    params: { min_score: minScore, days },
  });
  return data;
}

export async function fetchSectors(): Promise<SectorLabel[]> {
  const { data } = await api.get<SectorLabel[]>("/analytics/sectors");
  return data;
}
