import React from "react";
import type { EntityMetadata } from "../types";

interface TryItPanelProps {
  entitySet: string;
  metadata: EntityMetadata | null;
  onExecute: (
    params: { top?: number; skip?: number; filter?: string; orderby?: string }
  ) => void;
}

export const TryItPanel: React.FC<TryItPanelProps> = ({
  entitySet,
  metadata,
  onExecute,
}) => {
  const [top, setTop] = React.useState<number | undefined>(20);
  const [skip, setSkip] = React.useState<number | undefined>();
  const [filter, setFilter] = React.useState("");
  const [orderby, setOrderby] = React.useState("");

  const keyCol = metadata?.columns.find((c) => c.key);
  const placeholder = keyCol ? `e.g. ${keyCol.name} eq 'VALUE'` : "e.g. Field eq 'VALUE'";

  return (
    <section className="panel">
      <h3>Try it — GET /api/ctx/entities/{entitySet}/records</h3>
      <div className="form-grid">
        <div className="field">
          <label>$top</label>
          <input
            type="number"
            min="1"
            max="1000"
            value={top ?? ""}
            onChange={(e) => setTop(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="20"
          />
        </div>
        <div className="field">
          <label>$skip</label>
          <input
            type="number"
            min="0"
            value={skip ?? ""}
            onChange={(e) => setSkip(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="0"
          />
        </div>
        <div className="field">
          <label>$filter</label>
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder={placeholder}
          />
        </div>
        <div className="field">
          <label>$orderby</label>
          <input
            type="text"
            value={orderby}
            onChange={(e) => setOrderby(e.target.value)}
            placeholder="Column asc"
          />
        </div>
      </div>
      <button className="btn btn-primary" onClick={() => onExecute({ top, skip, filter: filter || undefined, orderby: orderby || undefined })}>
        Execute Request
      </button>
    </section>
  );
};
