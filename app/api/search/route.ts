import { NextRequest, NextResponse } from 'next/server'
import { QdrantClient } from '@qdrant/js-client-rest'
import {
  FlagEmbedding,
  SparseTextEmbedding,
  EmbeddingModel,
  SparseEmbeddingModel,
} from 'fastembed'

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

export interface ProductPayload {
  Product_name: string
  Price_corrected: number
  colors: string
  Pattern: string
  Description: string
  Gender: string
  image_base64?: string
  image_filename?: string
}

export interface Product {
  id: string | number
  payload: ProductPayload
  score?: number
}

export async function POST(request: NextRequest) {
  try {
    const body: SearchParams = await request.json()
    const { query: queryText, filters } = body

    const denseModel = await FlagEmbedding.init({
      model: EmbeddingModel.BGESmallENV15,
    })
    const sparseModel = await SparseTextEmbedding.init({
      model: SparseEmbeddingModel.SpladePPEnV1,
    })

    const denseEmbedding = (await denseModel.embed(['This is a test']).next())
      .value!

    const sparseEmbedding = (await sparseModel.embed(['This is a test']).next())
      .value!

    const sparseIndices = sparseEmbedding[0].indices
    const sparseValues = sparseEmbedding[0].values

    // TODO: Implement actual search logic
    // 1. Generate embeddings for the query
    // 2. Build Qdrant filter based on filters param
    // 3. Search Qdrant collection
    // 4. Return results
    const results = await client.query('products', {
      prefetch: [
        {
          query: Array.from(denseEmbedding[0]),
          using: 'dense',
          limit: 50,
        },
        {
          query: {
            values: sparseValues,
            indices: sparseIndices,
          },
          using: 'sparse',
          limit: 50,
        },
      ],
      query: {
        fusion: 'rrf',
      },
      with_payload: true,
      limit: 50,
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
