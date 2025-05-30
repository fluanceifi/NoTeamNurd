'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function ExpressionPage() {
  const params = useParams();
  const router = useRouter();
  const [outfitOptions, setOutfitOptions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 선택된 배경으로 3가지 의상 옵션 생성
    fetch('http://localhost:5050/outfit-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selected_index: parseInt(params.id)  // URL의 [id]
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        setOutfitOptions(data.options);  // [원본, 정장, 캐주얼]
      } else {
        console.error('의상 옵션 로드 실패:', data.message);
      }
    })
    .catch(error => {
      console.error('API 호출 실패:', error);
    })
    .finally(() => {
      setLoading(false);
    });
  }, [params.id]);

  const handleSelect = (optionType) => {
    setSelectedId(optionType);
  };

const handleNext = () => {
  if (selectedId !== null) {
    // 선택된 의상으로 최종 이미지 생성 요청
    fetch('http://localhost:5050/generate-final', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selected_index: parseInt(params.id),
        selected_outfit: selectedId
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        console.log('최종 이미지 생성 완료');
        router.push(`/result/final/${selectedId}`);
      } else {
        console.error('최종 이미지 생성 실패:', data.message);
      }
    })
    .catch(error => {
      console.error('API 호출 실패:', error);
    });
  }
};

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-pink-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">의상 스타일을 준비하는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          의상 스타일을 선택해주세요
        </h1>

        <p className="text-center mb-8 text-gray-700">
          아래 옵션 중 하나를 선택해주세요.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {outfitOptions.map((option) => (
            <div
              key={option.type}
              onClick={() => handleSelect(option.type)}
              className={`relative aspect-[3/4] rounded-lg overflow-hidden cursor-pointer transition-all duration-300 ${
                selectedId === option.type
                  ? 'ring-4 ring-blue-400 transform scale-105'
                  : 'hover:shadow-lg'
              }`}
            >
              <img
                src={`data:image/jpeg;base64,${option.image}`}
                alt={option.label}
                className="object-cover w-full h-full"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-3 text-center">
                {option.label}
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-center mt-8 space-x-4">
          <button
            onClick={() => router.back()}
            className="px-6 py-2 bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 rounded-lg transition duration-300"
          >
            이전으로
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
            완료
          </button>
        </div>
      </div>
    </div>
  );
}