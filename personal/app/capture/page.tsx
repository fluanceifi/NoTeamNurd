'use client';

import { useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { useRouter } from 'next/navigation';
import * as tf from '@tensorflow/tfjs';
import '@mediapipe/face_mesh';

export default function CapturePage() {
  const webcamRef = useRef<Webcam>(null);
  const router = useRouter();
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const captureImage = async () => {
    if (webcamRef.current) {
      setIsAnalyzing(true);
      const imageSrc = webcamRef.current.getScreenshot();
      
      // 여기에 퍼스널 컬러 분석 로직 추가
      // 임시로 3초 후 결과 페이지로 이동하도록 설정
      setTimeout(() => {
        router.push('/results?type=spring'); // 분석 결과에 따라 타입 변경
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">실시간 퍼스널 컬러 측정</h1>
        
        <div className="relative">
          <Webcam
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            className="w-full rounded-lg"
          />
          {isAnalyzing && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-lg">
              <div className="text-white text-xl">분석 중...</div>
            </div>
          )}
        </div>

        <div className="mt-6 flex justify-center space-x-4">
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition duration-300"
          >
            돌아가기
          </button>
          <button
            onClick={captureImage}
            disabled={isAnalyzing}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-300 disabled:bg-blue-300"
          >
            측정하기
          </button>
        </div>
      </div>
    </div>
  );
} 