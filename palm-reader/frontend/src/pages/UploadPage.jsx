import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile); // ✅ 실제 File 객체 저장
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      alert("이미지를 선택해주세요!");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append("image", file); // ✅ key 이름 "image" 중요!

    try {
      const res = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("서버 응답:", data);

      if (data.result_image) {
        navigate("/result", { state: { imageUrl: `http://127.0.0.1:5000${data.result_image}` } });
      } else {
        alert("분석 실패: " + (data.error || "알 수 없는 오류"));
      }
    } catch (err) {
      console.error(err);
      alert("서버와 통신 중 오류 발생");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-screen h-screen flex flex-col items-center justify-center bg-black/40 text-white">
      <h1 className="text-3xl font-bold mb-4">손바닥 이미지 업로드 🖐️</h1>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="mb-4"
      />

      <button
        onClick={handleAnalyze}
        disabled={isLoading}
        className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl shadow-lg"
      >
        {isLoading ? "분석 중..." : "분석 시작하기"}
      </button>
    </div>
  );
}
