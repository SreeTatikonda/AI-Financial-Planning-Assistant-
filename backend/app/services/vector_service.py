"""
Vector Database Service - ChromaDB for financial knowledge retrieval
Stores pre-embedded financial knowledge, best practices, and FAQs
"""
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from app.utils.config import settings as app_settings

logger = logging.getLogger(__name__)


class VectorService:
    """
    ChromaDB service for semantic search over financial knowledge
    Pre-loaded with financial best practices, tax rules, budgeting tips
    """
    
    def __init__(self):
        """Initialize ChromaDB client and collections"""
        try:
            self.client = chromadb.PersistentClient(
                path=app_settings.CHROMA_PERSIST_DIR,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collections
            self.financial_knowledge = self._get_or_create_collection(
                "financial_knowledge",
                "General financial planning knowledge and best practices"
            )
            
            self.budgeting_tips = self._get_or_create_collection(
                "budgeting_tips",
                "Budgeting strategies and spending optimization tips"
            )
            
            self.tax_rules = self._get_or_create_collection(
                "tax_rules",
                "Tax regulations and optimization strategies"
            )
            
            # Initialize with default knowledge if empty
            self._initialize_knowledge_base()
            
            logger.info("Vector service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    def _get_or_create_collection(self, name: str, metadata: str):
        """Get existing collection or create new one"""
        try:
            return self.client.get_collection(name=name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"description": metadata}
            )
    
    def _initialize_knowledge_base(self):
        """Initialize collections with default financial knowledge"""
        
        # Check if already initialized
        if self.financial_knowledge.count() > 0:
            logger.info("Knowledge base already initialized")
            return
        
        logger.info("Initializing financial knowledge base...")
        
        # Financial knowledge base
        financial_docs = [
            {
                "id": "fk_001",
                "text": "The 50/30/20 budgeting rule suggests allocating 50% of income to needs, 30% to wants, and 20% to savings and debt repayment.",
                "category": "budgeting"
            },
            {
                "id": "fk_002",
                "text": "An emergency fund should cover 3-6 months of essential expenses. This provides a financial safety net for unexpected events.",
                "category": "savings"
            },
            {
                "id": "fk_003",
                "text": "The debt avalanche method prioritizes paying off high-interest debt first, potentially saving more money on interest over time.",
                "category": "debt"
            },
            {
                "id": "fk_004",
                "text": "Dollar-cost averaging is an investment strategy where you invest a fixed amount regularly, regardless of market conditions, to reduce the impact of volatility.",
                "category": "investing"
            },
            {
                "id": "fk_005",
                "text": "A good debt-to-income ratio is generally below 36%, with no more than 28% going toward housing costs.",
                "category": "debt"
            },
            {
                "id": "fk_006",
                "text": "Compound interest is the addition of interest to the principal sum, allowing your money to grow exponentially over time. Starting early maximizes this effect.",
                "category": "investing"
            },
            {
                "id": "fk_007",
                "text": "Diversification reduces risk by spreading investments across different asset classes, sectors, and geographic regions.",
                "category": "investing"
            },
            {
                "id": "fk_008",
                "text": "Track every expense for at least one month to understand spending patterns and identify areas for improvement.",
                "category": "budgeting"
            }
        ]
        
        self.financial_knowledge.add(
            documents=[doc["text"] for doc in financial_docs],
            ids=[doc["id"] for doc in financial_docs],
            metadatas=[{"category": doc["category"]} for doc in financial_docs]
        )
        
        # Budgeting tips
        budgeting_docs = [
            {
                "id": "bt_001",
                "text": "Reduce dining out expenses by meal planning and cooking at home. This can save hundreds of dollars per month.",
                "category": "food"
            },
            {
                "id": "bt_002",
                "text": "Cancel unused subscriptions. Review all recurring charges monthly and eliminate services you rarely use.",
                "category": "subscriptions"
            },
            {
                "id": "bt_003",
                "text": "Use the 24-hour rule for impulse purchases. Wait a day before buying non-essential items to avoid regret purchases.",
                "category": "shopping"
            },
            {
                "id": "bt_004",
                "text": "Automate savings by setting up automatic transfers to savings accounts on payday. Pay yourself first.",
                "category": "savings"
            },
            {
                "id": "bt_005",
                "text": "Negotiate bills like insurance, internet, and phone plans annually. Providers often offer better rates to retain customers.",
                "category": "bills"
            }
        ]
        
        self.budgeting_tips.add(
            documents=[doc["text"] for doc in budgeting_docs],
            ids=[doc["id"] for doc in budgeting_docs],
            metadatas=[{"category": doc["category"]} for doc in budgeting_docs]
        )
        
        # Tax rules (simplified - can be expanded)
        tax_docs = [
            {
                "id": "tx_001",
                "text": "401(k) contributions are pre-tax, reducing your taxable income. For 2024, the contribution limit is $23,000 for those under 50.",
                "category": "retirement"
            },
            {
                "id": "tx_002",
                "text": "Tax-loss harvesting involves selling losing investments to offset capital gains and reduce tax liability.",
                "category": "investing"
            },
            {
                "id": "tx_003",
                "text": "Health Savings Accounts (HSAs) offer triple tax benefits: tax-deductible contributions, tax-free growth, and tax-free withdrawals for medical expenses.",
                "category": "healthcare"
            }
        ]
        
        self.tax_rules.add(
            documents=[doc["text"] for doc in tax_docs],
            ids=[doc["id"] for doc in tax_docs],
            metadatas=[{"category": doc["category"]} for doc in tax_docs]
        )
        
        logger.info(f"Knowledge base initialized with {len(financial_docs) + len(budgeting_docs) + len(tax_docs)} documents")
    
    def search(
        self,
        query: str,
        collection_name: str = "financial_knowledge",
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across financial knowledge
        
        Args:
            query: Search query
            collection_name: Which collection to search
            n_results: Number of results to return
        
        Returns:
            List of relevant documents with metadata
        """
        try:
            collection_map = {
                "financial_knowledge": self.financial_knowledge,
                "budgeting_tips": self.budgeting_tips,
                "tax_rules": self.tax_rules
            }
            
            collection = collection_map.get(collection_name, self.financial_knowledge)
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def search_all_collections(
        self,
        query: str,
        n_results_per_collection: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all collections
        
        Args:
            query: Search query
            n_results_per_collection: Results per collection
        
        Returns:
            Dictionary with results from each collection
        """
        return {
            "financial_knowledge": self.search(query, "financial_knowledge", n_results_per_collection),
            "budgeting_tips": self.search(query, "budgeting_tips", n_results_per_collection),
            "tax_rules": self.search(query, "tax_rules", n_results_per_collection)
        }
    
    def add_document(
        self,
        text: str,
        collection_name: str = "financial_knowledge",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a new document to the knowledge base"""
        try:
            collection_map = {
                "financial_knowledge": self.financial_knowledge,
                "budgeting_tips": self.budgeting_tips,
                "tax_rules": self.tax_rules
            }
            
            collection = collection_map.get(collection_name, self.financial_knowledge)
            
            # Generate ID
            doc_id = f"{collection_name}_{collection.count() + 1}"
            
            collection.add(
                documents=[text],
                ids=[doc_id],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"Added document {doc_id} to {collection_name}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
