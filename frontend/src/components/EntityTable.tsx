import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import clsx from "clsx";
import type { Entity } from "../types";
import ProspectBadge from "./ProspectBadge";

const SECTOR_LABELS: Record<string, string> = {
  fintech: "Fintech",
  artificial_intelligence: "AI",
  digital_health_biotech: "Health/Bio",
  cybersecurity: "Cybersec",
  saas_cloud_infra: "SaaS/Cloud",
  ecommerce_marketplaces: "E-commerce",
  real_estate_proptech: "PropTech",
  cleantech_energy: "CleanTech",
  fitness_wellness: "Fitness",
  education_creator: "Education",
  other: "Other",
};

const SECTOR_COLORS: Record<string, string> = {
  fintech: "bg-emerald-900/40 text-emerald-400",
  artificial_intelligence: "bg-violet-900/40 text-violet-400",
  digital_health_biotech: "bg-cyan-900/40 text-cyan-400",
  cybersecurity: "bg-red-900/40 text-red-400",
  saas_cloud_infra: "bg-blue-900/40 text-blue-400",
  ecommerce_marketplaces: "bg-orange-900/40 text-orange-400",
  real_estate_proptech: "bg-amber-900/40 text-amber-400",
  cleantech_energy: "bg-lime-900/40 text-lime-400",
  fitness_wellness: "bg-pink-900/40 text-pink-400",
  education_creator: "bg-sky-900/40 text-sky-400",
  other: "bg-gray-800 text-gray-500",
};

const ch = createColumnHelper<Entity>();

const columns = [
  ch.accessor("prospect_score", {
    header: "Score",
    cell: (info) => <ProspectBadge score={info.getValue()} />,
    size: 110,
  }),
  ch.accessor("date", {
    header: "Date",
    cell: (info) => (
      <span className="font-mono text-xs text-gray-400">{info.getValue()}</span>
    ),
    size: 100,
  }),
  ch.accessor("name", {
    header: "Business name",
    cell: (info) => (
      <span className="font-medium text-gray-100">{info.getValue()}</span>
    ),
  }),
  ch.accessor("jurisdiction", {
    header: "State",
    cell: (info) => (
      <span className="rounded border border-gray-700 bg-gray-800 px-1.5 py-0.5 font-mono text-xs text-gray-300">
        {info.getValue()}
      </span>
    ),
    size: 70,
  }),
  ch.accessor("sector", {
    header: "Sector",
    cell: (info) => {
      const s = info.getValue();
      return (
        <span
          className={clsx(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            SECTOR_COLORS[s] ?? SECTOR_COLORS.other
          )}
        >
          {SECTOR_LABELS[s] ?? s}
        </span>
      );
    },
    size: 120,
  }),
  ch.accessor("domain_com", {
    header: ".com",
    cell: (info) => {
      const dom = info.getValue();
      const avail = info.row.original.domain_available;
      if (!dom) return <span className="text-xs text-gray-600">—</span>;
      return (
        <div className="flex items-center gap-1.5">
          <span
            className={clsx(
              "h-1.5 w-1.5 rounded-full",
              avail === true
                ? "bg-emerald-500"
                : avail === false
                  ? "bg-red-500"
                  : "bg-gray-600"
            )}
          />
          <span
            className={clsx(
              "text-xs",
              avail === true ? "text-emerald-400" : "text-gray-400"
            )}
          >
            {dom}
          </span>
        </div>
      );
    },
    size: 170,
  }),
  ch.accessor("description", {
    header: "Description",
    cell: (info) => (
      <span className="line-clamp-2 text-xs text-gray-500">{info.getValue() || "—"}</span>
    ),
  }),
];

interface Props {
  data: Entity[];
  total: number;
  page: number;
  perPage: number;
  onPageChange: (p: number) => void;
  loading: boolean;
}

export default function EntityTable({
  data,
  total,
  page,
  perPage,
  onPageChange,
  loading,
}: Props) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    pageCount: Math.ceil(total / perPage),
  });

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="flex flex-col gap-3">
      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-800">
        <table className="w-full text-sm">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id} className="border-b border-gray-800 bg-gray-900">
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-widest text-gray-500"
                    style={{ width: header.column.columnDef.size }}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="py-16 text-center text-gray-600">
                  Loading…
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-16 text-center text-gray-600">
                  No entities found. Adjust filters or run a collection.
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => (
                <tr
                  key={row.id}
                  className={clsx(
                    "border-b border-gray-800/60 transition-colors hover:bg-gray-800/40",
                    row.original.prospect_score >= 80 && "bg-red-950/10",
                    row.original.prospect_score >= 60 &&
                      row.original.prospect_score < 80 &&
                      "bg-orange-950/10"
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          {total.toLocaleString()} total · page {page} / {totalPages || 1}
        </span>
        <div className="flex gap-1">
          <PagerBtn disabled={page <= 1} onClick={() => onPageChange(1)}>
            «
          </PagerBtn>
          <PagerBtn disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
            ‹
          </PagerBtn>
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            const p = Math.max(1, page - 2) + i;
            if (p > totalPages) return null;
            return (
              <PagerBtn key={p} active={p === page} onClick={() => onPageChange(p)}>
                {p}
              </PagerBtn>
            );
          })}
          <PagerBtn disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
            ›
          </PagerBtn>
          <PagerBtn disabled={page >= totalPages} onClick={() => onPageChange(totalPages)}>
            »
          </PagerBtn>
        </div>
      </div>
    </div>
  );
}

function PagerBtn({
  children,
  disabled,
  active,
  onClick,
}: {
  children: React.ReactNode;
  disabled?: boolean;
  active?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      className={clsx(
        "flex h-7 min-w-[28px] items-center justify-center rounded border px-2 text-xs transition-colors",
        active
          ? "border-blue-600 bg-blue-600/20 text-blue-400"
          : "border-gray-700 text-gray-400 hover:border-gray-600 hover:text-gray-200",
        disabled && "pointer-events-none opacity-30"
      )}
    >
      {children}
    </button>
  );
}
