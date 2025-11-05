'use client';

import { useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';

// 1. useRef의 타입을 위해 'react-webcam'의 *타입*을 import 합니다.
import type Webcam from 'react-webcam';

// 2. dynamic import를 수정합니다.
// .then(mod => mod.default)로 기본 모듈을 명시적으로 가져오고,
// <any> 타입을 지정하여 라이브러리의 타입 오류를 무시하고 빌드합니다.
const DynamicWebcam = dynamic(
  () => import('react-webcam').then((mod) => mod.default),
  { ssr: false }
) as React.ComponentType<any>; // eslint-disable-line @typescript-eslint/no-explicit-any

export default function CapturePage() {
  // 3. ref의 타입으로 import한 'Webcam' 타입을 사용합니다.
  const webcamRef = useRef<Webcam>(null);
  const router = useRouter();
  const [isCapturing, setIsCapturing] = useState(false);
  const [gender, setGender] = useState<'male' | 'female'>('male');

  const captureImage = async () => {
    if (!webcamRef.current) return;

    setIsCapturing(true);
    try {
      const imageSrc = webcamRef.current.getScreenshot();

      if (imageSrc) {
        const blob = await (await fetch(imageSrc)).blob();
        const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

        const formData = new FormData();
        formData.append('file', file);
        formData.append('gender', gender);

        // API 주소는 이전에 수정한 '/api/upload' 그대로 둡니다.
        const res = await fetch('/api/upload', {
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
          {/* ... (제목, 성별 선택 부분은 동일) ... */}

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

          {/* 4. JSX에서 <Webcam> 대신 새로 만든 <DynamicWebcam>을 사용합니다. */}
          <div className="relative bg-white rounded-lg shadow-lg overflow-hidden">
            <DynamicWebcam
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