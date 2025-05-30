'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';

const Webcam = dynamic(() => import('react-webcam'), { ssr: false });

export default function CapturePage() {
  const webcamRef = useRef<Webcam>(null);
  const router = useRouter();
  const [isCapturing, setIsCapturing] = useState(false);
  const [gender, setGender] = useState<'male' | 'female'>('male'); // ✅ 성별 상태 추가

  const captureImage = async () => {
    if (!webcamRef.current) return;

    setIsCapturing(true);
    try {
      const imageSrc = webcamRef.current.getScreenshot(); // base64 문자열

      if (imageSrc) {
        // 📌 base64 → File 변환
        const blob = await (await fetch(imageSrc)).blob();
        const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

        // Flask로 전송 (성별 정보 포함)
        const formData = new FormData();
        formData.append('file', file);
        formData.append('gender', gender); // ✅ 성별 정보 추가

        const res = await fetch('http://127.0.0.1:5050/upload', {
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
        <div className="space-y-6">
          {/* 제목 */}
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-800 mb-2">실시간 촬영</h1>
            <p className="text-sm text-gray-500">
              증명사진으로 변환할 사진을 촬영해주세요
            </p>
          </div>

          {/* 성별 선택 */}
          <div className="flex justify-center gap-4">
            <label className={`px-4 py-2 rounded-lg cursor-pointer border ${gender === 'male' ? 'bg-blue-100 border-blue-500 text-blue-800 font-semibold' : 'border-gray-300 text-gray-600'}`}>
              <input
                type="radio"
                name="gender"
                value="male"
                checked={gender === 'male'}
                onChange={() => setGender('male')}
                className="hidden"
              />
              남성
            </label>

            <label className={`px-4 py-2 rounded-lg cursor-pointer border ${gender === 'female' ? 'bg-pink-100 border-pink-500 text-pink-800 font-semibold' : 'border-gray-300 text-gray-600'}`}>
              <input
                type="radio"
                name="gender"
                value="female"
                checked={gender === 'female'}
                onChange={() => setGender('female')}
                className="hidden"
              />
              여성
            </label>
          </div>

          {/* 웹캠 */}
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
                className={`px-6 py-2 rounded-lg text-gray-700 font-semibold transition duration-300 ${
                  isCapturing
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-pink-100/70 hover:bg-pink-200/80'
                }`}
              >
                {isCapturing ? '분석 중...' : '촬영하기'}
              </button>
            </div>
          </div>

          {/* 하단 버튼 */}
          <div className="flex justify-center">
            <button
              onClick={() => router.push('/')}
              className="px-8 py-3 bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 rounded-lg transition duration-300"
            >
              돌아가기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}