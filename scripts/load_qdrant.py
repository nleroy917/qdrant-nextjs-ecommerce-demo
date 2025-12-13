import polars as pl
import base64

from sentence_transformers import SentenceTransformer
from fastembed import TextEmbedding, SparseTextEmbedding
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")

# dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")
# sparse_model = SparseTextEmbedding("naver/splade-v3")
dense_model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
sparse_model = SentenceTransformer("naver/splade-v3", device="mps")

df = pl.read_parquet('hf://datasets/rajuptvs/ecommerce_products_clip/data/train-00000-of-00001-1f042f20fd269c32.parquet')

# simulate a more realistic price column (remove chars, shift, cast)
df = df.with_columns(
    (pl.col("Price").str
    .replace(",", "").str
    .slice(1)
    .cast(pl.Int16) / pl.lit(10))
    .round()
    .cast(pl.Int16)
    .alias("Price_corrected")
)

# derive the gender column
df = df.with_columns(
    pl.when(pl.col("Product_name").str.contains("Men"))
    .then(pl.lit("Mens"))
    .when(pl.col("Product_name").str.contains("Women"))
    .then(pl.lit("Womens"))
    .otherwise(pl.lit("Unisex"))
    .alias("Gender")
)

# derive the column to embed
df = df.with_columns(
    pl.concat_str(
        [
            pl.col("Product_name"),
            pl.col("Price"),
            pl.col("colors"),
            pl.col("Pattern"),
            pl.col("Description"),
            pl.col("Other Details"),
            pl.col("Clipinfo")
        ],
        separator=" "
    ).alias("text_to_embed")
)

# convert binary image data to base64 string for JSON serialization
# The image column is a struct with bytes and path fields
df = df.with_columns(
    pl.col("image").struct.field("bytes").map_elements(
        lambda img_bytes: base64.b64encode(img_bytes).decode('utf-8') if img_bytes else None,
        return_dtype=pl.String
    ).alias("image_base64"),
    pl.col("image").struct.field("path").alias("image_filename")
).drop("image")


# dense_embeddings = list(dense_model.embed(df['text_to_embed'].to_list()))
# sparse_embeddings = list(sparse_model.embed(df['text_to_embed'].to_list()))
dense_embeddings = dense_model.encode(
    df['text_to_embed'].to_list(),
    show_progress_bar=True
)
sparse_embeddings = sparse_model.encode(
    df['text_to_embed'].to_list(),
    show_progress_bar=True
)


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

def generate_points_in_batches(
    batch_size: int = 128
):
    for i in range(0, len(df), batch_size):
        batch = df[i:i + batch_size]
        points = [
            models.PointStruct(
                id=idx,
                vector={
                    "dense": dense_embeddings[idx].tolist(),
                    "sparse": models.SparseVector(
                        indices=sparse_embeddings[idx].nonzero()[0].tolist(),
                        values=sparse_embeddings[idx][sparse_embeddings[idx].nonzero()[0]].tolist()
                    )
                },
                payload=row
            )
            for idx, row in enumerate(batch.iter_rows(named=True), start=i)
        ]
        yield points

for batch in generate_points_in_batches():
    client.upload_points(
        collection_name="products",
        points=batch
    )
