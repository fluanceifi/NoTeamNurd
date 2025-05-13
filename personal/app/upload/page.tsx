'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function UploadPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (selectedFile) {
      setIsAnalyzing(true);
      // 여기에 퍼스널 컬러 분석 로직 추가
      // 임시로 3초 후 결과 페이지로 이동하도록 설정
      setTimeout(() => {
        router.push('/results?type=summer');
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-2xl font-bold text-center mb-6">사진 업로드</h1>

        <div className="space-y-6">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-500 hover:text-blue-600"
            >
              {preview ? (
                <div className="relative w-full h-64">
                  <Image
                    src={preview}
                    alt="Preview"
                    fill
                    style={{ objectFit: 'contain' }}
                  />
                </div>
              ) : (
                <div className="py-8">
                  클릭하여 사진 업로드하기
                </div>
              )}
            </label>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition duration-300"
            >
              돌아가기
            </button>
            <button
              onClick={handleAnalyze}
              disabled={!selectedFile || isAnalyzing}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-300 disabled:bg-blue-300"
            >
              {isAnalyzing ? '분석 중...' : '분석하기'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 