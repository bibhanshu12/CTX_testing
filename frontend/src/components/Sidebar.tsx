import React from "react";
import type { EntityListItem } from "../types";

interface SidebarProps {
  entities: EntityListItem[];
  selected: string;
  onSelect: (name: string) => void;
  dataSource: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  entities,
  selected,
  onSelect,
  dataSource,
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>CTX Explorer</h2>
        <div className="badge">CTX Allowlist</div>
      </div>
      <div className="data-source">Source: {dataSource}</div>
      <nav>
        <ul>
          {entities.map((e) => (
            <li key={e.name}>
              <button
                className={selected === e.name ? "active" : ""}
                onClick={() => onSelect(e.name)}
              >
                {e.name}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};
