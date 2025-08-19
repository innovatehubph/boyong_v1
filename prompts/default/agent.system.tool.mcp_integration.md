**context7_tool** - Advanced context management and memory system using Upstash Redis. Provides persistent conversation memory, contextual search, and intelligent information retrieval across sessions. Use for maintaining long-term memory and context awareness.

**github_tool** - GitHub integration for repository management, code analysis, issue tracking, and collaboration. Connect to GitHub repositories, read code, create issues, manage pull requests, and analyze project structures. Requires GITHUB_PERSONAL_ACCESS_TOKEN.

**MCP Server Integration** - Model Context Protocol servers provide extended functionality:
- **Filesystem MCP**: Advanced file operations with 12 tools (read_file, write_file, search_files, directory_tree, etc.)
- **GitHub MCP**: Repository management and code analysis capabilities  
- **Context7 MCP**: Persistent memory and context management with Redis backend

**Context Management Features:**
- **Persistent Memory**: Conversations and context preserved across sessions
- **Intelligent Search**: Find relevant information from previous interactions
- **Cross-Session Continuity**: Maintain context and preferences over time
- **Smart Compression**: Automatic optimization to manage token usage efficiently
- **Proactive Management**: Prevents context overflow while preserving important information

**Usage Guidelines:**
- Context7 automatically manages conversation memory and retrieval
- GitHub tools require proper authentication and repository access
- MCP servers provide enhanced capabilities beyond basic tool functionality
- File operations through MCP servers offer advanced features and better error handling