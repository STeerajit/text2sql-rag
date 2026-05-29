#!/usr/bin/env python3
"""
Performance Dashboard Generator
Create HTML dashboard from evaluation results
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class DashboardGenerator:
    """Generate performance dashboard from evaluation results"""
    
    def __init__(self):
        self.results_dir = "results"
        self.dashboard_dir = "dashboard"
        
        # Create dashboard directory
        os.makedirs(self.dashboard_dir, exist_ok=True)
        
        # Set plot style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def load_evaluation_results(self) -> Dict[str, List[Dict]]:
        """Load all evaluation results from files"""
        results = {
            "performance": [],
            "llm_evaluation": [],
            "model_comparison": [],
            "comprehensive": []
        }
        
        # Find all result files
        result_files = glob.glob(f"{self.results_dir}/**/*.json", recursive=True)
        
        for file_path in result_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Categorize results based on filename
                filename = os.path.basename(file_path)
                if "performance_test" in filename:
                    results["performance"].append(data)
                elif "llm_evaluation" in filename:
                    results["llm_evaluation"].append(data)
                elif "model_comparison" in filename:
                    results["model_comparison"].append(data)
                elif "comprehensive" in filename:
                    results["comprehensive"].append(data)
                    
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return results
    
    def create_performance_plots(self, results: Dict[str, List[Dict]]) -> List[str]:
        """Create performance visualization plots"""
        plot_files = []
        
        # 1. LLM Performance Over Time
        if results["llm_evaluation"]:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('LLM Performance Metrics', fontsize=16)
            
            # Extract data
            timestamps = []
            similarities = []
            latencies = []
            accuracies = []
            
            for result in results["llm_evaluation"]:
                if "summary" in result:
                    timestamps.append(result.get("timestamp", ""))
                    similarities.append(result["summary"].get("avg_similarity", 0))
                    latencies.append(result["summary"].get("avg_latency", 0))
                    accuracies.append(result["summary"].get("type_accuracy", 0))
            
            if timestamps:
                # Similarity over time
                axes[0,0].plot(range(len(similarities)), similarities, 'o-')
                axes[0,0].set_title('SQL Similarity Over Time')
                axes[0,0].set_ylabel('Similarity Score')
                axes[0,0].grid(True)
                
                # Latency over time
                axes[0,1].plot(range(len(latencies)), latencies, 'o-', color='orange')
                axes[0,1].set_title('Response Latency Over Time')
                axes[0,1].set_ylabel('Latency (seconds)')
                axes[0,1].grid(True)
                
                # Type accuracy over time
                axes[1,0].plot(range(len(accuracies)), accuracies, 'o-', color='green')
                axes[1,0].set_title('Type Classification Accuracy')
                axes[1,0].set_ylabel('Accuracy')
                axes[1,0].grid(True)
                
                # Performance distribution
                axes[1,1].hist([similarities, latencies, accuracies], 
                              label=['Similarity', 'Latency', 'Accuracy'], 
                              alpha=0.7)
                axes[1,1].set_title('Performance Distribution')
                axes[1,1].legend()
                axes[1,1].grid(True)
            
            plt.tight_layout()
            plot_file = f"{self.dashboard_dir}/llm_performance.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(plot_file)
        
        # 2. Query Type Performance
        if results["comprehensive"]:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Aggregate query type performance
            type_performance = {}
            for result in results["comprehensive"]:
                if "results" in result:
                    for test_result in result["results"]:
                        query_type = test_result.get("query_type", "unknown")
                        similarity = test_result.get("exact_match", 0)
                        
                        if query_type not in type_performance:
                            type_performance[query_type] = []
                        type_performance[query_type].append(similarity)
            
            if type_performance:
                types = list(type_performance.keys())
                avg_scores = [sum(scores)/len(scores) for scores in type_performance.values()]
                
                bars = ax.bar(types, avg_scores, color='skyblue', alpha=0.8)
                ax.set_title('Performance by Query Type')
                ax.set_ylabel('Average Similarity Score')
                ax.set_ylim(0, 1)
                
                # Add value labels on bars
                for bar, score in zip(bars, avg_scores):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{score:.3f}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                plot_file = f"{self.dashboard_dir}/query_type_performance.png"
                plt.savefig(plot_file, dpi=300, bbox_inches='tight')
                plt.close()
                plot_files.append(plot_file)
        
        return plot_files
    
    def generate_html_dashboard(self, results: Dict[str, List[Dict]], plot_files: List[str]) -> str:
        """Generate HTML dashboard"""
        
        # Calculate summary statistics
        total_tests = 0
        successful_tests = 0
        avg_similarity = 0
        avg_latency = 0
        
        for result_type, result_list in results.items():
            for result in result_list:
                if "summary" in result:
                    summary = result["summary"]
                    total_tests += summary.get("total_tests", 0)
                    successful_tests += summary.get("successful_tests", 0)
                    avg_similarity += summary.get("avg_similarity", 0)
                    avg_latency += summary.get("avg_latency", 0)
        
        if len([r for result_list in results.values() for r in result_list]) > 0:
            avg_similarity /= len([r for result_list in results.values() for r in result_list])
            avg_latency /= len([r for result_list in results.values() for r in result_list])
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Text2SQL RAG Performance Dashboard</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                .section {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                .plot {{ text-align: center; margin: 20px 0; }}
                .plot img {{ max-width: 100%; height: auto; border-radius: 5px; }}
                .status-good {{ color: #27ae60; }}
                .status-warning {{ color: #f39c12; }}
                .status-error {{ color: #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Text2SQL RAG Performance Dashboard</h1>
                <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number status-{'good' if success_rate >= 90 else 'warning' if success_rate >= 70 else 'error'}">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_similarity:.3f}</div>
                    <div class="stat-label">Avg Similarity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_latency:.2f}s</div>
                    <div class="stat-label">Avg Latency</div>
                </div>
            </div>
        """
        
        # Add plots
        if plot_files:
            html += '<div class="section"><h2>Performance Visualizations</h2>'
            for plot_file in plot_files:
                plot_name = os.path.basename(plot_file)
                html += f'<div class="plot"><h3>{plot_name.replace("_", " ").replace(".png", "").title()}</h3>'
                html += f'<img src="{plot_name}" alt="{plot_name}"></div>'
            html += '</div>'
        
        # Add recent results table
        html += '''
            <div class="section">
                <h2>Recent Test Results</h2>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Test Type</th>
                        <th>Total Tests</th>
                        <th>Success Rate</th>
                        <th>Avg Similarity</th>
                        <th>Avg Latency</th>
                    </tr>
        '''
        
        # Add recent results
        all_results = []
        for result_type, result_list in results.items():
            for result in result_list:
                if "summary" in result:
                    all_results.append((result_type, result))
        
        # Sort by timestamp (most recent first)
        all_results.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)
        
        for result_type, result in all_results[:10]:  # Show last 10 results
            summary = result["summary"]
            timestamp = result.get("timestamp", "N/A")
            total = summary.get("total_tests", 0)
            successful = summary.get("successful_tests", 0)
            success_rate_row = (successful / total * 100) if total > 0 else 0
            similarity = summary.get("avg_similarity", 0)
            latency = summary.get("avg_latency", 0)
            
            html += f'''
                <tr>
                    <td>{timestamp}</td>
                    <td>{result_type.title()}</td>
                    <td>{total}</td>
                    <td class="status-{'good' if success_rate_row >= 90 else 'warning' if success_rate_row >= 70 else 'error'}">{success_rate_row:.1f}%</td>
                    <td>{similarity:.3f}</td>
                    <td>{latency:.3f}s</td>
                </tr>
            '''
        
        html += '''
                </table>
            </div>
            
            <div class="section">
                <h2>System Status</h2>
                <p><strong>Overall Status:</strong> 
                <span class="status-good">Healthy</span></p>
                <p><strong>Last Test:</strong> {}</p>
                <p><strong>Performance Score:</strong> {:.2f}/5.0</p>
            </div>
        </body>
        </html>
        '''.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            min(5.0, (success_rate/20 + avg_similarity*2 + (5-avg_latency)))
        )
        
        dashboard_file = f"{self.dashboard_dir}/index.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return dashboard_file
    
    def generate_dashboard(self) -> str:
        """Generate complete dashboard"""
        print("Generating Performance Dashboard...")
        
        # Load results
        results = self.load_evaluation_results()
        print(f"Loaded results: {sum(len(r) for r in results.values())} files")
        
        # Create plots
        plot_files = self.create_performance_plots(results)
        print(f"Generated {len(plot_files)} plots")
        
        # Generate HTML dashboard
        dashboard_file = self.generate_html_dashboard(results, plot_files)
        print(f"Dashboard generated: {dashboard_file}")
        
        return dashboard_file

def main():
    """Main function"""
    generator = DashboardGenerator()
    dashboard_file = generator.generate_dashboard()
    
    print(f"\nDashboard ready: {dashboard_file}")
    print("Open in browser to view performance metrics")

if __name__ == "__main__":
    main()


