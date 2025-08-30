#!/usr/bin/env python3
"""
Backup Manager for drxai
Automated backup system for workflow database and files.
"""

import os
import shutil
import sqlite3
import datetime
import gzip
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class BackupManager:
    """Manages automated backups of workflow database and files."""
    
    def __init__(self, db_path: str = "workflows.db", workflows_dir: str = "workflows", 
                 backup_dir: str = "backups"):
        self.db_path = Path(db_path)
        self.workflows_dir = Path(workflows_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_timestamp(self) -> str:
        """Create timestamp for backup files."""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def backup_database(self) -> str:
        """Create backup of SQLite database."""
        if not self.db_path.exists():
            print(f"❌ Database not found: {self.db_path}")
            return None
            
        timestamp = self.create_timestamp()
        backup_name = f"workflows_db_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create database backup using SQLite backup API
            source_conn = sqlite3.connect(str(self.db_path))
            backup_conn = sqlite3.connect(str(backup_path))
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            # Compress the backup
            compressed_path = backup_path.with_suffix('.db.gz')
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            # Remove uncompressed backup
            backup_path.unlink()
            
            print(f"✅ Database backup created: {compressed_path}")
            return str(compressed_path)
            
        except Exception as e:
            print(f"❌ Database backup failed: {e}")
            return None
            
    def backup_workflows(self) -> str:
        """Create backup of workflow files."""
        if not self.workflows_dir.exists():
            print(f"❌ Workflows directory not found: {self.workflows_dir}")
            return None
            
        timestamp = self.create_timestamp()
        backup_name = f"workflows_files_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create compressed archive
            shutil.make_archive(
                str(backup_path.with_suffix('')),
                'gztar',
                str(self.workflows_dir.parent),
                str(self.workflows_dir.name)
            )
            
            print(f"✅ Workflows backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Workflows backup failed: {e}")
            return None
            
    def backup_config(self) -> str:
        """Create backup of configuration files."""
        timestamp = self.create_timestamp()
        config_backup = self.backup_dir / f"config_{timestamp}.json"
        
        config_files = [
            "requirements.txt",
            "api_server.py",
            "workflow_db.py",
            "run.py",
            "import_workflows.py"
        ]
        
        config_data = {
            "timestamp": timestamp,
            "files": {}
        }
        
        for config_file in config_files:
            file_path = Path(config_file)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_data["files"][config_file] = {
                            "content": f.read(),
                            "size": file_path.stat().st_size,
                            "modified": datetime.datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat()
                        }
                except Exception as e:
                    print(f"⚠️  Could not backup {config_file}: {e}")
                    
        try:
            with open(config_backup, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
                
            print(f"✅ Configuration backup created: {config_backup}")
            return str(config_backup)
            
        except Exception as e:
            print(f"❌ Configuration backup failed: {e}")
            return None
            
    def create_full_backup(self) -> Dict[str, str]:
        """Create full backup of all components."""
        print("🔄 Starting full backup...")
        
        results = {
            "database": self.backup_database(),
            "workflows": self.backup_workflows(),
            "config": self.backup_config()
        }
        
        # Create backup manifest
        timestamp = self.create_timestamp()
        manifest_path = self.backup_dir / f"backup_manifest_{timestamp}.json"
        
        manifest = {
            "timestamp": timestamp,
            "backup_type": "full",
            "components": results,
            "stats": self.get_backup_stats()
        }
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
                
            print(f"📋 Backup manifest created: {manifest_path}")
            results["manifest"] = str(manifest_path)
            
        except Exception as e:
            print(f"⚠️  Could not create manifest: {e}")
            
        print("✅ Full backup completed!")
        return results
        
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get statistics about current data."""
        stats = {}
        
        # Database stats
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM workflows")
                stats["total_workflows"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM workflows WHERE active = 1")
                stats["active_workflows"] = cursor.fetchone()[0]
                
                conn.close()
                
            except Exception as e:
                print(f"⚠️  Could not get database stats: {e}")
                stats["database_error"] = str(e)
                
        # File stats
        if self.workflows_dir.exists():
            json_files = list(self.workflows_dir.glob("*.json"))
            stats["workflow_files"] = len(json_files)
            
            total_size = sum(f.stat().st_size for f in json_files)
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
        return stats
        
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                stat = backup_file.stat()
                
                backup_info = {
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": self.get_backup_type(backup_file.name)
                }
                
                backups.append(backup_info)
                
        return sorted(backups, key=lambda x: x["created"], reverse=True)
        
    def get_backup_type(self, filename: str) -> str:
        """Determine backup type from filename."""
        if "db_" in filename:
            return "database"
        elif "files_" in filename:
            return "workflows"
        elif "config_" in filename:
            return "configuration"
        elif "manifest_" in filename:
            return "manifest"
        else:
            return "unknown"
            
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backups older than specified days."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        removed_count = 0
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                file_date = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_date < cutoff_date:
                    try:
                        backup_file.unlink()
                        removed_count += 1
                        print(f"🗑️  Removed old backup: {backup_file.name}")
                    except Exception as e:
                        print(f"⚠️  Could not remove {backup_file.name}: {e}")
                        
        print(f"✅ Cleanup completed: {removed_count} old backups removed")
        
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup."""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
            
        try:
            # Create backup of current database
            if self.db_path.exists():
                current_backup = self.db_path.with_suffix('.db.backup')
                shutil.copy2(self.db_path, current_backup)
                print(f"📋 Current database backed up to: {current_backup}")
                
            # Restore from compressed backup
            if backup_file.suffix == '.gz':
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(self.db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_file, self.db_path)
                
            print(f"✅ Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Database restore failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Backup management for drxai")
    parser.add_argument("--action", choices=['backup', 'list', 'cleanup', 'restore'], 
                       default='backup', help="Action to perform")
    parser.add_argument("--type", choices=['full', 'database', 'workflows', 'config'], 
                       default='full', help="Backup type")
    parser.add_argument("--restore-file", help="Backup file to restore from")
    parser.add_argument("--keep-days", type=int, default=30, help="Days to keep backups")
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.action == 'backup':
        if args.type == 'full':
            manager.create_full_backup()
        elif args.type == 'database':
            manager.backup_database()
        elif args.type == 'workflows':
            manager.backup_workflows()
        elif args.type == 'config':
            manager.backup_config()
            
    elif args.action == 'list':
        backups = manager.list_backups()
        print(f"\n📋 Found {len(backups)} backups:\n")
        
        for backup in backups:
            print(f"  {backup['name']}")
            print(f"    Type: {backup['type']}")
            print(f"    Size: {backup['size_mb']} MB")
            print(f"    Created: {backup['created']}")
            print()
            
    elif args.action == 'cleanup':
        manager.cleanup_old_backups(args.keep_days)
        
    elif args.action == 'restore':
        if not args.restore_file:
            print("❌ Please specify --restore-file")
            return
            
        manager.restore_database(args.restore_file)

if __name__ == "__main__":
    main()

