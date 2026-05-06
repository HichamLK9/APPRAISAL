export interface Entity {
  id: number;
  name: string;
  description: string;
  date: string;
  jurisdiction: string;
  sector: string;
  raw_sector: string;
  entity_type: string;
  source: string;
  prospect_score: number;
  domain_com: string;
  domain_available: boolean | null;
  created_at: string;
}

export interface PaginatedEntities {
  total: number;
  page: number;
  per_page: number;
  items: Entity[];
}

export interface SectorDistribution {
  sector: string;
  count: number;
}

export interface EntitiesPerDay {
  date: string;
  count: number;
}

export interface DomainAvailabilityBySector {
  sector: string;
  total: number;
  available: number;
  pct_available: number;
}

export interface JurisdictionStat {
  jurisdiction: string;
  count: number;
  avg_score: number;
}

export interface Overview {
  total_entities: number;
  hot_prospects: number;
  with_com_available: number;
  avg_prospect_score: number;
}

export interface SectorLabel {
  key: string;
  label: string;
}

export interface Filters {
  date: string;
  date_from: string;
  date_to: string;
  sector: string[];
  jurisdiction: string[];
  min_score: number;
  domain_available: boolean | null;
  q: string;
  sort_by: string;
  sort_dir: string;
}
