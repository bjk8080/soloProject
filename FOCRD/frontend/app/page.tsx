"use client";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-green-50 to-green-100 px-6">
      
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-green-700 flex items-center justify-center gap-2">
          🍴FOCRD
        </h1>
        <p className="text-gray-600 mt-2">스마트 영양 성분 OCR 분석</p>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-3">
        사진 한 장으로 내 식단을 더 똑똑하게
      </h2>
      <p className="text-gray-500 mb-8 text-sm text-center leading-relaxed">
        영양성분표를 촬영하면 AI가 자동 분석하여<br />
        음식의 점수를 알려줍니다.
      </p>

      <div className="flex flex-col gap-4 w-full max-w-xs">
        <a
          href="/upload"
          className="bg-green-600 hover:bg-green-700 transition text-white font-semibold py-3 rounded-xl text-center shadow-md text-sm"
        >
          📸 사진 업로드
        </a>

        <a
          href="/history"
          className="bg-white border border-gray-300 hover:bg-gray-100 transition text-gray-800 font-medium py-3 rounded-xl text-center shadow text-sm"
        >
          📁 내 영양 분석 기록
        </a>
      </div>

      <footer className="mt-10 text-xs text-gray-500">
        © 2025 FOCRD AI Scanner made by Bbangjik
      </footer>
    </div>
  );
}
