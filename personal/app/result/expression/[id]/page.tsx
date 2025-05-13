'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';

export default function ExpressionPage() {
  const params = useParams();
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3;

  const backgroundId = params.id as string;
  const BACKGROUND_COLORS = {
    '1': '#FFF5E1',
    '2': '#F5F5F5',
    '3': '#E6F3FF',
  };

  useEffect(() => {
    if (isProcessing) {
      const timer = setTimeout(() => {
        setCurrentStep((prev) => {
          if (prev >= totalSteps) {
            setIsProcessing(false);
            return prev;
          }
          return prev + 1;
        });
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isProcessing, currentStep]);

  const handleStartProcessing = () => {
    setIsProcessing(true);
  };

  const handleComplete = () => {
    // TODO: 최종 이미지 저장 및 다운로드 로직 구현
    router.push(`/result/final/${backgroundId}`);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          표정 자연스럽게 만들기
        </h1>

        <div className="space-y-6">
          {!isProcessing ? (
            <div className="text-center">
              <p className="text-lg text-gray-700 mb-4">
                AI가 자연스러운 표정으로 수정해드립니다.
              </p>
              <button
                onClick={handleStartProcessing}
                className="px-6 py-2 bg-pink-100/70 hover:bg-pink-200/80 text-gray-700 rounded-lg transition duration-300"
              >
                시작하기
              </button>
            </div>
          ) : (
            <>
              <div className="relative h-4 bg-gray-200 rounded-full">
                <div
                  className="absolute h-full bg-sky-100/70 rounded-full transition-all duration-500"
                  style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                />
              </div>
              
              <div className="text-center">
                <p className="text-lg font-medium text-gray-700">
                  {currentStep === 1 && '표정 분석 중...'}
                  {currentStep === 2 && '자연스러운 표정 생성 중...'}
                  {currentStep === 3 && '최종 이미지 생성 완료!'}
                </p>
              </div>

              {currentStep === totalSteps && (
                <div className="flex justify-center mt-4">
                  <button
                    onClick={handleComplete}
                    className="px-6 py-2 bg-pink-100/70 hover:bg-pink-200/80 text-gray-700 rounded-lg transition duration-300"
                  >
                    완료
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
} 