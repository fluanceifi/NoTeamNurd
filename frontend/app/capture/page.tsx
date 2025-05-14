'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic'; // ✅ 추가
import { useRouter } from 'next/navigation';

const Webcam = dynamic(() => import('react-webcam'), { ssr: false }); // ✅ 수정


export default function CapturePage() {
  const webcamRef = useRef<Webcam>(null);
  const router = useRouter();
  const [isCapturing, setIsCapturing] = useState(false);

 const captureImage = async () => {
  if (!webcamRef.current) return;

  setIsCapturing(true);
  try {
    const imageSrc = webcamRef.current.getScreenshot(); // base64 문자열

    if (imageSrc) {
      // 📌 base64 → File 변환
      const blob = await (await fetch(imageSrc)).blob();
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

      // 📤 Flask로 전송
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('http://localhost:5050/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      console.log('Flask 응답:', data);

      if (data.success) {
        router.push('/result');
      } else {
        alert('서버 오류: ' + data.message);
      }
    }
  } catch (error) {
    console.error('업로드 중 오류 발생:', error);
    alert('업로드 실패');
  } finally {
    setIsCapturing(false);
  }
};


  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <div className="relative bg-white rounded-lg shadow-lg overflow-hidden">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={{
              width: 1280,
              height: 720,
              facingMode: "user"
            }}
            className="w-full h-auto"
          />
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
            <button
              onClick={captureImage}
              disabled={isCapturing}
              className={`px-6 py-2 rounded-lg text-gray-700 font-semibold ${
                isCapturing 
                  ? 'bg-gray-300 cursor-not-allowed' 
                  : 'bg-pink-100/70 hover:bg-pink-200/80'
              }`}
            >
              {isCapturing ? '분석 중...' : '촬영하기'}
            </button>
          </div>
        </div>
        
      </div>
    </div>
  );
} 