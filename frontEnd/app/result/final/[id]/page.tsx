'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function FinalPage() {
  const params = useParams();
  const router = useRouter();
  const [finalImage, setFinalImage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 최종 이미지 가져오기
    fetch('http://localhost:5050/final-image')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setFinalImage(data.image);
        } else {
          console.error('최종 이미지 로드 실패:', data.message);
        }
      })
      .catch(error => {
        console.error('API 호출 실패:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const downloadImage = () => {
    if (finalImage) {
      const link = document.createElement('a');
      link.href = `data:image/jpeg;base64,${finalImage}`;
      link.download = '증명사진.jpg';
      link.click();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-pink-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">최종 이미지를 준비하는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          증명사진이 완성되었습니다
        </h1>

        <div className="space-y-6">
          <div className="relative aspect-[3/4] rounded-lg overflow-hidden shadow-lg mx-auto max-w-sm">
            {finalImage ? (
              <img
                src={`data:image/jpeg;base64,${finalImage}`}
                alt="완성된 증명사진"
                className="object-cover w-full h-full"
              />
            ) : (
              <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                <p>이미지를 불러올 수 없습니다</p>
              </div>
            )}
          </div>

          <div className="flex flex-col items-center space-y-4">
            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={downloadImage}
                className="px-8 py-3 bg-pink-500 hover:bg-pink-600 text-white rounded-lg transition duration-300 font-semibold"
                disabled={!finalImage}
              >
                다운로드
              </button>
              <button
                onClick={() => router.push('/')}
                className="px-8 py-3 bg-gray-100/70 hover:bg-gray-200/80 text-gray-700 rounded-lg transition duration-300"
              >
                처음으로
              </button>
            </div>
          </div>

          <div className="text-center text-sm text-gray-500 mt-4">
            <p>다운로드 버튼을 눌러 증명사진을 저장하세요.</p>
            <p>고화질 JPEG 파일로 저장됩니다.</p>
          </div>
        </div>
      </div>
    </div>
  );
}