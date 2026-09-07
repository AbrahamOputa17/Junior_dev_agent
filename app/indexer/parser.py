import ast
import re
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class CodeChunk:
    file_path: str
    chunk_type: str  # function, class, import, route, block
    name: str
    start_line: int
    end_line: int
    content: str
    docstring: str = ""

class CodeParser:
    def parse_file(self, repo_root: str, rel_path: str, content: str) -> List[CodeChunk]:
        ext = rel_path.split(".")[-1].lower()
        if ext == "py":
            return self._parse_python(rel_path, content)
        else:
            return self._parse_generic(rel_path, content)

    def _parse_python(self, rel_path: str, content: str) -> List[CodeChunk]:
        chunks = []
        try:
            tree = ast.parse(content)
            lines = content.splitlines()

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start_line = node.lineno
                    end_line = getattr(node, "end_lineno", start_line + 10)
                    chunk_content = "\n".join(lines[start_line-1:end_line])
                    docstring = ast.get_docstring(node) or ""
                    
                    chunks.append(CodeChunk(
                        file_path=rel_path,
                        chunk_type="function",
                        name=node.name,
                        start_line=start_line,
                        end_line=end_line,
                        content=chunk_content,
                        docstring=docstring
                    ))

                elif isinstance(node, ast.ClassDef):
                    start_line = node.lineno
                    end_line = getattr(node, "end_lineno", start_line + 20)
                    chunk_content = "\n".join(lines[start_line-1:end_line])
                    docstring = ast.get_docstring(node) or ""
                    
                    chunks.append(CodeChunk(
                        file_path=rel_path,
                        chunk_type="class",
                        name=node.name,
                        start_line=start_line,
                        end_line=end_line,
                        content=chunk_content,
                        docstring=docstring
                    ))
        except Exception:
            return self._parse_generic(rel_path, content)

        if not chunks:
            return self._parse_generic(rel_path, content)
        return chunks

    def _parse_generic(self, rel_path: str, content: str) -> List[CodeChunk]:
        chunks = []
        lines = content.splitlines()
        
        # Regex for JS/TS function/class definitions
        fn_pattern = re.compile(r'(?:function\s+([a-zA-Z0-9_]+)|const\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\()')
        class_pattern = re.compile(r'class\s+([a-zA-Z0-9_]+)')

        for idx, line in enumerate(lines, 1):
            fn_match = fn_pattern.search(line)
            if fn_match:
                name = fn_match.group(1) or fn_match.group(2) or "anonymous"
                end_line = min(len(lines), idx + 20)
                chunks.append(CodeChunk(
                    file_path=rel_path,
                    chunk_type="function",
                    name=name,
                    start_line=idx,
                    end_line=end_line,
                    content="\n".join(lines[idx-1:end_line])
                ))

            class_match = class_pattern.search(line)
            if class_match:
                name = class_match.group(1)
                end_line = min(len(lines), idx + 30)
                chunks.append(CodeChunk(
                    file_path=rel_path,
                    chunk_type="class",
                    name=name,
                    start_line=idx,
                    end_line=end_line,
                    content="\n".join(lines[idx-1:end_line])
                ))

        if not chunks:
            # Fallback block chunk
            chunks.append(CodeChunk(
                file_path=rel_path,
                chunk_type="file_module",
                name=rel_path,
                start_line=1,
                end_line=len(lines),
                content=content[:2000]
            ))

        return chunks
