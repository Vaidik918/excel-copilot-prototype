'use client';

import React from 'react';

interface PreviewTableProps {
  data: Record<string, any>[];
}

export function PreviewTable({ data }: PreviewTableProps) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-gray-500">No preview data available.</p>;
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="overflow-auto border rounded-lg">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-100">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-3 py-2 text-left font-semibold text-gray-700">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="border-t">
              {columns.map((col) => (
                <td key={col} className="px-3 py-1 text-gray-800">
                  {String(row[col] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
