import { useState, useEffect, useCallback } from "react";
import type {
  EntityListResponse,
  EntityMetadata,
  RecordsResponse,
  ConnectionStatus,
  ImportMetadataResponse,
} from "./types";
import { api } from "./api/client";
import { Sidebar } from "./components/Sidebar";
import { MetadataPanel } from "./components/MetadataPanel";
import { TryItPanel } from "./components/TryItPanel";
import { ResponsePanel } from "./components/ResponsePanel";
import { DataTable } from "./components/DataTable";
import { SourceSelector } from "./components/SourceSelector";
import { ImportSection } from "./components/ImportSection";

export default function App() {
  const [entitiesResp, setEntitiesResp] = useState<EntityListResponse | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<EntityMetadata | null>(null);
  const [records, setRecords] = useState<RecordsResponse | null>(null);
  const [statusResp, setStatusResp] = useState<ConnectionStatus | null>(null);
  const [respStatus, setRespStatus] = useState<number | null>(null);
  const [respJson, setRespJson] = useState<any>(null);
  const [respError, setRespError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState("seed");

  const fetchEntities = useCallback(async () => {
    try {
      const data = await api.listEntities();
      setEntitiesResp(data);
      if (data.entities.length > 0 && !selected) {
        setSelected(data.entities[0].name);
      }
    } catch (e: any) {
      console.error("Failed to list entities", e);
    }
  }, [selected]);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.connectionStatus();
      setStatusResp(data);
      setDataSource(data.data_source === "odata" ? "odata" : "seed");
    } catch (e: any) {
      console.error("Failed to get status", e);
    }
  }, []);

  useEffect(() => {
    fetchEntities();
    fetchStatus();
  }, [fetchEntities, fetchStatus]);

  const handleSelect = (name: string) => {
    setSelected(name);
    setRecords(null);
    setRespStatus(null);
    setRespJson(null);
    setRespError(null);
  };

  useEffect(() => {
    if (!selected) return;
    (async () => {
      try {
        const meta = await api.getMetadata(selected);
        setMetadata(meta);
      } catch (e: any) {
        setRespError(e.response?.data?.message || e.message || "Failed to load metadata");
      }
    })();
  }, [selected]);

  const handleExecute = async (params: {
    top?: number;
    skip?: number;
    filter?: string;
    orderby?: string;
  }) => {
    if (!selected) return;
    setLoading(true);
    setRespStatus(null);
    setRespJson(null);
    setRespError(null);
    setRecords(null);
    try {
      const data = await api.getRecords(selected, params);
      setRecords(data);
      setRespStatus(200);
      setRespJson(data);
    } catch (e: any) {
      setRespError(e.response?.data?.message || e.message || "Request failed");
      setRespStatus(e.response?.status ?? 500);
    } finally {
      setLoading(false);
    }
  };

  const handleSourceChange = async (source: string) => {
    setDataSource(source);
    // Refresh status to reflect new source config note; backend source is driven by .env CTX_DATA_SOURCE
    await fetchStatus();
  };

  const handleImportComplete = (result: ImportMetadataResponse) => {
    // Informational; import does not change the allowlist
    console.log("Import result", result);
  };

  const entities = entitiesResp?.entities ?? [];

  return (
    <div className="app">
      <Sidebar
        entities={entities}
        selected={selected ?? ""}
        onSelect={handleSelect}
        dataSource={dataSource}
      />
      <main className="main">
        <section className="toolbar">
          <h1>CTX OData Explorer</h1>
          <div className="spacer" />
          <button className="btn btn-outline" onClick={fetchStatus}>Refresh Status</button>
        </section>

        <section className="content">
          <div className="left-col">
            {selected && metadata && (
              <>
                <MetadataPanel metadata={metadata} />
                <TryItPanel
                  entitySet={selected}
                  metadata={metadata}
                  onExecute={handleExecute}
                />
              </>
            )}
            {!selected && <div className="muted">Select a CTX entity set from the sidebar.</div>}
          </div>
          <div className="right-col">
            <SourceSelector
              status={statusResp}
              onSourceChange={handleSourceChange}
              currentSource={dataSource}
            />
            <ImportSection onImportComplete={handleImportComplete} />
            <ResponsePanel
              status={respStatus}
              json={respJson}
              error={respError}
              loading={loading}
            />
            <DataTable records={records} />
          </div>
        </section>
      </main>
    </div>
  );
}
