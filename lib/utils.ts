import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import fsp from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

// https://github.com/mastra-ai/mastra/issues/9217
async function getModelCachePath() {
  // ‼️ Make sure to use `/tmp` for Vercel functions here
  const isVercel = process.env.VERCEL === '1'
  const cachePath = isVercel
    ? path.join('/tmp', 'mastra', 'fastembed-models')
    : path.join(os.homedir(), '.cache', 'mastra', 'fastembed-models')
  await fsp.mkdir(cachePath, { recursive: true })
  return cachePath
}

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
