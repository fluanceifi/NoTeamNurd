'use client';

import {useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function FinalPage() {
  const router = useRouter();
  const [finalImage, setFinalImage] = useState(null);
  const [loading, setLoading] = useState(true);

  // --- ▼▼▼ 이메일 전송을 위한 상태 추가 ▼▼▼ ---
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailMessage, setEmailMessage] = useState('');
  // --- ▲▲▲ 여기까지 추가 ▲▲▲ ---

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

  // --- ▼▼▼ 이메일 전송 핸들러 함수 추가 ▼▼▼ ---
  const handleSendEmail = async () => {
    if (!email) {
      setEmailMessage('⚠️ 이메일 주소를 입력해주세요.');
      return;
    }
    // 간단한 이메일 형식 검사
    if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailMessage('⚠️ 올바른 이메일 형식이 아닙니다.');
      return;
    }

    setEmailLoading(true);
    setEmailMessage('');

    try {
      const response = await fetch('http://localhost:5050/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setEmailMessage(`✅ ${data.message}`);
      } else {
        setEmailMessage(`❌ 오류: ${data.message}`);
      }
    } catch (error) {
      console.error('Email sending error:', error);
      setEmailMessage('❌ 서버와 통신 중 오류가 발생했습니다.');
    } finally {
      setEmailLoading(false);
    }
  };
  // --- ▲▲▲ 여기까지 추가 ▲▲▲ ---

  //폰트 색 추가
  const getMessageColor = () => {
    if (emailMessage.startsWith('✅')) {
      return 'text-green-600'; // 성공 메시지 (초록색)
    }
    if (emailMessage.startsWith('❌') || emailMessage.startsWith('⚠️')) {
      return 'text-red-600'; // 오류 또는 경고 메시지 (빨간색)
    }
    return 'text-gray-700'; // 기본 텍스트 색상
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

            {/* --- ▼▼▼ 이메일 전송 UI 섹션 추가 ▼▼▼ --- */}
            <div className="border-t pt-6 mt-6">
              <h3 className="text-lg font-semibold text-center mb-4 text-gray-800">
                이메일로 사진 받기
              </h3>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 max-w-md mx-auto">
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="이메일 주소를 입력하세요"
                    disabled={emailLoading}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-pink-500 focus:border-pink-500 transition text-gray-900 placeholder-gray-500"
                />
                <button
                    onClick={handleSendEmail}
                    disabled={emailLoading || !finalImage}
                    className="w-full sm:w-auto px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition duration-300 font-semibold disabled:bg-gray-400"
                >
                  {emailLoading ? '전송 중...' : '전송'}
                </button>
              </div>
              {emailMessage && (
                  <p className={`text-center mt-3 text-sm font-medium ${getMessageColor()}`}>
                    {emailMessage}
                  </p>
              )}
            </div>
            {/* --- ▲▲▲ 여기까지 추가 ▲▲▲ --- */}

            <div className="text-center text-sm text-gray-500 mt-4">
              <p>다운로드 버튼을 눌러 증명사진을 저장하세요.</p>
              <p>고화질 JPEG 파일로 저장됩니다.</p>
            </div>
          </div>
        </div>
      </div>
  );
}