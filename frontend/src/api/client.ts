import axios, { AxiosInstance } from "axios";
import type {
  EntityListResponse,
  EntityMetadata,
  RecordsResponse,
  ConnectionStatus,
  ImportMetadataResponse,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: { Accept: "application/json" },
    });
  }

  async listEntities(): Promise<EntityListResponse> {
    const res = await this.client.get<EntityListResponse>("/ctx/entities");
    return res.data;
  }

  async getMetadata(entitySet: string): Promise<EntityMetadata> {
    const res = await this.client.get<EntityMetadata>(
      `/ctx/entities/${encodeURIComponent(entitySet)}/metadata`
    );
    return res.data;
  }

  async getRecords(
    entitySet: string,
    params?: { top?: number; skip?: number; filter?: string; orderby?: string }
  ): Promise<RecordsResponse> {
    const query: Record<string, string | number> = {};
    if (params?.top !== undefined) query["$top"] = params.top;
    if (params?.skip !== undefined) query["$skip"] = params.skip;
    if (params?.filter) query["$filter"] = params.filter;
    if (params?.orderby) query["$orderby"] = params.orderby;
    const res = await this.client.get<RecordsResponse>(
      `/ctx/entities/${encodeURIComponent(entitySet)}/records`,
      { params: query }
    );
    return res.data;
  }

  async connectionStatus(): Promise<ConnectionStatus> {
    const res = await this.client.get<ConnectionStatus>("/ctx/status");
    return res.data;
  }

  async importMetadata(content: string): Promise<ImportMetadataResponse> {
    const res = await this.client.post<ImportMetadataResponse>(
      "/ctx/import/metadata",
      { content }
    );
    return res.data;
  }

  async importMetadataFile(file: File): Promise<ImportMetadataResponse & { filename: string; size_bytes: number }> {
    const form = new FormData();
    form.append("file", file);
    const res = await this.client.post<ImportMetadataResponse & { filename: string; size_bytes: number }>(
      "/ctx/import/metadata/file",
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return res.data;
  }
}

export const api = new ApiClient();
