import React, { useState } from "react";

export default function Upload() {
  const [image, setImage] = useState(null);
  const [file, setFile] = useState(null); // 실제 파일 객체 저장
  const [spreadCards, setSpreadCards] = useState([]);
  const [isSpreading, setIsSpreading] = useState(false);

  const CARD_WIDTH = 160;
  const CARD_HEIGHT = 260;

  // ✅ 파일 선택 시 이미지 미리보기 & 파일 저장
  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setImage(URL.createObjectURL(selectedFile));
      setFile(selectedFile);
    }
  };

  // ✅ 분석 시작 함수
  const startAnalysis = async () => {
    if (!file) return alert("달 이미지를 선택해주세요!");

    // Flask로 파일 전송
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://210.109.55.9:5000/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      // 분석 결과 저장 (localStorage → /result 페이지에서 읽음)
      localStorage.setItem("moonResult", JSON.stringify(data));

      // 카드 펼침 애니메이션 시작
      startLeftToRightSpread();
    } catch (err) {
      console.error("분석 실패:", err);
      alert("서버 오류가 발생했습니다. Flask 서버를 확인하세요.");
    }
  };

  const startLeftToRightSpread = () => {
    setIsSpreading(true);
    setSpreadCards([]);

    const cardCount = 20;
    const windowWidth = window.innerWidth;
    const totalWidth = windowWidth * 0.9;
    const usableWidth = totalWidth - CARD_WIDTH;
    const spacing = usableWidth / (cardCount - 1);
    const offset = (windowWidth - totalWidth) / 2 - 100;

    let index = 0;
    const interval = setInterval(() => {
      setSpreadCards((prev) => [
        ...prev,
        { id: index, x: offset + spacing * index },
      ]);

      index++;
      if (index >= cardCount) {
        clearInterval(interval);
        setTimeout(() => {
          window.location.href = "/result"; // ✅ 결과 페이지로 이동
        }, 800);
      }
    }, 80);
  };

  // ✅ UI
  return (
    <div className="relative w-full min-h-screen flex items-center justify-center bg-black/40 overflow-hidden">
      {/* 카드 애니메이션 */}
      <div className="absolute inset-0 z-40 pointer-events-none">
        {isSpreading &&
          spreadCards.map((card) => (
            <img
              key={card.id}
              src={image || "/image1.jpeg"}
              style={{
                width: CARD_WIDTH,
                height: CARD_HEIGHT,
                position: "absolute",
                top: "50%",
                left: 0,
                transform: `translateY(-50%) translateX(${card.x}px)`,
                transition: "transform 0.3s ease-out",
              }}
            />
          ))}
      </div>

      {/* 업로드 UI */}
      {!isSpreading && (
        <div className="w-[380px] p-6 rounded-3xl bg-white/10 backdrop-blur-md shadow-2xl flex flex-col items-center border border-white/20 relative z-10">
          <h1 className="text-3xl font-bold mb-6 text-white flex items-center gap-2">
            쟁반같이 둥근 달 <span>☾</span>
          </h1>

          {/* 미리보기 */}
          {image ? (
            <img
              src={image}
              alt="미리보기"
              className="w-64 h-96 object-cover rounded-2xl mb-6 shadow-lg border border-white/20"
            />
          ) : (
            <div className="w-64 h-96 rounded-2xl relative overflow-hidden shadow-lg mb-6 bg-white/10 border border-white/20 flex items-center justify-center text-white/80">
              이미지 선택
            </div>
          )}

          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="mb-4 text-white"
          />

          <button
            onClick={startAnalysis}
            className="w-44 py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl shadow-md text-lg transition-all"
          >
            분석 시작하기
          </button>
        </div>
      )}
    </div>
  );
}
