'use client';

import { useEffect, useState } from 'react';

// 2. ImageOption 타입 정의
type ImageOption = {
  id: number;
  base64: string;
};

export default function ResultsContent() {
  // 3. params 변수 선언 삭제
  const [images, setImages] = useState<ImageOption[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [colorCategory, setColorCategory] = useState<string | null>(null);

  useEffect(() => {
    // Flask 서버에서 업로드 결과 요청
    fetch('/api/uploaded')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const imgList = data.images.map((b64: string, index: number) => ({
            id: index,
            base64: b64,
          }));
          setImages(imgList);
          setColorCategory(data.color_category); // 4. colorCategory 변수 사용 확인
        }
      })
      .catch(err => {
        console.error('이미지 로드 실패:', err);
      });
  }, []); // 종속성 배열이 비어 있으므로 params를 사용하지 않음

  const handleSelect = (id: number) => {
    setSelectedId(id);
  };

  const handleNext = () => {
    if (selectedId !== null) {
      console.log('선택된 이미지 ID:', selectedId);
      window.location.href = `/result/expression/${selectedId}`;
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          퍼스널컬러 분석 결과
        </h1>

        {/* 5. colorCategory 변수를 사용하는 JSX 확인 */}
        {colorCategory && (
            <p className="text-center text-lg font-medium text-pink-600 mb-6">
            당신의 퍼스널컬러는 <strong>{colorCategory}</strong>입니다.
            </p>
        )}

        <p className="text-center mb-8 text-gray-700">
          아래 이미지 중 하나를 선택해주세요. (임시 결과)
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {images.map((img) => (
            <div
              key={img.id}
              onClick={() => handleSelect(img.id)}
              className={`relative aspect-[3/4] rounded-lg overflow-hidden cursor-pointer transition-all duration-300 ${
                selectedId === img.id
                  ? 'ring-4 ring-blue-400 transform scale-105'
                  : 'hover:shadow-lg'
              }`}
            >
              <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`data:image/jpeg;base64,${img.base64}`}
                alt={`옵션 ${img.id + 1}`}
                className="object-cover w-full h-full"
              />
              </>
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-3 text-center">
                옵션 {img.id + 1}
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-center mt-8 space-x-4">
          <button
            onClick={() => window.location.href = '/'}
            className="px-6 py-2 bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 rounded-lg transition duration-300"
          >
            처음으로
          </button>

          {/* 6. handleNext 함수를 사용하는 JSX 확인 */}
          <button
            onClick={handleNext}
            disabled={selectedId === null}
            className={`px-6 py-2 rounded-lg transition duration-300 ${
              selectedId !== null
                ? 'bg-pink-100/70 hover:bg-pink-200/80 text-gray-700'
                : 'bg-gray-300 cursor-not-allowed text-gray-500'
            }`}
          >
            다음 단계로
          </button>
        </div>
      </div>
    </div>
  );
}