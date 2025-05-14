'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

type ImageOption = {
  id: number;
  base64: string;
};

export default function ResultPage() {
  const router = useRouter();
  const [images, setImages] = useState<ImageOption[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    // Flask 서버에서 업로드 결과 요청
    fetch('http://localhost:5050/uploaded')  // 🔁 나중엔 이 부분을 `/upload`의 응답 처리 후로 옮길 수 있음
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const imgList = data.images.map((b64: string, index: number) => ({
            id: index,
            base64: b64,
          }));
          setImages(imgList);
        }
      })
      .catch(err => {
        console.error('이미지 로드 실패:', err);
      });
  }, []);

  const handleSelect = (id: number) => {
    setSelectedId(id);
  };

  const handleNext = () => {
    if (selectedId !== null) {
      console.log('선택된 이미지 ID:', selectedId);
      // 나중에 선택한 이미지 서버로 전송하거나 페이지 이동 가능
      router.push(`/result/expression/${selectedId}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          퍼스널컬러 분석 결과
        </h1>

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
              <img
                src={`data:image/jpeg;base64,${img.base64}`}
                alt={`옵션 ${img.id + 1}`}
                className="object-cover w-full h-full"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-3 text-center">
                옵션 {img.id + 1}
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
