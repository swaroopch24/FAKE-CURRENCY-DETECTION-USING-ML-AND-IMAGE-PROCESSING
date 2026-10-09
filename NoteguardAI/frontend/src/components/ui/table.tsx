import React from "react";
import { cn } from "@/core/utils/cn";

export interface TableProps extends React.HTMLAttributes<HTMLTableElement> {}

export const Table = ({ className, children, ...props }: TableProps) => {
  return (
    <div className="w-full overflow-auto rounded-lg border border-slate-800 bg-slate-900/30">
      <table className={cn("w-full caption-bottom text-sm text-slate-200 border-collapse", className)} {...props}>
        {children}
      </table>
    </div>
  );
};

export const TableHeader = ({ className, children, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) => (
  <thead className={cn("bg-slate-900/60 border-b border-slate-800 text-left font-medium text-slate-400", className)} {...props}>
    {children}
  </thead>
);

export const TableBody = ({ className, children, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) => (
  <tbody className={cn("[&_tr:last-child]:border-0", className)} {...props}>
    {children}
  </tbody>
);

export const TableRow = ({ className, children, ...props }: React.HTMLAttributes<HTMLTableRowElement>) => (
  <tr className={cn("border-b border-slate-800/60 hover:bg-slate-900/80 hover:shadow-[inset_3px_0_0_0_#10B981] transition-all duration-200 cursor-pointer", className)} {...props}>
    {children}
  </tr>
);

export const TableHead = ({ className, children, ...props }: React.ThHTMLAttributes<HTMLTableCellElement>) => (
  <th className={cn("p-4 text-xs font-semibold uppercase tracking-wider text-slate-400 align-middle", className)} {...props}>
    {children}
  </th>
);

export const TableCell = ({ className, children, ...props }: React.TdHTMLAttributes<HTMLTableCellElement>) => (
  <td className={cn("p-4 align-middle text-sm", className)} {...props}>
    {children}
  </td>
);
