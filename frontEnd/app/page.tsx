'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { BsCameraFill } from 'react-icons/bs';
import { BiCloudUpload } from 'react-icons/bi';
import localFont from 'next/font/local';

const bmdohyeon = localFont({
  src: '../public/fonts/BMDOHYEON_ttf.ttf',
  variable: '--font-bmdohyeon'
});

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white via-pink-100/80 to-blue-100/80 p-4">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-xl p-8 max-w-4xl w-full">
        <div className="text-center space-y-4">
          <p className="text-sm text-gray-500">
            인생 <span className="font-semibold">증명사진</span>을 만들어 드립니다
          </p>
          <h1 className={`text-3xl md:text-4xl font-bold text-gray-800 mb-2 ${bmdohyeon.className}`}>
            톤.. 정했톤?
          </h1>
          <p className="text-sm text-gray-500 mb-8">
            AI <span className="font-semibold">퍼스널컬러</span> 증명사진
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="relative aspect-square rounded-lg overflow-hidden">
            <Image
              src="/images/spring.jpg"
              alt="봄"
              fill
              className="object-cover hover:scale-110 transition-transform duration-300"
              style={{ objectPosition: 'center' }}
              sizes="(max-width: 768px) 100vw, 25vw"
            />
            <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
              <span className="text-white font-semibold text-lg drop-shadow-lg">Spring</span>
            </div>
          </div>

          <div className="relative aspect-square rounded-lg overflow-hidden">
            <Image
              src="/images/summer.jpg"
              alt="여름"
              fill
              className="object-cover hover:scale-110 transition-transform duration-300"
              style={{ objectPosition: 'center' }}
              sizes="(max-width: 768px) 100vw, 25vw"
            />
            <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
              <span className="text-white font-semibold text-lg drop-shadow-lg">Summer</span>
            </div>
          </div>

          <div className="relative aspect-square rounded-lg overflow-hidden">
            <Image
              src="/images/autumn.jpg"
              alt="가을"
              fill
              className="object-cover hover:scale-110 transition-transform duration-300"
              style={{ objectPosition: 'center' }}
              sizes="(max-width: 768px) 100vw, 25vw"
            />
            <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
              <span className="text-white font-semibold text-lg drop-shadow-lg">Autumn</span>
            </div>
          </div>

          <div className="relative aspect-square rounded-lg overflow-hidden">
            <Image
              src="/images/winter.jpg"
              alt="겨울"
              fill
              className="object-cover hover:scale-110 transition-transform duration-300"
              style={{ objectPosition: 'center' }}
              sizes="(max-width: 768px) 100vw, 25vw"
            />
            <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
              <span className="text-white font-semibold text-lg drop-shadow-lg">Winter</span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <Link href="/capture" 
                className="block w-full text-center bg-pink-100/70 hover:bg-pink-200/80 text-gray-700 font-semibold py-4 px-6 rounded-lg transition duration-300">
            <div className="flex items-center justify-center space-x-2">
              <BsCameraFill className="text-xl" />
              <span>실시간 측정하기</span>
            </div>
          </Link>
          <Link href="/upload"
                className="block w-full text-center bg-sky-100/70 hover:bg-sky-200/80 text-gray-700 font-semibold py-4 px-6 rounded-lg transition duration-300">
            <div className="flex items-center justify-center space-x-2">
              <BiCloudUpload className="text-xl" />
              <span>사진 업로드하기</span>
            </div>
          </Link>
        </div>
      </div>
    </main>
  );
}
