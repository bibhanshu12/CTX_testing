import React from "react";
import type { RecordsResponse } from "../types";

interface DataTableProps {
  records: RecordsResponse | null;
}

export const DataTable: React.FC<DataTableProps> = ({ records }) => {
  if (!records || records.value.length === 0) return null;

  const keys = Object.keys(records.value[0]);

  return (
    <section className="panel">
      <h3>Data Table ({records.count} rows)</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>{keys.map((k) => <th key={k}>{k}</th>)}</tr>
          </thead>
          <tbody>
            {records.value.map((row, i) => (
              <tr key={i}>
                {keys.map((k) => (
                  <td key={k}>{row[k] !== undefined ? row[k] : ""}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};
