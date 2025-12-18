import polars as pl

from sentence_transformers import SentenceTransformer, SparseEncoder
# from fastembed import TextEmbedding, SparseTextEmbedding
from qdrant_client import QdrantClient, models

BATCH_SIZE = 128

client = QdrantClient(url="http://localhost:6333")

# dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")
# sparse_model = SparseTextEmbedding("prithivida/Splade_PP_en_v1")
dense_model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
sparse_model = SparseEncoder("prithivida/Splade_PP_en_v1", device="cpu")

# create collection if not exists
if not client.collection_exists("products"):
    client.create_collection(
        collection_name="products",
        vectors_config={
            "dense": models.VectorParams(
                size=dense_model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        },  # size and distance are model dependent
        sparse_vectors_config={"sparse": models.SparseVectorParams()},
    )

df = pl.read_parquet("../hm_ecommerce_products_enriched.parquet")

dense_embeddings = df['dense_embedding'].to_list()
sparse_indices = df['sparse_indices'].to_list()
sparse_values = df['sparse_values'].to_list()

def generate_points_in_batches(
    batch_size: int = BATCH_SIZE,
):
    for i in range(0, len(df), batch_size):
        batch = df[i:i + batch_size]
        points = [
            models.PointStruct(
                id=idx,
                vector={
                    "dense": dense_embeddings[idx],
                    "sparse": models.SparseVector(
                        indices=sparse_indices[idx],
                        values=sparse_values[idx]
                    )
                },
                payload={
                    "product_code": row.get("product_code"),
                    "prod_name": row.get("prod_name"),
                    "product_group_name": row.get("product_group_name"),
                    "colour_group_name": row.get("colour_group_name"),
                    "department_name": row.get("department_name"),
                    "section_name": row.get("section_name"),
                    "garment_group_name": row.get("garment_group_name"),
                    "detail_desc": row.get("detail_desc"),
                    "image_url": row.get("image_url"),
                }
            )
            for idx, row in enumerate(batch.iter_rows(named=True), start=i)
        ]
        yield points

for batch in generate_points_in_batches():
    client.upload_points(
        collection_name="products",
        points=batch
    )

# get collection info
collection_info = client.get_collection("products")
print("Collection info:")
print(collection_info)


# # Example: Add embeddings to the dataframe
# df = df.with_columns([
#     pl.Series("dense_embedding", [emb.tolist() for emb in dense_embeddings]),
#     pl.Series("sparse_indices", [emb.coalesce().indices()[0].tolist() for emb in sparse_embeddings]),
#     pl.Series("sparse_values", [emb.coalesce().values().tolist() for emb in sparse_embeddings]),
# ])
# # Count nulls and empty strings in the dataframe
# null_counts = df.null_count()
# print("Null counts per column:")
# print(null_counts)

# # Count empty strings in string columns
# empty_counts = {}
# for col in df.columns:
#     if df[col].dtype == pl.Utf8:
#         empty_counts[col] = (df[col] == "").sum()

# print("\nEmpty string counts per column:")
# for col, count in empty_counts.items():
#     print(f"  {col}: {count}")

# # drop nulls in detail_desc
# df = df.filter(pl.col("detail_desc").is_not_null())