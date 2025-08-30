#!/usr/bin/env python3
"""
File Organizer Tool for drxai
Organizes workflow files by categories, types, and other criteria.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import argparse

class FileOrganizer:
    """Organizes workflow files into structured directories."""
    
    def __init__(self, source_dir: str = "workflows", output_dir: str = "organized_workflows"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.stats = defaultdict(int)
        
    def analyze_workflow(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a workflow file and extract metadata for organization."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error reading {file_path}: {str(e)}")
            return None
            
        nodes = data.get('nodes', [])
        
        # Extract metadata
        metadata = {
            'filename': file_path.name,
            'active': data.get('active', False),
            'node_count': len(nodes),
            'trigger_type': 'Manual',
            'integrations': set(),
            'categories': set(),
            'complexity': 'low'
        }
        
        # Analyze nodes for categorization
        for node in nodes:
            node_type = node.get('type', '').lower()
            
            # Determine trigger type
            if 'webhook' in node_type:
                metadata['trigger_type'] = 'Webhook'
            elif 'cron' in node_type or 'schedule' in node_type:
                metadata['trigger_type'] = 'Scheduled'
            elif 'trigger' in node_type and metadata['trigger_type'] == 'Manual':
                metadata['trigger_type'] = 'Triggered'
                
            # Categorize by service type
            if any(x in node_type for x in ['telegram', 'discord', 'slack', 'whatsapp']):
                metadata['categories'].add('messaging')
                metadata['integrations'].add(self.extract_service_name(node_type))
            elif any(x in node_type for x in ['postgres', 'mysql', 'mongodb', 'airtable']):
                metadata['categories'].add('database')
                metadata['integrations'].add(self.extract_service_name(node_type))
            elif any(x in node_type for x in ['openai', 'anthropic', 'huggingface']):
                metadata['categories'].add('ai_ml')
                metadata['integrations'].add(self.extract_service_name(node_type))
            elif any(x in node_type for x in ['gmail', 'mailjet', 'outlook']):
                metadata['categories'].add('email')
                metadata['integrations'].add(self.extract_service_name(node_type))
            elif any(x in node_type for x in ['googledrive', 'dropbox', 'onedrive']):
                metadata['categories'].add('storage')
                metadata['integrations'].add(self.extract_service_name(node_type))
            elif any(x in node_type for x in ['github', 'gitlab', 'jira']):
                metadata['categories'].add('development')
                metadata['integrations'].add(self.extract_service_name(node_type))
            elif any(x in node_type for x in ['http', 'webhook', 'api']):
                metadata['categories'].add('api')
                
        # Determine complexity
        if metadata['node_count'] <= 5:
            metadata['complexity'] = 'low'
        elif metadata['node_count'] <= 15:
            metadata['complexity'] = 'medium'
        else:
            metadata['complexity'] = 'high'
            
        # Convert sets to lists for JSON serialization
        metadata['integrations'] = list(metadata['integrations'])
        metadata['categories'] = list(metadata['categories'])
        
        return metadata
        
    def extract_service_name(self, node_type: str) -> str:
        """Extract service name from node type."""
        service_mappings = {
            'telegram': 'Telegram',
            'discord': 'Discord',
            'slack': 'Slack',
            'whatsapp': 'WhatsApp',
            'gmail': 'Gmail',
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'openai': 'OpenAI',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'jira': 'Jira'
        }
        
        for key, value in service_mappings.items():
            if key in node_type.lower():
                return value
                
        return node_type.replace('dr.x-nodes-base.', '').title()
        
    def organize_by_category(self):
        """Organize files by service category."""
        print("🗂️  Organizing workflows by category...")
        
        category_dir = self.output_dir / "by_category"
        category_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.source_dir.glob("*.json"):
            metadata = self.analyze_workflow(file_path)
            if not metadata:
                continue
                
            categories = metadata['categories']
            if not categories:
                categories = ['uncategorized']
                
            for category in categories:
                dest_dir = category_dir / category
                dest_dir.mkdir(exist_ok=True)
                
                dest_file = dest_dir / file_path.name
                shutil.copy2(file_path, dest_file)
                self.stats[f'category_{category}'] += 1
                
        print(f"✅ Organized {sum(self.stats[k] for k in self.stats if k.startswith('category_'))} files by category")
        
    def organize_by_complexity(self):
        """Organize files by complexity level."""
        print("📊 Organizing workflows by complexity...")
        
        complexity_dir = self.output_dir / "by_complexity"
        complexity_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.source_dir.glob("*.json"):
            metadata = self.analyze_workflow(file_path)
            if not metadata:
                continue
                
            complexity = metadata['complexity']
            dest_dir = complexity_dir / complexity
            dest_dir.mkdir(exist_ok=True)
            
            dest_file = dest_dir / file_path.name
            shutil.copy2(file_path, dest_file)
            self.stats[f'complexity_{complexity}'] += 1
            
        print(f"✅ Organized {sum(self.stats[k] for k in self.stats if k.startswith('complexity_'))} files by complexity")
        
    def organize_by_trigger(self):
        """Organize files by trigger type."""
        print("🔄 Organizing workflows by trigger type...")
        
        trigger_dir = self.output_dir / "by_trigger"
        trigger_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.source_dir.glob("*.json"):
            metadata = self.analyze_workflow(file_path)
            if not metadata:
                continue
                
            trigger = metadata['trigger_type'].lower().replace(' ', '_')
            dest_dir = trigger_dir / trigger
            dest_dir.mkdir(exist_ok=True)
            
            dest_file = dest_dir / file_path.name
            shutil.copy2(file_path, dest_file)
            self.stats[f'trigger_{trigger}'] += 1
            
        print(f"✅ Organized {sum(self.stats[k] for k in self.stats if k.startswith('trigger_'))} files by trigger type")
        
    def organize_by_integration(self):
        """Organize files by main integration."""
        print("🔗 Organizing workflows by integration...")
        
        integration_dir = self.output_dir / "by_integration"
        integration_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.source_dir.glob("*.json"):
            metadata = self.analyze_workflow(file_path)
            if not metadata:
                continue
                
            integrations = metadata['integrations']
            if not integrations:
                integrations = ['no_integration']
                
            for integration in integrations:
                safe_name = integration.lower().replace(' ', '_').replace('.', '_')
                dest_dir = integration_dir / safe_name
                dest_dir.mkdir(exist_ok=True)
                
                dest_file = dest_dir / file_path.name
                shutil.copy2(file_path, dest_file)
                self.stats[f'integration_{safe_name}'] += 1
                
        print(f"✅ Organized {sum(self.stats[k] for k in self.stats if k.startswith('integration_'))} files by integration")
        
    def create_index_files(self):
        """Create index files for each organized directory."""
        print("📝 Creating index files...")
        
        for org_type in ['by_category', 'by_complexity', 'by_trigger', 'by_integration']:
            org_dir = self.output_dir / org_type
            if not org_dir.exists():
                continue
                
            for subdir in org_dir.iterdir():
                if not subdir.is_dir():
                    continue
                    
                index_file = subdir / "README.md"
                files = list(subdir.glob("*.json"))
                
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {subdir.name.replace('_', ' ').title()}\n\n")
                    f.write(f"Total workflows: {len(files)}\n\n")
                    f.write("## Files\n\n")
                    
                    for file_path in sorted(files):
                        f.write(f"- [{file_path.name}](./{file_path.name})\n")
                        
        print("✅ Created index files")
        
    def generate_report(self):
        """Generate organization report."""
        report_file = self.output_dir / "organization_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Workflow Organization Report\n\n")
            f.write(f"Generated on: {Path().cwd()}\n")
            f.write(f"Source directory: {self.source_dir}\n")
            f.write(f"Output directory: {self.output_dir}\n\n")
            
            f.write("## Statistics\n\n")
            
            # Group stats by type
            categories = [k for k in self.stats if k.startswith('category_')]
            complexities = [k for k in self.stats if k.startswith('complexity_')]
            triggers = [k for k in self.stats if k.startswith('trigger_')]
            integrations = [k for k in self.stats if k.startswith('integration_')]
            
            if categories:
                f.write("### By Category\n")
                for key in sorted(categories):
                    name = key.replace('category_', '').replace('_', ' ').title()
                    f.write(f"- {name}: {self.stats[key]} files\n")
                f.write("\n")
                
            if complexities:
                f.write("### By Complexity\n")
                for key in sorted(complexities):
                    name = key.replace('complexity_', '').replace('_', ' ').title()
                    f.write(f"- {name}: {self.stats[key]} files\n")
                f.write("\n")
                
            if triggers:
                f.write("### By Trigger Type\n")
                for key in sorted(triggers):
                    name = key.replace('trigger_', '').replace('_', ' ').title()
                    f.write(f"- {name}: {self.stats[key]} files\n")
                f.write("\n")
                
            if integrations:
                f.write("### By Integration\n")
                for key in sorted(integrations):
                    name = key.replace('integration_', '').replace('_', ' ').title()
                    f.write(f"- {name}: {self.stats[key]} files\n")
                f.write("\n")
                
        print(f"📊 Generated report: {report_file}")
        
    def organize_all(self):
        """Run all organization methods."""
        print("🚀 Starting workflow organization...")
        
        # Clear output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run organization methods
        self.organize_by_category()
        self.organize_by_complexity()
        self.organize_by_trigger()
        self.organize_by_integration()
        
        # Create documentation
        self.create_index_files()
        self.generate_report()
        
        print(f"✅ Organization complete! Check {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Organize workflow files")
    parser.add_argument("--source", default="workflows", help="Source directory")
    parser.add_argument("--output", default="organized_workflows", help="Output directory")
    parser.add_argument("--method", choices=['all', 'category', 'complexity', 'trigger', 'integration'], 
                       default='all', help="Organization method")
    
    args = parser.parse_args()
    
    organizer = FileOrganizer(args.source, args.output)
    
    if args.method == 'all':
        organizer.organize_all()
    elif args.method == 'category':
        organizer.organize_by_category()
    elif args.method == 'complexity':
        organizer.organize_by_complexity()
    elif args.method == 'trigger':
        organizer.organize_by_trigger()
    elif args.method == 'integration':
        organizer.organize_by_integration()

if __name__ == "__main__":
    main()

