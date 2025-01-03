import qdrant_client
from qdrant_client.models import VectorParams, Field
from langchain.vectorstores import Qdrant

# Setup connection
client = qdrant_client.QdrantClient(url="http://localhost:6333")
vector_store = Qdrant(client=client, collection_name="agent_actions", embedding=embedding_function)

# Create collection and vector index
client.create_collection(
    collection_name="agent_actions",
    vectors_config=VectorParams(size=512, distance="Cosine")
)

# Add vectors to store
def add_to_vector_store(agent_id, observation_vector, db: Session):
    vector_store.add(vectors=[observation_vector], metadatas=[{"agent_id": agent_id}])

