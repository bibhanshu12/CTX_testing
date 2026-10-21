import React from "react";
import type { ImportMetadataResponse } from "../types";
import { api } from "../api/client";

interface ImportSectionProps {
  onImportComplete: (result: ImportMetadataResponse) => void;
}

export const ImportSection: React.FC<ImportSectionProps> = ({
  onImportComplete,
}) => {
  const [text, setText] = React.useState("");
  const [file, setFile] = React.useState<File | null>(null);
  const [result, setResult] = React.useState<ImportMetadataResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleTextImport = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.importMetadata(text);
      setResult(res);
      onImportComplete(res);
    } catch (e: any) {
      setError(e.response?.data?.message || e.message || "Import failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFileImport = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.importMetadataFile(file);
      setResult(res);
      onImportComplete(res);
    } catch (e: any) {
      setError(e.response?.data?.message || e.message || "Import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <h3>Metadata Import</h3>
      <div className="form-grid">
        <div className="field" style={{ gridColumn: "span 2" }}>
          <label>Paste metadata text ($metadata / XML / JSON)</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            placeholder='EntityType Name="CTX_RULEBOOK" ...'
          />
        </div>
        <div className="field">
          <label>Or upload file (.xml, .json, .txt, .csn, .edmx)</label>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </div>
      </div>
      <div className="btn-row">
        <button className="btn" onClick={handleTextImport} disabled={loading}>
          Import Text
        </button>
        <button className="btn" onClick={handleFileImport} disabled={loading || !file}>
          Import File
        </button>
      </div>
      {loading && <div className="muted">Validating…</div>}
      {error && <div className="error-box">{error}</div>}
      {result && (
        <div className="result-box">
          <strong>Valid:</strong> {String(result.valid)} &nbsp;|&nbsp;
          <strong>CTX entities found:</strong> {result.ctx_entities_found.join(", ") || "—"}
        </div>
      )}
    </section>
  );
};
