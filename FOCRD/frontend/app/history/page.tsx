"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function HistoryPage() {
  const [records, setRecords] = useState<any[]>([]);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("focrd_results") || "[]");
    setRecords(saved);
  }, []);

  const deleteRecord = (idx: number) => {
    const updated = records.filter((_, i) => i !== idx);
    setRecords(updated);
    localStorage.setItem("focrd_results", JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-green-100 p-6">
      <div className="max-w-lg mx-auto bg-white p-6 rounded-xl shadow-md">

        <Link href="/" className="text-sm text-gray-500">
          ← 홈으로
        </Link>

        <h2 className="text-2xl font-bold mb-4 text-center">
          📁 내 영양 분석 기록
        </h2>

        {records.length === 0 ? (
          <p className="text-center text-gray-500">저장된 기록이 없습니다.</p>
        ) : (
          <div className="space-y-4">
            {records.map((r, idx) => (
              <div key={idx} className="p-4 border rounded-lg bg-gray-50">
                <div className="flex justify-between">
                  <div>
                    <p className="font-semibold">📅 {new Date(r.date).toLocaleString()}</p>
                    <p className="text-sm text-gray-600">
                      점수: {r.score} / 100 | 티어: <b>{r.tier}</b>
                    </p>
                  </div>
                  <button
                    onClick={() => deleteRecord(idx)}
                    className="text-red-500 text-sm"
                  >
                    삭제
                  </button>
                </div>

                <details className="mt-2">
                  <summary className="cursor-pointer text-blue-600 text-sm">
                    🔍 상세 보기
                  </summary>
                  <pre className="bg-white p-2 rounded text-xs mt-2">
                    {JSON.stringify(r.parsed, null, 2)}
                  </pre>
                </details>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
