import React, { useEffect, useState } from "react";

export default function Result() {
  const [result, setResult] = useState(null);

  useEffect(() => {
    const saved = localStorage.getItem("moonResult");
    if (saved) setResult(JSON.parse(saved));
  }, []);

  if (!result) {
    return (
      <div className="text-white flex items-center justify-center min-h-screen bg-black">
        결과를 불러오는 중입니다...
      </div>
    );
  }

  // ✅ Flask 서버 주소 고정 (HTTP)
  const backendBase = "http://10.0.3.214:5000";

  // ✅ Flask에서 반환된 경로를 완성된 URL로 변환
  const imageUrl = result.result_image
    ? `${backendBase}/${result.result_image}`
    : null;

  console.log("이미지 URL:", imageUrl);

  return (
    <div className="text-white min-h-screen bg-black flex flex-col items-center py-12">
      <h1 className="text-4xl font-bold mb-6">🌕 달 분석 결과</h1>

      <div className="text-lg space-y-2 text-center">
        <p>밝기 비율: <span className="font-semibold">{result.bright_ratio}%</span></p>
        <p>달 방향: <span className="font-semibold">{result.direction}</span></p>
        <p>위상: <span className="font-semibold text-purple-300">{result.phase}</span></p>
        {/* <p>OCR 인식: <span className="font-semibold">{result.ocr_text || "없음"}</span></p> */}
      </div>

      {/* ✅ Flask 결과 이미지
      {imageUrl && (
        <div className="mt-8 w-[420px] h-[420px] flex items-center justify-center border border-white/20 rounded-2xl bg-white/5 shadow-xl">
          <img
            src={imageUrl}
            alt="달 분석 결과"
            className="max-w-[400px] max-h-[400px] rounded-xl shadow-lg object-contain"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "/fallback_moon.png"; // 로드 실패시 대체 이미지
            }}
          />
        </div>
      )} */}

      <button
        onClick={() => (window.location.href = "/upload")}
        className="mt-10 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 rounded-xl shadow-lg text-lg font-semibold transition"
      >
        다시 분석하기
      </button>
    </div>
  );
}
