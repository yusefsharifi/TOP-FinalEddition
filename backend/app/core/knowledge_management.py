from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

class DocumentStatus(Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class DocumentType(Enum):
    ARTICLE = "article"
    GUIDE = "guide"
    PROCEDURE = "procedure"
    POLICY = "policy"
    TEMPLATE = "template"
    BEST_PRACTICE = "best_practice"
    FAQ = "faq"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"

class AccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    PRIVATE = "private"

class Document(BaseModel):
    id: int
    title: str
    description: str
    content: str
    type: DocumentType
    status: DocumentStatus
    access_level: AccessLevel
    author_id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    version: int = 1
    tags: List[str] = []
    categories: List[str] = []
    related_documents: List[int] = []
    attachments: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    views: int = 0
    likes: int = 0
    comments: List[Dict[str, Any]] = []
    contributors: List[Dict[str, Any]] = []
    reviewers: List[Dict[str, Any]] = []
    approval_history: List[Dict[str, Any]] = []

class KnowledgeManagementSystem:
    def __init__(self):
        self.documents: Dict[int, Document] = {}
        self.categories: Dict[str, List[int]] = {}
        self.tags: Dict[str, List[int]] = {}
        self.search_index: Dict[str, List[int]] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def create_document(self, title: str, description: str, content: str, 
                       doc_type: DocumentType, author_id: int, 
                       access_level: AccessLevel = AccessLevel.INTERNAL,
                       tags: List[str] = [], categories: List[str] = []) -> int:
        """Create a new document"""
        doc_id = len(self.documents) + 1
        document = Document(
            id=doc_id,
            title=title,
            description=description,
            content=content,
            type=doc_type,
            status=DocumentStatus.DRAFT,
            access_level=access_level,
            author_id=author_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags,
            categories=categories
        )
        self.documents[doc_id] = document
        self._update_indexes(doc_id, document)
        return doc_id

    def update_document(self, doc_id: int, content: str, 
                       updated_by: int, version_comment: str = "") -> bool:
        """Update an existing document"""
        if doc_id not in self.documents:
            return False
        
        document = self.documents[doc_id]
        document.content = content
        document.updated_at = datetime.now()
        document.version += 1
        
        # Add to approval history
        document.approval_history.append({
            "version": document.version,
            "updated_by": updated_by,
            "comment": version_comment,
            "timestamp": datetime.now()
        })
        
        return True

    def publish_document(self, doc_id: int, published_by: int) -> bool:
        """Publish a document"""
        if doc_id not in self.documents:
            return False
        
        document = self.documents[doc_id]
        if document.status != DocumentStatus.DRAFT:
            return False
        
        document.status = DocumentStatus.PUBLISHED
        document.published_at = datetime.now()
        document.approval_history.append({
            "action": "publish",
            "published_by": published_by,
            "timestamp": datetime.now()
        })
        
        self._notify_subscribers(doc_id, "document_published")
        return True

    def archive_document(self, doc_id: int, archived_by: int, reason: str) -> bool:
        """Archive a document"""
        if doc_id not in self.documents:
            return False
        
        document = self.documents[doc_id]
        document.status = DocumentStatus.ARCHIVED
        document.approval_history.append({
            "action": "archive",
            "archived_by": archived_by,
            "reason": reason,
            "timestamp": datetime.now()
        })
        
        self._notify_subscribers(doc_id, "document_archived")
        return True

    def add_comment(self, doc_id: int, user_id: int, content: str) -> bool:
        """Add a comment to a document"""
        if doc_id not in self.documents:
            return False
        
        document = self.documents[doc_id]
        document.comments.append({
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.now()
        })
        
        self._notify_subscribers(doc_id, "new_comment")
        return True

    def add_contributor(self, doc_id: int, user_id: int, role: str) -> bool:
        """Add a contributor to a document"""
        if doc_id not in self.documents:
            return False
        
        document = self.documents[doc_id]
        document.contributors.append({
            "user_id": user_id,
            "role": role,
            "added_at": datetime.now()
        })
        
        self._notify_subscribers(doc_id, "new_contributor")
        return True

    def search_documents(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for documents"""
        results = []
        query_terms = query.lower().split()
        
        for doc_id, document in self.documents.items():
            if not self._matches_filters(document, filters):
                continue
                
            score = 0
            for term in query_terms:
                if term in document.title.lower():
                    score += 3
                if term in document.description.lower():
                    score += 2
                if term in document.content.lower():
                    score += 1
                if term in [tag.lower() for tag in document.tags]:
                    score += 2
                    
            if score > 0:
                results.append({
                    "doc_id": doc_id,
                    "title": document.title,
                    "description": document.description,
                    "score": score,
                    "type": document.type,
                    "status": document.status,
                    "access_level": document.access_level,
                    "created_at": document.created_at,
                    "updated_at": document.updated_at
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def get_document_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for knowledge management system"""
        return {
            "document_statistics": {
                "total_documents": len(self.documents),
                "published_documents": len([d for d in self.documents.values() 
                                         if d.status == DocumentStatus.PUBLISHED]),
                "draft_documents": len([d for d in self.documents.values() 
                                     if d.status == DocumentStatus.DRAFT]),
                "archived_documents": len([d for d in self.documents.values() 
                                        if d.status == DocumentStatus.ARCHIVED])
            },
            "engagement_metrics": {
                "total_views": sum(d.views for d in self.documents.values()),
                "total_likes": sum(d.likes for d in self.documents.values()),
                "total_comments": sum(len(d.comments) for d in self.documents.values()),
                "average_views_per_document": self._calculate_average_views()
            },
            "content_analysis": {
                "document_types": self._get_document_type_distribution(),
                "top_categories": self._get_top_categories(),
                "top_tags": self._get_top_tags(),
                "top_authors": self._get_top_authors()
            }
        }

    def get_document_history(self, doc_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get the history of a document"""
        if doc_id not in self.documents:
            return None
        return self.documents[doc_id].approval_history

    def get_document_contributors(self, doc_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get contributors of a document"""
        if doc_id not in self.documents:
            return None
        return self.documents[doc_id].contributors

    def get_document_comments(self, doc_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get comments on a document"""
        if doc_id not in self.documents:
            return None
        return self.documents[doc_id].comments

    def _update_indexes(self, doc_id: int, document: Document) -> None:
        """Update search indexes and category/tag mappings"""
        # Update categories
        for category in document.categories:
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(doc_id)
        
        # Update tags
        for tag in document.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(doc_id)
        
        # Update search index
        terms = set(document.title.lower().split() + 
                   document.description.lower().split() + 
                   document.content.lower().split() +
                   [tag.lower() for tag in document.tags])
        
        for term in terms:
            if term not in self.search_index:
                self.search_index[term] = []
            self.search_index[term].append(doc_id)

    def _matches_filters(self, document: Document, filters: Dict[str, Any]) -> bool:
        """Check if a document matches the given filters"""
        if not filters:
            return True
            
        if "type" in filters and document.type != filters["type"]:
            return False
        if "status" in filters and document.status != filters["status"]:
            return False
        if "access_level" in filters and document.access_level != filters["access_level"]:
            return False
        if "author_id" in filters and document.author_id != filters["author_id"]:
            return False
        if "categories" in filters and not all(cat in document.categories 
                                             for cat in filters["categories"]):
            return False
        if "tags" in filters and not all(tag in document.tags 
                                      for tag in filters["tags"]):
            return False
            
        return True

    def _notify_subscribers(self, doc_id: int, event_type: str) -> None:
        """Notify subscribers about document events"""
        if doc_id not in self.notifications:
            self.notifications[doc_id] = []
            
        document = self.documents[doc_id]
        for contributor in document.contributors:
            user_id = contributor["user_id"]
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            self.notifications[user_id].append({
                "type": event_type,
                "doc_id": doc_id,
                "title": document.title,
                "timestamp": datetime.now(),
                "is_read": False
            })

    def _calculate_average_views(self) -> float:
        """Calculate average views per document"""
        total_views = sum(d.views for d in self.documents.values())
        total_docs = len(self.documents)
        return total_views / total_docs if total_docs > 0 else 0.0

    def _get_document_type_distribution(self) -> Dict[str, int]:
        """Get distribution of document types"""
        distribution = {dt.value: 0 for dt in DocumentType}
        for document in self.documents.values():
            distribution[document.type.value] += 1
        return distribution

    def _get_top_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top categories by document count"""
        category_counts = {cat: len(docs) for cat, docs in self.categories.items()}
        return [
            {"category": cat, "count": count}
            for cat, count in sorted(category_counts.items(), 
                                  key=lambda x: x[1], reverse=True)[:limit]
        ]

    def _get_top_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top tags by document count"""
        tag_counts = {tag: len(docs) for tag, docs in self.tags.items()}
        return [
            {"tag": tag, "count": count}
            for tag, count in sorted(tag_counts.items(), 
                                  key=lambda x: x[1], reverse=True)[:limit]
        ]

    def _get_top_authors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top authors by document count"""
        author_counts = {}
        for document in self.documents.values():
            if document.author_id not in author_counts:
                author_counts[document.author_id] = 0
            author_counts[document.author_id] += 1
            
        return [
            {"author_id": author_id, "count": count}
            for author_id, count in sorted(author_counts.items(), 
                                         key=lambda x: x[1], reverse=True)[:limit]
        ] 