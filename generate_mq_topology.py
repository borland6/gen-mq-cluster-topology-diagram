#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBM MQ Cluster Topology Generator
自動分析 IBM MQ 配置檔案並生成 Mermaid 架構圖
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class MQClusterAnalyzer:
    """IBM MQ 叢集配置分析器"""
    
    def __init__(self):
        self.queue_managers = {}
        self.clusters = {}
        
    def parse_mqsc_file(self, filepath: str) -> Dict:
        """解析 MQSC 配置檔案"""
        print(f"正在分析檔案: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 合併斷行（以 + 結尾的行）
        content = self._merge_continuation_lines(content)
        
        # 提取 Queue Manager 名稱
        qm_name = self._extract_qm_name(content)
        if not qm_name:
            print(f"警告: 無法從 {filepath} 提取 Queue Manager 名稱")
            return None
            
        # 提取 REPOS 資訊
        repos = self._extract_repos(content)
        
        # 提取 CLUSRCVR 通道資訊
        clusrcvr = self._extract_clusrcvr(content)
        
        # 提取 CLUSSDR 通道資訊
        clussdr = self._extract_clussdr(content)
        
        qm_info = {
            'name': qm_name,
            'repos': repos,
            'clusrcvr': clusrcvr,
            'clussdr': clussdr,
            'role': 'FR' if repos else 'PR' if (clusrcvr or clussdr) else 'Standalone'
        }
        
        print(f"  - Queue Manager: {qm_name}")
        print(f"  - 角色: {qm_info['role']}")
        print(f"  - Clusters: {repos if repos else [c['cluster'] for c in clusrcvr]}")
        
        return qm_info
    
    def _merge_continuation_lines(self, content: str) -> str:
        """合併以 + 結尾的斷行"""
        lines = content.split('\n')
        merged_lines = []
        current_line = ""
        
        for line in lines:
            stripped = line.strip()
            if stripped.endswith('+'):
                current_line += stripped[:-1].strip() + " "
            else:
                current_line += stripped
                if current_line:
                    merged_lines.append(current_line)
                current_line = ""
        
        return '\n'.join(merged_lines)
    
    def _extract_qm_name(self, content: str) -> str:
        """提取 Queue Manager 名稱"""
        match = re.search(r'\* Queue manager name:\s*(\S+)', content)
        if match:
            return match.group(1)
        return None
    
    def _extract_repos(self, content: str) -> List[str]:
        """提取 REPOS 資訊"""
        repos = []
        match = re.search(r"REPOS\('([^']+)'\)", content)
        if match:
            repo_value = match.group(1).strip()
            if repo_value and repo_value != ' ':
                repos.append(repo_value)
        return repos
    
    def _extract_clusrcvr(self, content: str) -> List[Dict]:
        """提取 CLUSRCVR 通道資訊"""
        clusrcvr_list = []
        
        # 找出所有 CLUSRCVR 通道定義
        pattern = r"DEFINE CHANNEL\('([^']+)'\)\s+CHLTYPE\(CLUSRCVR\)(.*?)(?=DEFINE|$)"
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            channel_name = match.group(1)
            channel_def = match.group(2)
            
            # 提取 CLUSTER
            cluster_match = re.search(r"CLUSTER\('([^']+)'\)", channel_def)
            cluster = cluster_match.group(1) if cluster_match else ''
            
            # 提取 CONNAME
            conname_match = re.search(r"CONNAME\('([^']+)'\)", channel_def)
            conname = conname_match.group(1) if conname_match else ''
            
            if cluster and cluster.strip() and cluster.strip() != ' ':
                clusrcvr_list.append({
                    'channel': channel_name,
                    'cluster': cluster,
                    'conname': conname
                })
        
        return clusrcvr_list
    
    def _extract_clussdr(self, content: str) -> List[Dict]:
        """提取 CLUSSDR 通道資訊"""
        clussdr_list = []
        
        # 找出所有 CLUSSDR 通道定義
        pattern = r"DEFINE CHANNEL\('([^']+)'\)\s+CHLTYPE\(CLUSSDR\)(.*?)(?=DEFINE|$)"
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            channel_name = match.group(1)
            channel_def = match.group(2)
            
            # 提取 CLUSTER
            cluster_match = re.search(r"CLUSTER\('([^']+)'\)", channel_def)
            cluster = cluster_match.group(1) if cluster_match else ''
            
            # 提取 CONNAME
            conname_match = re.search(r"CONNAME\('([^']+)'\)", channel_def)
            conname = conname_match.group(1) if conname_match else ''
            
            if cluster and cluster.strip() and cluster.strip() != ' ':
                clussdr_list.append({
                    'channel': channel_name,
                    'cluster': cluster,
                    'conname': conname
                })
        
        return clussdr_list
    
    def analyze_directory(self, directory: str = '.') -> None:
        """分析目錄中的所有 .txt 檔案"""
        print(f"\n開始分析目錄: {directory}")
        print("=" * 60)
        
        txt_files = list(Path(directory).glob('*.txt'))
        
        if not txt_files:
            print(f"錯誤: 在 {directory} 目錄中找不到 .txt 檔案")
            return
        
        for filepath in txt_files:
            qm_info = self.parse_mqsc_file(str(filepath))
            if qm_info:
                self.queue_managers[qm_info['name']] = qm_info
                
                # 組織叢集資訊
                for repo in qm_info['repos']:
                    if repo not in self.clusters:
                        self.clusters[repo] = {'fr': [], 'pr': []}
                    self.clusters[repo]['fr'].append(qm_info['name'])
                
                for clusrcvr in qm_info['clusrcvr']:
                    cluster = clusrcvr['cluster']
                    if cluster not in self.clusters:
                        self.clusters[cluster] = {'fr': [], 'pr': []}
                    if qm_info['name'] not in self.clusters[cluster]['fr']:
                        self.clusters[cluster]['pr'].append(qm_info['name'])
        
        print("=" * 60)
        print(f"分析完成! 共找到 {len(self.queue_managers)} 個 Queue Managers")
    
    def generate_mermaid(self) -> str:
        """生成 Mermaid 架構圖"""
        lines = ["flowchart TB"]
        
        if not self.clusters:
            print("警告: 沒有找到任何叢集配置")
            return ""
        
        # 為每個叢集生成子圖
        for cluster_name, cluster_info in self.clusters.items():
            lines.append(f'    subgraph {cluster_name}["Cluster: {cluster_name}"]')
            
            # Full Repositories 子圖
            if cluster_info['fr']:
                lines.append(f'        subgraph FR_{cluster_name}["Full Repositories"]')
                for qm_name in cluster_info['fr']:
                    qm = self.queue_managers[qm_name]
                    conname = ''
                    for clusrcvr in qm['clusrcvr']:
                        if clusrcvr['cluster'] == cluster_name:
                            conname = clusrcvr['conname']
                            break
                    lines.append(f'            {qm_name}["{qm_name} (FR)<br>{conname}"]')
                lines.append('        end')
            
            # Partial Repositories 子圖
            if cluster_info['pr']:
                lines.append(f'        subgraph PR_{cluster_name}["Partial Repositories"]')
                for qm_name in cluster_info['pr']:
                    qm = self.queue_managers[qm_name]
                    conname = ''
                    for clusrcvr in qm['clusrcvr']:
                        if clusrcvr['cluster'] == cluster_name:
                            conname = clusrcvr['conname']
                            break
                    lines.append(f'            {qm_name}["{qm_name} (PR)<br>{conname}"]')
                lines.append('        end')
            
            # FR 之間的雙向連線
            fr_list = cluster_info['fr']
            for i in range(len(fr_list)):
                for j in range(i + 1, len(fr_list)):
                    lines.append(f'        {fr_list[i]} <==> {fr_list[j]}')
            
            # PR 到 FR 的連線
            for pr_qm in cluster_info['pr']:
                qm = self.queue_managers[pr_qm]
                for clussdr in qm['clussdr']:
                    if clussdr['cluster'] == cluster_name:
                        # 根據 CONNAME 找出目標 FR
                        target_fr = self._find_target_qm(clussdr['conname'], cluster_name)
                        if target_fr:
                            lines.append(f'        {pr_qm} -.->|CLUSSDR: {clussdr["channel"]}| {target_fr}')
            
            lines.append('    end')
        
        # 處理 Standalone Queue Managers
        standalone_qms = [qm for qm in self.queue_managers.values() if qm['role'] == 'Standalone']
        if standalone_qms:
            lines.append('    subgraph Standalone["Standalone Queue Managers"]')
            for qm in standalone_qms:
                lines.append(f'        {qm["name"]}["{qm["name"]}"]')
            lines.append('    end')
        
        return '\n'.join(lines)
    
    def _find_target_qm(self, conname: str, cluster: str) -> str:
        """根據 CONNAME 找出目標 Queue Manager"""
        for qm_name, qm_info in self.queue_managers.items():
            for clusrcvr in qm_info['clusrcvr']:
                if clusrcvr['cluster'] == cluster and clusrcvr['conname'] == conname:
                    return qm_name
        return None
    
    def save_mermaid(self, output_file: str = 'mq_topology.md') -> None:
        """儲存 Mermaid 圖表到檔案"""
        mermaid_code = self.generate_mermaid()
        
        if not mermaid_code:
            print("錯誤: 無法生成 Mermaid 圖表")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('# IBM MQ Cluster Topology\n\n')
            f.write('```mermaid\n')
            f.write(mermaid_code)
            f.write('\n```\n\n')
            
            # 添加摘要資訊
            f.write('## 摘要\n\n')
            for cluster_name, cluster_info in self.clusters.items():
                f.write(f'### Cluster: {cluster_name}\n\n')
                f.write(f'- **Full Repositories ({len(cluster_info["fr"])}):** {", ".join(cluster_info["fr"])}\n')
                f.write(f'- **Partial Repositories ({len(cluster_info["pr"])}):** {", ".join(cluster_info["pr"])}\n\n')
                
                for qm_name in cluster_info['fr'] + cluster_info['pr']:
                    qm = self.queue_managers[qm_name]
                    f.write(f'#### {qm_name} ({qm["role"]})\n')
                    for clusrcvr in qm['clusrcvr']:
                        if clusrcvr['cluster'] == cluster_name:
                            f.write(f'- CLUSRCVR: {clusrcvr["channel"]} @ {clusrcvr["conname"]}\n')
                    for clussdr in qm['clussdr']:
                        if clussdr['cluster'] == cluster_name:
                            f.write(f'- CLUSSDR: {clussdr["channel"]} -> {clussdr["conname"]}\n')
                    f.write('\n')
        
        print(f"\n[OK] Mermaid 圖表已儲存至: {output_file}")
        print(f"[OK] 您可以將此檔案內容複製到 Notion 或 Mermaid Live Editor 中預覽")


def main():
    """主程式"""
    print("=" * 60)
    print("IBM MQ Cluster Topology Generator")
    print("=" * 60)
    
    # 取得目錄參數
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'mq_topology.md'
    
    # 建立分析器
    analyzer = MQClusterAnalyzer()
    
    # 分析配置檔案
    analyzer.analyze_directory(directory)
    
    # 生成並儲存 Mermaid 圖表
    if analyzer.queue_managers:
        analyzer.save_mermaid(output_file)
        
        # 同時輸出到終端機
        print("\n" + "=" * 60)
        print("Mermaid 程式碼:")
        print("=" * 60)
        print("```mermaid")
        print(analyzer.generate_mermaid())
        print("```")
    else:
        print("\n錯誤: 沒有找到任何 Queue Manager 配置")


if __name__ == '__main__':
    main()

# Made with Bob
