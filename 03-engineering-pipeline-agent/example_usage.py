"""
Example usage script for Engineering Pipeline Agent
Demonstrates how to use the orchestrator agent
"""

from agents.orchestrator_agent import OrchestratorAgent, PipelineStage

def main():
    """Example pipeline execution"""
    
    print("=" * 60)
    print("Engineering Pipeline Agent - Example Usage")
    print("=" * 60)
    
    # Configuration
    config = {
        'run_tests': True,
        'run_quality_checks': True,
        'stop_on_failure': True
    }
    
    project_config = {
        'name': 'example-web-app',
        'branch': 'main',
        'environment': 'production',
        'version': '1.0.0'
    }
    
    print(f"\nProject: {project_config['name']}")
    print(f"Branch: {project_config['branch']}")
    print(f"Environment: {project_config['environment']}")
    
    # Initialize orchestrator
    print("\nInitializing Orchestrator Agent...")
    orchestrator = OrchestratorAgent(config)
    
    # Execute pipeline
    print("\nExecuting Pipeline...")
    print("-" * 60)
    result = orchestrator.execute_pipeline(project_config)
    
    # Display results
    print("\n" + "=" * 60)
    print("Pipeline Execution Summary")
    print("=" * 60)
    print(f"Project: {result['project']}")
    print(f"Status: {result['pipeline_status'].upper()}")
    print(f"Total Time: {result['total_time_seconds']:.2f} seconds")
    print(f"Stages Completed: {result['stages_successful']}/{result['stages_total']}")
    
    if result['successful_stages']:
        print(f"\nSuccessful Stages:")
        for stage in result['successful_stages']:
            stage_result = result['stage_results'][stage]
            print(f"  ✓ {stage}: {stage_result['status']} ({stage_result['execution_time']:.2f}s)")
    
    if result['failed_stages']:
        print(f"\nFailed Stages:")
        for stage in result['failed_stages']:
            stage_result = result['stage_results'][stage]
            print(f"  ✗ {stage}: {stage_result['status']}")
            if stage_result.get('error'):
                print(f"    Error: {stage_result['error']}")
    
    print("\n" + "=" * 60)
    print("Pipeline Stages:")
    print("=" * 60)
    stages = [
        "1. SOURCE   - Checkout code",
        "2. BUILD    - Compile and build artifacts",
        "3. TEST     - Run automated tests",
        "4. QUALITY  - Code quality checks",
        "5. PACKAGE  - Create containers/images",
        "6. DEPLOY   - Deploy to environment",
        "7. VERIFY   - Post-deployment validation",
        "8. MONITOR  - Continuous monitoring"
    ]
    for stage in stages:
        print(f"  {stage}")
    
    print("\n" + "=" * 60)
    print("To use with CI/CD:")
    print("1. Configure pipelines in pipelines/ directory")
    print("2. Use deploy.sh script for deployments")
    print("3. Integrate with Jenkins, GitHub Actions, or GitLab CI")
    print("=" * 60)

if __name__ == "__main__":
    main()
