'use client';

import React from 'react';

interface CodeDisplayProps {
  code: string;
}

export function CodeDisplay({ code }: CodeDisplayProps) {
  return (
    <pre className="bg-slate-900 text-slate-100 text-sm rounded-lg p-4 overflow-auto">
      <code>{code}</code>
    </pre>
  );
}
