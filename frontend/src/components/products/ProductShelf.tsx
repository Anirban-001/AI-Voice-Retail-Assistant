import type { Product } from "../../lib/types";
import { ProductCard } from "./ProductCard";
import { Panel, PanelHeader } from "../layout/Panels";

interface ProductShelfProps {
  products: Product[];
  onAdd?: (id: string) => Promise<void> | void;
}

export function ProductShelf({ products, onAdd }: ProductShelfProps) {
  return (
    <Panel>
      <PanelHeader title="Live Recommendations" />
      {products.length === 0 ? (
        <div className="text-sm text-white/60">No products yet. Ask the agent for something specific.</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAdd={onAdd} />
          ))}
        </div>
      )}
    </Panel>
  );
}
