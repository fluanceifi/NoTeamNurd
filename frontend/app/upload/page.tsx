'use client';

import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { BiCloudUpload } from 'react-icons/bi';

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null); // ✅ File 객체 저장용
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected); // ✅ 파일 저장
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(selected);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('http://127.0.0.1:5050/upload', {
  method: 'POST',
  body: formData,
});


      const data = await res.json();

      if (data.success) {
        console.log('분석 결과:', data.result);
        router.push('/result'); // 필요시 쿼리로 result 넘기기 가능
      } else {
        alert('분석 실패: ' + data.error);
      }
    } catch (error) {
      console.error('업로드 중 오류 발생:', error);
      alert('서버 오류');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-2xl w-full">
        <div className="space-y-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-800 mb-2">사진 업로드</h1>
            <p className="text-sm text-gray-500">
              증명사진으로 변환할 이미지를 선택해주세요
            </p>
          </div>

   <div
  className="relative aspect-[3/4] max-w-xs mx-auto border-2 border-dashed border-gray-300 rounded-lg overflow-hidden hover:border-gray-400 transition-colors cursor-pointer"
  onClick={() => fileInputRef.current?.click()}
>
  {selectedImage ? (
    <>
      <Image
        src={selectedImage}
        alt="업로드된 이미지"
        fill
        className="object-cover"
      />
    </>
  ) : (
    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
      <BiCloudUpload className="w-12 h-12 mb-2" />
      <p className="text-sm">클릭하여 이미지 선택</p>
      <p className="text-xs text-gray-400">또는 드래그 앤 드롭</p>
    </div>
  )}
  <input
    ref={fileInputRef}
    type="file"
    accept="image/*"
    onChange={handleFileChange}
    className="hidden"
  />
</div>


          <div className="flex justify-center space-x-4">
            <button
              onClick={() => router.push('/')}
              className="px-8 py-3 bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 rounded-lg transition duration-300"
            >
              돌아가기
            </button>
            <button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className={`px-8 py-3 rounded-lg text-gray-700 transition duration-300 ${
                !file || isUploading
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-pink-100/70 hover:bg-pink-200/80'
              }`}
            >
              {isUploading ? '분석 중...' : '업로드하기'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
