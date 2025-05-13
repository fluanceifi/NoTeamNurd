'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ExpressionPage() {
  const params = useParams();
  const photoId = params.id;
  const [isProcessing, setIsProcessing] = useState(false);

  const handleExpressionChange = async () => {
    setIsProcessing(true);
    // 여기에 표정 수정 로직 추가
    setTimeout(() => {
      setIsProcessing(false);
    }, 2000);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          표정 자연스럽게 수정하기
        </h2>
        <p className="text-center text-gray-600 mb-8">
          AI가 자연스러운 표정으로 수정해드립니다
        </p>

        <div className="flex justify-center mb-8">
          <div className="relative w-64 aspect-[3/4]">
            <Image
              src={`/images/photo${photoId}.jpg`}
              alt="선택된 사진"
              fill
              className="object-cover rounded-lg"
            />
          </div>
        </div>

        <div className="flex flex-col items-center gap-4">
          <button
            onClick={handleExpressionChange}
            disabled={isProcessing}
            className={`px-8 py-3 rounded-lg transition-all duration-300 ${
              isProcessing
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-pink-100/70 hover:bg-pink-200/80 text-gray-700'
            }`}
          >
            {isProcessing ? '처리중...' : '표정 자연스럽게 수정하기'}
          </button>

          {!isProcessing && (
            <Link
              href={`/result/final/${photoId}`}
              className="px-8 py-3 rounded-lg bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 transition-all duration-300"
            >
              다음 단계로
            </Link>
          )}
        </div>
      </div>
    </main>
  );
} 