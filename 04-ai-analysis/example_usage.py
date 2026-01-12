"""
Example usage script for AI Analysis
Demonstrates how to use ML models for analysis
"""

import pandas as pd
import numpy as np
from src.preprocessing.data_loader import DataLoader
from src.preprocessing.feature_engineering import FeatureEngineer
from src.models.classifier import MLClassifier

def create_sample_data():
    """Create sample data for demonstration"""
    np.random.seed(42)
    n_samples = 100
    
    # Generate synthetic data
    data = {
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.randn(n_samples),
        'feature3': np.random.randn(n_samples),
        'feature4': np.random.choice(['A', 'B', 'C'], n_samples),
        'target': np.random.choice([0, 1], n_samples)
    }
    
    df = pd.DataFrame(data)
    return df

def main():
    """Example ML workflow"""
    
    print("=" * 60)
    print("AI Analysis - Example Usage")
    print("=" * 60)
    
    # Step 1: Load Data
    print("\n1. Data Loading")
    print("-" * 60)
    print("Creating sample data...")
    df = create_sample_data()
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nFirst few rows:")
    print(df.head())
    
    # Step 2: Feature Engineering
    print("\n2. Feature Engineering")
    print("-" * 60)
    engineer = FeatureEngineer()
    
    # Handle missing values
    df_cleaned = engineer.handle_missing_values(df)
    print("✓ Missing values handled")
    
    # Encode categorical variables
    df_encoded = engineer.encode_categorical(df_cleaned, columns=['feature4'], method='label')
    print("✓ Categorical variables encoded")
    
    # Scale features
    numeric_cols = ['feature1', 'feature2', 'feature3']
    df_scaled = engineer.scale_features(df_encoded, columns=numeric_cols, fit=True)
    print("✓ Features scaled")
    
    # Step 3: Prepare Data for Training
    print("\n3. Data Preparation")
    print("-" * 60)
    X = df_scaled.drop(columns=['target'])
    y = df_scaled['target']
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    # Step 4: Train Model
    print("\n4. Model Training")
    print("-" * 60)
    
    # Train Random Forest
    print("Training Random Forest Classifier...")
    rf_classifier = MLClassifier(algorithm='random_forest', n_estimators=50, random_state=42)
    training_results = rf_classifier.train(X, y, validation_split=0.2)
    
    print(f"\nTraining Results:")
    print(f"  Accuracy: {training_results['accuracy']:.4f}")
    print(f"  Precision: {training_results['precision']:.4f}")
    print(f"  Recall: {training_results['recall']:.4f}")
    print(f"  F1 Score: {training_results['f1_score']:.4f}")
    
    # Feature Importance
    if rf_classifier.feature_importance_ is not None:
        print(f"\nTop Features:")
        for feature, importance in rf_classifier.feature_importance_.head().items():
            print(f"  {feature}: {importance:.4f}")
    
    # Step 5: Cross-Validation
    print("\n5. Cross-Validation")
    print("-" * 60)
    cv_results = rf_classifier.cross_validate(X, y, cv=5)
    print(f"Mean Accuracy: {cv_results['mean_accuracy']:.4f} ± {cv_results['std_accuracy']:.4f}")
    
    # Step 6: Make Predictions
    print("\n6. Making Predictions")
    print("-" * 60)
    sample_data = X.head(5)
    predictions = rf_classifier.predict(sample_data)
    probabilities = rf_classifier.predict_proba(sample_data)
    
    print("Sample Predictions:")
    for i, (idx, pred) in enumerate(zip(sample_data.index, predictions)):
        prob = probabilities[i][int(pred)]
        print(f"  Sample {idx}: Prediction={pred}, Confidence={prob:.4f}")
    
    # Step 7: Save Model
    print("\n7. Model Persistence")
    print("-" * 60)
    model_path = 'models/saved_models/example_model.pkl'
    import os
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    rf_classifier.save_model(model_path)
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Use predictor.py to load and use saved models")
    print("2. Deploy model as API using FastAPI")
    print("3. Integrate with MLflow for experiment tracking")
    print("4. Create visualizations and analysis reports")
    print("=" * 60)

if __name__ == "__main__":
    main()
