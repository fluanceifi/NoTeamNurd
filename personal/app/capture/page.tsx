'use client';

import { useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { useRouter } from 'next/navigation';

export default function CapturePage() {
  const webcamRef = useRef<Webcam>(null);
  const router = useRouter();
  const [isCapturing, setIsCapturing] = useState(false);

  const captureImage = async () => {
    if (!webcamRef.current) return;
    
    setIsCapturing(true);
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        // TODO: 여기에 퍼스널컬러 분석 로직 추가
        // 임시로 3초 후 결과 페이지로 이동
        setTimeout(() => {
          router.push('/result');
        }, 3000);
      }
    } catch (error) {
      console.error('캡처 중 오류 발생:', error);
    }
    setIsCapturing(false);
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