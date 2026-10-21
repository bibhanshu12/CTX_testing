import React from "react";
import type { ConnectionStatus } from "../types";

interface SourceSelectorProps {
  status: ConnectionStatus | null;
  onSourceChange: (source: string) => void;
  currentSource: string;
}

export const SourceSelector: React.FC<SourceSelectorProps> = ({
  status,
  onSourceChange,
  currentSource,
}) => {
  return (
    <section className="panel">
      <h3>Source Selector</h3>
      <div className="form-grid">
        <div className="field">
          <label>Data Source</label>
          <select
            value={currentSource}
            onChange={(e) => onSourceChange(e.target.value)}
          >
            <option value="seed">Seed Mode (local fixtures)</option>
            <option value="odata">OData Mode (SAP CAPM service)</option>
          </select>
        </div>
        <div className="field" style={{ flexDirection: "column", gap: 8 }}>
          <label>CAPM OData Base URL</label>
          <input
            type="text"
            placeholder="https://<service>/sap/opu/odata/"
            readOnly
          />
        </div>
      </div>
      <div className="status-box">
        <strong>Connection:</strong>
        {status ? (
          <span className={status.connected ? "connected" : "disconnected"}>
            {status.connected ? "Connected" : "Disconnected"} — {status.message}
          </span>
        ) : (
          <span>Checking…</span>
        )}
      </div>
      <p className="small">
        Browser CORS: requests go through the frontend proxy to
        http://localhost:8000. Backend-to-OData calls are server-side and not
        subject to browser CORS.
      </p>
    </section>
  );
};
