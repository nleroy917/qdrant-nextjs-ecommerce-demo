'use client'

import { SearchBar } from '@/components/search-bar'

export default function Home() {
  return (
    <div className="flex flex-col gap-2 p-2">
      <div className="flex flex-row items-center justify-center w-2/3 max-w-2xl">
        <SearchBar />
      </div>
    </div>
  )
}
