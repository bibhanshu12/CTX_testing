import React from "react";

interface ResponsePanelProps {
  status: number | null;
  json: any;
  error: string | null;
  loading: boolean;
}

export const ResponsePanel: React.FC<ResponsePanelProps> = ({
  status,
  json,
  error,
  loading,
}) => {
  return (
    <section className="panel response-panel">
      <div className="panel-row">
        <h3>Response</h3>
        <span className={`badge status ${status ? (status >= 200 && status < 300 ? "ok" : "err") : ""}`}>
          {loading ? "Loading…" : status ?? "—"}
        </span>
      </div>
      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>
      )}
      {!loading && json !== undefined && !error ? (
        <pre className="json-view">{JSON.stringify(json, null, 2)}</pre>
      ) : loading ? (
        <div className="muted">Sending request…</div>
      ) : null}
    </section>
  );
};
