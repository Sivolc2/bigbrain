from supabase import create_client
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class SupabaseManager:
    def __init__(self):
        self.memories_table = "memories"

    async def store_memory(self, memory: Dict) -> None:
        """
        Store a memory in the Supabase database
        """
        try:
            data = supabase.table(self.memories_table).insert(memory).execute()
            return data
        except Exception as e:
            print(f"Error storing memory: {e}")
            return None

    async def get_memories(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent memories from the Supabase database
        """
        try:
            response = supabase.table(self.memories_table)\
                .select("*")\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []

    async def search_memories(self, query: str) -> List[Dict]:
        """
        Search memories using text search
        """
        try:
            response = supabase.table(self.memories_table)\
                .select("*")\
                .textSearch("content", query)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a specific memory by ID
        """
        try:
            supabase.table(self.memories_table)\
                .delete()\
                .eq("id", memory_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
