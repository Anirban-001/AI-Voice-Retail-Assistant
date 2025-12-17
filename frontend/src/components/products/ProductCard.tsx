import { ShoppingBag } from "lucide-react";
import type { Product } from "../../lib/types";
import { formatCurrency } from "../../lib/utils";

interface ProductCardProps {
  product: Product;
  onAdd?: (id: string) => void;
}

export function ProductCard({ product, onAdd }: ProductCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 flex flex-col gap-3">
      <div className="h-36 rounded-xl bg-black/40 flex items-center justify-center text-white/40 text-xs uppercase tracking-[0.2em]">
        {product.category}
      </div>
      <div>
        <h3 className="text-base font-semibold">{product.name}</h3>
        <p className="text-sm text-white/70 line-clamp-2">{product.description}</p>
      </div>
      <div className="flex items-center justify-between mt-auto">
        <span className="text-lg font-semibold">{formatCurrency(product.price)}</span>
        <button
          type="button"
          onClick={() => onAdd?.(product.id)}
          className="flex items-center gap-2 rounded-full border border-white/15 px-3 py-1.5 text-xs uppercase tracking-wide text-white/80"
        >
          <ShoppingBag size={14} /> Add
        </button>
      </div>
    </div>
  );
}
