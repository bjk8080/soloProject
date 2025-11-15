"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ResultPage() {
  const params = useSearchParams();
  const router = useRouter();
  const filename = params.get("filename");

  const API = process.env.NEXT_PUBLIC_API_URL;
  const [data, setData] = useState<any>(null);

  // ✅ 서버에서 분석 데이터 가져오기
  useEffect(() => {
    if (!filename) return;

    const fetchData = async () => {
  try {
    const res = await fetch(`${API}/api/analyze?filename=${filename}`);
    const json = await res.json();

    // ✅ 추가된 부분 — OCR 인식 실패 시 알림 + 업로드 페이지로 이동
    if (!json.ok) {
      alert(json.error || "영양성분 인식이 불완전합니다. 이미지를 다시 업로드해주세요.");
      router.push("/upload");
      return;
    }

    setData(json);
  } catch (err) {
    console.error("⚠️ 분석 요청 실패:", err);
    alert("서버와 연결할 수 없습니다. 다시 시도해주세요.");
    router.push("/upload");
  }
};


    fetchData();
  }, [filename, API]);

  if (!filename) return <div className="p-10 text-center">❗ 파일 정보 없음</div>;
  if (!data) return <div className="p-10 text-center text-lg">AI 분석 중... 🔍</div>;

  // ✅ 분석 결과 저장 함수
  const saveResult = () => {
    if (!data) return;

    const previous = JSON.parse(localStorage.getItem("focrd_results") || "[]");

    const newResult = {
      date: new Date().toISOString(),
      filename,
      parsed: data.parsed,
      score: data.score ?? 0,
      tier: data.tier ?? "N/A",
    };

    const updated = [newResult, ...previous];

    localStorage.setItem("focrd_results", JSON.stringify(updated));

    alert("✅ 분석 결과가 저장되었습니다!");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-green-100 flex flex-col items-center p-6">
      <div className="w-full max-w-lg bg-white p-6 rounded-xl shadow-lg">
        
        <button
          onClick={() => router.push("/")}
          className="text-sm text-gray-500 mb-4"
        >
          &larr; 홈으로
        </button>

        <h2 className="text-2xl font-bold mb-5 text-center">AI 영양 분석 결과</h2>

        {/* ✅ 티어 표시 */}
        <div className="flex items-center justify-center mb-4">
          <span className="text-4xl font-bold text-green-600">{data.tier}</span>
          <span className="ml-2 text-xl text-gray-600">티어</span>
        </div>

        {/* ✅ 점수 표시 */}
        <p className="text-center text-lg mb-4">
          점수: <span className="font-bold">{data.score}</span> / 100
        </p>

        {/* ✅ 영양 분석 출력 */}
        <h3 className="font-bold mt-4 mb-2 text-lg">영양성분</h3>
        <pre className="bg-gray-100 p-3 rounded text-[13px] overflow-auto">
{JSON.stringify(data.parsed, null, 2)}
        </pre>

        {/* ✅ 결과 저장 버튼 */}
        <button
          onClick={saveResult}
          className="mt-5 w-full bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 rounded-lg shadow transition"
        >
          ⭐ 결과 저장
        </button>

      </div>
    </div>
  );
}
