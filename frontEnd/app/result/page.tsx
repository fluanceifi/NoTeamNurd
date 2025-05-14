'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

type ColorType = '봄 웜톤' | '여름 쿨톤' | '가을 웜톤' | '겨울 쿨톤';

const BACKGROUND_COLORS = [
  { id: 1, name: '웜 아이보리', color: '#FFF5E1', image: '/images/photo1.jpg' },
  { id: 2, name: '쿨 화이트', color: '#F5F5F5', image: '/images/photo2.jpg' },
  { id: 3, name: '소프트 블루', color: '#E6F3FF', image: '/images/photo3.jpg' },
];

export default function ResultPage() {
  const router = useRouter();
  const [selectedColor, setSelectedColor] = useState<number | null>(null);
  // 실제로는 API나 props로 받아와야 하는 값입니다
  const colorResult: ColorType = '봄 웜톤';

  const handleColorSelect = (colorId: number) => {
    setSelectedColor(colorId);
  };

  const handleNext = () => {
    if (selectedColor) {
      router.push(`/result/expression/${selectedColor}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          퍼스널컬러 분석 결과
        </h1>
        
        <div className="space-y-6">
          <div className="text-center mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              당신의 퍼스널 컬러는 <span className="text-amber-500">{colorResult}</span> 입니다
            </h2>
            <p className="text-lg text-gray-700 mb-2">
              분석 결과에 따른 최적의 배경색을 선택해주세요.
            </p>
            <p className="text-sm text-gray-500">
              기본적인 피부보정이 완료되었습니다.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {BACKGROUND_COLORS.map((bg) => (
              <div
                key={bg.id}
                onClick={() => handleColorSelect(bg.id)}
                className={`relative aspect-[3/4] rounded-lg overflow-hidden cursor-pointer transition-all duration-300 ${
                  selectedColor === bg.id
                    ? 'ring-4 ring-blue-400 transform scale-105'
                    : 'hover:shadow-lg'
                }`}
              >
                <Image
                  src={bg.image}
                  alt={`배경색 ${bg.name}`}
                  fill
                  className="object-cover"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-3 text-center">
                  {bg.name}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-center mt-8 space-x-4">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-2 bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 rounded-lg transition duration-300"
            >
              처음으로
            </button>
            <button
              onClick={handleNext}
              disabled={!selectedColor}
              className={`px-6 py-2 rounded-lg transition duration-300 ${
                selectedColor
                  ? 'bg-pink-100/70 hover:bg-pink-200/80 text-gray-700'
                  : 'bg-gray-300 cursor-not-allowed text-gray-500'
              }`}
            >
              다음 단계로
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 