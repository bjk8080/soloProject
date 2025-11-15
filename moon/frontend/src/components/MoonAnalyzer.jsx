"use client";
import { useState } from "react";

export default function MoonAnalyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("달 이미지를 선택하세요!");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("업로드 실패:", err);
      alert("서버 오류: Flask 연결을 확인하세요");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-10 space-y-8">
      <h1 className="text-3xl font-bold text-white">🌕 Moon Phase Analyzer</h1>

      {/* 업로드 폼 */}
      <form onSubmit={handleUpload} className="flex flex-col items-center space-y-4">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          className="text-white border p-2 rounded"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded transition"
        >
          {loading ? "분석 중..." : "달 분석하기"}
        </button>
      </form>

      {/* 분석 결과 카드 */}
      {result && (
        <div className="bg-gray-800 rounded-2xl shadow-xl w-[480px] p-5 text-white border border-gray-700">
          <h2 className="text-2xl font-semibold mb-2">{result.phase}</h2>
          <p className="text-gray-300 mb-1">
            <strong>밝기 비율:</strong> {result.bright_ratio}%
          </p>
          <p className="text-gray-300 mb-1">
            <strong>달 방향:</strong> {result.direction}
          </p>
          <p className="text-gray-300 mb-3">
            <strong>OCR 결과:</strong> {result.ocr_text}
          </p>

          {/* 이미지 */}
          <div className="flex justify-center">
            <img
              src={`http://localhost:5000/${result.result_image}`}
              alt="분석 결과 달 이미지"
              className="rounded-lg border border-gray-600 shadow-md"
            />
          </div>
        </div>
      )}
    </div>
  );
}
