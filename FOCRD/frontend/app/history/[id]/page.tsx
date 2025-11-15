// frontend/app/history/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type HistoryItem = {
  id: string;
  date: string;
  filename?: string;
  parsed: Record<string, number | null>;
  text?: string;
  score?: number;
  tier?: string;
};

export default function HistoryDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const API = process.env.NEXT_PUBLIC_API_URL;

  const [item, setItem] = useState<HistoryItem | null>(null);
  const [processedUrl, setProcessedUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const run = async () => {
      try {
        const res = await fetch(`${API}/api/history/${id}`);
        const json = await res.json();
        if (json.ok) {
          setItem(json.data);
          if (json.data?.filename) {
            setProcessedUrl(`${API}/api/processed?filename=${encodeURIComponent(json.data.filename)}`);
          }
        } else {
          alert("❌ 기록을 찾을 수 없습니다.");
        }
      } catch (e) {
        alert("❌ 상세 불러오기 실패");
      }
    };
    run();
  }, [API, id]);

  if (!id) return <div className="p-6">잘못된 접근입니다.</div>;
  if (!item) return <div className="p-6">불러오는 중…</div>;

  return (
    <div className="min-h-screen p-6 bg-gradient-to-b from-green-50 to-green-100">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow p-6">
        <a href="/history" className="text-sm text-gray-500">&larr; 목록으로</a>

        <h1 className="text-2xl font-bold mt-2 mb-4">🔎 분석 상세</h1>

        <div className="grid sm:grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-500 mb-2">
              {item.date ? new Date(item.date).toLocaleString() : "날짜 미상"}
            </div>
            {item.tier && item.score !== undefined && (
              <div className="mb-3">
                <div className="text-lg">
                  티어: <b className="text-green-700">{item.tier}</b> · 점수: <b>{item.score}</b>
                </div>
              </div>
            )}
            <h3 className="font-semibold mt-2 mb-1">영양성분 (Parsed)</h3>
            <pre className="bg-gray-100 p-3 rounded text-[13px] overflow-auto">
{JSON.stringify(item.parsed, null, 2)}
            </pre>

            {item.text && (
              <>
                <h3 className="font-semibold mt-4 mb-1">원문 OCR 텍스트</h3>
                <pre className="bg-gray-50 p-3 rounded text-[12px] overflow-auto whitespace-pre-wrap">
{item.text}
                </pre>
              </>
            )}
          </div>

          <div>
            <h3 className="font-semibold mb-2">전처리된 이미지</h3>
            {processedUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={processedUrl}
                alt="processed"
                className="w-full rounded border"
              />
            ) : (
              <div className="text-sm text-gray-500">이미지 없음</div>
            )}
            {item.filename && (
              <div className="text-xs text-gray-500 mt-2">파일: {item.filename}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
