import path from 'path'
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Ensure these packages are not bundled on the server (works with Turbopack)
  outputFileTracingRoot: path.join(__dirname, '../'),
  serverExternalPackages: [
    'onnxruntime-node',
    'fastembed',
    '@anush008/tokenizers',
  ],
}

export default nextConfig
