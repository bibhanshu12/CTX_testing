export interface ColumnDef {
  name: string;
  type: string;
  key: boolean;
}

export interface EntityMetadata {
  name: string;
  namespace: string;
  key: string;
  columns: ColumnDef[];
  source: any;
}

export interface EntityListItem {
  name: string;
  path: string;
}

export interface EntityListResponse {
  data_source: string;
  entities: EntityListItem[];
}

export interface RecordsResponse {
  entity_set: string;
  count: number;
  value: any[];
}

export interface ConnectionStatus {
  data_source: string;
  connected: boolean;
  message: string;
  details: any;
}

export interface ImportMetadataResponse {
  valid: boolean;
  entity_sets_found: string[];
  ctx_entities_found: string[];
  additional_ctx_discovered?: string[];
  message: string;
}

export interface ApiError {
  error: string;
  message: string;
  details: any;
}

export type DataSource = "seed" | "odata";
