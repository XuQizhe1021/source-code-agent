# API 全量接口清单

- 生成时间：2026-03-31T19:27:59.683398
- 总接口数：185

## GET /api/models/
- 鉴权：否
- 核心参数：query:name, query:provider, query:type, query:status, query:vision_support, query:page, query:limit
- 预期行为：Read Models

## POST /api/models/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create New Model

## GET /api/models/providers
- 鉴权：否
- 核心参数：无
- 预期行为：Get Provider List

## POST /api/models/providers/reload
- 鉴权：否
- 核心参数：无
- 预期行为：Reload Providers

## GET /api/models/providers/modules
- 鉴权：否
- 核心参数：无
- 预期行为：Get Provider Modules

## GET /api/models/providers/scan
- 鉴权：否
- 核心参数：无
- 预期行为：Scan Provider Directory

## GET /api/models/{model_id}
- 鉴权：否
- 核心参数：path:model_id*
- 预期行为：Read Model

## PUT /api/models/{model_id}
- 鉴权：否
- 核心参数：path:model_id*, body*
- 预期行为：Update Model Api

## DELETE /api/models/{model_id}
- 鉴权：否
- 核心参数：path:model_id*
- 预期行为：Delete Model Api

## POST /api/models/{model_id}/test
- 鉴权：否
- 核心参数：path:model_id*
- 预期行为：Test Model Api

## GET /api/users/
- 鉴权：是
- 核心参数：query:page, query:limit, query:username, query:name, query:role, query:status
- 预期行为：Get Users

## POST /api/users/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create New User

## GET /api/users/departments
- 鉴权：是
- 核心参数：无
- 预期行为：Get Departments

## GET /api/users/positions
- 鉴权：是
- 核心参数：query:department
- 预期行为：Get Positions

## GET /api/users/info
- 鉴权：是
- 核心参数：无
- 预期行为：Get Current User Info

## GET /api/users/statistics
- 鉴权：是
- 核心参数：无
- 预期行为：Get User Statistics

## PUT /api/users/profile
- 鉴权：是
- 核心参数：body*
- 预期行为：Update User Profile

## PUT /api/users/password
- 鉴权：是
- 核心参数：body*
- 预期行为：Change Password

## POST /api/users/avatar
- 鉴权：是
- 核心参数：body*
- 预期行为：Upload Avatar

## GET /api/users/roles
- 鉴权：是
- 核心参数：无
- 预期行为：Read Roles

## GET /api/users/{user_id}
- 鉴权：是
- 核心参数：path:user_id*
- 预期行为：Read User

## PUT /api/users/{user_id}
- 鉴权：是
- 核心参数：path:user_id*, body*
- 预期行为：Update User Info

## DELETE /api/users/{user_id}
- 鉴权：是
- 核心参数：path:user_id*
- 预期行为：Delete User Api

## POST /api/users/{user_id}/reset-password
- 鉴权：是
- 核心参数：path:user_id*
- 预期行为：Reset Password

## GET /api/users/test-auth
- 鉴权：是
- 核心参数：无
- 预期行为：Test Authentication

## POST /api/auth/login
- 鉴权：否
- 核心参数：body*
- 预期行为：Login

## POST /api/auth/register
- 鉴权：否
- 核心参数：body*
- 预期行为：Register

## POST /api/auth/token
- 鉴权：否
- 核心参数：body*
- 预期行为：Login For Access Token

## POST /api/auth/logout
- 鉴权：否
- 核心参数：无
- 预期行为：Logout

## GET /api/auth/me
- 鉴权：是
- 核心参数：无
- 预期行为：Read Users Me

## GET /api/knowledge/chunking-methods
- 鉴权：是
- 核心参数：无
- 预期行为：Get Chunking Methods

## GET /api/knowledge/embedding-models
- 鉴权：是
- 核心参数：无
- 预期行为：Get Embedding Models

## GET /api/knowledge/
- 鉴权：是
- 核心参数：query:name, query:status, query:page, query:limit
- 预期行为：Read Knowledge List

## POST /api/knowledge/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create New Knowledge

## GET /api/knowledge/{knowledge_id}
- 鉴权：是
- 核心参数：path:knowledge_id*
- 预期行为：Read Knowledge Detail

## PUT /api/knowledge/{knowledge_id}
- 鉴权：是
- 核心参数：path:knowledge_id*, body*
- 预期行为：Update Knowledge Api

## DELETE /api/knowledge/{knowledge_id}
- 鉴权：是
- 核心参数：path:knowledge_id*
- 预期行为：Delete Knowledge Api

## GET /api/knowledge/{knowledge_id}/files
- 鉴权：是
- 核心参数：path:knowledge_id*, query:status, query:page, query:limit
- 预期行为：Read Knowledge Files

## POST /api/knowledge/{knowledge_id}/upload
- 鉴权：是
- 核心参数：path:knowledge_id*, body*
- 预期行为：Upload File

## DELETE /api/knowledge/{knowledge_id}/files/{file_id}
- 鉴权：是
- 核心参数：path:knowledge_id*, path:file_id*
- 预期行为：Delete File

## POST /api/knowledge/{knowledge_id}/files/{file_id}/reprocess
- 鉴权：是
- 核心参数：path:knowledge_id*, path:file_id*
- 预期行为：Reprocess File

## POST /api/knowledge/{knowledge_id}/retrieve
- 鉴权：是
- 核心参数：path:knowledge_id*, body*
- 预期行为：Test Knowledge Retrieval

## POST /api/knowledge/{knowledge_id}/files/{file_id}/process
- 鉴权：是
- 核心参数：path:knowledge_id*, path:file_id*, body*
- 预期行为：Process File

## POST /api/knowledge/{knowledge_id}/files/{file_id}/embed
- 鉴权：是
- 核心参数：path:knowledge_id*, path:file_id*
- 预期行为：Embed File

## POST /api/knowledge/trigger_file_embedding/{knowledge_id}/{file_id}
- 鉴权：否
- 核心参数：path:knowledge_id*, path:file_id*
- 预期行为：Trigger File Embedding After Processing

## GET /api/knowledge/file/{file_id}
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Get File Detail

## GET /api/knowledge/file/{file_id}/chunks
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Get File Chunks

## GET /api/knowledge/file/{file_id}/embeddings
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Get File Embeddings

## POST /api/knowledge/{knowledge_id}/associate-files
- 鉴权：是
- 核心参数：path:knowledge_id*, body*
- 预期行为：Associate Files

## POST /api/knowledge/{knowledge_id}/files/{file_id}/preview-chunking
- 鉴权：是
- 核心参数：path:knowledge_id*, path:file_id*, body*
- 预期行为：Preview File Chunking

## POST /api/knowledge/{knowledge_id}/files/{file_id}/process-with-config
- 鉴权：是
- 核心参数：path:knowledge_id*, path:file_id*, body*
- 预期行为：Process File With Config

## GET /api/roles/
- 鉴权：是
- 核心参数：无
- 预期行为：Read Roles

## GET /api/agents/
- 鉴权：是
- 核心参数：query:page, query:limit, query:name, query:type, query:status
- 预期行为：Get Agents

## POST /api/agents/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create Agent

## GET /api/agents/types
- 鉴权：是
- 核心参数：无
- 预期行为：Get Agent Types

## GET /api/agents/{agent_id}
- 鉴权：是
- 核心参数：path:agent_id*
- 预期行为：Get Agent Detail

## PUT /api/agents/{agent_id}
- 鉴权：是
- 核心参数：path:agent_id*, body*
- 预期行为：Update Agent

## DELETE /api/agents/{agent_id}
- 鉴权：是
- 核心参数：path:agent_id*
- 预期行为：Delete Agent

## POST /api/agents/{agent_id}/avatar
- 鉴权：是
- 核心参数：path:agent_id*, body*
- 预期行为：Update Agent Avatar

## POST /api/agents/{agent_id}/chat
- 鉴权：否
- 核心参数：path:agent_id*, query:token, query:user_id, body*
- 预期行为：Chat With Agent

## POST /api/agents/{agent_id}/generate-share-token
- 鉴权：是
- 核心参数：path:agent_id*, query:name
- 预期行为：Generate Agent Share Token

## POST /api/agents/{agent_id}/generate-api-key
- 鉴权：是
- 核心参数：path:agent_id*, query:name
- 预期行为：Generate Agent Api Key

## GET /api/agents/{agent_id}/api-keys
- 鉴权：是
- 核心参数：path:agent_id*
- 预期行为：Get Agent Api Keys

## GET /api/agents/{agent_id}/share-tokens
- 鉴权：是
- 核心参数：path:agent_id*
- 预期行为：Get Agent Share Tokens

## DELETE /api/agents/{agent_id}/api-keys/{key_id}
- 鉴权：是
- 核心参数：path:agent_id*, path:key_id*
- 预期行为：Delete Agent Api Key

## DELETE /api/agents/{agent_id}/share-tokens/{token_id}
- 鉴权：是
- 核心参数：path:agent_id*, path:token_id*
- 预期行为：Delete Agent Share Token

## POST /api/agents/{agent_id}/toggle-share
- 鉴权：是
- 核心参数：path:agent_id*, query:enabled*
- 预期行为：Toggle Agent Share

## POST /api/agents/{agent_id}/toggle-api
- 鉴权：是
- 核心参数：path:agent_id*, query:enabled*
- 预期行为：Toggle Agent Api

## GET /api/agents/share/{token}
- 鉴权：否
- 核心参数：path:token*
- 预期行为：Get Agent By Share Token

## POST /api/agents/chat-with-api-key
- 鉴权：否
- 核心参数：query:user_id, header:api-key*, body*
- 预期行为：Chat With Agent Api

## GET /api/agents/{agent_id}/logs
- 鉴权：是
- 核心参数：path:agent_id*, query:skip, query:limit, query:session_id, query:user_id
- 预期行为：Get Agent Chat Logs

## GET /api/agents/{agent_id}/share-chat/{share_id}
- 鉴权：否
- 核心参数：path:agent_id*, path:share_id*
- 预期行为：Get Agent Share Info

## POST /api/agents/{agent_id}/share-chat/{share_id}/chat
- 鉴权：否
- 核心参数：path:agent_id*, path:share_id*, body*
- 预期行为：Share Chat With Agent

## GET /api/graphs/
- 鉴权：是
- 核心参数：query:page, query:limit, query:name
- 预期行为：Get Graphs

## POST /api/graphs/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create Graph

## GET /api/graphs/{graph_id}
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Get Graph Detail

## PUT /api/graphs/{graph_id}
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Update Graph

## DELETE /api/graphs/{graph_id}
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Delete Graph

## POST /api/graphs/{graph_id}/test
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Test Graph Connection

## GET /api/graphs/{graph_id}/export
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Export Graph

## GET /api/graphs/{graph_id}/visualization
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Get Graph Visualization

## GET /api/graphs/{graph_id}/nodes
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Get Graph Nodes

## POST /api/graphs/{graph_id}/nodes
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Add Graph Node

## GET /api/graphs/{graph_id}/edges
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Get Graph Edges

## POST /api/graphs/{graph_id}/edges
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Add Graph Edge

## GET /api/graphs/{graph_id}/schema
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Get Graph Schema

## PUT /api/graphs/{graph_id}/schema
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Update Graph Schema

## GET /api/graphs/{graph_id}/nodes/{node_id}/properties
- 鉴权：是
- 核心参数：path:graph_id*, path:node_id*
- 预期行为：Get Node Properties

## PUT /api/graphs/{graph_id}/nodes/{node_id}/properties
- 鉴权：是
- 核心参数：path:graph_id*, path:node_id*, body*
- 预期行为：Update Node Properties

## POST /api/graphs/{graph_id}/entities
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Add Entity

## GET /api/graphs/{graph_id}/entities
- 鉴权：是
- 核心参数：path:graph_id*, query:entity_type, query:name, query:skip, query:limit
- 预期行为：Get Entities

## GET /api/graphs/{graph_id}/entity-types/{entity_type}/properties
- 鉴权：是
- 核心参数：path:graph_id*, path:entity_type*
- 预期行为：Get Entity Type Properties

## POST /api/graphs/{graph_id}/chat
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Chat With Graph

## POST /api/graphs/{graph_id}/files/upload
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Upload File

## GET /api/graphs/{graph_id}/files
- 鉴权：是
- 核心参数：path:graph_id*, query:status, query:page, query:limit
- 预期行为：Read Graph Files

## DELETE /api/graphs/{graph_id}/files/{file_id}
- 鉴权：是
- 核心参数：path:graph_id*, path:file_id*
- 预期行为：Delete File

## POST /api/graphs/{graph_id}/files/{file_id}/parse
- 鉴权：是
- 核心参数：path:graph_id*, path:file_id*
- 预期行为：Parse File

## GET /api/graphs/{graph_id}/files/{file_id}/status
- 鉴权：是
- 核心参数：path:graph_id*, path:file_id*
- 预期行为：Get File Parse Status

## POST /api/graphs/{graph_id}/extract
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Extract Knowledge

## POST /api/graphs/{graph_id}/extraction-tasks/{task_id}/retry
- 鉴权：是
- 核心参数：path:graph_id*, path:task_id*, body*
- 预期行为：Retry Extraction Task

## GET /api/graphs/{graph_id}/extraction-tasks
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Get Extraction Tasks

## GET /api/graphs/{graph_id}/extraction-tasks/{task_id}
- 鉴权：是
- 核心参数：path:graph_id*, path:task_id*
- 预期行为：Get Extraction Task Detail

## GET /api/graphs/{graph_id}/extraction-tasks/{task_id}/result
- 鉴权：是
- 核心参数：path:graph_id*, path:task_id*
- 预期行为：Get Extraction Task Result

## POST /api/graphs/{graph_id}/extraction-tasks/{task_id}/cancel
- 鉴权：是
- 核心参数：path:graph_id*, path:task_id*
- 预期行为：Cancel Extraction Task

## GET /api/graphs/{graph_id}/files/{file_id}/preview
- 鉴权：是
- 核心参数：path:graph_id*, path:file_id*
- 预期行为：Get File Preview

## POST /api/graphs/{graph_id}/neo4j-test
- 鉴权：是
- 核心参数：path:graph_id*, body
- 预期行为：Test Neo4J Connection

## POST /api/graphs/{graph_id}/neo4j-subgraph
- 鉴权：是
- 核心参数：path:graph_id*, body
- 预期行为：Create Neo4J Subgraph

## DELETE /api/graphs/{graph_id}/neo4j-subgraph
- 鉴权：是
- 核心参数：path:graph_id*
- 预期行为：Delete Neo4J Subgraph

## GET /api/graphs/{graph_id}/neo4j-visualization
- 鉴权：是
- 核心参数：path:graph_id*, query:limit
- 预期行为：Get Neo4J Visualization

## POST /api/graphs/{graph_id}/extract-with-neo4j
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Extract With Neo4J

## POST /api/graphs/{graph_id}/extract-with-llm
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Extract With Llm

## POST /api/graphs/{graph_id}/associate-files
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Associate Files To Graph

## POST /api/graphs/{graph_id}/extract-from-file
- 鉴权：是
- 核心参数：path:graph_id*, body*
- 预期行为：Extract From File

## POST /api/files/upload
- 鉴权：是
- 核心参数：body*
- 预期行为：Upload File

## POST /api/files/upload/batch
- 鉴权：是
- 核心参数：body*
- 预期行为：Upload Multiple Files

## GET /api/files/
- 鉴权：是
- 核心参数：query:skip, query:limit, query:filename, query:file_type, query:status
- 预期行为：List Files

## GET /api/files/{file_id}
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Get File Detail

## PUT /api/files/{file_id}
- 鉴权：是
- 核心参数：path:file_id*, body*
- 预期行为：Update File

## DELETE /api/files/{file_id}
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Delete File

## POST /api/files/{file_id}/reprocess
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Reprocess File

## POST /api/files/batch-reprocess
- 鉴权：是
- 核心参数：body*
- 预期行为：Batch Reprocess Files

## PUT /api/files/{file_id}/content
- 鉴权：否
- 核心参数：path:file_id*, body*
- 预期行为：Update File Content

## GET /api/files/{file_id}/content
- 鉴权：否
- 核心参数：path:file_id*
- 预期行为：Get File Content

## GET /api/files/status/{file_id}
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Get File Status

## POST /api/files/process
- 鉴权：是
- 核心参数：body*
- 预期行为：Process Files

## GET /api/files/{file_id}/download
- 鉴权：否
- 核心参数：path:file_id*
- 预期行为：Download File

## GET /api/files/minio-download/{bucket}/{object_name}
- 鉴权：否
- 核心参数：path:bucket*, path:object_name*, query:download
- 预期行为：Direct Download From Minio

## GET /api/files/{file_id}/preview-pdf
- 鉴权：否
- 核心参数：path:file_id*, query:type
- 预期行为：Preview Pdf File

## GET /api/files/image/{file_id}/{image_name}
- 鉴权：否
- 核心参数：path:file_id*, path:image_name*
- 预期行为：Serve Image

## GET /api/files/markdown-image/{path}
- 鉴权：否
- 核心参数：path:path*
- 预期行为：Serve Markdown Image

## GET /api/files/img/{path}
- 鉴权：否
- 核心参数：path:path*
- 预期行为：Serve Image Smart

## POST /api/files/test-minio-connection
- 鉴权：是
- 核心参数：无
- 预期行为：Test Minio Connection

## GET /api/files/verify-file-access/{file_id}
- 鉴权：是
- 核心参数：path:file_id*
- 预期行为：Verify File Access

## GET /api/files/{file_id}/preview
- 鉴权：否
- 核心参数：path:file_id*
- 预期行为：Preview File

## GET /api/file-preview/{file_id}/original
- 鉴权：否
- 核心参数：path:file_id*, query:token
- 预期行为：Preview Original File

## GET /api/file-preview/{file_id}/processed
- 鉴权：否
- 核心参数：path:file_id*, query:token, header:authorization
- 预期行为：Preview Processed File

## GET /api/file-preview/{file_id}/images
- 鉴权：否
- 核心参数：path:file_id*, query:token, header:authorization
- 预期行为：List Processed Images

## GET /api/file-preview/{file_id}/image/{image_name}
- 鉴权：否
- 核心参数：path:file_id*, path:image_name*, query:token
- 预期行为：Preview Image

## GET /api/file-preview/{file_id}/markdown
- 鉴权：否
- 核心参数：path:file_id*, query:token
- 预期行为：Preview Markdown

## GET /api/file-preview/{file_id}/visual
- 鉴权：否
- 核心参数：path:file_id*, query:token
- 预期行为：Preview Visual

## GET /api/file-preview/uploads/{path}
- 鉴权：否
- 核心参数：path:path*, query:token, header:authorization
- 预期行为：Preview Uploads File

## GET /api/file-preview/uploads/files/{file_id}/{image_name}
- 鉴权：否
- 核心参数：path:file_id*, path:image_name*, query:token, header:authorization
- 预期行为：Preview Simple Image

## GET /api/datasources/
- 鉴权：是
- 核心参数：query:skip, query:limit, query:name, query:type
- 预期行为：Get Datasources

## POST /api/datasources/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create Datasource

## GET /api/datasources/{datasource_id}
- 鉴权：是
- 核心参数：path:datasource_id*
- 预期行为：Get Datasource

## PUT /api/datasources/{datasource_id}
- 鉴权：是
- 核心参数：path:datasource_id*, body*
- 预期行为：Update Datasource

## DELETE /api/datasources/{datasource_id}
- 鉴权：是
- 核心参数：path:datasource_id*
- 预期行为：Delete Datasource

## POST /api/datasources/test_connection
- 鉴权：是
- 核心参数：body*
- 预期行为：Test Connection

## GET /api/datasources/{datasource_id}/structure
- 鉴权：是
- 核心参数：path:datasource_id*
- 预期行为：Get Database Structure

## POST /api/datasources/execute_query
- 鉴权：是
- 核心参数：body*
- 预期行为：Execute Query

## POST /api/datasources/generate_sql
- 鉴权：是
- 核心参数：body*
- 预期行为：Generate Sql

## GET /api/datasources/{datasource_id}/queries
- 鉴权：是
- 核心参数：path:datasource_id*, query:skip, query:limit, query:status
- 预期行为：Get Datasource Queries

## DELETE /api/datasources/queries/{query_id}
- 鉴权：是
- 核心参数：path:query_id*
- 预期行为：Delete Datasource Query

## GET /api/mcp/services
- 鉴权：是
- 核心参数：query:type, query:deployment_type, query:is_official, query:page, query:limit
- 预期行为：Get Service List

## POST /api/mcp/services
- 鉴权：是
- 核心参数：body*
- 预期行为：Create Service

## GET /api/mcp/services/types
- 鉴权：是
- 核心参数：无
- 预期行为：Get Service Types

## GET /api/mcp/services/providers
- 鉴权：是
- 核心参数：无
- 预期行为：Get Service Providers

## GET /api/mcp/services/recommend
- 鉴权：是
- 核心参数：无
- 预期行为：Get Recommend Services

## GET /api/mcp/services/search
- 鉴权：是
- 核心参数：query:keyword*
- 预期行为：Search Services

## GET /api/mcp/services/{service_id}
- 鉴权：是
- 核心参数：path:service_id*
- 预期行为：Get Service Detail

## PUT /api/mcp/services/{service_id}
- 鉴权：是
- 核心参数：path:service_id*, body*
- 预期行为：Update Service

## DELETE /api/mcp/services/{service_id}
- 鉴权：是
- 核心参数：path:service_id*
- 预期行为：Delete Service

## POST /api/mcp/services/connect
- 鉴权：是
- 核心参数：body*
- 预期行为：Connect Service

## GET /api/mcp/services/connections
- 鉴权：是
- 核心参数：无
- 预期行为：Get User Connections

## POST /api/mcp/services/from-github
- 鉴权：是
- 核心参数：body*
- 预期行为：Create Service From Github

## POST /api/mcp/services/{service_id}/test
- 鉴权：是
- 核心参数：path:service_id*, body*
- 预期行为：Test Service Connection

## POST /api/mcp/services/{service_id}/call
- 鉴权：是
- 核心参数：path:service_id*, body*
- 预期行为：Call Service Function

## GET /api/dashboard/stats
- 鉴权：是
- 核心参数：query:force_refresh_recommended
- 预期行为：Get Dashboard Stats

## GET /api/user/
- 鉴权：是
- 核心参数：query:page, query:limit, query:username, query:name, query:role, query:status
- 预期行为：Get Users

## POST /api/user/
- 鉴权：是
- 核心参数：body*
- 预期行为：Create New User

## GET /api/user/departments
- 鉴权：是
- 核心参数：无
- 预期行为：Get Departments

## GET /api/user/positions
- 鉴权：是
- 核心参数：query:department
- 预期行为：Get Positions

## GET /api/user/info
- 鉴权：是
- 核心参数：无
- 预期行为：Get Current User Info

## GET /api/user/statistics
- 鉴权：是
- 核心参数：无
- 预期行为：Get User Statistics

## PUT /api/user/profile
- 鉴权：是
- 核心参数：body*
- 预期行为：Update User Profile

## PUT /api/user/password
- 鉴权：是
- 核心参数：body*
- 预期行为：Change Password

## POST /api/user/avatar
- 鉴权：是
- 核心参数：body*
- 预期行为：Upload Avatar

## GET /api/user/roles
- 鉴权：是
- 核心参数：无
- 预期行为：Read Roles

## GET /api/user/{user_id}
- 鉴权：是
- 核心参数：path:user_id*
- 预期行为：Read User

## PUT /api/user/{user_id}
- 鉴权：是
- 核心参数：path:user_id*, body*
- 预期行为：Update User Info

## DELETE /api/user/{user_id}
- 鉴权：是
- 核心参数：path:user_id*
- 预期行为：Delete User Api

## POST /api/user/{user_id}/reset-password
- 鉴权：是
- 核心参数：path:user_id*
- 预期行为：Reset Password

## GET /api/user/test-auth
- 鉴权：是
- 核心参数：无
- 预期行为：Test Authentication

## GET /api/agent-types
- 鉴权：是
- 核心参数：无
- 预期行为：Agent Types Endpoint

## GET /
- 鉴权：否
- 核心参数：无
- 预期行为：Root
