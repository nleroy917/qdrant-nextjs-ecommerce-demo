import { NextRequest, NextResponse } from 'next/server'
import { QdrantClient } from '@qdrant/js-client-rest'

const client = new QdrantClient({
  url: process.env.QDRANT_URL || 'http://localhost:6333',
  apiKey: process.env.QDRANT_API_KEY,
})

export interface SearchParams {
  query: string
  filters?: {
    color?: string
    gender?: string
    price?: [number, number]
  }
  limit?: number
}

export interface Product {
  id: string | number
  Product_name: string
  Price_corrected: number
  colors: string
  Pattern: string
  Description: string
  Gender: string
  image_base64?: string
  image_filename?: string
  score?: number
}

export async function POST(request: NextRequest) {
  try {
    const body: SearchParams = await request.json()
    const { query: queryText, filters } = body

    // TODO: Implement actual search logic
    // 1. Generate embeddings for the query
    // 2. Build Qdrant filter based on filters param
    // 3. Search Qdrant collection
    // 4. Return results
    const results = await client.query('products', {
      prefetch: [
        {
          query: {
            text: queryText,
            model: 'BAAI/bge-small-en-v1.5',
          },
          using: 'dense',
        },
        {
          query: {
            text: queryText,
            model: 'prithivida/Splade-PP-en-v1',
          },
          using: 'sparse',
        },
      ],
      query: {
        fusion: 'rrf',
      },
    })

    return NextResponse.json({
      success: true,
      results,
      count: results.points.length,
      query: queryText,
      filters,
    })
  } catch (error) {
    console.error('Search error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    )
  }
}
