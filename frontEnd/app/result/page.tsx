// 📄 app/results/page.tsx

import { Suspense } from 'react';
import ResultsContent from './results-content'; // 👈 아래 2번 파일

// Suspense가 감싸는 동안 보여줄 로딩 화면
function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-pink-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">결과를 불러오는 중...</p>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    // <Suspense>로 감싸서 빌드 오류를 해결합니다.
    <Suspense fallback={<LoadingFallback />}>
      <ResultsContent />
    </Suspense>
  );
}