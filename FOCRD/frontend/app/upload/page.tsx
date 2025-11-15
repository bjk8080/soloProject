"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

console.log("✅ API Base URL:", process.env.NEXT_PUBLIC_API_URL);

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");

  const API = process.env.NEXT_PUBLIC_API_URL;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const handleUpload = async () => {
    if (!file) return alert("파일을 선택해주세요!");

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API}/api/upload`, {
        method: "POST",
        body: form,
      });
      const data = await res.json();

      if (data.ok) {
        router.push(`/result?filename=${data.filename}`);
      } else {
        alert("업로드 실패");
      }
    } catch (e) {
      alert("서버 연결 실패. 백엔드 확인하세요.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-green-50 to-green-100 p-4">
      <a href="/" className="text-sm text-gray-500 mb-4">&larr; 홈으로</a>

      <h1 className="text-2xl font-bold mb-2">영양성분 업로드</h1>
      <p className="text-gray-600 mb-6">영양성분표 사진을 업로드해주세요</p>

      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-md text-center">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="block w-full p-2 border rounded-md mb-3"
        />

        {preview && (
          <img
            src={preview}
            className="w-full h-48 object-cover rounded mb-3"
          />
        )}

        <button
          onClick={handleUpload}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition"
        >
          📤 업로드 & 분석 시작
        </button>
      </div>
    </div>
  );
}
