import os
import sys
from abc import ABC, abstractmethod
from typing import List

# ### Problem Statement:

# Current AI architectures rely heavily on retrieval-augmented generation (RAG), which introduces inefficiencies in information retrieval and synthesis. The goal of this project is to develop a novel hierarchical AI approach, where AI agents form a structured tree to process and summarize information progressively. This method eliminates the need for RAG by allowing knowledge to bubble up through layers of specialized agents.

# ### Proposed Solution:

# - **Hierarchical Tree Structure:**
#     - **Leaf AI Agents:** Ingest raw source files and become domain experts on specific topics.
#     - **Intermediate AI Agents:** Summarize and refine knowledge from lower layers.
#     - **Root AI Agent:** Provides the final, high-level synthesis of all collected and processed information. This is another intermediate agent in practice.


class Node(ABC):
    """
    Abstract base Node class.
    All subclasses must implement the summarize() method.
    """

    @abstractmethod
    def summarize(self) -> str:
        """
        Produce a summary as a string.
        """
        pass


class LeafNode(Node):
    """
    LeafNode ingests files from a folder (or a single file) and produces a summary.
    """

    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.processed_text = self._ingest_files(folder_path)

    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary by looking at its first few bytes.
        """
        try:
            with open(file_path, 'rb') as f:
                # Read first 1024 bytes to check for binary content
                chunk = f.read(1024)
                return b'\0' in chunk  # Binary files typically contain null bytes
        except Exception:
            return True  # If we can't read the file, treat it as binary

    def _ingest_files(self, folder_path: str) -> str:
        """
        Ingest all files in the folder and return formatted content.
        Each file's contents are labeled with its relative path.
        Silently skips binary files.
        """
        all_text = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)

                if self._is_binary_file(file_path):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()

                    # Format the file content with its path
                    formatted_content = (
                        f"Contents of file {rel_path}:\n\n```\n{file_content}\n```\n"
                    )
                    all_text.append(formatted_content)
                except (UnicodeDecodeError, Exception):
                    continue

        return "\n\n".join(all_text)

    def summarize(self) -> str:
        """
        Summarize the ingested text. For now, let's just return a placeholder
        or the raw text. In practice, you'd use an LLM or your own summarization
        algorithm.
        """
        # Placeholder for your real summarization logic
        # e.g. call an LLM or a custom summarizer on self.processed_text
        return f"Summary of folder '{self.folder_path}' with content length {len(self.processed_text)}"


class TopLevelLeafNode(LeafNode):
    """
    A specialized LeafNode that only processes files in the immediate directory,
    ignoring subdirectories. This is useful for handling "straggler" files that
    exist alongside subdirectories in a parent folder.
    """

    def _ingest_files(self, folder_path: str) -> str:
        """
        Ingest only the files in the immediate directory, ignoring subdirectories.
        Each file's contents are labeled with its relative path.
        Silently skips binary files.
        """
        all_text = []

        for item in os.listdir(folder_path):
            file_path = os.path.join(folder_path, item)
            if not os.path.isfile(file_path):  # Skip directories
                continue

            if self._is_binary_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                # Format the file content with its path
                formatted_content = (
                    f"Contents of file {item}:\n\n```\n{file_content}\n```\n"
                )
                all_text.append(formatted_content)
            except (UnicodeDecodeError, Exception):
                continue

        return "\n\n".join(all_text)

    def summarize(self) -> str:
        """
        Summarize the ingested text, specifically noting these are top-level files.
        """
        return f"Summary of top-level files in '{self.folder_path}' with content length {len(self.processed_text)}"


class PlannerNode(Node):
    """
    PlannerNode holds a list of children nodes.
    It queries each child for its summary, then synthesizes a final result.
    """

    def __init__(self, children: List[Node]):
        self.children = children

    def summarize(self) -> str:
        """
        Summarize by aggregating the summaries from all child nodes.
        In a real system, you'd probably do more sophisticated orchestration.
        """
        summaries = [child.summarize() for child in self.children]

        # For demonstration, we'll just join the summaries
        # In a more advanced use case, you'd feed these into another LLM or aggregator.
        combined_summary = "\n\n".join(summaries)

        # Optionally, you could do another pass of summarization on 'combined_summary'
        # with an LLM or text summarizer. For now, returning as-is.
        return f"PlannerNode Summary:\n{combined_summary}"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_repo>")
        sys.exit(1)

    repo_path = sys.argv[1]

    # Handle root level files
    root_files_node = TopLevelLeafNode(repo_path)

    # Frontend structure
    frontend_root = os.path.join(repo_path, "frontend")
    frontend_top_files = TopLevelLeafNode(frontend_root)
    frontend_src = LeafNode(os.path.join(frontend_root, "src"))
    frontend_public = LeafNode(os.path.join(frontend_root, "public"))
    
    frontend_planner = PlannerNode([
        frontend_top_files,
        frontend_src,
        frontend_public
    ])

    # Backend structure
    backend_root = os.path.join(repo_path, "backend")
    backend_top_files = TopLevelLeafNode(backend_root)
    backend_datasets = LeafNode(os.path.join(backend_root, "datasets"))
    backend_schemas = LeafNode(os.path.join(backend_root, "schemas"))
    backend_scripts = LeafNode(os.path.join(backend_root, "scripts"))
    backend_services = LeafNode(os.path.join(backend_root, "services"))
    backend_tests = LeafNode(os.path.join(backend_root, "tests"))

    backend_planner = PlannerNode([
        backend_top_files,
        backend_datasets,
        backend_schemas,
        backend_scripts,
        backend_services,
        backend_tests
    ])

    # Root planner combines everything
    root_planner = PlannerNode([
        root_files_node,
        frontend_planner,
        backend_planner
    ])

    # Get the overall summary
    summary_output = root_planner.summarize()
    print("\nTree-structured Summary:")
    print("=" * 80)
    print(summary_output)
