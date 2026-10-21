import React from "react";
import type { EntityMetadata } from "../types";

interface MetadataPanelProps {
  metadata: EntityMetadata | null;
}

export const MetadataPanel: React.FC<MetadataPanelProps> = ({
  metadata,
}) => {
  if (!metadata) return null;

  return (
    <section className="panel">
      <h3>Metadata — {metadata.name}</h3>
      <p className="small">
        Namespace: {metadata.namespace} &nbsp;|&nbsp; Key: {metadata.key}
      </p>
      <table className="cols-table">
        <thead>
          <tr>
            <th>Column</th>
            <th>Type</th>
            <th>Key</th>
          </tr>
        </thead>
        <tbody>
          {metadata.columns.map((c) => (
            <tr key={c.name}>
              <td>{c.name}</td>
              <td>{c.type}</td>
              <td>{c.key ? "Yes" : ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};
