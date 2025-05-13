'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useParams } from 'next/navigation';
import { QRCodeSVG } from 'qrcode.react';

export default function FinalPage() {
  const params = useParams();
  const photoId = params.id;
  const [shareUrl, setShareUrl] = useState('');

  useEffect(() => {
    // 실제 배포 환경에서는 여기에 실제 도메인을 사용해야 합니다
    setShareUrl(`http://localhost:3000/share/${photoId}`);
  }, [photoId]);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          최종 결과
        </h2>

        <div className="flex flex-col md:flex-row items-center justify-center gap-8 mb-8">
          <div className="relative w-64 aspect-[3/4]">
            <Image
              src={`/images/photo${photoId}.jpg`}
              alt="최종 사진"
              fill
              className="object-cover rounded-lg"
            />
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="bg-white p-4 rounded-lg shadow-md">
              <QRCodeSVG value={shareUrl} size={200} />
            </div>
            <p className="text-center text-gray-600">
              QR 코드를 스캔하여<br />
              결과를 공유하세요
            </p>
          </div>
        </div>

        <div className="flex justify-center gap-4">
          <button
            onClick={() => window.print()}
            className="px-8 py-3 rounded-lg bg-pink-100/70 hover:bg-pink-200/80 text-gray-700 transition-all duration-300"
          >
            인쇄하기
          </button>
          <button
            onClick={() => {
              navigator.clipboard.writeText(shareUrl);
              alert('링크가 복사되었습니다!');
            }}
            className="px-8 py-3 rounded-lg bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 transition-all duration-300"
          >
            링크 복사하기
          </button>
        </div>
      </div>
    </main>
  );
} 