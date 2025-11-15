import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function Result() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const imageUrl = state?.imageUrl || "/sample-hand.jpg";
  const lines = state?.lines || {};
  const message = state?.message || "손금 결과를 불러올 수 없습니다.";

  return (
    <div className="w-full min-h-screen flex flex-col items-center bg-black/40 text-white py-14 relative overflow-hidden">
      <h1 className="text-4xl font-bold mb-8 z-10">손금 분석 결과</h1>

      <div className="relative w-[360px] h-[480px] bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-xl overflow-hidden z-10">
        <img src={imageUrl} className="w-full h-full object-cover opacity-90" />

        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {Object.entries(lines).map(([key, poly]) =>
            poly ? (
              <polyline
                key={key}
                points={poly}
                fill="none"
                stroke={
                  key === "heart"
                    ? "#ff4f6d"
                    : key === "head"
                    ? "#3bd2f6"
                    : key === "life"
                    ? "#3bf65a"
                    : "#ffcc33"
                }
                strokeWidth="4"
                strokeLinecap="round"
              />
            ) : null
          )}
        </svg>
      </div>

      <div className="w-[420px] mt-10 space-y-6 z-10">
        <div className="p-5 rounded-xl bg-white/10 border border-white/20 backdrop-blur-md shadow-lg">
          <h2 className="text-2xl font-semibold mb-2">🔮 손금 해석</h2>
          <p className="opacity-85">{message}</p>
        </div>

        <button
          onClick={() => navigate("/")}
          className="w-full py-3 mt-6 bg-green-500 hover:bg-green-600 text-white rounded-xl shadow-lg transition-all"
        >
          다시 분석하기
        </button>
      </div>
    </div>
  );
}
