import { ProductPayload } from '@/app/api/search/route'
import Image from 'next/image'

interface ProductCardProps {
  product: ProductPayload
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="border rounded-lg p-4 space-y-3 hover:shadow-lg transition-shadow">
      <div className="relative w-full aspect-square bg-gray-100 rounded-md overflow-hidden">
        {product.image_base64 ? (
          <Image
            src={`data:image/jpeg;base64,${product.image_base64}`}
            alt={product.Product_name}
            fill
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No Image
          </div>
        )}
      </div>
      <div className="space-y-1">
        <h3 className="font-semibold text-lg line-clamp-2">
          {product.Product_name}
        </h3>
        <p className="text-xl font-bold text-primary">
          ${product.Price_corrected.toFixed(2)}
        </p>
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          {product.Gender && (
            <span className="bg-accent px-2 py-1 rounded">
              {product.Gender}
            </span>
          )}
          {product.colors && (
            <span className="bg-accent px-2 py-1 rounded">
              {product.colors}
            </span>
          )}
          {product.Pattern && (
            <span className="bg-accent px-2 py-1 rounded">
              {product.Pattern}
            </span>
          )}
        </div>
        {product.Description && (
          <p className="text-sm text-muted-foreground line-clamp-2">
            {product.Description}
          </p>
        )}
      </div>
    </div>
  )
}
