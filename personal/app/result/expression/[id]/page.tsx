'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';

type ColorType = '봄 웜톤' | '여름 쿨톤' | '가을 웜톤' | '겨울 쿨톤';

export default function ExpressionPage() {
  const params = useParams();
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3;

  const backgroundId = params.id as string;
  const BACKGROUND_COLORS = {
    '1': '#FFF5E1', // 봄 웜톤에 어울리는 아이보리 베이지
    '2': '#F5F5F5', // 여름 쿨톤에 어울리는 화이트 그레이
    '3': '#E6F3FF', // 겨울 쿨톤에 어울리는 아이스 블루
  };

  // 퍼스널 컬러 결과 데이터 (실제로는 API나 서버에서 받아와야 함)
  const colorResult = {
    type: '봄 웜톤' as ColorType, // 실제로는 API에서 받아와야 함
    description: {
      '봄 웜톤': '밝고 선명한 색감이 잘 어울리며, 노란빛이 도는 따뜻한 색조가 피부를 환하게 밝혀줍니다.',
      '여름 쿨톤': '시원하고 부드러운 파스텔톤이 잘 어울리며, 푸른빛이 도는 차가운 색조가 피부를 맑고 깨끗해 보이게 합니다.',
      '가을 웜톤': '깊이 있고 차분한 컬러가 잘 어울리며, 골드빛이 도는 따뜻한 색조가 피부를 건강하게 보이게 합니다.',
      '겨울 쿨톤': '선명하고 강렬한 컬러가 잘 어울리며, 푸른빛이 도는 차가운 색조가 피부를 도도하고 세련되게 보이게 합니다.'
    } as const
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