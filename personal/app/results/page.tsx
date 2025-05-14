'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { QRCodeSVG } from 'qrcode.react';

const colorTypes = {
  spring: {
    title: '봄 웜톤',
    description: '밝고 선명한 톤의 증명사진이 잘 어울립니다.',
    backgrounds: ['#FFE4E1', '#FFF0F5', '#F0F8FF'],
  },
  summer: {
    title: '여름 쿨톤',
    description: '부드럽고 시원한 톤의 증명사진이 잘 어울립니다.',
    backgrounds: ['#E6E6FA', '#F0FFFF', '#F5F5F5'],
  },
  autumn: {
    title: '가을 웜톤',
    description: '차분하고 깊이감 있는 톤의 증명사진이 잘 어울립니다.',
    backgrounds: ['#FFF8DC', '#FAF0E6', '#FDF5E6'],
  },
  winter: {
    title: '겨울 쿨톤',
    description: '선명하고 차가운 톤의 증명사진이 잘 어울립니다.',
    backgrounds: ['#F0F8FF', '#F5FFFA', '#F8F8FF'],
  },
};

export default function ResultsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedBackground, setSelectedBackground] = useState<string>('');
  const colorType = searchParams.get('type') as keyof typeof colorTypes || 'spring';

  useEffect(() => {
    setSelectedBackground(colorTypes[colorType].backgrounds[0]);
  }, [colorType]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          당신의 퍼스널 컬러는 {colorTypes[colorType].title}입니다
        </h1>
        <p className="text-center text-gray-600 mb-8">
          {colorTypes[colorType].description}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {colorTypes[colorType].backgrounds.map((bg, index) => (
            <div
              key={bg}
              className="relative aspect-[3/4] rounded-lg overflow-hidden cursor-pointer"
              style={{ backgroundColor: bg }}
              onClick={() => setSelectedBackground(bg)}
            >
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-gray-600">추천 배경 {index + 1}</p>
                </div>
              </div>
              {selectedBackground === bg && (
                <div className="absolute inset-0 border-4 border-blue-500 rounded-lg" />
              )}
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-col items-center">
          <QRCodeSVG
            value={`https://your-domain.com/share?type=${colorType}&bg=${selectedBackground.substring(1)}`}
            size={128}
            className="mb-4"
          />
          <p className="text-sm text-gray-500">
            QR 코드를 스캔하여 결과를 공유하세요
          </p>
        </div>

        <div className="mt-8 flex justify-center space-x-4">
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition duration-300"
          >
            처음으로
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-300"
          >
            저장하기
          </button>
        </div>
      </div>
    </div>
  );
}