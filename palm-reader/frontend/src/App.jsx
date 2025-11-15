import { Routes, Route } from "react-router-dom";
import StarfallBackground from "./components/StarfallBackground";
import UploadPage from "./pages/UploadPage";
import Result from "./pages/Result";


function App() {
  return (
    <div className="relative w-screen h-screen text-white">
      <StarfallBackground />

      <Routes>
        {/* 메인 화면 */}
        <Route
          path="/"
          element={
            <div className="w-screen h-screen flex items-center justify-center px-4">
              <div
                className="
                w-full max-w-lg
                bg-white/10 backdrop-blur-xl
                border border-white/20
                rounded-3xl shadow-2xl
                p-10 flex flex-col items-center gap-6 text-center
                "
              >
                <h1 className="text-4xl font-bold drop-shadow-xl">
                  당신의 미래가 궁금한가? 🔮
                </h1>

                <p className="text-lg opacity-90 max-w-sm">
                  당신의 미래.. 손금으로 예측해드립니다.
                </p>

                <a
                  href="/upload"
                  className="
                  mt-2 px-6 py-3
                  bg-gradient-to-r from-purple-400 to-purple-600
                  hover:from-purple-500 hover:to-purple-700
                  text-white font-semibold rounded-xl
                  shadow-lg transition
                  "
                >
                  시작하기
                </a>
              </div>
            </div>
          }
        />

        {/* 업로드 페이지 */}
        <Route path="/upload" element={<UploadPage />} />

        {/* ✅ 결과 페이지 추가 */}
        <Route path="/result" element={<Result />} />
      </Routes>
    </div>
  );
}

export default App;
