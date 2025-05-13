'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';

export default function ResultPage() {
  const [selectedImage, setSelectedImage] = useState<number | null>(null);

  const recommendedPhotos = [
    { id: 1, src: '/images/photo1.jpg', background: '파스텔 핑크' },
    { id: 2, src: '/images/photo2.jpg', background: '소프트 블루' },
    { id: 3, src: '/images/photo3.jpg', background: '라이트 그레이' },
  ];

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          추천 증명사진
        </h2>
        <p className="text-center text-gray-600 mb-8">
          가장 잘 어울리는 배경색으로 3가지 스타일을 추천해드립니다
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {recommendedPhotos.map((photo) => (
            <div
              key={photo.id}
              className={`relative rounded-lg overflow-hidden cursor-pointer transition-all duration-300 ${
                selectedImage === photo.id
                  ? 'ring-4 ring-blue-400 transform scale-105'
                  : 'hover:shadow-lg'
              }`}
              onClick={() => setSelectedImage(photo.id)}
            >
              <div className="aspect-[3/4] relative">
                <Image
                  src={photo.src}
                  alt={`추천 스타일 ${photo.id}`}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-3 text-center">
                {photo.background}
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-center">
          <Link
            href={selectedImage ? `/result/expression/${selectedImage}` : '#'}
            className={`px-8 py-3 rounded-lg transition-all duration-300 ${
              selectedImage
                ? 'bg-pink-100/70 hover:bg-pink-200/80 text-gray-700'
                : 'bg-gray-300 cursor-not-allowed text-gray-500'
            }`}
          >
            다음 단계로
          </Link>
        </div>
      </div>
    </main>
  );
} 