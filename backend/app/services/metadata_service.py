"""
File: metadata_service.py

Overview:
Comprehensive metadata tracking and audit trail service for ML operations.

Purpose:
Tracks all data transformations, maintains audit logs, and ensures reproducibility.

Dependencies:
- sqlalchemy: Database operations
- pandas: Data manipulation
- json: Metadata serialization

Last Modified: 2025-08-15
Author: Claude
"""

import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging
import pickle
import base64

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class TransformationType(Enum):
    """Types of data transformations"""
    IMPORT = "import"
    IMPUTATION = "imputation"
    ENCODING = "encoding"
    SCALING = "scaling"
    FEATURE_ENGINEERING = "feature_engineering"
    CORRELATION_ANALYSIS = "correlation_analysis"
    EXPORT = "export"
    CUSTOM = "custom"


class AuditAction(Enum):
    """Types of audit actions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    TRANSFORM = "transform"
    ANALYZE = "analyze"
    EXPORT = "export"


@dataclass
class TransformationRecord:
    """Record of a single data transformation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    transformation_type: TransformationType = TransformationType.CUSTOM
    operation: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    affected_columns: List[str] = field(default_factory=list)
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class DatasetMetadata:
    """Comprehensive metadata for a dataset"""
    dataset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    source_file: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    file_size_bytes: int = 0
    row_count: int = 0
    column_count: int = 0
    column_info: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    data_hash: str = ""
    schema_version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLogEntry:
    """Entry in the audit log"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    action: AuditAction = AuditAction.READ
    entity_type: str = ""
    entity_id: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None


# SQLAlchemy Models
class TransformationHistoryDB(Base):
    """Database model for transformation history"""
    __tablename__ = 'transformation_history'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    transformation_type = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    parameters = Column(JSON)
    affected_columns = Column(JSON)
    before_state = Column(JSON)
    after_state = Column(JSON)
    user_id = Column(String)
    session_id = Column(String)
    duration_seconds = Column(Float)
    success = Column(Integer)
    error_message = Column(Text)


class DatasetMetadataDB(Base):
    """Database model for dataset metadata"""
    __tablename__ = 'dataset_metadata'
    
    dataset_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    source_file = Column(String)
    created_at = Column(DateTime, nullable=False)
    last_modified = Column(DateTime, nullable=False)
    file_size_bytes = Column(Integer)
    row_count = Column(Integer)
    column_count = Column(Integer)
    column_info = Column(JSON)
    data_hash = Column(String)
    schema_version = Column(String)
    tags = Column(JSON)
    custom_metadata = Column(JSON)


class AuditLogDB(Base):
    """Database model for audit log"""
    __tablename__ = 'audit_log'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String)
    entity_id = Column(String)
    user_id = Column(String)
    session_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(Text)
    details = Column(JSON)
    success = Column(Integer)
    error_message = Column(Text)


class MetadataService:
    """
    Service for comprehensive metadata management and audit trail
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize metadata service"""
        self.database_url = database_url or "sqlite:///metadata.db"
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.current_session_id = str(uuid.uuid4())
        self.transformation_stack: List[TransformationRecord] = []
        
    def create_dataset_metadata(
        self,
        df: pd.DataFrame,
        name: str,
        source_file: Optional[str] = None,
        tags: Optional[List[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> DatasetMetadata:
        """
        Create comprehensive metadata for a dataset
        
        Args:
            df: DataFrame to analyze
            name: Dataset name
            source_file: Source file path
            tags: Optional tags
            custom_metadata: Optional custom metadata
            
        Returns:
            DatasetMetadata object
        """
        # Generate column information
        column_info = {}
        for col in df.columns:
            col_data = df[col]
            info = {
                'dtype': str(col_data.dtype),
                'missing_count': int(col_data.isnull().sum()),
                'missing_percentage': float(col_data.isnull().sum() / len(df) * 100),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float(col_data.nunique() / len(df) * 100)
            }
            
            # Add statistics for numeric columns
            if pd.api.types.is_numeric_dtype(col_data):
                info.update({
                    'mean': float(col_data.mean()) if not col_data.isnull().all() else None,
                    'std': float(col_data.std()) if not col_data.isnull().all() else None,
                    'min': float(col_data.min()) if not col_data.isnull().all() else None,
                    'max': float(col_data.max()) if not col_data.isnull().all() else None,
                    'q25': float(col_data.quantile(0.25)) if not col_data.isnull().all() else None,
                    'q50': float(col_data.quantile(0.50)) if not col_data.isnull().all() else None,
                    'q75': float(col_data.quantile(0.75)) if not col_data.isnull().all() else None,
                })
            
            # Add info for categorical columns
            if pd.api.types.is_object_dtype(col_data):
                mode_val = col_data.mode()
                info.update({
                    'mode': str(mode_val[0]) if not mode_val.empty else None,
                    'mode_frequency': int((col_data == mode_val[0]).sum()) if not mode_val.empty else 0,
                    'top_values': col_data.value_counts().head(5).to_dict()
                })
            
            column_info[col] = info
        
        # Calculate data hash
        data_hash = self._calculate_data_hash(df)
        
        # Create metadata object
        metadata = DatasetMetadata(
            name=name,
            source_file=source_file or "",
            file_size_bytes=df.memory_usage(deep=True).sum(),
            row_count=len(df),
            column_count=len(df.columns),
            column_info=column_info,
            data_hash=data_hash,
            tags=tags or [],
            custom_metadata=custom_metadata or {}
        )
        
        # Store in database
        self._store_dataset_metadata(metadata)
        
        # Log audit entry
        self.log_audit(
            action=AuditAction.CREATE,
            entity_type="dataset",
            entity_id=metadata.dataset_id,
            details={'name': name, 'rows': len(df), 'columns': len(df.columns)}
        )
        
        return metadata
    
    def track_transformation(
        self,
        transformation_type: TransformationType,
        operation: str,
        parameters: Dict[str, Any],
        affected_columns: List[str],
        df_before: Optional[pd.DataFrame] = None,
        df_after: Optional[pd.DataFrame] = None,
        duration_seconds: Optional[float] = None
    ) -> TransformationRecord:
        """
        Track a data transformation
        
        Args:
            transformation_type: Type of transformation
            operation: Description of operation
            parameters: Parameters used
            affected_columns: Columns affected
            df_before: DataFrame before transformation
            df_after: DataFrame after transformation
            duration_seconds: Operation duration
            
        Returns:
            TransformationRecord object
        """
        # Create before/after state summaries
        before_state = None
        after_state = None
        
        if df_before is not None:
            before_state = {
                'shape': df_before.shape,
                'missing_count': int(df_before.isnull().sum().sum()),
                'data_hash': self._calculate_data_hash(df_before)
            }
        
        if df_after is not None:
            after_state = {
                'shape': df_after.shape,
                'missing_count': int(df_after.isnull().sum().sum()),
                'data_hash': self._calculate_data_hash(df_after)
            }
        
        # Create transformation record
        record = TransformationRecord(
            transformation_type=transformation_type,
            operation=operation,
            parameters=parameters,
            affected_columns=affected_columns,
            before_state=before_state,
            after_state=after_state,
            session_id=self.current_session_id,
            duration_seconds=duration_seconds
        )
        
        # Add to stack
        self.transformation_stack.append(record)
        
        # Store in database
        self._store_transformation(record)
        
        # Log audit entry
        self.log_audit(
            action=AuditAction.TRANSFORM,
            entity_type="transformation",
            entity_id=record.id,
            details={'operation': operation, 'affected_columns': affected_columns}
        )
        
        return record
    
    def log_audit(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log an audit entry
        
        Args:
            action: Action performed
            entity_type: Type of entity
            entity_id: Entity identifier
            details: Additional details
            user_id: User identifier
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action succeeded
            error_message: Error message if failed
            
        Returns:
            AuditLogEntry object
        """
        entry = AuditLogEntry(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            session_id=self.current_session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            success=success,
            error_message=error_message
        )
        
        # Store in database
        self._store_audit_log(entry)
        
        return entry
    
    def get_transformation_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[TransformationRecord]:
        """
        Get transformation history
        
        Args:
            session_id: Optional session filter
            limit: Maximum records to return
            
        Returns:
            List of transformation records
        """
        with self.SessionLocal() as session:
            query = session.query(TransformationHistoryDB)
            
            if session_id:
                query = query.filter_by(session_id=session_id)
            
            query = query.order_by(TransformationHistoryDB.timestamp.desc())
            query = query.limit(limit)
            
            records = []
            for db_record in query.all():
                record = TransformationRecord(
                    id=db_record.id,
                    timestamp=db_record.timestamp,
                    transformation_type=TransformationType(db_record.transformation_type),
                    operation=db_record.operation,
                    parameters=db_record.parameters or {},
                    affected_columns=db_record.affected_columns or [],
                    before_state=db_record.before_state,
                    after_state=db_record.after_state,
                    user_id=db_record.user_id,
                    session_id=db_record.session_id,
                    duration_seconds=db_record.duration_seconds,
                    success=bool(db_record.success),
                    error_message=db_record.error_message
                )
                records.append(record)
            
            return records
    
    def get_audit_log(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """
        Get audit log entries
        
        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            action: Filter by action
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum entries to return
            
        Returns:
            List of audit log entries
        """
        with self.SessionLocal() as session:
            query = session.query(AuditLogDB)
            
            if entity_type:
                query = query.filter_by(entity_type=entity_type)
            if entity_id:
                query = query.filter_by(entity_id=entity_id)
            if action:
                query = query.filter_by(action=action.value)
            if start_date:
                query = query.filter(AuditLogDB.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLogDB.timestamp <= end_date)
            
            query = query.order_by(AuditLogDB.timestamp.desc())
            query = query.limit(limit)
            
            entries = []
            for db_entry in query.all():
                entry = AuditLogEntry(
                    id=db_entry.id,
                    timestamp=db_entry.timestamp,
                    action=AuditAction(db_entry.action),
                    entity_type=db_entry.entity_type,
                    entity_id=db_entry.entity_id,
                    user_id=db_entry.user_id,
                    session_id=db_entry.session_id,
                    ip_address=db_entry.ip_address,
                    user_agent=db_entry.user_agent,
                    details=db_entry.details or {},
                    success=bool(db_entry.success),
                    error_message=db_entry.error_message
                )
                entries.append(entry)
            
            return entries
    
    def create_reproducibility_package(
        self,
        dataset_id: str,
        transformations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a reproducibility package for a dataset
        
        Args:
            dataset_id: Dataset identifier
            transformations: Optional list of transformation IDs
            
        Returns:
            Reproducibility package dictionary
        """
        package = {
            'package_id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'dataset_id': dataset_id
        }
        
        # Get dataset metadata
        with self.SessionLocal() as session:
            metadata = session.query(DatasetMetadataDB).filter_by(dataset_id=dataset_id).first()
            if metadata:
                package['dataset_metadata'] = {
                    'name': metadata.name,
                    'source_file': metadata.source_file,
                    'row_count': metadata.row_count,
                    'column_count': metadata.column_count,
                    'data_hash': metadata.data_hash,
                    'column_info': metadata.column_info
                }
        
        # Get transformations
        if transformations:
            package['transformations'] = []
            with self.SessionLocal() as session:
                for trans_id in transformations:
                    trans = session.query(TransformationHistoryDB).filter_by(id=trans_id).first()
                    if trans:
                        package['transformations'].append({
                            'id': trans.id,
                            'timestamp': trans.timestamp.isoformat(),
                            'operation': trans.operation,
                            'parameters': trans.parameters,
                            'affected_columns': trans.affected_columns
                        })
        else:
            # Get all transformations for this session
            package['transformations'] = []
            for trans in self.transformation_stack:
                package['transformations'].append({
                    'id': trans.id,
                    'timestamp': trans.timestamp.isoformat(),
                    'operation': trans.operation,
                    'parameters': trans.parameters,
                    'affected_columns': trans.affected_columns
                })
        
        # Add environment info
        package['environment'] = {
            'python_version': '3.10+',
            'libraries': {
                'pandas': pd.__version__,
                'numpy': np.__version__
            }
        }
        
        return package
    
    def export_lineage(self, dataset_id: str) -> Dict[str, Any]:
        """
        Export complete data lineage for a dataset
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Data lineage dictionary
        """
        lineage = {
            'dataset_id': dataset_id,
            'lineage_graph': []
        }
        
        # Get all transformations related to this dataset
        with self.SessionLocal() as session:
            # Get dataset metadata
            metadata = session.query(DatasetMetadataDB).filter_by(dataset_id=dataset_id).first()
            if metadata:
                lineage['source'] = {
                    'file': metadata.source_file,
                    'created_at': metadata.created_at.isoformat(),
                    'initial_shape': [metadata.row_count, metadata.column_count]
                }
            
            # Build lineage graph
            transformations = session.query(TransformationHistoryDB).filter_by(
                session_id=self.current_session_id
            ).order_by(TransformationHistoryDB.timestamp).all()
            
            for trans in transformations:
                node = {
                    'id': trans.id,
                    'timestamp': trans.timestamp.isoformat(),
                    'operation': trans.operation,
                    'type': trans.transformation_type,
                    'parameters': trans.parameters,
                    'affected_columns': trans.affected_columns,
                    'before_state': trans.before_state,
                    'after_state': trans.after_state,
                    'duration': trans.duration_seconds
                }
                lineage['lineage_graph'].append(node)
        
        return lineage
    
    def generate_compliance_report(
        self,
        dataset_id: str,
        compliance_framework: str = "GDPR"
    ) -> Dict[str, Any]:
        """
        Generate compliance documentation
        
        Args:
            dataset_id: Dataset identifier
            compliance_framework: Compliance framework (GDPR, HIPAA, etc.)
            
        Returns:
            Compliance report dictionary
        """
        report = {
            'dataset_id': dataset_id,
            'framework': compliance_framework,
            'generated_at': datetime.now().isoformat(),
            'compliance_checks': []
        }
        
        # Get dataset metadata
        with self.SessionLocal() as session:
            metadata = session.query(DatasetMetadataDB).filter_by(dataset_id=dataset_id).first()
            
            if metadata:
                # Check for PII columns (simplified check)
                pii_patterns = ['email', 'phone', 'ssn', 'address', 'name', 'dob', 'birth']
                potential_pii = []
                
                for col in metadata.column_info.keys():
                    if any(pattern in col.lower() for pattern in pii_patterns):
                        potential_pii.append(col)
                
                report['compliance_checks'].append({
                    'check': 'PII Detection',
                    'status': 'Warning' if potential_pii else 'Pass',
                    'details': f"Potential PII columns: {potential_pii}" if potential_pii else "No PII detected"
                })
                
                # Check audit trail
                audit_count = session.query(AuditLogDB).filter_by(entity_id=dataset_id).count()
                report['compliance_checks'].append({
                    'check': 'Audit Trail',
                    'status': 'Pass' if audit_count > 0 else 'Fail',
                    'details': f"{audit_count} audit entries found"
                })
                
                # Check data retention
                data_age = (datetime.now() - metadata.created_at).days
                report['compliance_checks'].append({
                    'check': 'Data Retention',
                    'status': 'Info',
                    'details': f"Data age: {data_age} days"
                })
                
                # Check encryption (placeholder)
                report['compliance_checks'].append({
                    'check': 'Encryption',
                    'status': 'Info',
                    'details': "Encryption status should be verified at storage level"
                })
        
        return report
    
    # Private helper methods
    
    def _calculate_data_hash(self, df: pd.DataFrame) -> str:
        """Calculate hash of DataFrame for integrity checking"""
        # Use shape, columns, and sample of data
        hash_input = f"{df.shape}_{','.join(df.columns.tolist())}"
        
        # Add sample of actual data (first and last 10 rows)
        if len(df) > 0:
            sample_data = pd.concat([df.head(10), df.tail(10)])
            hash_input += str(sample_data.values.tolist())
        
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _store_dataset_metadata(self, metadata: DatasetMetadata):
        """Store dataset metadata in database"""
        with self.SessionLocal() as session:
            db_metadata = DatasetMetadataDB(
                dataset_id=metadata.dataset_id,
                name=metadata.name,
                source_file=metadata.source_file,
                created_at=metadata.created_at,
                last_modified=metadata.last_modified,
                file_size_bytes=metadata.file_size_bytes,
                row_count=metadata.row_count,
                column_count=metadata.column_count,
                column_info=metadata.column_info,
                data_hash=metadata.data_hash,
                schema_version=metadata.schema_version,
                tags=metadata.tags,
                custom_metadata=metadata.custom_metadata
            )
            session.add(db_metadata)
            session.commit()
    
    def _store_transformation(self, record: TransformationRecord):
        """Store transformation record in database"""
        with self.SessionLocal() as session:
            db_record = TransformationHistoryDB(
                id=record.id,
                timestamp=record.timestamp,
                transformation_type=record.transformation_type.value,
                operation=record.operation,
                parameters=record.parameters,
                affected_columns=record.affected_columns,
                before_state=record.before_state,
                after_state=record.after_state,
                user_id=record.user_id,
                session_id=record.session_id,
                duration_seconds=record.duration_seconds,
                success=int(record.success),
                error_message=record.error_message
            )
            session.add(db_record)
            session.commit()
    
    def _store_audit_log(self, entry: AuditLogEntry):
        """Store audit log entry in database"""
        with self.SessionLocal() as session:
            db_entry = AuditLogDB(
                id=entry.id,
                timestamp=entry.timestamp,
                action=entry.action.value,
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                user_id=entry.user_id,
                session_id=entry.session_id,
                ip_address=entry.ip_address,
                user_agent=entry.user_agent,
                details=entry.details,
                success=int(entry.success),
                error_message=entry.error_message
            )
            session.add(db_entry)
            session.commit()