'use client';

import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { QRCodeSVG } from 'qrcode.react';
import { useState } from 'react';

export default function FinalPage() {
  const params = useParams();
  const router = useRouter();
  const [showQR, setShowQR] = useState(false);

  // 임시 이미지 URL (실제로는 서버에서 생성된 이미지 URL을 사용해야 함)
  const imageUrl = `/images/photo${params.id}.jpg`;
  const downloadUrl = imageUrl; // 실제로는 다운로드 가능한 URL로 변경 필요

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">
          증명사진이 완성되었습니다
        </h1>

        <div className="space-y-6">
          <div className="relative aspect-[3/4] rounded-lg overflow-hidden shadow-lg mx-auto max-w-sm">
            <Image
              src={imageUrl}
              alt="완성된 증명사진"
              fill
              className="object-cover"
            />
          </div>

          <div className="flex flex-col items-center space-y-4">
            {showQR ? (
              <div className="bg-white p-4 rounded-lg shadow-md">
                <QRCodeSVG
                  value={downloadUrl}
                  size={200}
                  level="H"
                  includeMargin={true}
                />
              </div>
            ) : null}

            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={() => setShowQR(!showQR)}
                className="px-6 py-2 bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 rounded-lg transition duration-300"
              >
                {showQR ? 'QR코드 숨기기' : 'QR코드 보기'}
              </button>
              <a
                href={downloadUrl}
                download="증명사진.jpg"
                className="px-6 py-2 bg-pink-100/70 hover:bg-pink-200/80 text-gray-700 rounded-lg transition duration-300"
              >
                다운로드
              </a>
              <button
                onClick={() => router.push('/')}
                className="px-6 py-2 bg-gray-100/70 hover:bg-gray-200/80 text-gray-700 rounded-lg transition duration-300"
              >
                처음으로
              </button>
            </div>
          </div>

          <div className="text-center text-sm text-gray-500 mt-4">
            <p>QR코드를 스캔하거나 다운로드 버튼을 눌러 이미지를 저장하세요.</p>
            <p>이미지는 24시간 동안만 보관됩니다.</p>
          </div>
        </div>
      </div>
    </div>
  );
} 